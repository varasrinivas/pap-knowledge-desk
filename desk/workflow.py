"""The Knowledge Desk as an Agno Workflow.

    triage ─▶ Parallel(gather: 5 RAG sources + 5 tools) ─▶ decide (code: the gate) ─▶ compose (agent) ─▶ Router(act)
                                                                                                          ├ resolve / refuse / clarify
                                                                                                          ├ link_live (no new ticket)
                                                                                                          ├ dedup (work note on the open ticket)
                                                                                                          ├ gap (log the gap event, answer from history)
                                                                                                          └ raise (agent + confirmable tool: the run pauses)

Every gather step reads the triage plan and returns 'skipped' when it was not asked for: the Parallel step runs them all
at once, so the slowest planned source sets the latency, not the sum of them.
"""
from __future__ import annotations

import json
import re
import time
from datetime import datetime, timezone

from agno.run import RunContext
from agno.workflow import Parallel, Router, Step, StepInput, StepOutput, Workflow

from desk import config, tools
from desk.agents import agent, db
from desk.rag.search import retrieve
from desk.redact import redact
from desk.world import iso, now, region_for_zip, routing_rules, users

DOC_SOURCES = ["kb_policy", "kb_workflow", "kb_ui", "kb_drafts"]
CITE = re.compile(r"\[((?:POL|WF|UI|DRAFT|FIX)-\d{2}|INC\d{7}|portal:\w+|servicenow:\w+)")
GAPS_FILE = config.RUNTIME_DIR / "gaps.jsonl"
OPEN_STATES = ("New", "In Progress", "On Hold")


def T(rc: RunContext) -> dict:
    return rc.session_state.setdefault("turn", {})


# ---------------- 1. triage ----------------
def triage(step_input: StepInput, run_context: RunContext) -> StepOutput:
    req = step_input.input
    t0 = time.time()
    text, kinds = redact(req["message"])
    user = users().get(req["user_id"], {})
    run_context.session_state["turn"] = turn = {"message": text, "redacted": kinds, "user_id": req["user_id"], "user": user,
                                                "t0": t0, "evidence": {}, "tools_called": [], "sources_searched": {}}
    r = agent("triage").run(json.dumps({"message": text, "role": user.get("role", "")}))
    turn["plan"] = r.content.model_dump() if hasattr(r.content, "model_dump") else dict(r.content)
    return StepOutput(content=json.dumps(turn["plan"]))


# ---------------- 2. gather (run in parallel) ----------------
def rag_step(source: str):
    def run(step_input: StepInput, run_context: RunContext) -> StepOutput:
        turn = T(run_context)
        if source not in turn["plan"]["sources"]:
            return StepOutput(content="skipped")
        where = {"bucket_pred": {"$ne": "duplicate_noise"}} if source == "incident_resolutions" else None   # metadata filter
        try:
            r = retrieve(source, turn["message"], k=4, where=where)
        except Exception:
            r = retrieve(source, turn["message"], k=4)
        turn["sources_searched"][source] = {"top": r["top"], "gate": r["gate"], "above_gate": r["above_gate"],
                                            "hits": [h["id"] for h in r["hits"]]}
        turn["evidence"][source] = r
        return StepOutput(content=f"{source}: top {r['top']:.3f} (gate {r['gate']})")
    run.__name__ = f"rag_{source}"
    return Step(name=f"rag_{source}", executor=run)


def tool_access(step_input: StepInput, run_context: RunContext) -> StepOutput:
    turn = T(run_context)
    if "access" not in turn["plan"]["tools"]:
        return StepOutput(content="skipped")
    uid = turn["user_id"]
    out = {"self": tools.get_user_access(uid)}
    if turn["plan"].get("action"):
        out["check"] = tools.check_permission(uid, turn["plan"]["action"])
    me = turn["user"]
    if me.get("role") == "PROVIDER_OFFICE_MGR":                       # a manager may check colleagues in the same office
        for oid, u in users().items():
            if oid != uid and u.get("org") == me.get("org") and u["displayName"].split()[0].lower() in turn["message"].lower():
                out.setdefault("colleagues", {})[oid] = tools.check_permission(oid, "intake.submit")
    turn["tools_called"] += ["get_user_access"] + (["check_permission"] if "check" in out else [])
    turn["evidence"]["access"] = out
    return StepOutput(content=json.dumps(out)[:300])


