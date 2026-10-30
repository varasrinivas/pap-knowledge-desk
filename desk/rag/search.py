"""Querying one collection three ways: vector (Chroma), keyword (BM25), hybrid (reciprocal-rank fusion of the two).

Each collection has its own relevance gate, calibrated by `python -m desk retrieval-eval` and stored in .runtime/gates.json:
a cosine similarity below the gate means "this source has nothing on it", which is how knowledge gaps are detected.
"""
from __future__ import annotations

import json

from desk import config
from desk.rag import bm25
from desk.rag.embed import embedder
from desk.rag.index import get_collection

GATES_FILE = config.RUNTIME_DIR / "gates.json"
DEFAULT_GATES = {"kb_policy": 0.62, "kb_workflow": 0.62, "kb_ui": 0.62, "incident_resolutions": 0.70, "kb_drafts": 0.62}
SOURCES = ["kb_policy", "kb_workflow", "kb_ui", "incident_resolutions", "kb_drafts"]


def gates() -> dict:
    try:
        return {**DEFAULT_GATES, **json.loads(GATES_FILE.read_text())}
    except (OSError, ValueError):
        return dict(DEFAULT_GATES)


def vector(source: str, query: str, k: int = 8, where: dict | None = None, prefix: bool = True) -> list[dict]:
    col = get_collection(source)
    if col.count() == 0:
        return []
    q = embedder().query(query, prefix=prefix)
    r = col.query(query_embeddings=[q.tolist()], n_results=min(k, col.count()), where=where or None,
                  include=["documents", "metadatas", "distances"])
    return [{"id": i, "text": d, "meta": m, "score": round(1 - dist, 4)}           # cosine distance -> similarity
            for i, d, m, dist in zip(r["ids"][0], r["documents"][0], r["metadatas"][0], r["distances"][0])]


def keyword(source: str, query: str, k: int = 8) -> list[tuple[str, float]]:
    idx = bm25.load(source)
    return idx.search(query, k) if idx else []


def hybrid(source: str, query: str, k: int = 5, where: dict | None = None, rrf_k: int = 60, depth: int = 20) -> list[dict]:
    """RRF: score = sum over rankers of 1/(rrf_k + rank). Ranks, not raw scores, so cosine and BM25 scales never meet."""
    vec = vector(source, query, k=depth, where=where)
    kw = keyword(source, query, k=depth)
    by_id = {h["id"]: h for h in vec}
    fused: dict[str, float] = {}
    for rank, h in enumerate(vec, 1):
        fused[h["id"]] = fused.get(h["id"], 0) + 1 / (rrf_k + rank)
    kw_rank = {}
    for rank, (cid, _) in enumerate(kw, 1):
        kw_rank[cid] = rank
        if where and cid not in by_id:
            continue                                  # a keyword hit outside the metadata filter is not allowed in
        fused[cid] = fused.get(cid, 0) + 1 / (rrf_k + rank)
    missing = [cid for cid in fused if cid not in by_id]
    if missing:
        got = get_collection(source).get(ids=missing, include=["documents", "metadatas", "embeddings"])
        qv = embedder().query(query)
        for i, d, m, e in zip(got["ids"], got["documents"], got["metadatas"], got["embeddings"]):
            by_id[i] = {"id": i, "text": d, "meta": m, "score": round(float(qv @ e), 4)}
    out = []
    for cid, s in sorted(fused.items(), key=lambda x: -x[1])[:k]:
        h = dict(by_id[cid])
        h.update(rrf=round(s, 5), vector_rank=next((r for r, v in enumerate(vec, 1) if v["id"] == cid), None), keyword_rank=kw_rank.get(cid))
        out.append(h)
    return out


def retrieve(source: str, query: str, k: int = 4, where: dict | None = None) -> dict:
    """Hybrid hits plus the gate verdict for this source: {'hits': [...], 'above_gate': bool, 'top': float, 'gate': float}."""
    try:
        hits = hybrid(source, query, k=k, where=where)
    except Exception as e:                                       # a missing collection is "no evidence", never a crash
        return {"source": source, "hits": [], "above_gate": False, "top": 0.0, "gate": gates()[source], "error": str(e)[:120]}
    top = max((h["score"] for h in hits), default=0.0)
    g = gates()[source]
    return {"source": source, "hits": hits, "above_gate": top >= g, "top": top, "gate": g}
