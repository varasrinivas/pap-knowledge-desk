"""Generate 15,000 historical ServiceNow incidents (and a live 12-hour window) with a known root-cause bucket per incident.

Deterministic for a given seed. PHI-free: every name is a CANON persona or a generated office name; a few fake member IDs
and phone numbers are planted on purpose so the RAG build's redaction stage has something to count.

The answer key (bucket + topic per incident) is returned separately and is never stored in ServiceNow: in real life you do
not have it, which is exactly why the profiler has to be measured against a held-out labelled sample.

    python -m desk generate --stats
"""
from __future__ import annotations

import random
from collections import Counter
from dataclasses import dataclass, field
from datetime import timedelta

from desk import config
from desk.world import REGIONS, iso, now

CATEGORIES = ["portal_access", "portal_defect", "data_issue", "performance", "other"]
CITIES = {"SOUTH_CENTRAL": ["Dallas", "Houston"], "NORTHEAST": ["Boston", "Hartford"], "WEST": ["Phoenix", "Denver"]}
OFFICES = ["Lakeside Orthopedics", "Harbor Spine Clinic", "Sierra Rehab Partners", "North Texas Heart Associates",
           "Bayview Imaging", "Granite Family Medicine", "Mesa Cardiology", "Riverbend Oncology", "Cedar Behavioral Health",
           "Summit Home Health", "Prairie Sleep Center", "Copper State Surgical"]
ROLES = ["PROVIDER_NURSE"] * 6 + ["PROVIDER_OFFICE_MGR"] * 2 + ["UM_NURSE"] * 2 + ["REGIONAL_DIRECTOR"]
BROWSERS = ["Chrome", "Edge", "Safari", "Firefox", "Chrome on a shared kiosk PC"]
RELEASES = {"24.1": 150, "24.2": 95, "24.3": 30}          # days ago each release went out (defects cluster after them)
SIGNATURE = "\n-- {analyst}, Service Desk | Northwind Health Plan\nThis message may contain confidential information. If you received it in error, delete it."
ANALYSTS = ["Devika Menon", "Jordan Pike", "Rosa Alvarez", "Ken Ito"]


@dataclass
class Topic:
    bucket: str
    topic: str
    category: str            # the category a careful analyst would choose (the recorded one is noisy)
    subcategory: str
    group: str               # assignment group
    weight: float
    asks: list[str]
    closes: list[str]
    close_codes: list[str]
    notes: list[str] = field(default_factory=list)


