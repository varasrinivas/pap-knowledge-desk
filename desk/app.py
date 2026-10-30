"""The desk's web service: our routes + UI on a FastAPI app, wrapped by Agno's AgentOS (which adds its /agents, /workflows,
/sessions endpoints for the same agents and workflow).

    uvicorn desk.app:app --port 8180
"""
from __future__ import annotations

import json
import os

os.environ.setdefault("AGNO_TELEMETRY", "false")

from fastapi import Body, FastAPI, HTTPException                                  # noqa: E402
from fastapi.responses import FileResponse, PlainTextResponse                    # noqa: E402

from desk import config, tools                                                   # noqa: E402
from desk.world import users                                                     # noqa: E402

base = FastAPI(title="Knowledge Desk")
UI = config.ROOT / "desk" / "ui" / "index.html"


@base.get("/")
def home():
    return FileResponse(UI)


@base.get("/health")
def health():
    from desk.smoke import health as h
    out = h()
    out["desk"] = {"status": "ok", "model": f"claude ({config.LLM_MODEL})" if config.live_llm() else "fixture",
                   "profile": (config.RUNTIME_DIR / "profile.json").exists(), "gates": (config.RUNTIME_DIR / "gates.json").exists()}
    return out


@base.get("/api/personas")
def personas():
    return [{"userId": k, "displayName": u["displayName"], "role": u["role"], "region": u["region"], "org": u["org"]} for k, u in users().items()]


@base.post("/api/chat")
def chat(body: dict = Body(...)):
    from desk.workflow import ask
    if not body.get("message"):
        raise HTTPException(400, "message required")
    return ask(body.get("user_id", "u-priya"), body["message"], body.get("thread_id", "ui"))


@base.post("/api/confirm")
def confirm_ticket(body: dict = Body(...)):
    from desk.workflow import confirm
    return confirm(body["pending"], approve=body.get("approve", True))


@base.get("/api/profile")
def profile():
    p = config.RUNTIME_DIR / "profile.json"
    if not p.exists():
        raise HTTPException(404, "profile not built yet (the ingest container builds it)")
    return json.loads(p.read_text())


@base.get("/api/live")
def live(region: str = "SOUTH_CENTRAL"):
    st = tools.sn_region_status(region)
    recent = tools._get(tools._sn, "/api/now/table/incident", sysparm_query="active=true^ORDERBYDESCsys_created_on",
                        sysparm_fields="number,short_description,priority,state,u_region,sys_created_on,parent_incident,major_incident", sysparm_limit=25)
    return {"status": st, "recent": recent.get("result", [])}


@base.get("/api/rag/collections")
def collections():
    from desk.rag.index import client
    return [{"name": c.name, "count": c.count(), "metadata": c.metadata} for c in client().list_collections()]


@base.get("/api/rag/search")
def rag_search(source: str, q: str):
    """Vector, keyword and fused ranks side by side, for the RAG inspector."""
    from desk.rag.search import gates, hybrid, keyword, vector
    vec = vector(source, q, k=8)
    kw = keyword(source, q, k=8)
    hy = hybrid(source, q, k=8)
    return {"source": source, "gate": gates().get(source), "vector": [{"id": h["id"], "score": h["score"], "meta": h["meta"], "text": h["text"][:400]} for h in vec],
            "keyword": [{"id": i, "score": round(s, 3)} for i, s in kw],
            "hybrid": [{"id": h["id"], "rrf": h["rrf"], "score": h["score"], "vector_rank": h["vector_rank"], "keyword_rank": h["keyword_rank"]} for h in hy]}


@base.get("/api/drafts")
def drafts():
    from desk.knowledge_fix import list_drafts
    return list_drafts()


@base.post("/api/drafts/generate")
def drafts_generate():
    from desk.knowledge_fix import draft_from_profile
    return draft_from_profile()


@base.post("/api/drafts/reset")
def drafts_reset():
    """Back to 'no drafts' (pending and approved removed, kb_drafts emptied): for demos and screenshots."""
    from desk.knowledge_fix import reset_drafts
    reset_drafts()
    return {"ok": True}


@base.post("/api/admin/clear-desk")
def clear_desk():
    """Remove tickets and access requests the desk created (the 15,000-incident history stays)."""
    from desk.evaluate import clear_desk_tickets
    clear_desk_tickets()
    return {"ok": True}


@base.post("/api/drafts/{file}/approve")
def drafts_approve(file: str):
    from desk.knowledge_fix import approve
    return approve(file)


@base.get("/api/reports/{name}", response_class=PlainTextResponse)
def report(name: str):
    allowed = {"ingest": "INGEST-REPORT.md", "profile": "PROFILE-REPORT.md", "eval": "eval.json"}
    p = config.RUNTIME_DIR / allowed.get(name, "")
    if name not in allowed or not p.exists():
        raise HTTPException(404)
    return p.read_text(encoding="utf-8")


def build_app() -> FastAPI:
    """Wrap our app with AgentOS so the Agno agents and the workflow are also served on Agno's standard endpoints."""
    try:
        from agno.os import AgentOS

        from desk.agents import agent, db
        from desk.workflow import desk
        os_ = AgentOS(id="knowledge-desk", name="Knowledge Desk", db=db(), agents=[agent(k) for k in ("triage", "compose", "raise", "article")],
                      workflows=[desk()], base_app=base, on_route_conflict="preserve_base_app", telemetry=False)
        return os_.get_app()
    except Exception as e:                                       # the desk still works without the AgentOS layer
        print(f"AgentOS not mounted: {e}")
        return base


app = build_app()
