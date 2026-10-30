#!/usr/bin/env bash
# One click (macOS/Linux): make sure Docker is running, build and start the stack, wait for the desk, open the browser.
set -euo pipefail
cd "$(dirname "$0")"
say() { echo "[$(date +%H:%M:%S)] $*"; }

command -v docker >/dev/null || { say "Docker is not installed: https://www.docker.com/products/docker-desktop/"; exit 1; }
if ! docker info >/dev/null 2>&1; then
  if [[ "$(uname)" == "Darwin" ]]; then say "Starting Docker Desktop..."; open -a Docker; else say "Start the Docker daemon, then rerun."; exit 1; fi
  for _ in $(seq 1 60); do sleep 3; docker info >/dev/null 2>&1 && break; done
  docker info >/dev/null 2>&1 || { say "Docker did not start within 3 minutes."; exit 1; }
fi
say "Docker is running."
[[ -f .env ]] || { cp .env.example .env; say "Created .env (fixture model, no API key needed)."; }

say "Building and starting the stack (docker compose up -d --build)..."
docker compose up -d --build

say "Waiting for ingest (first run embeds 15,000 incidents; progress below)..."
last=""
for _ in $(seq 1 360); do
  curl -fs http://localhost:8180/health >/dev/null 2>&1 && break
  line=$(docker compose logs --no-log-prefix --tail 1 ingest 2>/dev/null | tail -1 || true)
  [[ -n "$line" && "$line" != "$last" ]] && { say "  ingest: ${line:0:150}"; last="$line"; }
  if docker compose ps -a --format '{{.Service}} {{.State}} {{.ExitCode}}' | grep -Eq '^ingest exited [1-9]'; then
    say "ingest failed - run: docker compose logs ingest"; exit 1
  fi
  sleep 5
done
say "The Knowledge Desk is up: http://localhost:8180"
(open http://localhost:8180 2>/dev/null || xdg-open http://localhost:8180 2>/dev/null || true)
