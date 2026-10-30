"""Measure retrieval per source, then four experiments, then calibrate each source's gate.

    python -m desk retrieval-eval

  1 per source x method (vector / BM25 / hybrid): hit@1, hit@4, MRR, split lexical vs paraphrase
  2 the bge query prefix: vector search with and without it
  3 split vs merged: the three document collections searched as one (vectors copied, nothing re-embedded)
  4 Agno's built-in ChromaDb hybrid vs ours, on the UI documents
  5 gates: per source, the cosine threshold that keeps answerable questions and rejects the 'none' ones -> .runtime/gates.json
"""
from __future__ import annotations

import json
import time

import numpy as np

from desk import config
from desk.rag.index import client, get_collection
from desk.rag.search import GATES_FILE, hybrid, keyword, vector
from desk.stats import bootstrap_ci

EVAL = json.loads((config.EVAL_DIR / "retrieval.json").read_text(encoding="utf-8"))
DOCS = ["kb_policy", "kb_workflow", "kb_ui"]


def doc_of(cid: str) -> str:
    return cid.split("#")[0]


def ranks(ids: list[str], relevant: list[str]) -> int | None:
    seen = []
    for cid in ids:
        d = doc_of(cid)
        if d not in seen:
            seen.append(d)                                   # rank documents, not chunks: two chunks of one doc count once
        if d in relevant:
            return seen.index(d) + 1
    return None


def score(rs: list[int | None]) -> dict:
    n = max(1, len(rs))
    return {"hit1": sum(r == 1 for r in rs) / n, "hit4": sum(r is not None and r <= 4 for r in rs) / n,
            "mrr": sum(1 / r for r in rs if r) / n, "rr": [1 / r if r else 0.0 for r in rs]}


def method_ids(source: str, q: str, method: str, prefix: bool = True) -> list[str]:
    if method == "vector":
        return [h["id"] for h in vector(source, q, k=12, prefix=prefix)]
    if method == "bm25":
        return [i for i, _ in keyword(source, q, k=12)]
    return [h["id"] for h in hybrid(source, q, k=12)]


