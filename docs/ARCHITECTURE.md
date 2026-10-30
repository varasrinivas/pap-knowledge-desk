# Architecture

## Containers

| Service | Image | Port (host → container) | State | Job |
|---|---|---|---|---|
| `chroma` | `chromadb/chroma:1.5.9` | 8183 → 8000 | volume `chroma-data:/data` | The vector database. Five collections, cosine space, HNSW index |
| `servicenow` | `knowledge-desk:local` | 8182 | volume `desk-runtime` (SQLite) | Table API mock. Seeds 15,000 historical incidents and a live 12-hour window on its first start, then a ticker adds one incident every 5 minutes |
| `portal` | `knowledge-desk:local` | 8181 | none (computed) | Prior Auth Portal mock: users, access and permissions, intake requests, the routing rule table, the routing explainer |
| `ingest` | `knowledge-desk:local` | none | writes `desk-runtime` and `chroma` | One-shot: build RAG → profile → calibrate gates → re-index approved drafts. Exits 0 |
| `agent` | `knowledge-desk:local` | 8180 | reads both volumes | The Agno workflow, the UI, and AgentOS endpoints (`/agents`, `/workflows`, `/sessions`) |

The four desk services share one image; compose picks each one's command. The agent starts only after `ingest` has completed
successfully (`depends_on: condition: service_completed_successfully`). `ingest` waits for ServiceNow and the portal to pass their
healthchecks, and for Chroma's `/api/v2/heartbeat`. The Chroma image is not documented to contain curl, so compose has no
healthcheck for it.

## The workflow (`desk/workflow.py`)

```
triage (agent, output_schema=Triage)
  └▶ Parallel "gather"   rag_kb_policy · rag_kb_workflow · rag_kb_ui · rag_incident_resolutions · rag_kb_drafts
                         tool_access · tool_routing · tool_live · tool_region_status · tool_request
       └▶ decide (code: the gate)  →  route + findings + ticket proposal + dedup check
            └▶ compose (agent)  →  cited answer
                 └▶ Router "act"   answer | raise (agent + @tool(requires_confirmation=True): the run pauses) | dedup (work note) | gap (log + answer from history)
```

- **Models plan and write; code decides.** Triage chooses which sources and tools to use. `decide` applies the rules:
  - a live outage beats a new ticket;
  - a locked account is raised, because unlocking is not self-service;
  - a lapsed delegation is explained, not raised;
  - a misrouted request is raised with its rule id;
  - a document above its gate resolves the question;
  - if the most similar past incidents were profiled as `knowledge_gap`, documents did not help those callers, so the question is
    treated as a gap unless an approved draft now covers it;
  - nothing anywhere means a ticket.
- **The `gather` step runs everything at once.** Every gather step reads the plan and returns "skipped" when it was not asked for,
  so the latency is set by the slowest planned step, not by the sum of them.
- **Confirmation is a real pause.** `raise` runs an Agno agent whose ticket tools are decorated with
  `@tool(requires_confirmation=True)`. The run pauses, the UI shows the arguments, and `/api/confirm` calls
  `agent.continue_run(...)` with the confirmed requirement.
- **Offline by default.** `FixtureModel` subclasses `agno.models.base.Model` and implements its six abstract methods. With
  `LLM_PROVIDER=anthropic`, the same agents run on `agno.models.anthropic.Claude`.

## Where Agno differs from the LangGraph desk in T3–T5

| Concern | LangGraph (course T3–T5) | Agno (this capstone) |
|---|---|---|
| Fan-out | `Send` to parallel nodes | `Parallel(step, step, …)` |
| Branching | conditional edges | `Router(selector=…, choices=[…])` |
| Human confirmation | `interrupt()` + `Command(resume=…)` | `@tool(requires_confirmation=True)` + `continue_run` |
| Shared state | typed `State` channels | `run_context.session_state` |
| Structured output | `with_structured_output` | `Agent(output_schema=…)` |
| Serving | your own FastAPI | `AgentOS(base_app=…).get_app()` |

## Data flow for one question

1. The UI posts `{user_id, message}` to `/api/chat`.
2. `redact()` masks PHI-like strings, and triage plans.
3. The `gather` step runs the planned searches and tools in parallel:
   - each RAG step runs a hybrid search (Chroma vectors + a BM25 side index, fused by reciprocal rank) and compares the top cosine with
     that source's gate;
   - each tool step calls the portal or ServiceNow over HTTP.
4. `decide` writes `route`, `findings` and an optional `ticket_proposal`.
5. `compose` writes the answer, citing sources such as `[UI-05]`, `[INC0030001]` and `[portal:routing]`.
6. `act` ends the turn. The JSON reply carries the route, answer, citations, tools called, the sources searched (with their top score
   and gate), and any pending confirmation.
