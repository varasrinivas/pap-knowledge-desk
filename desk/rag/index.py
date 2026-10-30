"""Stage 5, INDEX: write chunks + vectors + metadata into the Chroma container, idempotently.

- One collection per source, named '<source>_<suffix>' (suffix v1). A new embedding model gets a new suffix; you never
  mix vectors from two models in one collection.
- Collection config: cosine space (vectors are unit length) and HNSW build/search parameters set explicitly.
- Deterministic ids: '<source_id>#<section index>.<part>' and a content hash in the metadata. A rerun embeds only chunks
  whose hash changed, upserts them, and deletes ids that no longer exist in the source: rebuilds are cheap and safe.
- Upserts go in batches (Chroma caps a single request's size).
"""
from __future__ import annotations

import hashlib
import time

from desk import config
from desk.rag import bm25
from desk.rag.embed import embedder

HNSW = {"hnsw:space": "cosine", "hnsw:construction_ef": 128, "hnsw:M": 16, "hnsw:search_ef": 64}
BATCH = 1000


def client():
    import chromadb
    return chromadb.HttpClient(host=config.CHROMA_HOST, port=config.CHROMA_PORT)


def collection_name(source: str) -> str:
    return f"{source}_{config.COLLECTION_SUFFIX}"


def get_collection(source: str, create: bool = False):
    c = client()
    name = collection_name(source)
    if create:
        return c.get_or_create_collection(name, metadata={**HNSW, "embedding_model": config.EMBED_MODEL, "dim": config.EMBED_DIM,
                                                          "source": source})
    return c.get_collection(name)


def content_hash(text: str, meta: dict) -> str:
    return hashlib.sha1((text + "|" + str(sorted((k, str(v)) for k, v in meta.items()))).encode()).hexdigest()[:16]


def assign_ids(chunks: list[dict]) -> list[dict]:
    seen: dict[str, int] = {}
    for c in chunks:
        sid = c["meta"]["source_id"]
        i = seen.get(sid, 0)
        seen[sid] = i + 1
        c["id"] = sid if c["meta"].get("doc_type") == "incident" else f"{sid}#{i}"
        c["meta"]["chunk"] = i
        c["meta"]["hash"] = content_hash(c["text"], {k: v for k, v in c["meta"].items() if k != "hash"})
    return chunks


def index(source: str, chunks: list[dict], log=print) -> dict:
    """Upsert changed chunks, delete vanished ones, rebuild the BM25 side index. Returns what happened, with timings."""
    t_all = time.time()
    col = get_collection(source, create=True)
    chunks = assign_ids(chunks)
    existing: dict[str, str] = {}
    offset = 0
    while True:                                                    # read back ids + hashes already stored
        got = col.get(include=["metadatas"], limit=5000, offset=offset)
        for i, m in zip(got["ids"], got["metadatas"]):
            existing[i] = (m or {}).get("hash", "")
        if len(got["ids"]) < 5000:
            break
        offset += 5000
    todo = [c for c in chunks if existing.get(c["id"]) != c["meta"]["hash"]]
    gone = sorted(set(existing) - {c["id"] for c in chunks})
    t0 = time.time()
    vecs = embedder().docs([c["text"] for c in todo]) if todo else []
    t_embed = time.time() - t0
    t0 = time.time()
    for s in range(0, len(todo), BATCH):
        part = todo[s: s + BATCH]
        col.upsert(ids=[c["id"] for c in part], documents=[c["text"] for c in part],
                   metadatas=[c["meta"] for c in part], embeddings=[v.tolist() for v in vecs[s: s + BATCH]])
    for s in range(0, len(gone), BATCH):
        col.delete(ids=gone[s: s + BATCH])
    t_upsert = time.time() - t0
    bm25.save(source, [c["id"] for c in chunks], [c["text"] for c in chunks])
    return {"collection": collection_name(source), "chunks": len(chunks), "unchanged": len(chunks) - len(todo),
            "embedded": len(todo), "deleted": len(gone), "embed_s": round(t_embed, 1), "upsert_s": round(t_upsert, 1),
            "batches": (len(todo) + BATCH - 1) // BATCH, "count_after": col.count(), "total_s": round(time.time() - t_all, 1)}
