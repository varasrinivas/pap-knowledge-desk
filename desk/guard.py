"""The COMPOSE prompt's rules, checked in code after the reply is written.

A system prompt asks; it cannot guarantee. Each rule below is one clause of COMPOSE (desk/agents.py) that a model can break
without any error being raised. The guard runs on every reply, whichever model wrote it:

  cited           every line that states a fact ends with a source in brackets   (desk statements such as "I can raise..." are exempt)
  grounded        every cited id appears in the evidence pack the model was given
  length          160 words or fewer
  no_identifiers  no member id, SSN, phone, e-mail or date of birth (the patterns in desk/redact.py)
  no_promises     no promised outcome or time ("will be approved", "by tomorrow")
  no_clinical     no clinical advice ("you should get the MRI")

grounded, no_identifiers and no_clinical are BLOCKING: the reply is replaced by the safe fallback. The others are recorded.
"""
from __future__ import annotations

import json
import re

from desk.redact import PATTERNS

CITE = re.compile(r"\[((?:POL|WF|UI|DRAFT|FIX)-\d{2}|INC\d{7}|portal:\w+|servicenow:\w+)")
DESK_LINE = re.compile(r"^\s*(I |I'|Confirm|No document covers|Updates are posted|You do not need)", re.I)
PROMISE = re.compile(r"\bwill (?:definitely |surely )?be (?:approved|decided|fixed|resolved|processed)\b|\bby (?:tomorrow|tonight|end of day|"
                     r"monday|tuesday|wednesday|thursday|friday)\b|\bguarantee", re.I)
CLINICAL = re.compile(r"\byou should (?:get|order|start|try|schedule) (?:the |an? )?(?:mri|ct|pet|physical therapy|surgery|medication|"
                      r"injection)|\bis (?:not )?medically necessary\b|\bclinically,? (?:the patient|you) should\b", re.I)
WORD_LIMIT = 160
BLOCKING = ("grounded", "no_identifiers", "no_clinical")
EXEMPT_ROUTES = ("refuse", "clarify")


def check(reply: str, pack: dict) -> dict:
    """Return {'ok': bool, 'failed': [...], 'blocking': bool, 'detail': {...}} for one reply and the pack it was written from."""
    failed, detail = [], {}
    lines = [ln for ln in reply.splitlines() if ln.strip()]
    if pack.get("route") not in EXEMPT_ROUTES:
        uncited = [ln for ln in lines if not CITE.search(ln) and not DESK_LINE.match(ln)]
        if uncited:
            failed.append("cited"); detail["uncited"] = [ln[:80] for ln in uncited]
    evidence = json.dumps(pack, default=str)
    unknown = sorted({c for c in CITE.findall(reply) if c not in evidence})
    if unknown:
        failed.append("grounded"); detail["unknown_citations"] = unknown
    words = len(re.findall(r"\S+", reply))
    if words > WORD_LIMIT:
        failed.append("length"); detail["words"] = words
    kinds = [kind for kind, pat, _ in PATTERNS if pat.search(reply)]
    if kinds:
        failed.append("no_identifiers"); detail["identifiers"] = kinds
    if PROMISE.search(reply):
        failed.append("no_promises"); detail["promise"] = PROMISE.search(reply).group(0)
    if CLINICAL.search(reply):
        failed.append("no_clinical"); detail["clinical"] = CLINICAL.search(reply).group(0)
    return {"ok": not failed, "failed": failed, "blocking": any(f in BLOCKING for f in failed), "detail": detail}