def tool_routing(step_input: StepInput, run_context: RunContext) -> StepOutput:
    turn = T(run_context)
    if "routing" not in turn["plan"]["tools"]:
        return StepOutput(content="skipped")
    out = {"explained": [], "rule_anomalies": []}
    rid = turn["plan"].get("request_id")
    ids = [rid] if rid else [r["requestId"] for r in tools.list_my_requests(turn["user_id"]).get("requests", [])]
    for i in ids:
        ex = tools.explain_routing(i)
        if "error" not in ex:
            out["explained"].append(ex)
    turn["tools_called"].append("explain_routing")
    me = turn["user"]
    if me.get("role") == "UM_NURSE":                                  # reviewers: scan the rule table for their region
        res = tools.get_routing_rules(region=me["region"])
        turn["tools_called"].append("get_routing_rules")
        for r in res.get("rules", []):
            m = r["match"]
            wrong_type = m.get("service_type") and r["queue_service_type"] != m["service_type"]
            wrong_region = m.get("zip_prefix") and any(region_for_zip(z + "00") != r["queue_region"] for z in m["zip_prefix"])
            if (wrong_type or wrong_region) and (r["queue_region"] == me["region"]):
                out["rule_anomalies"].append(r)
    turn["evidence"]["routing"] = out
    return StepOutput(content=f"{len(out['explained'])} explained, {len(out['rule_anomalies'])} anomalies")


def tool_live(step_input: StepInput, run_context: RunContext) -> StepOutput:
    turn = T(run_context)
    if "live" not in turn["plan"]["tools"]:
        return StepOutput(content="skipped")
    found = {"major_incidents": [], "recent": [], "keywords": turn["plan"]["keywords"]}
    for kw in turn["plan"]["keywords"][:2]:
        r = tools.sn_live_incidents(kw)
        turn["tools_called"].append(f"sn_live_incidents({kw})")
        for m in r.get("major_incidents", []):
            if m["number"] not in {x["number"] for x in found["major_incidents"]}:
                found["major_incidents"].append(m)
        found["recent"] += r.get("recent", [])
    turn["evidence"]["live"] = found
    return StepOutput(content=f"{len(found['major_incidents'])} major incident(s) match")


def tool_region_status(step_input: StepInput, run_context: RunContext) -> StepOutput:
    turn = T(run_context)
    if "region_status" not in turn["plan"]["tools"]:
        return StepOutput(content="skipped")
    r = tools.sn_region_status(turn["user"].get("region", "SOUTH_CENTRAL"))
    turn["tools_called"].append("sn_region_status")
    turn["evidence"]["region_status"] = r
    return StepOutput(content=f"{r.get('open', 0)} open")


def tool_request(step_input: StepInput, run_context: RunContext) -> StepOutput:
    turn = T(run_context)
    if "request" not in turn["plan"]["tools"] or not turn["plan"].get("request_id"):
        return StepOutput(content="skipped")
    r = tools.get_intake_request(turn["plan"]["request_id"])
    turn["tools_called"].append("get_intake_request")
    turn["evidence"]["request"] = r
    return StepOutput(content=r.get("status", r.get("error", "")))


# ---------------- 3. decide: the gate, in code ----------------
def _hours_since(s: str) -> float:
    return (now() - datetime.strptime(s, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)).total_seconds() / 3600


