"""The desk's tools: thin HTTP clients for the portal and ServiceNow. Each returns a small dict (the agent never sees raw dumps).

Read tools are called freely. Write tools (create incident, access request, work note) are only reached through the
workflow's raise step, behind a confirmation.
"""
from __future__ import annotations

from datetime import timedelta

import httpx

from desk import config
from desk.world import iso, now


def _portal() -> httpx.Client:
    return httpx.Client(base_url=config.PORTAL_API, timeout=15, trust_env=False)


def _sn() -> httpx.Client:
    return httpx.Client(base_url=config.SERVICENOW_API, auth=(config.SERVICENOW_USER, config.SERVICENOW_PASS), timeout=20, trust_env=False)


def _get(client_fn, path: str, **params) -> dict:
    try:
        with client_fn() as c:
            r = c.get(path, params={k: v for k, v in params.items() if v is not None})
            if r.status_code == 404:
                return {"error": "not_found", "path": path}
            r.raise_for_status()
            return r.json()
    except httpx.HTTPError as e:
        return {"error": "unavailable", "detail": str(e)[:120]}


# ---------------- portal ----------------
def get_user_access(user_id: str) -> dict:
    """Role, region, lock and MFA state, delegation and effective permissions for one portal user."""
    return _get(_portal, f"/api/v1/users/{user_id}/access")


def check_permission(user_id: str, action: str) -> dict:
    """Whether the user may perform `action` (e.g. intake.submit) and exactly why not."""
    return _get(_portal, "/api/v1/permissions/check", user=user_id, action=action)


def get_intake_request(request_id: str) -> dict:
    """Status, service type, urgency, routing and dates for one intake request (IR-YYYY-NNNNN)."""
    return _get(_portal, f"/api/v1/intake-requests/{request_id}")


def list_my_requests(user_id: str) -> dict:
    return _get(_portal, "/api/v1/intake-requests", submittedBy=user_id)


def explain_routing(request_id: str) -> dict:
    """Which routing rule placed the request in its queue, which queue it should be in, and whether it is misrouted."""
    return _get(_portal, f"/api/v1/routing/explain/{request_id}")


def get_routing_rules(region: str | None = None, service_type: str | None = None) -> dict:
    return _get(_portal, "/api/v1/routing/rules", region=region, service_type=service_type)


# ---------------- ServiceNow ----------------
def sn_live_incidents(keyword: str, hours: int = config.LIVE_WINDOW_HOURS, region: str | None = None) -> dict:
    """Incidents opened in the last `hours` whose text mentions `keyword`, plus any open major incident that matches."""
    since = iso(now() - timedelta(hours=hours))
    q = f"sys_created_on>={since}^short_descriptionLIKE{keyword}^ORdescriptionLIKE{keyword}"
    if region:
        q += f"^u_regionIN{region},ALL"
    q += "^ORDERBYDESCsys_created_on"
    fields = "number,short_description,description,priority,state,active,u_region,sys_created_on,parent_incident,major_incident,work_notes"
    res = _get(_sn, "/api/now/table/incident", sysparm_query=q, sysparm_fields=fields, sysparm_limit=50)
    if "error" in res:
        return res
    rows = res["result"]
    majors = [r for r in rows if r.get("major_incident") == "true" and r.get("active") == "true"]
    parents = {r["parent_incident"] for r in rows if r.get("parent_incident")}
    if parents - {m["number"] for m in majors}:
        for p in parents:
            got = _get(_sn, f"/api/now/table/incident/{p}")
            if "result" in got and got["result"].get("active") == "true":
                majors.append(got["result"])
    return {"keyword": keyword, "hours": hours, "since": since, "count": len(rows), "open": sum(r["active"] == "true" for r in rows),
            "major_incidents": [{k: m.get(k) for k in ("number", "short_description", "description", "priority", "state", "sys_created_on", "work_notes")}
                                for m in majors],
            "recent": [{k: r.get(k) for k in ("number", "short_description", "priority", "state", "u_region", "sys_created_on")} for r in rows[:8]]}


def sn_region_status(region: str, hours: int = config.LIVE_WINDOW_HOURS) -> dict:
    """Everything open in a region (and platform-wide) in the window: the director's 'is anything wrong right now?'."""
    since = iso(now() - timedelta(hours=hours))
    q = f"sys_created_on>={since}^active=true^u_regionIN{region},ALL^ORDERBYDESCpriority"
    res = _get(_sn, "/api/now/table/incident", sysparm_query=q, sysparm_fields="number,short_description,priority,u_region,major_incident,parent_incident", sysparm_limit=200)
    if "error" in res:
        return res
    rows = res["result"]
    return {"region": region, "open": len(rows), "major_incidents": [r for r in rows if r.get("major_incident") == "true"],
            "by_priority": {p: sum(r["priority"] == p for r in rows) for p in ("P1", "P2", "P3", "P4")}}


def sn_find_open_duplicate(caller: str, category: str, region: str, subcategory: str | None = None) -> dict:
    """Desk dedup rule: the same caller + category within 4 h, or an open P1/P2 on the same category and subcategory in the
    caller's region (or platform-wide). The oldest match wins; the new report becomes a work note on it."""
    since = iso(now() - timedelta(hours=config.DEDUP_WINDOW_HOURS))
    sub = f"^subcategory={subcategory}" if subcategory else ""
    queries = [f"active=true^category={category}^sys_created_on>={since}^caller_id={caller}",
               f"active=true^category={category}{sub}^priorityINP1,P2^u_regionIN{region},ALL"]
    found = []
    for q in queries:
        res = _get(_sn, "/api/now/table/incident", sysparm_query=q + "^ORDERBYsys_created_on",
                   sysparm_fields="number,sys_id,short_description,priority,sys_created_on,caller_id", sysparm_limit=5)
        found += res.get("result", [])
    found.sort(key=lambda r: r["sys_created_on"])
    return {"duplicate": found[0] if found else None, "candidates": len(found)}


def sn_create_incident(short_description: str, description: str, category: str, subcategory: str, caller: str, region: str,
                       role: str, impact: int = 3, urgency: int = 3, request_id: str = "", work_notes: str = "") -> dict:
    with _sn() as c:
        r = c.post("/api/now/table/incident", json={"short_description": short_description[:160], "description": description,
                                                     "category": category, "subcategory": subcategory, "caller_id": caller, "u_region": region,
                                                     "u_portal_user_role": role, "impact": impact, "urgency": urgency, "u_request_id": request_id,
                                                     "contact_type": "chatbot", "assignment_group": "Service Desk", "work_notes": work_notes})
        r.raise_for_status()
        return r.json()["result"]


def sn_create_access_request(requested_for: str, item: str, approver: str, description: str) -> dict:
    with _sn() as c:
        r = c.post("/api/now/table/sc_request", json={"requested_for": requested_for, "item": item, "approver": approver,
                                                       "short_description": item, "description": description})
        r.raise_for_status()
        return r.json()["result"]


def sn_add_work_note(number: str, text: str) -> dict:
    with _sn() as c:
        r = c.patch(f"/api/now/table/incident/{number}", json={"work_notes": text})
        r.raise_for_status()
        return r.json()["result"]