def run():
    t0 = time.time()
    print("# Retrieval evaluation (labelled questions in data/eval/retrieval.json)\n")
    print("1 PER SOURCE x METHOD (document-level ranks)")
    print(f"   {'source':12s} {'method':7s} {'hit@1':>6s} {'hit@4':>6s} {'MRR':>5s}  {'lexical':>7s} {'paraphr.':>8s}   MRR 95% CI")
    best = {}
    for src in DOCS:
        qs = EVAL[src]
        for m in ("vector", "bm25", "hybrid"):
            rs = [ranks(method_ids(src, x["q"], m), x["relevant"]) for x in qs]
            s = score(rs)
            lx = score([r for r, x in zip(rs, qs) if x["kind"] == "lexical"])["mrr"]
            px = score([r for r, x in zip(rs, qs) if x["kind"] == "paraphrase"])["mrr"]
            lo, hi = bootstrap_ci(s["rr"])
            print(f"   {src:12s} {m:7s} {s['hit1']:6.2f} {s['hit4']:6.2f} {s['mrr']:5.2f}  {lx:7.2f} {px:8.2f}   ({lo:.2f}-{hi:.2f})")
            best.setdefault(src, {})[m] = s["mrr"]
    # incidents: relevance by answer-key topic
    key = json.loads((config.RUNTIME_DIR / "answer_key.json").read_text())
    print("\n   incident_resolutions (relevant = same true topic in the answer key)")
    for m in ("vector", "bm25", "hybrid"):
        p4, h1 = [], []
        for x in EVAL["incident_resolutions"]:
            ids = method_ids("incident_resolutions", x["q"], m)[:4]
            tops = [key.get(i, {}).get("topic") for i in ids]
            p4.append(sum(t == x["topic"] for t in tops) / max(1, len(tops)))
            h1.append(1.0 if tops and tops[0] == x["topic"] else 0.0)
        print(f"   {'incidents':12s} {m:7s} precision@4 {np.mean(p4):.2f} · top-1 right topic {np.mean(h1):.2f}")

    print("\n2 THE bge QUERY PREFIX (vector search; fastembed's query_embed does not add it for this model)")
    for src in DOCS:
        qs = EVAL[src]
        w = score([ranks(method_ids(src, x["q"], "vector", True), x["relevant"]) for x in qs])["mrr"]
        wo = score([ranks(method_ids(src, x["q"], "vector", False), x["relevant"]) for x in qs])["mrr"]
        print(f"   {src:12s} MRR with prefix {w:.2f} · without {wo:.2f} · difference {w - wo:+.2f}")

    print("\n3 SPLIT vs MERGED (one collection holding policy + workflow + UI chunks; same vectors, copied not re-embedded)")
    merged = client().get_or_create_collection("kb_merged_eval", metadata={"hnsw:space": "cosine"})
    for src in DOCS:
        got = get_collection(src).get(include=["embeddings", "documents", "metadatas"])
        merged.upsert(ids=got["ids"], embeddings=got["embeddings"], documents=got["documents"], metadatas=got["metadatas"])
    from desk.rag.embed import embedder
    wrong_type = 0
    for src in DOCS:
        qs = EVAL[src]
        split_rs, merged_rs = [], []
        for x in qs:
            split_rs.append(ranks(method_ids(src, x["q"], "vector"), x["relevant"]))
            qv = embedder().query(x["q"])
            r = merged.query(query_embeddings=[qv.tolist()], n_results=12, include=["metadatas"])
            merged_rs.append(ranks(r["ids"][0], x["relevant"]))
            if src == "kb_ui" and r["metadatas"][0][0]["doc_type"] != "ui":
                wrong_type += 1
        print(f"   {src:12s} hit@1 split {score(split_rs)['hit1']:.2f} · merged {score(merged_rs)['hit1']:.2f}   "
              f"MRR split {score(split_rs)['mrr']:.2f} · merged {score(merged_rs)['mrr']:.2f}")
    print(f"   'how do I' UI questions whose merged top-1 was a policy or workflow chunk: {wrong_type}/{len(EVAL['kb_ui'])}")
    client().delete_collection("kb_merged_eval")

    print("\n4 AGNO'S BUILT-IN HYBRID (ChromaDb SearchType.hybrid + FastEmbedEmbedder) vs OURS, on kb_ui")
    try:
        agno_mrr, ours_mrr = _agno_compare()
        print(f"   MRR Agno built-in {agno_mrr:.2f} · ours (BM25 + prefixed vectors, RRF) {ours_mrr:.2f}")
        print("   why: Agno's keyword half filters on the query's FIRST WORD ($contains 'How'), and its embedder uses no query prefix")
    except Exception as e:
        print(f"   skipped: {str(e)[:120]}")

    print("\n5 GATES (top cosine of the right answer vs top cosine for 'none' questions)")
    gates = {}
    for src in DOCS + ["incident_resolutions"]:
        pos = []
        qs = EVAL[src]
        for x in qs:
            hits = vector(src, x["q"], k=1)
            if hits:
                pos.append(hits[0]["score"])
        neg = [vector(src, q, k=1)[0]["score"] for q in EVAL["none"]]
        grid = np.round(np.arange(0.5, 0.95, 0.005), 3)
        g = float(max(grid, key=lambda t: sum(p >= t for p in pos) + 2 * sum(n < t for n in neg)))   # a false 'covered' costs double
        gates[src] = g
        print(f"   {src:22s} answerable top-1 min {min(pos):.3f} median {np.median(pos):.3f} · none max {max(neg):.3f} -> gate {g:.3f} "
              f"(keeps {sum(p >= g for p in pos)}/{len(pos)}, rejects {sum(n < g for n in neg)}/{len(neg)})")
    gates["kb_drafts"] = gates["kb_ui"]
    GATES_FILE.write_text(json.dumps(gates, indent=1))
    print(f"   written to {GATES_FILE.name}")
    hy = np.mean([best[s]["hybrid"] for s in DOCS])
    print(f"\nretrieval_mrr: {hy:.2f} (hybrid, mean over policy/workflow/UI) · {time.time() - t0:.0f}s")


def _agno_compare() -> tuple[float, float]:
    from agno.knowledge.document import Document
    from agno.knowledge.embedder.fastembed import FastEmbedEmbedder
    from agno.vectordb.chroma import ChromaDb
    from agno.vectordb.search import SearchType
    from chromadb.config import Settings
    st = Settings(chroma_api_impl="chromadb.api.fastapi.FastAPI", chroma_server_host=config.CHROMA_HOST, chroma_server_http_port=config.CHROMA_PORT)
    vdb = ChromaDb(collection="agno_ui_eval", embedder=FastEmbedEmbedder(), search_type=SearchType.hybrid, settings=st)
    vdb.create()
    got = get_collection("kb_ui").get(include=["documents", "metadatas"])
    vdb.insert(content_hash="kb_ui_eval", documents=[Document(content=d, meta_data={"source_id": m["source_id"]}, id=i)
                                                     for i, d, m in zip(got["ids"], got["documents"], got["metadatas"])])
    agno_rs, ours_rs = [], []
    for x in EVAL["kb_ui"]:
        docs = vdb.search(x["q"], limit=12)
        agno_rs.append(ranks([d.meta_data.get("source_id", "") for d in docs], x["relevant"]))
        ours_rs.append(ranks(method_ids("kb_ui", x["q"], "hybrid"), x["relevant"]))
    vdb.client.delete_collection("agno_ui_eval")
    return score(agno_rs)["mrr"], score(ours_rs)["mrr"]