def decide(step_input: StepInput, run_context: RunContext) -> StepOutput:
    turn = T(run_context)
    plan, ev, me = turn["plan"], turn["evidence"], turn["user"]
    findings, route, proposal = [], None, None
    if plan.get("refuse_reason"):
        route = "refuse"
    elif plan.get("clarify_question"):
        route = "clarify"
    # live incidents first: a known outage beats a new ticket
    live = ev.get("live", {})
    if not route and live.get("major_incidents"):
        route = "link_live"
    # access
    acc = ev.get("access", {})
    s = acc.get("self", {})
    if s.get("locked"):
        findings.append({"text": f"Your account has been locked since {s['lockedSince']} UTC after {s['failedAttempts']} failed sign-ins "
                                 f"(MFA state {s['mfaState']}). Lockouts are not self-service; the Service Desk unlocks accounts.", "source": "portal:access"})
        route = route or "raise"
        proposal = proposal or {"tool": "create_incident", "short_description": "Portal account locked after MFA reset", "category": "portal_access",
                                "subcategory": "login", "impact": 3, "urgency": 2}
    chk = acc.get("check", {})
    if chk and not chk.get("allowed") and not s.get("locked"):
        if "delegation lapsed" in chk.get("reason", ""):
            findings.append({"text": f"You cannot use {chk['action']} because your {chk['reason']}.", "source": "portal:permissions"})
            route = route or "resolve"
        elif plan["intent"] == "access_request":
            findings.append({"text": f"Your role {chk['role']} does not include {chk['action']}; access changes go through the access catalog with an approver.",
                             "source": "portal:permissions"})
            director = next((u for u in users().values() if u["role"] == "REGIONAL_DIRECTOR" and u["region"] == me.get("region")), None)
            route = route or "raise_access"
            proposal = {"tool": "create_access_request", "requested_for": turn["user_id"], "item": f"Grant {chk['action']} ({me.get('region')})",
                        "approver": director["userId"] if director else "u-marcus", "description": f"Requested via the desk by {me.get('displayName')}."}
    for oid, c in acc.get("colleagues", {}).items():
        if not c.get("allowed"):
            findings.append({"text": f"{users()[oid]['displayName']} cannot submit: {c['reason']}. As office manager you can renew it yourself.",
                             "source": "portal:permissions"})
    # routing
    rt = ev.get("routing", {})
    for ex in rt.get("explained", []):
        age = _hours_since(ex["submittedAt"])
        sla = 24 if ex["urgency"] == "URGENT" else 72
        if ex["misrouted"] or ex["unassigned"]:
            what = ("is in UNASSIGNED because the servicing provider has no practice location on file" if ex["unassigned"] else
                    f"was routed to {ex['actualQueue']} by rule {ex['matchedRule']} ('{ex['ruleNote']}'), but the servicing provider "
                    f"{ex['servicingProvider']['name']} is in ZIP {ex['servicingProvider']['zip']}, so it belongs in {ex['expectedQueue']}")
            findings.append({"text": f"{ex['requestId']} {what}. It has waited {age:.0f} h of its {sla} h review time.", "source": "portal:routing"})
            at_risk = ex["unassigned"] or age >= sla * 0.6
            route = route or "raise"
            proposal = proposal or {"tool": "create_incident", "short_description": f"{ex['requestId']} misrouted ({ex['matchedRule'] or 'UNASSIGNED'})",
                                    "category": "other", "subcategory": "routing", "impact": 2 if at_risk else 3, "urgency": 1 if at_risk else 3,
                                    "request_id": ex["requestId"]}
    for r in rt.get("rule_anomalies", []):
        findings.append({"text": f"Routing rule {r['rule_id']} ('{r['note']}', added in {r['added_in']}) sends {r['match']} to "
                                 f"{r['queue_region']}-{r['queue_service_type']}, which is why those cases reach your queue.", "source": "portal:routing"})
        route = route or "raise"
        proposal = proposal or {"tool": "create_incident", "short_description": f"Routing rule {r['rule_id']} sends cases to the wrong reviewer queue",
                                "category": "other", "subcategory": "routing", "impact": 3, "urgency": 2}
    # the request itself
    rq = ev.get("request", {})
    if rq.get("letterStatus") and rq["letterStatus"] != rq.get("status"):
        findings.append({"text": f"{rq['requestId']} shows {rq['status']} in the portal but its letter says {rq['letterStatus']}.", "source": "portal:request"})
        route = route or "raise"
        proposal = proposal or {"tool": "create_incident", "short_description": f"{rq['requestId']} status and decision letter disagree",
                                "category": "data_issue", "subcategory": "status_mismatch", "impact": 3, "urgency": 3, "request_id": rq["requestId"]}
    if rq.get("pendCode"):
        findings.append({"text": f"{rq['requestId']} is {rq['status']} with code {rq['pendCode']}.", "source": "portal:request"})
    rs = ev.get("region_status")
    if rs and "error" not in rs:
        majors = ", ".join(f"{m['number']} {m['short_description']} ({m['priority']})" for m in rs["major_incidents"]) or "no major incidents"
        findings.append({"text": f"{rs['open']} incidents are open in {rs['region']} or platform-wide in the last 12 h: {majors}.", "source": "servicenow:live"})
        route = route or "resolve"
    # documents and history
    doc_hits = sorted([h for s_ in DOC_SOURCES if s_ in ev and ev[s_]["above_gate"] for h in ev[s_]["hits"][:2]],
                      key=lambda h: -h["score"])
    doc_above = bool(doc_hits)
    inc = ev.get("incident_resolutions", {})
    inc_hits = inc.get("hits", []) if inc.get("above_gate") else []
    defect_like = [h for h in inc_hits if h["meta"].get("bucket_pred") == "defect"]
    if not route and plan["intent"] in ("defect_report", "data_problem") and inc_hits:
        top = defect_like[0] if defect_like else inc_hits[0]
        findings.append({"text": f"This matches a known problem: {top['text'].split('Resolution:', 1)[-1].strip()}", "source": top["id"]})
        route = "raise"
        cat = "portal_defect" if plan["intent"] == "defect_report" else "data_issue"
        proposal = {"tool": "create_incident", "short_description": turn["message"][:120], "category": cat,
                    "subcategory": top["meta"].get("subcategory", "other"), "impact": 3, "urgency": 3}
    draft_hit = "kb_drafts" in ev and ev["kb_drafts"]["above_gate"]                # an approved draft closed the gap after those incidents
    gap_history = not draft_hit and sum(h["meta"].get("bucket_pred") == "knowledge_gap" for h in inc_hits) >= 2   # the profiler's verdict
    if not route and inc_hits and gap_history and plan["intent"] in ("how_to", "policy_question"):
        route = "gap_resolve"                       # documents may be ABOUT this, but they did not answer it for the last callers
        findings.append({"text": "Past callers with this question were answered by an analyst, not by a document.", "source": inc_hits[0]["id"]})
    if not route and doc_above:
        route = "resolve"
    if not route and inc_hits:
        route = "gap_resolve"
    if not route:
        route = "raise"
        proposal = {"tool": "create_incident", "short_description": turn["message"][:120], "category": "other", "subcategory": "how_to",
                    "impact": 3, "urgency": 3}
        turn["gap"] = True
    if route == "gap_resolve":
        turn["gap"] = True
    # dedup before any new incident
    dup = None
    if route == "raise" and proposal and proposal["tool"] == "create_incident":
        d = tools.sn_find_open_duplicate(turn["user_id"], proposal["category"], me.get("region", ""), proposal.get("subcategory"))
        turn["tools_called"].append("sn_find_open_duplicate")
        if d.get("duplicate"):
            dup, route = d["duplicate"], "dedup"
    if proposal and proposal["tool"] == "create_incident":
        similar = [h["id"] for h in inc_hits[:3]]
        proposal.update(caller=turn["user_id"], region=me.get("region", ""), role=me.get("role", ""),
                        description=f"Reported via the Knowledge Desk: {turn['message']}\nFindings: " + " | ".join(f["text"] for f in findings)
                                    + (f"\nSimilar past incidents: {', '.join(similar)}" if similar else ""),
                        work_notes="Desk evidence: " + json.dumps(turn["sources_searched"])[:900])
    turn.update(route=route, findings=findings, ticket_proposal=proposal, duplicate=dup,
                doc_hits=doc_hits[:3], incident_hits=inc_hits[:3])
    return StepOutput(content=route)


