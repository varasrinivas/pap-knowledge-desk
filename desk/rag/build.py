"""Build every RAG collection, stage by stage, and explain what each stage did with real numbers.

    python -m desk build-rag --explain          # prints each stage; writes .runtime/INGEST-REPORT.md
    python -m desk build-rag --bench            # also times embedding batch sizes on 1,000 incidents

Order: load -> clean -> chunk -> embed+index (idempotent) -> verify. Running it twice embeds nothing the second time.
"""
from __future__ import annotations

import json
import statistics
import time
from collections import Counter

from desk import config
from desk.rag import chunk as chunking
from desk.rag.clean import clean_documents, clean_incidents
from desk.rag.embed import QUERY_PREFIX, benchmark, embedder
from desk.rag.index import HNSW, index
from desk.rag.load import DOC_SOURCES, load_documents, load_incidents
from desk.rag.verify import verify

REPORT = config.RUNTIME_DIR / "INGEST-REPORT.md"
RULES = {"kb_policy": "one chunk per '## ' section; sections over the cap split on paragraphs with overlap",
         "kb_workflow": "one chunk per '### Step', with the document Summary prepended; Exceptions as their own chunk",
         "kb_ui": "one chunk per '## Procedure:' (never split mid-procedure) plus one for 'Common errors'",
         "kb_drafts": "same rule as the collection the draft targets"}


def _hist(lengths: list[int], edges=(0, 64, 128, 192, 256, 350, 512, 10_000)) -> list[str]:
    rows = []
    for lo, hi in zip(edges, edges[1:]):
        n = sum(lo <= x < hi for x in lengths)
        label = f"{lo}-{hi - 1}" if hi < 10_000 else f"{lo}+"
        rows.append(f"    {label:>8} tokens | {'#' * max(0, round(40 * n / max(1, len(lengths))))} {n}")
    return rows


