# Building the RAG databases, stage by stage

`python -m desk build-rag --explain` runs every stage and prints what it did. The ingest container runs the same code and
writes the full transcript to `/runtime/INGEST-REPORT.md` (in the UI: Reports → RAG build report). The numbers below come from a
real run on the fixture data. Your timings will differ: embedding speed depends on the CPU.

The pipeline is six files in `desk/rag/`, one per stage:

```
load.py → clean.py → chunk.py → embed.py → index.py → verify.py          (build.py runs them; search.py queries the result)
```

## 1. Load: three source types, five collections

| Collection | Source | Loader | Count |
|---|---|---|---|
| `kb_policy_v1` | `data/kb/policy/*.md` | front matter + body per file | 20 documents |
| `kb_workflow_v1` | `data/kb/workflow/*.md` | same | 12 documents |
| `kb_ui_v1` | `data/kb/ui/*.md` | same | 18 documents |
| `incident_resolutions_v1` | ServiceNow Table API | paged `GET /api/now/table/incident` | about 15,060 resolved/closed incidents |
| `kb_drafts_v1` | `/runtime/drafts/approved/*.md` | front matter + body | 0 until the knowledge-fix loop approves drafts |

**Why five collections and not one?**
- **The sources answer different questions.** Policy says what is required, workflow says who does what next, UI says where to
  click, and incidents say what fixed it last time.
- **They are owned by different teams.**
- **They need different chunking and different filters.**

`python -m desk retrieval-eval` measures what merging costs. It copies the same vectors into one collection and searches the same
labelled questions:

| | hit@1 split | hit@1 merged |
|---|---|---|
| policy | 0.69 | 0.50 |
| workflow | 0.92 | 0.54 |
| UI | 0.94 | 0.81 |

**Paging incidents.** The query is `stateINResolved,Closed^ORDERBYnumber`, with `sysparm_fields` set to the 17 fields we use,
`sysparm_limit=1000`, and `sysparm_offset` advancing until `X-Total-Count` is reached. The fixture run read 16 pages in 3.6 s.
Open incidents stay out of RAG: the live 12-hour window changes every minute, so the `sn_live_incidents` tool queries it fresh.

## 2. Clean: before anything is embedded

| What | Why | Fixture run |
|---|---|---|
| Strip e-mail signatures and confidentiality footers from work notes | Identical boilerplate makes unrelated incidents look similar to the model | 7,571 work-note sets cleaned |
| Drop exact duplicates (same caller, problem and resolution) | Duplicates inflate one answer's weight in retrieval | 262 removed |
| Redact PHI-like strings (member ids `NW-…`, phone numbers, SSNs, e-mails) | What is embedded is stored, returned and shown | 589 member ids and 712 phone numbers masked |

Documents get whitespace normalisation and the same redaction. The redaction found 1 hit: an example member-id pattern inside
a UI document.

## 3. Chunk: one rule per source type

| Source | Rule | Why | Result |
|---|---|---|---|
| Policy | one chunk per `## ` section; sections over 350 tokens are split on paragraphs with about 50 tokens of overlap | a policy rule stands alone; headings are written as the question a nurse asks | 101 chunks, median 115 tokens, max 309 |
| Workflow | one chunk per `### Step …`, with the document's Summary prepended; Exceptions and "What the provider office sees" become chunks too | "Step 4: place the request" means nothing without the process around it | 86 chunks, median 212 tokens |
| UI | one chunk per `## Procedure:`, never split; plus one chunk for "Common errors" | half a click-path is worse than none; an over-cap procedure is kept whole and flagged | 78 chunks, median 197 tokens, 0 over the cap |
| Incident | one document: `Problem: … / Details: … / Resolution: …` | the problem is what users ask; the resolution is the answer | median 31 tokens, max 96 |

- **Titles go into every chunk.** Each chunk carries its document title (and the heading), so a chunk retrieved alone still
  says what it is about.
- **Token counts are real.** They come from the embedding model's own WordPiece tokenizer
  (`TextEmbedding.model.tokenizer`). bge-small truncates input at 512 tokens, so a chunk longer than that would silently
  lose its end.

**What is embedded and what is metadata.** For incidents, only the problem/resolution text is embedded. The fields you filter on
are stored as metadata:
- `category`, `subcategory`, `region`, `role`, `assignment_group`, `close_code`, `priority`, `parent_incident`, `created_epoch`;
- `bucket_pred`, which the profiler adds later.

**Dates are stored as an integer epoch.** Chroma's `where` filters compare numbers (`{"created_epoch": {"$gte": …}}`), not date
strings. Lists such as `audience` and `related` become comma-joined strings, because Chroma metadata values must be scalars.

## 4. Embed: text to 384 numbers, on the CPU

