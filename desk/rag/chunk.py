"""Stage 3, CHUNK: one rule per source type, because each type breaks in a different place.

policy   -> one chunk per '## ' section (a rule stands alone). Sections over the token cap are split on paragraphs with overlap.
workflow -> one chunk per '### Step', with the document's Summary prepended (a step means nothing without its process).
            'Exceptions' and 'What the provider office sees' become chunks of their own, also with the Summary.
ui       -> one chunk per '## Procedure:' and one for '## Common errors', never split mid-procedure (half a click-path is
            worse than none). A procedure over the cap is kept whole and flagged.
incident -> one document per incident: "Problem ... Resolution ..." is embedded; everything filterable stays metadata.

Every chunk carries the document title and heading in its text, so a chunk read alone still says what it is about.
Token counts use the embedding model's own tokenizer (bge-small truncates at 512 tokens).
"""
from __future__ import annotations

import re
from datetime import datetime, timezone

TOKEN_CAP = 350
OVERLAP = 50
H2 = re.compile(r"^## (.+)$", re.M)
H3_STEP = re.compile(r"^### (Step .+)$", re.M)

_tok = None


def count_tokens(text: str) -> int:
    global _tok
    if _tok is None:
        from desk.rag.embed import embedder
        _tok = embedder().tokenizer
    return len(_tok.encode(text).ids)


def _sections(body: str, pattern: re.Pattern) -> list[tuple[str, str]]:
    """Split on a heading pattern -> [(heading, text)], dropping the preamble before the first heading."""
    marks = list(pattern.finditer(body))
    return [(m.group(1).strip(), body[m.end(): marks[i + 1].start() if i + 1 < len(marks) else len(body)].strip())
            for i, m in enumerate(marks)]


def _preamble(body: str) -> str:
    first = re.search(r"^##", body, re.M)
    text = body[: first.start()] if first else body
    return re.sub(r"^# .+$", "", text, flags=re.M).strip()


def _split_long(text: str, cap: int = TOKEN_CAP, overlap: int = OVERLAP) -> list[str]:
    """Paragraph-greedy split; the last ~overlap tokens of a part are repeated at the start of the next."""
    paras = [p for p in text.split("\n\n") if p.strip()]
    parts, cur = [], []
    for p in paras:
        if cur and count_tokens("\n\n".join(cur + [p])) > cap:
            parts.append("\n\n".join(cur))
            tail = " ".join("\n\n".join(cur).split()[-int(overlap * 0.75):])
            cur = [tail, p]
        else:
            cur.append(p)
    if cur:
        parts.append("\n\n".join(cur))
    return parts


def _base_meta(doc: dict) -> dict:
    m = doc["meta"]
    out = {"source_id": m["id"], "title": m.get("title", ""), "doc_type": m.get("doc_type", ""), "owner": m.get("owner", ""),
           "version": m.get("version", ""), "last_reviewed": m.get("last_reviewed", ""), "path": doc["path"],
           "kb_version": m.get("kb_version", m.get("version", ""))}
    for k in ("audience", "service_types", "related", "queues", "stages", "screens"):
        if m.get(k):
            out[k] = ",".join(m[k])                     # Chroma metadata values are scalars: lists become comma strings
    for k in ("role_required", "permission", "approved_at", "target_collection"):
        if m.get(k):
            out[k] = m[k]
    return out


def chunk_policy(doc: dict) -> list[dict]:
    title, base, out = doc["meta"]["title"], _base_meta(doc), []
    for heading, text in _sections(doc["body"], H2):
        parts = _split_long(text) if count_tokens(text) > TOKEN_CAP else [text]
        for j, part in enumerate(parts):
            out.append({"text": f"{title}\n## {heading}\n{part}", "meta": {**base, "section": heading, "part": j}})
    return out


def chunk_workflow(doc: dict) -> list[dict]:
    title, base = doc["meta"]["title"], _base_meta(doc)
    summary = dict(_sections(doc["body"], H2)).get("Summary", "").split("### ")[0].strip()
    out = []
    for heading, text in _sections(doc["body"], H3_STEP):
        text = re.split(r"^## ", text, flags=re.M)[0].strip()          # a step ends where the next '## ' section starts
        out.append({"text": f"{title}\nSummary: {summary}\n### {heading}\n{text}", "meta": {**base, "section": heading, "part": 0}})
    for heading, text in _sections(doc["body"], H2):
        if heading in ("Summary",):
            continue
        out.append({"text": f"{title}\nSummary: {summary}\n## {heading}\n{text}", "meta": {**base, "section": heading, "part": 0}})
    return out


def chunk_ui(doc: dict) -> list[dict]:
    title, base = doc["meta"]["title"], _base_meta(doc)
    intro = _preamble(doc["body"])
    out = []
    for heading, text in _sections(doc["body"], H2):
        body = f"{title}\n{intro}\n## {heading}\n{text}" if heading.startswith("Procedure") else f"{title}\n## {heading}\n{text}"
        out.append({"text": body, "meta": {**base, "section": heading, "part": 0, "over_cap": count_tokens(body) > TOKEN_CAP}})
    return out


def _epoch(s: str) -> int:
    try:
        return int(datetime.strptime(s, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc).timestamp())
    except (TypeError, ValueError):
        return 0


def incident_document(r: dict) -> dict:
    """The field template: what the model reads (text) vs what the filter reads (metadata)."""
    text = f"Problem: {r['short_description']}"
    if r.get("description") and r["description"] != r["short_description"]:
        text += f"\nDetails: {r['description']}"
    text += f"\nResolution: {r.get('close_notes') or 'none recorded'}"
    meta = {"source_id": r["number"], "doc_type": "incident", "category": r.get("category", ""), "subcategory": r.get("subcategory", ""),
            "region": r.get("u_region", ""), "role": r.get("u_portal_user_role", ""), "assignment_group": r.get("assignment_group", ""),
            "close_code": r.get("close_code", ""), "priority": r.get("priority", ""), "parent_incident": r.get("parent_incident", ""),
            "created_epoch": _epoch(r.get("sys_created_on")), "created": r.get("sys_created_on", ""), "section": "incident", "part": 0}
    return {"text": text, "meta": meta}


CHUNKERS = {"policy": chunk_policy, "workflow": chunk_workflow, "ui": chunk_ui}


def chunk_documents(docs: list[dict]) -> list[dict]:
    out = []
    for d in docs:
        dtype = d["meta"].get("doc_type") or d["meta"].get("target_doc_type", "ui")
        out += CHUNKERS.get(dtype, chunk_ui)(d)
    return out