def build(explain: bool = True, bench: bool = False) -> dict:
    lines: list[str] = []

    def say(s: str = ""):
        lines.append(s)
        if explain:
            print(s, flush=True)

    t_start = time.time()
    summary = {}
    e = embedder()
    say(f"# RAG build: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    say(f"embedding model {e.name} · {config.EMBED_DIM} dimensions · CPU (ONNX) · query prefix '{QUERY_PREFIX.strip()}' (queries only)")
    say(f"Chroma http://{config.CHROMA_HOST}:{config.CHROMA_PORT} · collection config {HNSW}")

    # ---------------- documents ----------------
    for source in ["kb_policy", "kb_workflow", "kb_ui", "kb_drafts"]:
        t0 = time.time()
        docs = load_documents(source)
        if not docs and source == "kb_drafts":
            say(f"\n## {source}: no approved drafts yet (the knowledge-fix loop fills it)")
            from desk.rag.index import get_collection
            get_collection(source, create=True)
            from desk.rag import bm25
            bm25.save(source, [], [])
            summary[source] = {"chunks": 0}
            continue
        say(f"\n## {source}  (data/kb/{DOC_SOURCES[source]}/)")
        say(f"1 LOAD    {len(docs)} documents, front matter keys: {sorted({k for d in docs for k in d['meta']})}")
        docs, crep = clean_documents(docs)
        say(f"2 CLEAN   normalised whitespace; PHI-like strings found: {crep['redacted'] or 'none'}")
        chunks = chunking.chunk_documents(docs)
        toks = [chunking.count_tokens(c["text"]) for c in chunks]
        over = [c["meta"]["source_id"] + " / " + c["meta"]["section"] for c, t in zip(chunks, toks) if t > chunking.TOKEN_CAP]
        say(f"3 CHUNK   rule: {RULES[source]}")
        say(f"          {len(chunks)} chunks from {len(docs)} documents ({len(chunks) / max(1, len(docs)):.1f} per doc); tokens min {min(toks)}, "
            f"median {int(statistics.median(toks))}, max {max(toks)}; over the {chunking.TOKEN_CAP}-token cap: {len(over)}")
        for row in _hist(toks):
            say(row)
        if over:
            say(f"          kept whole although over the cap: {', '.join(over[:4])}{' ...' if len(over) > 4 else ''}")
        ex = chunks[1] if len(chunks) > 1 else chunks[0]
        say(f"          example chunk {ex['meta']['source_id']} / {ex['meta']['section']} ({toks[1 if len(chunks) > 1 else 0]} tokens):")
        say("            " + ex["text"][:300].replace("\n", "\n            ") + (" ..." if len(ex["text"]) > 300 else ""))
        say(f"          metadata: {json.dumps({k: v for k, v in ex['meta'].items() if k not in ('hash',)})[:400]}")
        r = index(source, chunks)
        say(f"4 EMBED+INDEX  embedded {r['embedded']} new/changed, {r['unchanged']} unchanged, deleted {r['deleted']} · "
            f"embed {r['embed_s']}s · upsert {r['upsert_s']}s in {r['batches']} batch(es)")
        v = verify(source, len(chunks), {d["source_id"] for d in docs})
        _say_verify(say, v)
        summary[source] = {"documents": len(docs), "chunks": len(chunks), "median_tokens": int(statistics.median(toks)), **r,
                           "verify_ok": v["counts_match"] and not v["orphans"] and not v["duplicate_ids"], "seconds": round(time.time() - t0, 1)}

    # ---------------- incidents ----------------
    source = "incident_resolutions"
    t0 = time.time()
    say(f"\n## {source}  (ServiceNow Table API {config.SERVICENOW_API})")
    rows, lrep = load_incidents()
    say(f"1 LOAD    {len(rows):,} resolved/closed incidents in {lrep['pages']} pages of {lrep['page_size']} "
        f"(sysparm_limit/sysparm_offset) in {lrep['seconds']}s; open incidents stay out: they are the live tool's job")
    rows, crep = clean_incidents(rows)
    say(f"2 CLEAN   signatures/footers stripped from {crep['signatures_stripped']:,} work-note sets · exact duplicates removed "
        f"{crep['duplicates_removed']} · redacted {crep['redacted']} · empty resolutions {crep['empty_resolution']}")
    chunks = [chunking.incident_document(r) for r in rows]
    sample_toks = [chunking.count_tokens(c["text"]) for c in chunks[:2000]]
    say(f"3 CHUNK   one document per incident: 'Problem / Details / Resolution' is embedded; category, region, role, "
        f"close_code, priority, created_epoch, parent stay metadata for filters")
    say(f"          tokens (first 2,000): median {int(statistics.median(sample_toks))}, max {max(sample_toks)} (far below bge's 512 limit)")
    ex = chunks[7]
    say("          example document:\n            " + ex["text"].replace("\n", "\n            "))
    say(f"          metadata: {json.dumps(ex['meta'])}")
    say("          dates are stored as created_epoch (int) because Chroma's where-filters compare numbers ($gte/$lt), not date strings")
    if bench:
        b = benchmark([c["text"] for c in chunks[:1000]])
        say("          embedding batch size vs throughput (1,000 incidents): " + "; ".join(f"batch {x['batch_size']}: {x['docs_per_s']} docs/s" for x in b))
    r = index(source, chunks)
    say(f"4 EMBED+INDEX  embedded {r['embedded']:,} new/changed, {r['unchanged']:,} unchanged, deleted {r['deleted']} · "
        f"embed {r['embed_s']}s · upsert {r['upsert_s']}s in {r['batches']} batch(es) of up to 1,000")
    v = verify(source, len(chunks), {c["meta"]["source_id"] for c in chunks})
    _say_verify(say, v)
    cats = Counter(c["meta"]["category"] for c in chunks)
    say(f"          by recorded category: {dict(cats.most_common())}")
    summary[source] = {"documents": len(rows), "chunks": len(chunks), **r,
                       "verify_ok": v["counts_match"] and not v["orphans"] and not v["duplicate_ids"], "seconds": round(time.time() - t0, 1)}

    total = round(time.time() - t_start, 1)
    say(f"\nrag_build: {sum(s.get('chunks', 0) for s in summary.values()):,} chunks in {len(summary)} collections · "
        f"all verified: {all(s.get('verify_ok', True) for s in summary.values())} · {total}s")
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    (config.RUNTIME_DIR / "rag_build.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
    return summary


def _say_verify(say, v: dict):
    s = v["sample"]
    say(f"5 VERIFY  stored {v['stored']:,} / expected {v['expected']:,} -> {'OK' if v['counts_match'] else 'MISMATCH'} · "
        f"orphans {v['orphans']} · duplicate ids {v['duplicate_ids']}")
    say(f"          sample {s['id']}: dim {s['dim']}, norm {s['norm']}, first 8 values {s['vector_first8']}")
    if "sanity" in v:
        sn = v["sanity"]
        say(f"          sanity query '{sn['query']}' -> {', '.join(f'{i} ({sc:.3f})' for i, sc in sn['top'])} -> {'OK' if sn['ok'] else 'CHECK'}")
