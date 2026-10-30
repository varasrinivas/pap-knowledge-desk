# Verified versions and facts (2026-10-30)

| Component | Version | Source |
|---|---|---|
| agno | 3.1.12 (2026-10-29) | https://pypi.org/project/agno/ |
| chromadb (client) | 1.5.9 | https://pypi.org/project/chromadb/ |
| chromadb/chroma (server image) | 1.5.9 (amd64 + arm64; persists to `/data`, port 8000, `/api/v2/heartbeat`) | https://hub.docker.com/r/chromadb/chroma/tags · https://docs.trychroma.com/guides/deploy/docker.md |
| fastembed | 0.9.1 | https://pypi.org/project/fastembed/ |
| BAAI/bge-small-en-v1.5 | 384 dimensions | https://huggingface.co/BAAI/bge-small-en-v1.5 |
| scikit-learn | 1.9.1 | https://pypi.org/project/scikit-learn/ |
| fastapi / uvicorn / httpx / pydantic | 0.162.0 / 0.54.0 / 0.28.1 / 2.14.2 | PyPI |

## Agno APIs used (checked in the installed 3.1.12 source)

- `agno.agent.Agent(model=, instructions=, tools=, output_schema=, db=)`;
- `agno.workflow.Workflow`, `Step`, `Parallel`, `Router(selector=, choices=)`, `StepInput`, `StepOutput`;
- function steps that take `run_context: RunContext` share `run_context.session_state`;
- `agno.tools.tool(requires_confirmation=True)`, `RunOutput.is_paused` / `active_requirements` / `requirement.confirm()`,
  and `Agent.continue_run(run_id=, requirements=)`, which needs a `db`;
- `agno.db.sqlite.SqliteDb(db_file=)`, which needs `sqlalchemy[asyncio]` and `aiosqlite`;
- `agno.models.base.Model`: six abstract methods (`invoke`, `ainvoke`, `invoke_stream`, `ainvoke_stream`,
  `_parse_provider_response`, `_parse_provider_response_delta`);
- `agno.os.AgentOS(base_app=, on_route_conflict=, telemetry=)`, which needs `python-multipart`, plus `.get_app()`.

## Facts the docs did not state (measured here)

- **Remote Chroma from Agno.** `agno.vectordb.chroma.ChromaDb` has no host or port argument. A remote server works by passing
  `settings=chromadb.config.Settings(chroma_api_impl="chromadb.api.fastapi.FastAPI", chroma_server_host=…, chroma_server_http_port=…)`,
  which is forwarded to `chromadb.Client`.
- **Agno's hybrid search.** `ChromaDb(search_type=SearchType.hybrid)` builds its keyword half from the query's **first word**
  only (`$contains: query_words[0]`).
- **Agno's FastEmbed embedder.** `FastEmbedEmbedder` embeds queries with `embed()`, not `query_embed()`.
- **fastembed and the bge instruction.** `TextEmbedding.query_embed()` returns the same vector as `embed()` for
  bge-small-en-v1.5, so the bge query instruction is not added for you.
- **Chroma collection names** must be 3–512 characters.