T = Topic
TOPICS: list[Topic] = [
    # ---------------- user education: the answer exists in a document, the caller did not find or follow it ----------------
    T("user_education", "attachment_size", "portal_defect", "upload", "Service Desk", 3.0,
      ["upload keeps spinning then stops on a {size} MB pdf", "cant attach clinical notes, the bar just sits there ({size} MB file)",
       "Document upload fails for {req}, file is about {size}MB", "Attachments won't go through on the Documents tab, tried 3 times",
       "big scan of the chart will not upload, is there a cap?"],
      ["Explained the 25 MB per-file limit; caller compressed the PDF and upload succeeded.", "Advised to split the file into parts under 25 MB. Resolved.",
       "Pointed caller to the attachments guide (file size limit). Upload worked after reducing size.", "Explained to caller, resolved."],
      ["Solved (Work Around)", "Closed/Resolved by Caller"]),
    T("user_education", "mfa_reset_signin", "portal_access", "mfa", "Service Desk", 2.2,
      ["new phone, now the code doesnt work", "after MFA reset I cant get past the 6 digit code screen", "Changed authenticator app and the portal rejects my code",
       "MFA reset done yesterday but sign in still fails"],
      ["Explained first sign-in after MFA reset needs the new authenticator code plus the emailed one-time code. Caller signed in.",
       "Walked caller through MFA reset sign-in per guide; resolved.", "Explained to caller, resolved."],
      ["Solved (Work Around)", "Solved Remotely (Permanently)"]),
    T("user_education", "delegation_lapsed", "portal_access", "permissions", "Service Desk", 2.0,
      ["Submit button disappeared, I can only save draft", "I can fill out the whole request but there is no Submit anymore", "lost the ability to submit requests for my office",
       "Submit is greyed/missing on step 6 since monday"],
      ["Office delegation had expired (180 days). Explained office manager renews it under My Office > Delegation. Manager renewed; resolved.",
       "Explained delegation expiry; caller's manager re-added delegate. Resolved.", "Explained to caller how delegation works, resolved."],
      ["Solved (Work Around)", "Closed/Resolved by Caller"]),
    T("user_education", "pend_code_meaning", "other", "how_to", "Service Desk", 2.0,
      ["what does {pend} mean on {req}", "request got pended with {pend}, what do they want from us", "Pended (Info Requested) - code {pend}, not sure what to send",
       "how do I answer a pend? it says {pend}"],
      ["Explained pend code {pend} and the Respond to Pend panel. Caller uploaded the document.", "Sent the pend code reference; caller responded to pend. Resolved.",
       "Explained to caller, resolved."],
      ["Solved (Work Around)", "Closed/Resolved by Caller"]),
    T("user_education", "appeal_deadline", "other", "how_to", "Service Desk", 1.2,
      ["how long do we have to appeal a denial", "denied last month can we still appeal", "Where do I file an appeal for {req}?", "is there a deadline for appeals"],
      ["Explained the 60-day appeal window and the Appeal this decision button. Service desk does not file appeals.", "Pointed caller to appeals guide. Resolved.",
       "Explained to caller, resolved."],
      ["Solved (Work Around)"]),
    T("user_education", "routing_region_rule", "other", "routing", "Service Desk", 1.0,
      ["why did my request go to a different region than our office", "request is in the Northeast queue but we're in {city}?? (not cardiology)",
       "which region reviews our requests"],
      ["Explained routing uses the servicing provider's practice location, not the submitting office. Request routed correctly.",
       "Explained region is taken from servicing provider location; no misroute. Resolved."],
      ["Solved (Work Around)", "Closed/Resolved by Caller"]),
    T("user_education", "documents_tab_delay", "portal_defect", "upload", "Service Desk", 1.4,
      ["uploaded a file and it's not on the Documents tab", "Where did my attachment go? uploaded 1 min ago", "reviewer says they can't see the notes I just uploaded"],
      ["Explained attachments appear within 2 minutes; re-upload only after 10 minutes. File appeared.", "File was in Scanning status; explained the delay. Resolved.",
       "Explained to caller, resolved."],
      ["Closed/Resolved by Caller", "Solved (Work Around)"]),
    T("user_education", "export_format", "portal_defect", "report", "Service Desk", 0.8,
      ["how do I get the report into excel", "export button only gives csv?", "Need the past-SLA list as a spreadsheet"],
      ["Explained Reports > Export and the Excel format option. Resolved.", "Showed caller the export format selector. Resolved."],
      ["Solved (Work Around)"]),
    T("user_education", "status_meaning", "other", "how_to", "Service Desk", 1.0,
      ["what does Pending Clinical Review mean, has anyone looked at it", "how long until {req} is decided?", "is 72 hours business days or calendar"],
      ["Explained statuses and the 72h/24h review clock (paused while pended). Resolved.", "Explained to caller, resolved."],
      ["Solved (Work Around)"]),

    # ---------------- knowledge gaps: no document covers it; the fix lived only in analysts' heads ----------------
    T("knowledge_gap", "second_servicing_provider", "other", "how_to", "Service Desk", 1.6,
      ["how do I add a second servicing provider to {req}", "need to add another facility to an existing request", "the surgery is split between two sites, where do I put the second provider",
       "can't find where to add an additional servicing provider after submitting", "Providers step only lets me enter one servicing provider??"],
      ["No article covers this. Workaround: withdraw and resubmit with the main servicing provider; second site added by Service Desk as a note.",
       "Told caller there is no screen for a second servicing provider; added it via work note on request. No KB found.",
       "Explained workaround (withdraw and resubmit). Resolved.", "Explained to caller, resolved."],
      ["Solved (Work Around)"]),
    T("knowledge_gap", "p2p_banner", "other", "how_to", "Service Desk", 1.2,
      ["what does the Peer-to-peer requested banner mean", "banner on the decision tab says peer to peer requested, do I need to do something",
       "we got a 'peer-to-peer requested' message on {req}", "Reviewer requested peer to peer? who calls who"],
      ["Explained: reviewer asked for a peer-to-peer; office must call scheduling within 2 business days or the case is decided on the record. No KB article for the banner.",
       "Explained the banner meaning to caller. No documentation found.", "Explained to caller, resolved."],
      ["Solved (Work Around)"]),
    T("knowledge_gap", "fax_draft_matching", "other", "how_to", "Service Desk", 1.2,
      ["we faxed the request last week and nothing shows in the portal", "faxed intake not in worklist", "where do faxed requests show up",
       "sent by fax, is it being reviewed?"],
      ["Explained faxed requests appear as Draft tagged FAX within 4 hours and must be submitted from the worklist. No article covers fax matching.",
       "Found the FAX draft in caller's worklist; caller submitted it. Explained the process.", "Explained to caller, resolved."],
      ["Solved (Work Around)"]),

    # ---------------- access & permissions ----------------
    T("access_permission", "lockout", "portal_access", "login", "Service Desk", 2.6,
      ["locked out of the portal", "account locked after too many tries", "it says my account is locked, I have 15 requests to submit today", "Locked out again!!"],
      ["Account unlocked after identity verification.", "Unlocked account; advised to wait for the emailed code. Resolved.", "Unlock performed."],
      ["Solved Remotely (Permanently)"], ["Verified identity via callback to office number {phone}."]),
    T("access_permission", "role_change", "portal_access", "permissions", "Service Desk", 1.8,
      ["need office manager role for {name}", "please change my role, I moved to the review team", "new hire needs access to submit requests",
       "can't see the Regional Dashboard, I am the new director"],
      ["Access request {reqn} raised in catalog; approved by manager; role updated.", "Role updated via access catalog {reqn}.", "Provisioned after approval."],
      ["Solved (Permanently)"]),
    T("access_permission", "approver_group", "portal_access", "permissions", "Service Desk", 1.0,
      ["add {name} as approver for {region}", "I need approver rights in {region}", "approver group membership for the new UM lead"],
      ["Catalog request {reqn} approved; added to approver group.", "Added to approvers group after director approval."],
      ["Solved (Permanently)"]),
    T("access_permission", "region_access", "portal_access", "permissions", "Service Desk", 0.9,
      ["can't see requests from our Hartford office", "need access to second region", "worklist missing the other site's requests"],
      ["Region added to user profile via {reqn}.", "Granted additional region after approval."],
      ["Solved (Permanently)"]),

    # ---------------- defects ----------------
    T("defect", "export_blank", "portal_defect", "report", "Platform Engineering", 1.6,
      ["Excel export gives a blank file", "report export downloads empty", "exported past-SLA report has headers only", "export to excel is broken"],
      ["Known defect PRB0041127: Excel export blank when filter spans >31 days. Fixed in release 24.2.1.", "Linked to PRB0041127; workaround CSV export.",
       "Defect confirmed and fixed by Platform Engineering."],
      ["Known Error", "Solved (Permanently)"]),
    T("defect", "upload_scanning_stuck", "portal_defect", "upload", "Platform Engineering", 1.4,
      ["file stuck in Scanning forever", "attachment status Scanning for an hour", "uploads stuck at scanning since this morning"],
      ["Virus-scan queue backlog, PRB0041190. Platform restarted scanner workers.", "Linked to PRB0041190; resolved by fix in 24.3.1.", "Defect fixed."],
      ["Known Error", "Solved (Permanently)"]),
    T("defect", "letter_download_fails", "portal_defect", "letters", "Platform Engineering", 1.0,
      ["decision letter download gives an error", "Download letter button does nothing", "letter pdf won't open, says corrupted"],
      ["PRB0040988: letter service returned 500 for letters >2 pages. Fixed.", "Linked to PRB0040988; fixed in release."],
      ["Known Error", "Solved (Permanently)"]),
    T("defect", "timeline_missing", "portal_defect", "ui", "Platform Engineering", 0.8,
      ["timeline tab is empty for {req}", "Timeline doesn't show the pend we responded to", "history missing on request"],
      ["PRB0041302 timeline events not rendering after 24.3; fixed.", "Defect, linked PRB0041302."],
      ["Known Error"]),
    T("defect", "wizard_error", "portal_defect", "ui", "Platform Engineering", 1.0,
      ["wizard throws an error on step 4", "Next button on the Clinical step gives 'something went wrong'", "can't get past step 3 providers, error"],
      ["PRB0041355 validation bug on step 4 for diagnosis codes with suffix. Fixed in 24.3.2.", "Reproduced; defect logged PRB0041355."],
      ["Known Error", "Solved (Permanently)"]),

    # ---------------- routing / configuration ----------------
    T("routing_config", "cardiology_misroute", "other", "routing", "Utilization Management Ops", 1.4,
      ["cardiology request went to the Northeast queue but we're in {city}", "our cardiology requests keep landing in Boston queue", "{req} routed to NORTHEAST-CARDIOLOGY, we are a Dallas practice",
       "wrong region for heart cath request"],
      ["Routing rule RR-0412 sends Dallas ZIP cardiology to NORTHEAST. Request reassigned by director; rule fix requested.", "Reassigned to SOUTH_CENTRAL queue. Root cause routing rule RR-0412.",
       "Request reassigned."],
      ["Solved (Work Around)"]),
    T("routing_config", "oncology_to_ortho", "other", "routing", "Utilization Management Ops", 0.9,
      ["I'm on ortho team but keep getting oncology cases", "urgent oncology requests showing in the ortho reviewers queue", "why are oncology cases in WEST-ORTHO_SURGERY-URGENT"],
      ["Rule RR-0577 fallback routes WEST urgent oncology to ortho queue. Reassigned; config change requested.", "Reassigned cases; routing fallback rule identified."],
      ["Solved (Work Around)"]),
    T("routing_config", "unassigned_queue", "other", "routing", "Utilization Management Ops", 1.1,
      ["request sitting in Unassigned for 2 days", "{req} shows queue UNASSIGNED", "nobody picked up our request, it says unassigned"],
      ["Servicing provider had no practice location on file; location added and request reassigned.", "Moved from UNASSIGNED after provider location update."],
      ["Solved (Permanently)"]),

    # ---------------- data issues ----------------
    T("data_issue", "status_mismatch", "data_issue", "status_mismatch", "Platform Engineering", 1.2,
      ["status says Approved but the letter says Pended", "portal and letter disagree on {req}", "decision tab shows approved, letter pended???"],
      ["Letter regenerated from current status; data sync job re-run.", "Data corrected by platform team; letter regenerated."],
      ["Solved (Permanently)"]),
    T("data_issue", "duplicate_request_record", "data_issue", "duplicate_record", "Platform Engineering", 0.8,
      ["the same request shows up twice in my worklist", "{req} duplicated", "two identical requests created when I clicked submit once"],
      ["Duplicate record removed by platform; root cause double-submit, fixed.", "Data corrected; duplicate withdrawn."],
      ["Solved (Permanently)"]),
    T("data_issue", "wrong_provider_npi", "data_issue", "provider_data", "Provider Data Team", 0.8,
      ["provider NPI is wrong in the portal", "our NPI shows the old practice", "servicing provider address wrong"],
      ["Provider data corrected in directory feed.", "NPI record fixed by provider data team."],
      ["Solved (Permanently)"]),
    T("data_issue", "eligibility_display", "data_issue", "eligibility", "Platform Engineering", 0.7,
      ["member shows not eligible but card is active", "eligibility check fails for member {member}", "eligibility banner wrong"],
      ["Eligibility feed delay; data refreshed.", "Data corrected after eligibility file reload."],
      ["Solved (Permanently)"]),

    # ---------------- outage / performance (children of historical major incidents get a parent) ----------------
    T("outage_performance", "slowness", "performance", "slowness", "Platform Engineering", 2.0,
      ["portal is really slow in {city}", "everything takes a minute to load", "pages timing out this morning", "site crawling for our whole office"],
      ["Resolved under major incident {parent}.", "Performance degradation, see parent {parent}. Resolved.", "Resolved by platform team."],
      ["Solved (Permanently)"]),
    T("outage_performance", "outage", "performance", "outage", "Platform Engineering", 1.6,
      ["portal down", "can't reach the portal at all", "503 error on login page", "is the portal down?? nobody in office can get in"],
      ["Outage, resolved under major incident {parent}.", "Linked to parent {parent}; service restored.", "Service restored."],
      ["Solved (Permanently)"]),

    # ---------------- duplicates & noise ----------------
    T("duplicate_noise", "duplicate_report", "other", "duplicate", "Service Desk", 1.6,
      ["same as my earlier ticket", "following up again on the issue from this morning", "reporting again - still broken"],
      ["Duplicate of {dup}.", "Closed as duplicate of {dup}."],
      ["Duplicate"]),
    T("duplicate_noise", "no_response", "other", "other", "Service Desk", 1.0,
      ["call dropped", "test", "please call me back", "nevermind"],
      ["No response from caller after 3 attempts.", "Caller could not be reached; closed.", "Test ticket."],
      ["Closed/Resolved by Caller", "Not Solved (Not Reproducible)"]),
]

