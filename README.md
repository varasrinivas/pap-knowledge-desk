# The Knowledge Desk

A support agent for the (fictional) Northwind Prior Auth Portal. It answers nurses' questions by drawing on five RAG sources and
eight live tools, raises ServiceNow tickets only when it should, and profiles 15,000 past incidents to find and close knowledge gaps.
It is built with **Agno** and runs entirely in **Docker**, ChromaDB included, with one click. No API key needed.

This is the capstone project of the course *Resolve or Raise* (track T8, modules m36 to m44).

## Run it

| | |
|---|---|
| Windows | double-click `start.cmd` |
| macOS | double-click `start.command` (or `./start.sh`) |
| Linux | `./start.sh` |

The script starts Docker Desktop if it is not running, builds the image, starts five containers, waits for the ingest job and
opens http://localhost:8180. The first run takes about 10 minutes, most of it spent embedding 15,000 incidents. Later starts take seconds.
`stop.cmd` keeps the data; `reset.cmd` deletes the volumes and rebuilds from scratch next time.

## What runs

```
 browser ─▶ agent :8180 ─────────────┬─▶ chroma :8183   5 collections (policy, workflow, UI, incidents, drafts)
            Agno Workflow + UI       ├─▶ portal :8181   users, permissions, routing rules
            AgentOS endpoints        └─▶ servicenow :8182  15,000 incidents + live 12-hour window
 ingest (one-shot): build RAG ─▶ profile incidents ─▶ calibrate gates ─▶ exits 0, then the agent starts
```

## What to try

- **Chat tab**: pick a persona and ask. For example, as Priya, "My cardiology request went to the Northeast queue, but we're in
  Dallas." The routing tool finds rule RR-0412, the desk proposes a ticket, and you confirm it.
- **Ops dashboard**: the 15,000 incidents in eight root-cause buckets, the weekly trend, the knowledge-gap clusters, the contradiction
  the profiler found in UI-05, and the live window.
- **RAG inspector**: vector, keyword and hybrid ranks side by side for any collection.
- **Knowledge fix**: draft articles from the gap clusters, approve one, and ask the gap question again.

## Measure it

```bash
docker compose exec agent python -m desk eval               # 29 labelled scenarios
docker compose exec agent python -m desk retrieval-eval     # per-source retrieval + 4 experiments + gates
docker compose exec agent python -m desk profile            # bucket accuracy against the held-out answer key
docker compose exec agent python -m desk knowledge-fix --demo
docker compose exec agent python -m desk build-rag --explain    # rebuild (idempotent) and explain every stage
```

## Use Claude instead of the fixture model

Set `LLM_PROVIDER=anthropic`, `ANTHROPIC_API_KEY` and `LLM_MODEL` in `.env`, then run `docker compose up -d agent`.
Use a model id you have verified on Anthropic's models page. Redaction runs before any text leaves the container.

## Read more

- `docs/ARCHITECTURE.md`: the containers, the workflow, and how data moves.
- `docs/RAG-BUILD.md`: how the RAG databases are built, stage by stage, with real numbers.
- `docs/RUNBOOK.md`: operating, troubleshooting and resetting.
- `docs/VERSIONS.md`: verified versions and the facts the docs did not state.
- `data/kb/CANON.md`: the fictional world.
- `data/kb/PLANTED.md`: the deliberate gaps and stale facts.

All data is synthetic. There is no PHI anywhere.
