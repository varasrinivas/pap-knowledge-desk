"""What the one-shot `ingest` container runs before the agent starts (docker compose: service_completed_successfully).

1 wait for ServiceNow, the portal and Chroma to be healthy
2 build every RAG collection (idempotent: unchanged chunks are skipped, so a restart costs seconds, not minutes)
3 profile the incidents, unless the profile is newer than the answer key
4 calibrate the per-source gates, unless gates.json exists
Exit 0 means the agent may start.
"""
from __future__ import annotations

import sys
import time

import httpx

from desk import config


def wait(url: str, name: str, timeout: int = 600):
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            if httpx.get(url, timeout=5, trust_env=False).status_code == 200:
                print(f"ingest: {name} healthy after {time.time() - t0:.0f}s", flush=True)
                return
        except httpx.HTTPError:
            pass
        time.sleep(3)
    print(f"ingest: {name} not healthy after {timeout}s", flush=True)
    sys.exit(1)


def run():
    t0 = time.time()
    wait(f"{config.SERVICENOW_API}/health", "servicenow")
    wait(f"{config.PORTAL_API}/health", "portal")
    wait(f"http://{config.CHROMA_HOST}:{config.CHROMA_PORT}/api/v2/heartbeat", "chroma")
    from desk.rag.build import build
    build(explain=True)
    key = config.RUNTIME_DIR / "answer_key.json"
    prof = config.RUNTIME_DIR / "profile.json"
    if not prof.exists() or prof.stat().st_mtime < key.stat().st_mtime:
        from desk.profile import run as profile
        profile(explain=True)
    else:
        print("ingest: profile is up to date, skipped", flush=True)
    if not (config.RUNTIME_DIR / "gates.json").exists():
        from desk.retrieval_eval import run as reval
        reval()
    from desk.knowledge_fix import reindex_drafts
    reindex_drafts()
    print(f"ingest: done in {time.time() - t0:.0f}s", flush=True)