PEND = [f"PI-DOC-{i:03d}" for i in range(1, 13)]
GENERIC_CLOSES = ["Resolved.", "Assisted caller. Resolved.", "Issue resolved, closing.", "Caller confirmed working.", "Fixed.",
                  "Resolved per caller."]                                  # what real close notes often look like: no signal at all
MIX = ["also the site is slow today", "this is urgent, member is waiting", "also can't download the letter", "not sure if this is the right place to ask",
       "my manager asked me to raise this", "happened on chrome and edge"]


def _typo(text: str, rnd: random.Random, p: float = 0.12) -> str:
    out = []
    for w in text.split(" "):
        if len(w) > 4 and rnd.random() < p:
            i = rnd.randrange(1, len(w) - 1)
            w = w[:i] + w[i + 1:] if rnd.random() < 0.5 else w[:i] + w[i + 1] + w[i] + w[i + 2:]
        out.append(w)
    return " ".join(out)


def slots(rnd: random.Random, region: str, extra: dict) -> dict:
    """Draw every slot value once per incident, so the problem and its resolution talk about the same code, size and request."""
    vals = dict(size=rnd.choice([21, 26, 28, 30, 34, 41, 55]), req=f"IR-2026-{rnd.randrange(100, 9999):05d}", pend=rnd.choice(PEND),
                city=rnd.choice(CITIES[region]), region=region, name=rnd.choice(["the new nurse", "my colleague", "our office manager", "a new UM nurse"]),
                reqn=f"REQ00{rnd.randrange(10000, 99999)}", member=f"NW-{rnd.randrange(10**6, 10**7):07d}",
                phone=f"{rnd.randrange(200, 999)}-555-{rnd.randrange(1000, 9999)}", parent="INC00", dup="INC00")
    vals.update(extra)
    return vals


