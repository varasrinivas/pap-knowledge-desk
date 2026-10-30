"""Stage 2, CLEAN: remove what should never be embedded, before it is embedded.

- e-mail signatures and confidentiality footers in work notes (they make every incident look alike to the model)
- exact duplicates (same caller, same normalised text): keep the oldest, count the rest
- PHI-like strings (member ids, phone numbers, SSNs, e-mails): redacted, and counted by kind
"""
from __future__ import annotations

import re
from collections import Counter

from desk.redact import redact

SIGNATURE = re.compile(r"\n--\s.*?(?:Service Desk|Northwind).*?(?:\n.*?confidential.*)?$", re.I | re.S)
FOOTER = re.compile(r"This message may contain confidential information.*$", re.I | re.S)
WS = re.compile(r"\s+")


def norm(s: str) -> str:
    return WS.sub(" ", (s or "")).strip()


def clean_note(text: str) -> str:
    return norm(FOOTER.sub("", SIGNATURE.sub("", text or "")))


def clean_incidents(rows: list[dict]) -> tuple[list[dict], dict]:
    report = {"in": len(rows), "signatures_stripped": 0, "duplicates_removed": 0, "redacted": Counter(), "empty_resolution": 0}
    seen, out = set(), []
    for r in rows:
        notes_raw = r.get("work_notes") or ""
        notes = clean_note(notes_raw)
        if len(notes) < len(norm(notes_raw)):
            report["signatures_stripped"] += 1
        dkey = (r.get("caller_id", ""), norm(r["short_description"]).lower(), norm(r.get("close_notes")).lower())
        if dkey in seen:
            report["duplicates_removed"] += 1
            continue
        seen.add(dkey)
        fields = {}
        for f in ("short_description", "description", "close_notes"):
            txt, kinds = redact(norm(r.get(f)))
            fields[f] = txt
            report["redacted"].update(kinds)
        notes, kinds = redact(notes)
        report["redacted"].update(kinds)
        if not fields["close_notes"]:
            report["empty_resolution"] += 1
        out.append({**r, **fields, "work_notes": notes})
    report["out"] = len(out)
    report["redacted"] = dict(report["redacted"])
    return out, report


def clean_documents(docs: list[dict]) -> tuple[list[dict], dict]:
    """Documents are authored text: normalise line endings and trailing spaces, redact (should find nothing), keep structure."""
    found = Counter()
    out = []
    for d in docs:
        body = "\n".join(line.rstrip() for line in d["body"].replace("\r\n", "\n").split("\n"))
        body, kinds = redact(body)
        found.update(kinds)
        out.append({**d, "body": body})
    return out, {"in": len(docs), "out": len(out), "redacted": dict(found)}