# ---------------- 4. compose ----------------
def compose(step_input: StepInput, run_context: RunContext) -> StepOutput:
    turn = T(run_context)
    pack = {"route": turn["route"], "findings": turn["findings"], "refuse_reason": turn["plan"].get("refuse_reason"),
            "clarify_question": turn["plan"].get("clarify_question"), "doc_hits": turn["doc_hits"], "incident_hits": turn["incident_hits"],
            "live": turn["evidence"].get("live"), "ticket_proposal": turn["ticket_proposal"], "duplicate": turn["duplicate"],
            "use_docs": turn["route"] not in ("raise",) or not turn["findings"]}
    r = agent("compose").run(json.dumps(pack, default=str))
    turn["answer"] = r.content
    return StepOutput(content=r.content)


# ---------------- 5. act ----------------
def _result(turn: dict) -> StepOutput:
    cites = sorted(set(CITE.findall(turn.get("answer", ""))))
    out = {k: turn.get(k) for k in ("route", "answer", "plan", "findings", "tools_called", "sources_searched", "ticket", "pending",
                                     "duplicate", "redacted", "gap")}
    out["citations"] = cites
    out["latency_ms"] = int((time.time() - turn["t0"]) * 1000)
    return StepOutput(content=json.dumps(out, default=str))