def _fill(t: str, rnd: random.Random, region: str, extra: dict, vals: dict | None = None) -> str:
    return t.format(**(vals or slots(rnd, region, extra)))


def _when(rnd: random.Random, topic: Topic, end_hours_ago: int, days: int):
    """Business-hours-weighted timestamp; defects cluster in the weeks after a release."""
    base = now() - timedelta(hours=end_hours_ago)
    if topic.bucket == "defect" and rnd.random() < 0.7:
        rel = rnd.choice(list(RELEASES.values()))
        days_ago = max(0.6, rel - rnd.expovariate(1 / 6))
    else:
        days_ago = rnd.uniform(0, days)
    t = base - timedelta(days=days_ago)
    hour = int(min(19, max(7, rnd.gauss(11, 3))))
    t = t.replace(hour=hour, minute=rnd.randrange(60), second=rnd.randrange(60))
    if t.weekday() >= 5 and rnd.random() < 0.8:
        t -= timedelta(days=t.weekday() - 4)
    return min(t, base)


def generate(n: int = config.HISTORY_SIZE, seed: int = config.SEED, days: int = config.HISTORY_DAYS) -> tuple[list[dict], dict, list[dict]]:
    """Returns (history incidents, answer key {number: {bucket, topic}}, live 12-hour incidents)."""
    rnd = random.Random(seed)
    weights = [t.weight for t in TOPICS]
    # historical major incidents: parents for outage/performance children
    parents = []
    for k in range(14):
        start = now() - timedelta(hours=14) - timedelta(days=rnd.uniform(1, days))
        parents.append({"number": f"INC00{9000 + k:05d}", "start": start, "region": rnd.choice(REGIONS + ["ALL"])})
    history, key = [], {}
    seq = 10000
    recent_by_user: dict[str, dict] = {}
    for i in range(n):
        topic = rnd.choices(TOPICS, weights=weights)[0]
        region = rnd.choice(REGIONS)
        extra = {}
        if topic.bucket == "outage_performance":
            p = rnd.choice(parents)
            extra["parent"] = p["number"]
            opened = p["start"] + timedelta(minutes=rnd.uniform(0, 240))
            region = p["region"] if p["region"] != "ALL" else region
        else:
            opened = _when(rnd, topic, 12, days)
        seq += 1
        number = f"INC00{seq:05d}"
        caller = f"usr{rnd.randrange(1, 900):04d}"
        if topic.bucket == "duplicate_noise" and topic.topic == "duplicate_report" and recent_by_user:
            prev = rnd.choice(list(recent_by_user.values()))
            extra["dup"] = prev["number"]
            caller, region = prev["caller_id"], prev["u_region"]
        sv = slots(rnd, region, extra)
        if "dup" in extra:
            short = rnd.choice(topic.asks).format(**sv) + " - " + prev["short_description"][:60]
        else:
            short = rnd.choice(topic.asks).format(**sv)
        if rnd.random() < 0.15:
            short = _typo(short, rnd)
        desc = short
        if rnd.random() < 0.18:
            desc += ". " + rnd.choice(MIX)                                   # mixed signals: profiling is not keyword matching
        if rnd.random() < 0.03:
            desc += f" member {sv['member']}"         # planted PHI-like strings for the redaction count
        if rnd.random() < 0.02:
            desc += f" call me at {sv['phone']}"
        category = topic.category if rnd.random() > 0.30 else rnd.choice([c for c in CATEGORIES if c != topic.category])
        analyst = rnd.choice(ANALYSTS)
        notes = [{"at": iso(opened + timedelta(minutes=rnd.randrange(5, 90))), "by": analyst,
                  "text": "Contacted caller." + (SIGNATURE.format(analyst=analyst) if rnd.random() < 0.5 else "")}]
        for nt in topic.notes:
            notes.append({"at": iso(opened + timedelta(minutes=rnd.randrange(10, 120))), "by": analyst, "text": nt.format(**sv)})
        resolved = opened + timedelta(hours=rnd.uniform(0.3, 72))
        rec = {
            "number": number, "short_description": short[:160], "description": desc, "category": category, "subcategory": topic.subcategory,
            "assignment_group": topic.group, "impact": 2 if topic.bucket == "outage_performance" else 3,
            "urgency": 2 if topic.bucket in ("outage_performance", "access_permission") else 3,
            "priority": "P2" if topic.bucket == "outage_performance" else rnd.choice(["P3", "P3", "P4"]),
            "state": "Closed" if resolved < now() - timedelta(days=3) else "Resolved", "active": "false",
            "caller_id": caller, "contact_type": rnd.choice(["phone", "email", "self-service", "chatbot"]),
            "u_portal_user_role": rnd.choice(ROLES), "u_region": region, "u_office": rnd.choice(OFFICES),
            "sys_created_on": iso(opened), "sys_updated_on": iso(resolved), "resolved_at": iso(resolved),
            "close_code": rnd.choice(topic.close_codes),
            "close_notes": (rnd.choice(GENERIC_CLOSES) if topic.bucket != "duplicate_noise" and rnd.random() < 0.25
                            else rnd.choice(topic.closes).format(**sv)),
            "work_notes": notes, "parent_incident": extra.get("parent", ""),
        }
        history.append(rec)
        key[number] = {"bucket": topic.bucket, "topic": topic.topic}
        recent_by_user[caller] = rec
        if len(recent_by_user) > 400:
            recent_by_user.pop(next(iter(recent_by_user)))
    for p in parents:                                                   # the parents themselves (not in the answer key's 15,000)
        pass
    live = generate_live(seed)
    return history, key, live


