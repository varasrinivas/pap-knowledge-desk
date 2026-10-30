"""What the offline FixtureModel 'thinks': a keyword planner for triage, templates for answers and article drafts.

This is the stand-in for an LLM so every lab runs with no key. It is deliberately simple and readable; with
LLM_PROVIDER=anthropic the same Agno agents run on Claude instead and these functions are not called.
"""
from __future__ import annotations

import json
import re

REQ = re.compile(r"\bIR-\d{4}-\d{5}\b")
LIVE_TERMS = ["fax", "upload", "scanning", "attach", "export", "login", "sign in", "slow", "down", "letter", "timeline", "wizard"]
SERVICE_WORDS = {"mri": "IMAGING", "ct ": "IMAGING", "imaging": "IMAGING", "ortho": "ORTHO_SURGERY", "knee": "ORTHO_SURGERY",
                 "cardio": "CARDIOLOGY", "heart": "CARDIOLOGY", "oncology": "ONCOLOGY", "radiation": "ONCOLOGY", "dme": "HOME_HEALTH_DME",
                 "behavioral": "BEHAVIORAL_HEALTH", "sleep": "SLEEP_STUDY"}


def has(t: str, *words) -> bool:
    return any(w in t for w in words)


def plan(message: str, role: str = "PROVIDER_NURSE") -> dict:
    """Message -> triage plan: intent, which RAG sources, which tools, keywords for the live search, the permission to check."""
    t = " " + message.lower() + " "
    p = {"intent": "how_to", "sources": [], "tools": [], "keywords": [], "request_id": None, "action": None,
         "refuse_reason": None, "clarify_question": None, "service_type": None}
    m = REQ.search(message)
    if m:
        p["request_id"] = m.group(0)
        p["tools"].append("request")
    p["service_type"] = next((v for k, v in SERVICE_WORDS.items() if k in t), None)
    # ---- guards first: injection, never-list, clinical advice, too vague ----
    if has(t, "ignore your rules", "ignore previous", "all users", "everyone's permissions", "system prompt"):
        p.update(intent="injection", refuse_reason="I can only look at your own account and requests.")
        return p
    if has(t, "approve ir", "approve it", "just approve", "override the decision", "change the decision", "expedite"):
        p.update(intent="decision_change", refuse_reason="The assistant and the service desk cannot approve, expedite or change a decision.")
        return p
    if has(t, "should this patient", "should the patient", " or physical therapy first", "which treatment", "is it medically necessary"):
        p.update(intent="clinical_advice", refuse_reason="Clinical and medical-necessity questions go to the Clinical Policy Desk.")
        return p
    if len(re.findall(r"[a-z]+", t)) <= 3 or t.strip() in ("it's broken", "its broken", "help", "not working"):
        p.update(intent="unclear", clarify_question="What were you trying to do, and what did you see? A request ID (IR-...) helps.")
        return p
    # ---- live / outage signals ----
    live = has(t, "today", "this morning", "right now", "since ", "isn't working", "not working", "failing", "down", "anything wrong", "can't upload", "cant upload")
    if has(t, "anything wrong", "status of the portal", "is the portal"):
        p.update(intent="outage_check")
        p["tools"].append("region_status")
    if live and p["intent"] != "outage_check":
        p["keywords"] = [k.strip() for k in LIVE_TERMS if k in t][:2] or ["portal"]
        p["tools"].append("live")
    # ---- access ----
    if has(t, "locked", "lock out", "locked out", "changing phones", "new phone", "mfa"):
        p.update(intent="access_problem", action="intake.view")
        p["tools"].append("access")
        p["sources"] += ["kb_ui", "kb_workflow"]
    if has(t, "submit button", "can't submit", "cannot submit", "no submit"):
        p.update(intent="access_problem", action="intake.submit")
        p["tools"].append("access")
        p["sources"] += ["kb_ui", "incident_resolutions"]
    if has(t, "approver rights", "approver for", "need approver", "role change", "access to"):
        p.update(intent="access_request", action="access.request.approve" if "approver" in t else "intake.view")
        p["tools"].append("access")
        p["sources"] += ["kb_workflow"]
    if has(t, "can't upload", "cant upload", "can't see requests", "cannot see"):
        p["tools"].append("access")
        p["action"] = p["action"] or ("intake.attach" if "upload" in t else "intake.view")
    if has(t, "on my behalf", "submit for", "let my new nurse", "delegate"):
        p.update(intent="how_to")
        p["tools"].append("access")
        p["sources"] += ["kb_ui", "kb_workflow"]
    # ---- routing ----
    if has(t, "queue", "routed", "went to the", "unassigned", "keep getting", "wrong region"):
        p.update(intent="routing_problem")
        p["tools"].append("routing")
        p["sources"] += ["kb_workflow", "incident_resolutions"]
        if has(t, "past 24", "two days", "2 days", "sat in", "sla"):
            p["sources"].append("kb_policy")
    # ---- defects / data ----
    if has(t, "blank file", "empty file", "export", "error", "something went wrong"):
        p["intent"] = "defect_report" if p["intent"] == "how_to" else p["intent"]
        p["sources"] += ["incident_resolutions"]
    if has(t, "status shows", "letter says", "disagree", "duplicated", "shows up twice"):
        p["intent"] = "data_problem"
        p["sources"] += ["incident_resolutions"]
    # ---- documents ----
    if has(t, "need prior auth", "prior auth", "what notes", "how long", "deadline", "appeal", "pend", "pended", "denial", "denied",
           "urgent", "retro", "out-of-network", "reason code", "turnaround"):
        p["sources"].append("kb_policy")
        if p["intent"] == "how_to":
            p["intent"] = "policy_question"
    if has(t, "how do i", "where do i", "where can i", "how can i", "button", "screen", "tab", "upload", "attach", "download", "spinning"):
        p["sources"].append("kb_ui")
    if has(t, "what happens", "who can", "who owns", "next step", "process", "what do i send", "what do i do"):
        p["sources"].append("kb_workflow")
    if p["intent"] in ("how_to", "policy_question", "access_problem", "defect_report") or not p["sources"]:
        p["sources"].append("incident_resolutions")
    if p["sources"]:
        p["sources"].append("kb_drafts")
    if p["intent"] == "how_to" and not any(s in p["sources"] for s in ("kb_ui", "kb_workflow", "kb_policy")):
        p["sources"] += ["kb_ui", "kb_workflow"]
    p["sources"] = list(dict.fromkeys(p["sources"]))
    p["tools"] = list(dict.fromkeys(p["tools"]))
    return p


