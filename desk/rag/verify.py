"""Stage 6, VERIFY: prove the index holds what the sources hold, before any agent trusts it.

- counts: chunks stored == chunks produced, per collection
- a sample stored record: its document, metadata, the first 8 vector values and the vector norm (should be 1.0)
- a nearest-neighbour sanity query per collection with a known right answer
- orphans and duplicates: every stored id maps to a current source; no id appears twice
"""
from __future__ import annotations

import numpy as np

from desk.rag.index import get_collection
from desk.rag.search import vector

SANITY = {
    "kb_policy": ("what does pend code PI-DOC-004 mean", "POL-10"),
    "kb_workflow": ("who can reassign a misrouted request", "WF-08"),
    "kb_ui": ("how do I upload clinical notes to a request", "UI-05"),
    "incident_resolutions": ("Excel export downloads an empty file", None),     # any defect incident about export is right
}


def verify(source: str, expected_chunks: int, source_ids: set[str]) -> dict:
    col = get_collection(source)
    n = col.count()
    sample = col.get(limit=1, include=["documents", "metadatas", "embeddings"])
    emb = np.array(sample["embeddings"][0]) if len(sample["ids"]) else np.zeros(1)
    ids, offset = [], 0
    while True:
        got = col.get(include=["metadatas"], limit=5000, offset=offset)
        ids += [(i, (m or {}).get("source_id")) for i, m in zip(got["ids"], got["metadatas"])]
        if len(got["ids"]) < 5000:
            break
        offset += 5000
    orphans = [i for i, sid in ids if sid not in source_ids]
    dupes = len(ids) - len({i for i, _ in ids})
    out = {"collection": col.name, "stored": n, "expected": expected_chunks, "counts_match": n == expected_chunks,
           "orphans": len(orphans), "duplicate_ids": dupes,
           "sample": {"id": sample["ids"][0] if sample["ids"] else None,
                      "document": (sample["documents"][0] if sample["ids"] else "")[:220],
                      "metadata": sample["metadatas"][0] if sample["ids"] else {},
                      "vector_first8": [round(float(x), 4) for x in emb[:8]], "dim": int(emb.shape[0]),
                      "norm": round(float(np.linalg.norm(emb)), 4)},
           "config": col.metadata}
    if source in SANITY:
        q, want = SANITY[source]
        hits = vector(source, q, k=3)
        out["sanity"] = {"query": q, "top": [(h["id"], h["score"]) for h in hits],
                         "ok": (hits and (want is None and "export" in hits[0]["text"].lower() or hits[0]["meta"]["source_id"] == want))}
    return out