LIVE_P1 = {"number": "INC0030001", "short_description": "Fax-to-portal intake not creating requests (NORTHEAST)",
           "description": "Faxed intake requests since early morning are not appearing as drafts. Workaround: use New request in the portal.",
           "category": "performance", "subcategory": "outage", "priority": "P1", "impact": 1, "urgency": 1, "u_region": "NORTHEAST",
           "keywords": "fax intake", "hours_ago": 3.1}
LIVE_P2 = {"number": "INC0030002", "short_description": "Uploads failing with 'Scanning' stuck after release 24.3",
           "description": "Attachments over 10 MB stay in Scanning status. Workaround: uploads under 10 MB succeed; split larger files.",
           "category": "portal_defect", "subcategory": "upload", "priority": "P2", "impact": 2, "urgency": 2, "u_region": "ALL",
           "keywords": "upload scanning attachment", "hours_ago": 6.2}


def generate_live(seed: int = config.SEED, routine: int = 120) -> list[dict]:
    """The last 12 hours: two planted active issues with child reports, plus routine traffic (open and recently resolved)."""
    rnd = random.Random(seed + 1)
    n0 = now()
    out = []
    for k, p in enumerate([LIVE_P1, LIVE_P2]):
        opened = n0 - timedelta(hours=p["hours_ago"])
        out.append({**{f: p[f] for f in ("number", "short_description", "description", "category", "subcategory", "priority", "impact", "urgency", "u_region")},
                    "state": "In Progress", "active": "true", "assignment_group": "Platform Engineering", "caller_id": "u-tom",
                    "contact_type": "monitoring", "u_portal_user_role": "PLATFORM_ADMIN", "sys_created_on": iso(opened),
                    "sys_updated_on": iso(n0 - timedelta(minutes=25)), "parent_incident": "", "major_incident": "true",
                    "work_notes": [{"at": iso(n0 - timedelta(minutes=25)), "by": "Tom Okafor", "text": "Update: mitigation in progress. Next update in 60 minutes."}]})
        child_asks = (["fax intake isn't working", "our faxed requests aren't showing up", "fax not going through to portal today"] if k == 0 else
                      ["uploads failing since this morning", "file stuck on Scanning", "can't attach notes, scanning forever"])
        for c in range(8 if k == 0 else 11):
            t = opened + timedelta(minutes=rnd.uniform(10, p["hours_ago"] * 60 - 5))
            out.append({"number": f"INC00{30010 + k * 20 + c}", "short_description": rnd.choice(child_asks), "description": "reported by provider office",
                        "category": p["category"], "subcategory": p["subcategory"], "priority": "P3", "impact": 3, "urgency": 2,
                        "u_region": p["u_region"] if p["u_region"] != "ALL" else rnd.choice(REGIONS), "state": "In Progress", "active": "true",
                        "assignment_group": "Platform Engineering", "caller_id": f"usr{rnd.randrange(1, 900):04d}", "contact_type": "chatbot",
                        "u_portal_user_role": "PROVIDER_NURSE", "sys_created_on": iso(t), "sys_updated_on": iso(t),
                        "parent_incident": p["number"], "work_notes": []})
    routine_topics = [t for t in TOPICS if t.bucket not in ("outage_performance", "duplicate_noise")]
    for i in range(routine):
        topic = rnd.choice(routine_topics)
        region = rnd.choice(REGIONS)
        t = n0 - timedelta(hours=rnd.uniform(0.1, 11.9))
        closed = rnd.random() < 0.45
        out.append({"number": f"INC00{30100 + i}", "short_description": _fill(rnd.choice(topic.asks), rnd, region, {})[:160], "description": "",
                    "category": topic.category, "subcategory": topic.subcategory, "priority": rnd.choice(["P3", "P4"]), "impact": 3, "urgency": 3,
                    "u_region": region, "state": "Resolved" if closed else rnd.choice(["New", "In Progress", "On Hold"]), "active": "false" if closed else "true",
                    "assignment_group": topic.group, "caller_id": f"usr{rnd.randrange(1, 900):04d}", "contact_type": rnd.choice(["phone", "chatbot", "self-service"]),
                    "u_portal_user_role": rnd.choice(ROLES), "sys_created_on": iso(t), "sys_updated_on": iso(t), "parent_incident": "", "work_notes": [],
                    "close_notes": _fill(rnd.choice(topic.closes), rnd, region, {}) if closed else "", "close_code": rnd.choice(topic.close_codes) if closed else ""})
    return out


