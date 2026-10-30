"""PHI minimum-necessary redaction (ported from the course simulator). Runs before embedding and before any live model call."""
from __future__ import annotations

import re

PATTERNS = [
    ("ssn", re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "[SSN-REDACTED]"),
    ("member_id", re.compile(r"\bNW-\d{7}\b"), "[MEMBER-ID-REDACTED]"),
    ("dob", re.compile(r"\b(?:DOB|dob|born)[:\s]+\d{1,2}/\d{1,2}/\d{2,4}\b"), "[DOB-REDACTED]"),
    ("phone", re.compile(r"\(?\b\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}\b"), "[PHONE-REDACTED]"),
    ("email", re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.]+\b"), "[EMAIL-REDACTED]"),
]


def redact(text: str) -> tuple[str, list[str]]:
    """Return (redacted_text, kinds_found)."""
    hits = []
    for kind, pat, repl in PATTERNS:
        if pat.search(text):
            text = pat.sub(repl, text)
            hits.append(kind)
    return text, hits
