"""Prior Auth Portal mock: users and access, a permission check, the routing rule table and a routing explainer.

Endpoints (all GET): /health, /api/v1/users, /api/v1/users/{id}, /api/v1/users/{id}/access,
/api/v1/permissions/check?user=&action=, /api/v1/intake-requests/{id}, /api/v1/intake-requests?submittedBy=,
/api/v1/routing/rules?region=&service_type=, /api/v1/routing/explain/{request_id}
"""
from __future__ import annotations

from fastapi import FastAPI, HTTPException

from desk.world import PROVIDERS, ROLE_PERMISSIONS, effective_permissions, expected_queue, intake_requests, routing_rules, users

app = FastAPI(title="Prior Auth Portal mock (Knowledge Desk)")


@app.get("/health")
def health():
    return {"status": "ok", "service": "portal", "users": len(users()), "routing_rules": len(routing_rules())}


@app.get("/api/v1/users")
def list_users(name: str | None = None, region: str | None = None):
    out = [{k: u[k] for k in ("userId", "displayName", "role", "region", "org")} for u in users().values()]
    if name:
        out = [u for u in out if name.lower() in u["displayName"].lower()]
    if region:
        out = [u for u in out if u["region"] == region]
    return {"users": out}


@app.get("/api/v1/users/{uid}")
def get_user(uid: str):
    u = users().get(uid)
    if not u:
        raise HTTPException(404, "user not found")
    return {k: u[k] for k in ("userId", "displayName", "role", "region", "org", "office")}


@app.get("/api/v1/users/{uid}/access")
def access(uid: str):
    u = users().get(uid)
    if not u:
        raise HTTPException(404, "user not found")
    return {"userId": uid, "role": u["role"], "region": u["region"], "mfaState": u["mfaState"], "locked": u["locked"],
            "lockedSince": u["lockedSince"], "failedAttempts": u["failedAttempts"], "delegation": u.get("delegation"),
            "team": u.get("team"), "permissions": effective_permissions(u)}


@app.get("/api/v1/permissions/check")
def check(user: str, action: str):
    """Is `action` allowed for `user`, and if not, exactly why (role, lapsed delegation, lockout)?"""
    u = users().get(user)
    if not u:
        raise HTTPException(404, "user not found")
    perms = effective_permissions(u)
    allowed = action in perms or "config.*" in perms
    reason = "granted by role" if allowed else "not granted to role " + u["role"]
    if not allowed and action in ROLE_PERMISSIONS.get(u["role"], []):
        reason = f"office delegation lapsed on {u['delegation']['expiresOn']}; an office manager renews it on My Office > Delegation"
    if u["locked"]:
        allowed, reason = False, f"account locked since {u['lockedSince']} ({u['failedAttempts']} failed attempts, MFA {u['mfaState']}); unlock is not self-service"
    return {"user": user, "action": action, "allowed": allowed, "reason": reason, "role": u["role"]}


@app.get("/api/v1/intake-requests")
def list_requests(submittedBy: str | None = None):
    rs = list(intake_requests().values())
    if submittedBy:
        rs = [r for r in rs if r["submittedBy"] == submittedBy]
    return {"requests": rs}


@app.get("/api/v1/intake-requests/{rid}")
def get_request(rid: str):
    r = intake_requests().get(rid)
    if not r:
        raise HTTPException(404, "request not found")
    return r


@app.get("/api/v1/routing/rules")
def rules(region: str | None = None, service_type: str | None = None):
    out = routing_rules()
    if service_type:
        out = [r for r in out if r["match"].get("service_type") == service_type]
    if region:
        out = [r for r in out if r["match"].get("region") in (region, None) or r["queue_region"] == region]
    return {"rules": out}


@app.get("/api/v1/routing/explain/{rid}")
def explain(rid: str):
    """Which rule routed this request, which queue CANON says it should be in, and whether those differ."""
    r = intake_requests().get(rid)
    if not r:
        raise HTTPException(404, "request not found")
    prov = PROVIDERS[r["providerId"]]
    exp = expected_queue(r)
    actual = r["routing"]["queue"]
    return {"requestId": rid, "serviceType": r["serviceType"], "urgency": r["urgency"],
            "servicingProvider": {"id": r["providerId"], "name": prov["name"], "zip": prov["zip"], "city": prov["city"]},
            "actualQueue": actual, "matchedRule": r["routing"]["rule_id"], "ruleNote": r["routing"]["reason"],
            "expectedQueue": exp, "misrouted": exp is not None and exp != actual, "unassigned": actual == "UNASSIGNED",
            "submittedAt": r["submittedAt"], "status": r["status"]}