def stats(history: list[dict], key: dict, live: list[dict]) -> str:
    b = Counter(v["bucket"] for v in key.values())
    lines = [f"history incidents: {len(history):,} over {config.HISTORY_DAYS} days · live window (last 12 h): {len(live)} incidents",
             f"answer key: {len(key):,} labels (held aside; never stored in ServiceNow)", "", "true root-cause bucket   count   share"]
    for k, v in b.most_common():
        lines.append(f"  {k:22s} {v:6,d}  {v / len(key):5.1%}")
    agree = sum(1 for r in history if r["category"] == next(t.category for t in TOPICS if t.topic == key[r["number"]]["topic"]))
    lines.append(f"\nrecorded category matches the careful category: {agree / len(history):.1%} (the rest were mis-categorised at intake)")
    gaps = Counter(v["topic"] for v in key.values() if v["bucket"] == "knowledge_gap")
    lines.append("knowledge-gap topics: " + ", ".join(f"{k} {v}" for k, v in gaps.most_common()))
    lines.append(f"incidents with a parent major incident: {sum(1 for r in history if r['parent_incident'])}")
    lines.append(f"planted PHI-like strings: member ids {sum('NW-' in r['description'] for r in history)}, phone numbers {sum('-555-' in r['description'] for r in history)}")
    lines.append(f"live: {sum(1 for r in live if r.get('major_incident') == 'true')} major incidents open, "
                 f"{sum(1 for r in live if r['active'] == 'true')} open incidents in the window")
    return "\n".join(lines)
