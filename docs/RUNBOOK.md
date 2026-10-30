# Runbook

## Start, stop, reset

| Action | Windows | macOS / Linux | Effect |
|---|---|---|---|
| Start | `start.cmd` | `./start.sh` | builds if needed, starts all services, waits for ingest, opens the UI |
| Stop | `stop.cmd` | `./stop.sh` | stops the containers; volumes keep the data |
| Reset | `reset.cmd` | `./reset.sh` | `docker compose down -v`: deletes collections, ServiceNow data, profile and drafts |

## Where things are

| Thing | Where |
|---|---|
| Desk UI | http://localhost:8180 |
| AgentOS endpoints | http://localhost:8180/agents, `/workflows`, `/sessions`, `/docs` |
| ServiceNow mock | http://localhost:8182/health (Basic auth `svc_desk` / `svc_desk` for the Table API) |
| Portal mock | http://localhost:8181/health |
| Chroma | http://localhost:8183/api/v2/heartbeat |
| Reports | `docker compose exec agent cat /runtime/INGEST-REPORT.md` (also `PROFILE-REPORT.md`, `eval.json`) |

## Troubleshooting

| Symptom | Check | Fix |
|---|---|---|
| The start script waits a long time on first run | `docker compose logs -f ingest` | Normal: embedding 15,000 incidents takes several minutes on a CPU |
| `ingest exited 1` | `docker compose logs ingest` | Usually a service was not healthy in time; run `docker compose up -d` again (ingest is idempotent) |
| The agent never becomes healthy | `docker compose ps -a` | The agent waits for ingest to exit 0 |
| The UI says "profile not built yet" | `/runtime/profile.json` is missing | `docker compose exec agent python -m desk profile` |
| A port is already in use | `netstat -ano \| findstr 8180` | Stop whatever holds the port (the course simulator uses 8080–8082, so it does not clash) |
| You changed `data/kb/*.md` | | `docker compose build && docker compose up -d`; ingest re-embeds only changed chunks |
| You want the live model | `.env` | Set `LLM_PROVIDER=anthropic`, `ANTHROPIC_API_KEY` and `LLM_MODEL`, then `docker compose up -d agent` |
