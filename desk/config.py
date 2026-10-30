"""All settings come from environment variables with offline defaults. Inside Docker, compose sets the service URLs."""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.getenv("DESK_DATA_DIR", ROOT / "data"))
KB_DIR = DATA_DIR / "kb"
EVAL_DIR = DATA_DIR / "eval"
RUNTIME_DIR = Path(os.getenv("DESK_RUNTIME_DIR", ROOT / ".runtime"))
RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
MODEL_CACHE = Path(os.getenv("FASTEMBED_CACHE_PATH", RUNTIME_DIR / "models"))

PORTAL_API = os.getenv("PORTAL_API", "http://127.0.0.1:8181")
SERVICENOW_API = os.getenv("SERVICENOW_API", "http://127.0.0.1:8182")
SERVICENOW_USER = os.getenv("SERVICENOW_USER", "svc_desk")
SERVICENOW_PASS = os.getenv("SERVICENOW_PASS", "svc_desk")
CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8183"))

SEED = int(os.getenv("DESK_SEED", "2026"))
HISTORY_SIZE = int(os.getenv("DESK_HISTORY_SIZE", "15000"))
HISTORY_DAYS = int(os.getenv("DESK_HISTORY_DAYS", "180"))
LIVE_TICKER_SECONDS = int(os.getenv("DESK_LIVE_TICKER_SECONDS", "300"))   # one new routine incident every 5 minutes

EMBED_MODEL = os.getenv("DESK_EMBED_MODEL", "BAAI/bge-small-en-v1.5")
EMBED_DIM = 384
EMBED_BATCH = int(os.getenv("DESK_EMBED_BATCH", "16"))      # measured: small batches pad less, so they are faster on CPU
COLLECTION_SUFFIX = os.getenv("DESK_COLLECTION_SUFFIX", "v1")   # a new embedding model means a new suffix, not an overwrite

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "fixture")             # fixture | anthropic
LLM_MODEL = os.getenv("LLM_MODEL", "")                          # verify the id at build time; never hard-coded here
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

DEDUP_WINDOW_HOURS = 4
LIVE_WINDOW_HOURS = 12


def live_llm() -> bool:
    """A live model only when the provider is chosen AND a key AND a model id are set; otherwise the fixture."""
    return LLM_PROVIDER == "anthropic" and bool(ANTHROPIC_API_KEY) and bool(LLM_MODEL)
