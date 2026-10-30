"""Stage 1, LOAD: read every source into plain records, keeping where each one came from.

Three source types, three loaders:
  markdown documents (policy, workflow, ui, drafts) -> front matter + body, one record per file
  ServiceNow incidents -> paged through the Table API (sysparm_limit / sysparm_offset), resolved and closed only
"""
from __future__ import annotations

import time
from pathlib import Path

import httpx

from desk import config

DOC_SOURCES = {"kb_policy": "policy", "kb_workflow": "workflow", "kb_ui": "ui", "kb_drafts": "drafts"}
LIST_KEYS = {"audience", "service_types", "related", "queues", "stages", "screens", "roles"}


def parse_front_matter(text: str) -> tuple[dict, str]:
    """A deliberately small YAML subset: 'key: value' lines between --- fences; known list keys split on commas."""
    if not text.startswith("---"):
        return {}, text
    _, fm, body = text.split("---", 2)
    meta = {}
    for line in fm.strip().splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        v = v.strip().strip('"').strip("'")
        meta[k.strip()] = [x.strip() for x in v.split(",") if x.strip()] if k.strip() in LIST_KEYS else v
    return meta, body.strip()


def load_documents(collection: str) -> list[dict]:
    folder = (config.RUNTIME_DIR / "drafts" / "approved") if collection == "kb_drafts" else config.KB_DIR / DOC_SOURCES[collection]
    out = []
    for path in sorted(folder.glob("*.md")) if folder.exists() else []:
        meta, body = parse_front_matter(path.read_text(encoding="utf-8"))
        if not meta.get("id"):
            continue
        out.append({"source_id": meta["id"], "path": path.name if collection == "kb_drafts" else str(Path(path).relative_to(config.ROOT)).replace("\\", "/"), "meta": meta, "body": body})
    return out


def sn_client() -> httpx.Client:
    return httpx.Client(base_url=config.SERVICENOW_API, auth=(config.SERVICENOW_USER, config.SERVICENOW_PASS), timeout=60, trust_env=False)


def load_incidents(page_size: int = 1000) -> tuple[list[dict], dict]:
    """Page through the Table API exactly as you would against a real instance: a filter, a field list, limit + offset."""
    fields = ("number,caller_id,short_description,description,category,subcategory,assignment_group,priority,state,u_region,"
              "u_portal_user_role,sys_created_on,resolved_at,close_code,close_notes,work_notes,parent_incident")
    query = "stateINResolved,Closed^ORDERBYnumber"                      # history only: the live window is a tool, not RAG
    out, pages, t0 = [], 0, time.time()
    with sn_client() as c:
        while True:
            r = c.get("/api/now/table/incident", params={"sysparm_query": query, "sysparm_fields": fields,
                                                         "sysparm_limit": page_size, "sysparm_offset": len(out)})
            r.raise_for_status()
            rows = r.json()["result"]
            pages += 1
            total = int(r.headers.get("X-Total-Count", "0"))
            out += rows
            if not rows or len(out) >= total:
                break
    return out, {"pages": pages, "page_size": page_size, "total_reported": total, "seconds": round(time.time() - t0, 1)}