def compose(e: dict) -> str:
    """Evidence pack -> answer. Every factual sentence ends with the source it came from."""
    route = e["route"]
    if route == "refuse":
        return f"{e['refuse_reason']} I can help with portal questions, request status, access and routing problems."
    if route == "clarify":
        return e["clarify_question"]
    lines = []
    for f in e.get("findings", []):
        lines.append(f"{f['text']} [{f['source']}]")
    docs = e.get("doc_hits", [])
    if docs and route in ("resolve", "gap_resolve", "link_live", "raise") and e.get("use_docs", True):
        for h in docs[:2]:
            lines.append(f"{_snippet(h['text'])} [{h['meta']['source_id']}: {h['meta'].get('title', '')}]")
    if route == "gap_resolve":
        lines.append("No document covers this yet, so here is what resolved the same problem for other offices:")
        for h in e.get("incident_hits", [])[:2]:
            res = h["text"].split("Resolution:", 1)[-1].strip()
            lines.append(f"- {res} [{h['id']}]")
        lines.append("I have flagged this as a knowledge gap so the team can write it down.")
    if route == "link_live":
        m = e["live"]["major_incidents"][0]
        lines.insert(0, f"This is a known issue right now: {m['number']} \"{m['short_description']}\" ({m['priority']}, {m['state']}). "
                        f"{_workaround(m)} Updates are posted on {m['number']}; you do not need a new ticket. [{m['number']}]")
    if route in ("raise", "raise_access") and e.get("ticket_proposal"):
        tp = e["ticket_proposal"]
        lines.append(f"I can raise {'an access request' if route == 'raise_access' else 'a ticket'} for this: "
                     f"\"{tp.get('short_description') or tp.get('item')}\" ({tp.get('category', 'access catalog')}"
                     f"{', approver ' + tp['approver'] if tp.get('approver') else ''}). Confirm and I will submit it.")
    if route == "dedup":
        d = e["duplicate"]
        lines.append(f"This is already open as {d['number']} (opened {d['sys_created_on']}). I have added your report to it as a work note "
                     f"instead of opening a second ticket. [{d['number']}]")
    if not lines:
        lines.append("I could not find anything reliable on this. I can raise a ticket so an analyst looks at it.")
    return "\n".join(lines)


def _snippet(text: str, n: int = 260) -> str:
    body = text.split("\n", 2)[-1]
    body = re.sub(r"^#+ .*$", "", body, flags=re.M)
    body = re.sub(r"\s+", " ", body).strip()
    return body[:n].rsplit(" ", 1)[0] + ("..." if len(body) > n else "")


def _workaround(m: dict) -> str:
    d = m.get("description") or ""
    w = re.search(r"Workaround: ([^.]+\.)", d)
    return f"Workaround: {w.group(1)}" if w else ""


def article(cluster: dict) -> str:
    """Gap cluster -> draft article in the UI-document format, built from what analysts actually said (a human edits and approves it)."""
    ex = cluster["examples"]
    fixes = cluster.get("resolutions") or [x["resolution"] for x in ex]
    title = cluster.get("title") or "How to: " + ", ".join(cluster["top_words"][:3])
    main = max(fixes, key=len)
    sentences = [re.sub(r"^(Workaround|Explained|Told caller|Explained to caller)[:,]?\s*", "", s.strip()) for s in re.split(r"(?<=[.;])\s+", main)]
    sentences = [s for s in sentences if len(s) > 3 and not re.match(r"(No (article|KB|documentation)|Resolved)", s, re.I)]   # bookkeeping, not steps
    steps = "\n".join(f"{i + 1}. {s[0].upper() + s[1:]}" for i, s in enumerate(sentences))
    also = "\n".join(f"- {f}" for f in fixes if f != main)
    errors = "\n".join(f"- **{x['problem']}**: {x['resolution']}" for x in ex[:3])
    return (f"# {title}\n\nDrafted from {cluster['size']} resolved incidents that no existing document answered. "
            f"Check every step with the owning team before approving [CHECK].\n\n## Procedure: {title}\n{steps}\n\n"
            f"**What you should see:** the request shows the change, or the analyst's workaround applies.\n\n"
            + (f"Other resolutions analysts recorded:\n{also}\n\n" if also else "")
            + f"## Common errors on this screen\n{errors}")


def raise_args(message: str) -> dict:
    """The raise agent's message is the JSON ticket proposal; the fixture just passes it to the tool."""
    return json.loads(message)
