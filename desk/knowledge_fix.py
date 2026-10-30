"""Close knowledge gaps: cluster -> draft article -> human approval -> index into kb_drafts -> measure deflection again.

    python -m desk knowledge-fix --demo

Deflection = the share of gap questions the desk answers from a document (route 'resolve') instead of from analysts'
history or a new ticket. The demo measures it before, drafts one article per gap cluster plus a correction for any
contradiction the profiler found (the stale 20 MB limit in UI-05), approves them (in the UI a person presses Approve),
re-indexes, and measures again on the same questions.
"""
from __future__ import annotations

import json
import random
import re
import time

from desk import config
from desk.agents import agent
from desk.rag.chunk import chunk_documents
from desk.rag.index import index
from desk.rag.load import load_documents
from desk.world import iso, now

DRAFTS = config.RUNTIME_DIR / "drafts"
PENDING, APPROVED = DRAFTS / "pending", DRAFTS / "approved"


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:50]


def draft_from_profile() -> list[dict]:
    """One pending draft per gap cluster, plus one correction per contradiction."""
    prof = json.loads((config.RUNTIME_DIR / "profile.json").read_text())
    PENDING.mkdir(parents=True, exist_ok=True)
    out = []
    for n, c in enumerate(prof["clusters"], 1):
        if c["size"] < 20:
            continue
        title = c["examples"][0]["problem"].rstrip("?").strip()
        title = title[0].upper() + title[1:]
        c = {**c, "title": title}
        body = agent("article").run(json.dumps(c, default=str)).content
        did = f"DRAFT-{n:02d}"
        meta = {"id": did, "title": title, "doc_type": "ui", "owner": "Knowledge Desk (draft)", "version": "0.1", "kb_version": "0.1",
                "source": f"gap cluster {c['cluster']} ({c['size']} incidents)", "status": "pending", "target_collection": "kb_ui"}
        out.append(_write(did, meta, body))
    for k, ctr in enumerate(prof.get("contradictions", []), 1):
        did = f"FIX-{k:02d}"
        says = max(ctr["resolutions_say"], key=ctr["resolutions_say"].get)
        body = (f"# Correction to {ctr['doc']}: {ctr['title']}\n\n{ctr['doc']} states {', '.join(x + ' MB' for x in ctr['doc_says'])}. "
                f"{ctr['incidents']} resolved incidents state {says} MB, matching the documentation-standards policy.\n\n"
                f"## Procedure: Check the file size limit before uploading\n1. The per-file limit is **{says} MB** [CHECK with the portal team].\n"
                f"2. Compress or split larger files before **Upload files**.\n\n**What you should see:** files under {says} MB reach `Available`.\n")
        meta = {"id": did, "title": f"Correction: {ctr['title']} size limit", "doc_type": "ui", "owner": "Knowledge Desk (draft)",
                "version": "0.1", "kb_version": "0.1", "source": f"contradiction with {ctr['doc']}", "status": "pending", "target_collection": "kb_ui"}
        out.append(_write(did, meta, body))
    return out


def _write(did: str, meta: dict, body: str) -> dict:
    fm = "\n".join(f"{k}: {v}" for k, v in meta.items())
    path = PENDING / f"{did}-{_slug(meta['title'])}.md"
    path.write_text(f"---\n{fm}\n---\n{body}\n", encoding="utf-8")
    return {"id": did, "title": meta["title"], "path": str(path), "source": meta["source"]}


def list_drafts() -> dict:
    def read(folder):
        out = []
        for p in sorted(folder.glob("*.md")) if folder.exists() else []:
            t = p.read_text(encoding="utf-8")
            title = re.search(r"^title: (.+)$", t, re.M)
            src = re.search(r"^source: (.+)$", t, re.M)
            out.append({"file": p.name, "title": title.group(1) if title else p.stem, "source": src.group(1) if src else "", "text": t})
        return out
    return {"pending": read(PENDING), "approved": read(APPROVED)}


def approve(file: str, by: str = "u-devika") -> dict:
    """A person approved the draft: stamp it, move it, re-index kb_drafts (only this draft's chunks are new)."""
    APPROVED.mkdir(parents=True, exist_ok=True)
    src = PENDING / file
    t = src.read_text(encoding="utf-8").replace("status: pending", f"status: approved\napproved_at: {iso(now())}\napproved_by: {by}")
    (APPROVED / file).write_text(t, encoding="utf-8")
    src.unlink()
    return reindex_drafts()


def reindex_drafts() -> dict:
    docs = load_documents("kb_drafts")
    return index("kb_drafts", chunk_documents(docs))


def gap_questions(n: int = 30) -> list[dict]:
    """Held-out questions from gap incidents (their real wording), the course's G-01 question, and a few stale-fact ones."""
    key = json.loads((config.RUNTIME_DIR / "answer_key.json").read_text())
    import httpx
    gap_ids = [k for k, v in key.items() if v["bucket"] == "knowledge_gap"]
    rnd = random.Random(7)
    pick = rnd.sample(gap_ids, min(n, len(gap_ids)))
    qs = []
    with httpx.Client(base_url=config.SERVICENOW_API, auth=(config.SERVICENOW_USER, config.SERVICENOW_PASS), trust_env=False, timeout=20) as c:
        for num in pick:
            r = c.get(f"/api/now/table/incident/{num}")
            if r.status_code == 200:
                qs.append({"q": r.json()["result"]["short_description"], "topic": key[num]["topic"]})
    qs.append({"q": "How do I add a second servicing provider to an existing request?", "topic": "second_servicing_provider"})
    return qs


def deflection(qs: list[dict]) -> tuple[float, list[str]]:
    from desk.workflow import ask
    routes = [ask("u-liam", x["q"], thread_id=f"kf-{i}")["route"] for i, x in enumerate(qs)]
    return sum(r == "resolve" for r in routes) / len(routes), routes


def reset_drafts():
    """Start the demo from 'no drafts': delete pending and approved files and empty the kb_drafts collection."""
    import shutil
    shutil.rmtree(DRAFTS, ignore_errors=True)
    reindex_drafts()


def demo():
    t0 = time.time()
    reset_drafts()
    qs = gap_questions()
    print(f"# Knowledge fix · {len(qs)} gap questions (real wording from held-out gap incidents)\n")
    before, rb = deflection(qs)
    print(f"1 BEFORE   answered from a document: {before:.0%} · routes {dict((r, rb.count(r)) for r in set(rb))}")
    drafts = draft_from_profile()
    print(f"2 DRAFT    {len(drafts)} drafts written to {PENDING.relative_to(config.RUNTIME_DIR.parent) if PENDING.is_relative_to(config.RUNTIME_DIR.parent) else PENDING}:")
    for d in drafts:
        print(f"           {d['id']}  {d['title'][:70]}  ({d['source']})")
    first = list_drafts()["pending"][0] if drafts else None
    if first:
        print("\n           first draft, as the reviewer sees it:\n           " + first["text"][:700].replace("\n", "\n           "))
    for d in list_drafts()["pending"]:
        r = approve(d["file"])
    print(f"\n3 APPROVE  {len(drafts)} approved (demo approves all; in the UI a person approves each) -> kb_drafts re-indexed: "
          f"{r['chunks'] if drafts else 0} chunks, {r['embedded'] if drafts else 0} embedded")
    after, ra = deflection(qs)
    print(f"4 AFTER    answered from a document: {after:.0%} · routes {dict((r, ra.count(r)) for r in set(ra))}")
    print(f"\ndeflection: {before:.0%} -> {after:.0%} on {len(qs)} gap questions · {time.time() - t0:.0f}s")