- **The model** is `BAAI/bge-small-en-v1.5`, run through fastembed (ONNX). It produces 384 dimensions, needs no key, and runs
  offline. The Dockerfile downloads it at build time and sets `HF_HUB_OFFLINE=1`.
- **The vectors come back unit-length** (norm 1.0, checked in stage 6), so cosine similarity equals the dot product, and the
  collections use the cosine space.
- **Query prefix.** bge was trained with an instruction in front of short queries, and fastembed's `query_embed` does not add it
  for this model. We measured that: the query and document vectors were identical. So `embed.py` adds the prefix to queries
  itself, and never to documents.
- **It's worth measuring before you rely on it.** `retrieval-eval` experiment 2 found the prefix changes MRR by -0.01 to 0.00 on
  these collections. For v1.5 the instruction is effectively optional.
- **Batch size.** Measured on 1,000 incidents on the development laptop:

  | batch | docs/s |
  |---|---|
  | 16 | 48 |
  | 64 | 39 |
  | 256 | 33 |

  Smaller batches pad less, because each batch is padded to its longest text, so `DESK_EMBED_BATCH` defaults to 16. Run
  `build-rag --bench` to measure your own machine.

## 5. Index: write to the Chroma container, idempotently

- **Collection config:** `{"hnsw:space": "cosine", "hnsw:construction_ef": 128, "hnsw:M": 16, "hnsw:search_ef": 64}`. Each
  collection also records which embedding model and dimension it holds.
- **Names carry a version suffix** (`_v1`). A different embedding model means a new suffix and a fresh build. Never mix vectors
  from two models in one collection: their similarity scores are not comparable.
- **Ids are deterministic.** Documents use `<doc id>#<chunk index>` and incidents use the incident number. Every chunk also
  stores a content hash.
- **A rerun reads back the stored ids and hashes,** embeds only chunks whose hash changed, upserts them in batches of 1,000, and
  deletes ids that no longer exist in the source.
  - In the fixture, the second build embedded **0** document chunks.
  - After the incidents were regenerated, it embedded 10,978, skipped 3,821 that were unchanged, and deleted 166 that had
    vanished.
- **BM25 side index.** A keyword index per collection is saved next to the data (`/runtime/bm25_<collection>.pkl`). Embeddings
  blur exact tokens such as `PI-DOC-004`, `RR-0412` and `25 MB`; BM25 matches them exactly.
- **Hybrid search** (`search.py`) fuses the two rankings with reciprocal-rank fusion:
  `score = Σ 1 / (60 + rank)`. It uses ranks, not raw scores, so cosine and BM25 scales never need to agree.

## 6. Verify: before any agent trusts the index

| Check | Fixture result |
|---|---|
| stored count = chunks produced | policy 101/101, workflow 86/86, UI 78/78, incidents 14,906/14,906 |
| orphans (stored id with no current source) | 0 |
| duplicate ids | 0 |
| sample record: dim, norm, first 8 values | dim 384, norm 1.0 |
| nearest-neighbour sanity query per collection | "what does pend code PI-DOC-004 mean" → POL-10 (0.760); "who can reassign a misrouted request" → WF-08 (0.834); "how do I upload clinical notes" → UI-05 (0.853); "Excel export downloads an empty file" → an export-defect incident (0.860) |

## 7. Enrich: the profiler writes back

After profiling (`python -m desk profile`), each incident's metadata gains `bucket_pred`. The desk uses it at query time:
- `where={"bucket_pred": {"$ne": "duplicate_noise"}}` keeps noise out of answers;
- when the most similar past incidents are `knowledge_gap`, the desk treats the question as a gap.

## 8. Gates: when is "nearest" not good enough?

Every search returns *something*. `retrieval-eval` experiment 5 compares the top cosine for labelled answerable questions with the
top cosine for five questions no source answers. It then picks each source's gate, counting a false "covered" as twice as bad as a
missed answer:

| source | gate | keeps | rejects |
|---|---|---|---|
| `kb_policy` | 0.655 | 12/16 | 5/5 |
| `kb_workflow` | 0.620 | 11/13 | 5/5 |
| `kb_ui` | 0.630 | 16/16 | 4/5 |
| `incident_resolutions` | 0.730 | | |

The one question the UI gate admits ("change the member's mailing address") is scenario G-03, the desk's one measured failure.

## 9. Re-index and version

- **A changed article:** edit the markdown and rerun `build-rag`. Only that article's chunks are re-embedded.
- **An approved draft:** `approve()` stamps `approved_at` and `approved_by`, moves the file to `drafts/approved`, and re-indexes
  `kb_drafts`. The draft's `kb_version` travels in the metadata, so an answer that cites `[DRAFT-01]` can be traced to the exact
  approved text.
- **A new embedding model:** set `DESK_EMBED_MODEL` and `DESK_COLLECTION_SUFFIX=v2` and rebuild. The `v1` collections stay until
  you delete them, so you can compare old and new before switching.