def act_answer(step_input: StepInput, run_context: RunContext) -> StepOutput:
    return _result(T(run_context))


def act_dedup(step_input: StepInput, run_context: RunContext) -> StepOutput:
    turn = T(run_context)
    tools.sn_add_work_note(turn["duplicate"]["number"], f"Same issue reported again via the desk by {turn['user_id']}: {turn['message']}")
    turn["tools_called"].append("sn_add_work_note")
    turn["ticket"] = {"number": turn["duplicate"]["number"], "action": "work_note"}
    return _result(turn)


def act_gap(step_input: StepInput, run_context: RunContext) -> StepOutput:
    turn = T(run_context)
    with GAPS_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"at": iso(now()), "user": turn["user_id"], "question": turn["message"],
                            "searched": turn["sources_searched"], "answered_from": [h["id"] for h in turn["incident_hits"]]}) + "\n")
    return _result(turn)


def act_raise(step_input: StepInput, run_context: RunContext) -> StepOutput:
    """The raise agent calls a tool marked requires_confirmation: the run pauses here until the user confirms in the UI."""
    turn = T(run_context)
    if turn.get("gap"):
        act_gap(step_input, run_context)
    r = agent("raise").run(json.dumps(turn["ticket_proposal"]), session_id=f"raise-{turn['user_id']}")
    if r.is_paused:
        req = r.active_requirements[0]
        turn["pending"] = {"run_id": r.run_id, "session_id": f"raise-{turn['user_id']}", "tool": req.tool_execution.tool_name,
                           "args": req.tool_execution.tool_args}
    return _result(turn)


def select(step_input: StepInput, run_context: RunContext = None):
    route = (step_input.previous_step_outputs or {}).get("decide").content if step_input.previous_step_outputs else None
    route = T(run_context)["route"] if run_context else route
    return {"raise": [RAISE], "raise_access": [RAISE], "dedup": [DEDUP], "gap_resolve": [GAP]}.get(route, [ANSWER])


ANSWER = Step(name="answer", executor=act_answer)
RAISE = Step(name="raise", executor=act_raise)
DEDUP = Step(name="dedup", executor=act_dedup)
GAP = Step(name="gap", executor=act_gap)


def build() -> Workflow:
    gather = Parallel(*[rag_step(s) for s in ["kb_policy", "kb_workflow", "kb_ui", "incident_resolutions", "kb_drafts"]],
                      Step(name="tool_access", executor=tool_access), Step(name="tool_routing", executor=tool_routing),
                      Step(name="tool_live", executor=tool_live), Step(name="tool_region_status", executor=tool_region_status),
                      Step(name="tool_request", executor=tool_request), name="gather")
    return Workflow(name="knowledge-desk", description="Resolve or raise, with five RAG sources and five tools",
                    steps=[Step(name="triage", executor=triage), gather, Step(name="decide", executor=decide),
                           Step(name="compose", executor=compose),
                           Router(name="act", selector=select, choices=[ANSWER, RAISE, DEDUP, GAP])],
                    db=db(), session_state={})


_wf = None


def desk() -> Workflow:
    global _wf
    if _wf is None:
        _wf = build()
    return _wf


def ask(user_id: str, message: str, thread_id: str = "default") -> dict:
    r = desk().run(input={"user_id": user_id, "message": message}, session_id=f"{user_id}:{thread_id}")
    return json.loads(r.content)


def confirm(pending: dict, approve: bool = True) -> dict:
    a = agent("raise")
    run = a.get_run_output(run_id=pending["run_id"], session_id=pending["session_id"])
    for req in run.active_requirements:
        req.confirm() if approve else req.reject()
    r = a.continue_run(run_id=pending["run_id"], requirements=run.requirements, session_id=pending["session_id"])
    return {"confirmed": approve, "result": r.content}
