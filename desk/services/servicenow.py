"""ServiceNow Table API mock, backed by SQLite so 15,000 incidents survive restarts (docker volume `sn-data`).

On first start it runs the generator, stores the history and the live 12-hour window, and writes the answer key to the
runtime volume (DESK_RUNTIME_DIR/answer_key.json): the key is the course's ground truth, not something ServiceNow holds.
A background ticker adds one routine incident every DESK_LIVE_TICKER_SECONDS so "the last 12 hours" keeps moving.

Supported: GET /api/now/table/{table}?sysparm_query=&sysparm_fields=&sysparm_limit=&sysparm_offset=  (encoded query operators
=, !=, LIKE, STARTSWITH, >=, <=, IN, ISEMPTY, ISNOTEMPTY, ^ (AND), ^OR, ORDERBY / ORDERBYDESC), GET .../{sys_id|number},
POST incident / sc_request, PATCH (appends work_notes). Basic auth svc_desk / svc_desk. Responses carry X-Total-Count.
"""
from __future__ import annotations

import json
import random
import secrets
import sqlite3
import threading
import time
from datetime import timedelta

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from desk import config
from desk.generate import TOPICS, _fill, generate
from desk.world import REGIONS, iso, now

DB_PATH = config.RUNTIME_DIR / "servicenow.sqlite"
COLS = ["sys_id", "number", "short_description", "description", "category", "subcategory", "assignment_group", "impact",
        "urgency", "priority", "state", "active", "caller_id", "contact_type", "u_portal_user_role", "u_region", "u_office",
        "sys_created_on", "sys_updated_on", "resolved_at", "close_code", "close_notes", "parent_incident", "major_incident",
        "u_request_id", "work_notes"]
REQ_COLS = ["sys_id", "number", "short_description", "description", "requested_for", "item", "approver", "state",
            "sys_created_on", "sys_updated_on", "work_notes"]
TABLES = {"incident": COLS, "sc_request": REQ_COLS}
LOCK = threading.Lock()
security = HTTPBasic()
app = FastAPI(title="ServiceNow mock (Knowledge Desk)")


def auth(c: HTTPBasicCredentials = Depends(security)):
    if not (secrets.compare_digest(c.username, config.SERVICENOW_USER) and secrets.compare_digest(c.password, config.SERVICENOW_PASS)):
        raise HTTPException(401, "bad credentials")


def db() -> sqlite3.Connection:
    con = sqlite3.connect(DB_PATH, check_same_thread=False)
    con.row_factory = sqlite3.Row
    return con


def _row(rec: dict, cols: list[str]) -> list:
    out = []
    for c in cols:
        v = rec.get(c, "")
        if c == "sys_id" and not v:
            v = secrets.token_hex(16)
        if c == "work_notes":
            v = json.dumps(v or [])
        out.append("" if v is None else str(v))
    return out


def insert(con, table: str, recs: list[dict]):
    cols = TABLES[table]
    con.executemany(f"INSERT INTO {table} ({','.join(cols)}) VALUES ({','.join('?' * len(cols))})", [_row(r, cols) for r in recs])


def init_db(force: bool = False) -> dict:
    con = db()
    with LOCK:
        for t, cols in TABLES.items():
            con.execute(f"CREATE TABLE IF NOT EXISTS {t} ({', '.join(c + ' TEXT' for c in cols)})")
        con.execute("CREATE INDEX IF NOT EXISTS ix_inc_created ON incident(sys_created_on)")
        con.execute("CREATE UNIQUE INDEX IF NOT EXISTS ix_inc_number ON incident(number)")
        have = con.execute("SELECT COUNT(*) FROM incident").fetchone()[0]
        if have and not force:
            con.commit()
            return {"seeded": False, "incidents": have}
        con.execute("DELETE FROM incident")
        con.execute("DELETE FROM sc_request")
        history, key, live = generate()
        insert(con, "incident", history)
        insert(con, "incident", live)
        con.commit()
    (config.RUNTIME_DIR / "answer_key.json").write_text(json.dumps(key), encoding="utf-8")
    return {"seeded": True, "incidents": len(history) + len(live)}


def next_number(con, table: str) -> str:
    prefix = "INC" if table == "incident" else "REQ"
    top = con.execute(f"SELECT MAX(CAST(SUBSTR(number, 4) AS INTEGER)) FROM {table}").fetchone()[0] or (40000 if table == "incident" else 10000)
    return f"{prefix}{max(top + 1, 40001 if table == 'incident' else 10001):07d}"


# ---------------- encoded query → SQL ----------------
OPS = ["ISNOTEMPTY", "ISEMPTY", "STARTSWITH", "NOT IN", "IN", "LIKE", "!=", ">=", "<=", "="]


def _clause(raw: str, cols: list[str]) -> tuple[str, list]:
    for op in OPS:
        if op in ("ISEMPTY", "ISNOTEMPTY"):
            if raw.endswith(op):
                f = raw[: -len(op)]
                if f not in cols:
                    raise HTTPException(400, f"unknown field {f}")
                return (f"COALESCE({f},'') {'=' if op == 'ISEMPTY' else '!='} ''", [])
            continue
        if op in raw:
            f, v = raw.split(op, 1)
            if f not in cols:
                raise HTTPException(400, f"unknown field {f}")
            if op == "LIKE":
                return (f"LOWER({f}) LIKE ?", [f"%{v.lower()}%"])
            if op == "STARTSWITH":
                return (f"{f} LIKE ?", [f"{v}%"])
            if op in ("IN", "NOT IN"):
                vals = v.split(",")
                return (f"{f} {'NOT ' if op == 'NOT IN' else ''}IN ({','.join('?' * len(vals))})", vals)
            return (f"{f} {op} ?", [v])
    raise HTTPException(400, f"cannot parse clause {raw}")


def to_sql(q: str | None, cols: list[str]) -> tuple[str, list, str]:
    """'activeISTRUE^short_descriptionLIKEfax^ORdescriptionLIKEfax^ORDERBYDESCsys_created_on' → WHERE, params, ORDER BY."""
    if not q:
        return "1=1", [], ""
    groups: list[list[tuple[str, list]]] = []
    order = ""
    for raw in q.split("^"):
        if not raw:
            continue
        if raw.startswith("ORDERBYDESC"):
            order = f" ORDER BY {raw[11:]} DESC" if raw[11:] in cols else ""
        elif raw.startswith("ORDERBY"):
            order = f" ORDER BY {raw[7:]}" if raw[7:] in cols else ""
        elif raw.startswith("OR") and groups:
            groups[-1].append(_clause(raw[2:], cols))                    # ^OR binds to the previous clause
        else:
            groups.append([_clause(raw, cols)])
    where, params = [], []
    for g in groups:
        where.append("(" + " OR ".join(s for s, _ in g) + ")")
        for _, p in g:
            params += p
    return " AND ".join(where) or "1=1", params, order


def _public(r: sqlite3.Row) -> dict:
    d = dict(r)
    notes = json.loads(d.get("work_notes") or "[]")
    d["work_notes"] = "\n".join(f"{n['at']} {n['by']}: {n['text']}" for n in notes)
    d["work_notes_count"] = len(notes)
    return d


@app.on_event("startup")
def _startup():
    info = init_db()
    print(f"servicenow mock: {info}", flush=True)
    threading.Thread(target=_ticker, daemon=True).start()


def _ticker():
    rnd = random.Random()
    topics = [t for t in TOPICS if t.bucket not in ("outage_performance", "duplicate_noise")]
    while True:
        time.sleep(config.LIVE_TICKER_SECONDS)
        t = rnd.choice(topics)
        region = rnd.choice(REGIONS)
        con = db()
        with LOCK:
            insert(con, "incident", [{"number": next_number(con, "incident"), "short_description": _fill(rnd.choice(t.asks), rnd, region, {})[:160],
                                      "category": t.category, "subcategory": t.subcategory, "priority": "P3", "impact": 3, "urgency": 3,
                                      "state": "New", "active": "true", "u_region": region, "assignment_group": t.group,
                                      "caller_id": f"usr{rnd.randrange(1, 900):04d}", "contact_type": "self-service",
                                      "u_portal_user_role": "PROVIDER_NURSE", "sys_created_on": iso(now()), "sys_updated_on": iso(now())}])
            con.commit()


@app.get("/health")
def health():
    con = db()
    return {"status": "ok", "service": "servicenow", "incidents": con.execute("SELECT COUNT(*) FROM incident").fetchone()[0],
            "open": con.execute("SELECT COUNT(*) FROM incident WHERE active='true'").fetchone()[0]}


@app.post("/admin/reset", dependencies=[Depends(auth)])
def reset():
    return init_db(force=True)


@app.post("/admin/clear-desk", dependencies=[Depends(auth)])
def clear_desk():
    """Remove what the desk created (incidents opened via the chatbot after seeding, all access requests); keep the history."""
    con = db()
    with LOCK:
        n = con.execute("DELETE FROM incident WHERE contact_type='chatbot' AND CAST(SUBSTR(number, 4) AS INTEGER) > 40000").rowcount
        m = con.execute("DELETE FROM sc_request").rowcount
        con.commit()
    return {"incidents_removed": n, "requests_removed": m}


@app.get("/api/now/table/{table}", dependencies=[Depends(auth)])
def list_table(table: str, response: Response, sysparm_query: str | None = None, sysparm_fields: str | None = None,
               sysparm_limit: int = 100, sysparm_offset: int = 0):
    if table not in TABLES:
        raise HTTPException(404, f"table {table} not supported")
    cols = TABLES[table]
    where, params, order = to_sql(sysparm_query, cols)
    fields = [f for f in (sysparm_fields or "").split(",") if f in cols] or cols
    con = db()
    total = con.execute(f"SELECT COUNT(*) FROM {table} WHERE {where}", params).fetchone()[0]
    rows = con.execute(f"SELECT {','.join(fields)} FROM {table} WHERE {where}{order or ' ORDER BY rowid'} LIMIT ? OFFSET ?",
                       params + [min(sysparm_limit, 10000), sysparm_offset]).fetchall()
    response.headers["X-Total-Count"] = str(total)
    return {"result": [_public(r) if "work_notes" in fields else dict(r) for r in rows]}


@app.get("/api/now/table/{table}/{ident}", dependencies=[Depends(auth)])
def get_one(table: str, ident: str):
    if table not in TABLES:
        raise HTTPException(404)
    r = db().execute(f"SELECT * FROM {table} WHERE sys_id=? OR number=?", (ident, ident)).fetchone()
    if not r:
        raise HTTPException(404, "record not found")
    return {"result": _public(r)}


PRIORITY = {(1, 1): "P1", (1, 2): "P2", (2, 1): "P2", (2, 2): "P3", (1, 3): "P3", (3, 1): "P3"}


@app.post("/api/now/table/{table}", dependencies=[Depends(auth)])
async def create(table: str, request: Request):
    if table not in TABLES:
        raise HTTPException(404)
    body = await request.json()
    con = db()
    with LOCK:
        rec = {k: v for k, v in body.items() if k in TABLES[table]}
        rec["sys_id"] = secrets.token_hex(16)
        rec["number"] = next_number(con, table)
        rec["sys_created_on"] = rec["sys_updated_on"] = iso(now())
        if table == "incident":
            imp, urg = int(rec.get("impact", 3)), int(rec.get("urgency", 3))
            rec.update(state="New", active="true", priority=PRIORITY.get((imp, urg), "P4"))     # priority computed here, not by the caller
        else:
            rec.update(state="Pending Approval")
        if isinstance(body.get("work_notes"), str) and body["work_notes"]:
            rec["work_notes"] = [{"at": iso(now()), "by": "knowledge-desk", "text": body["work_notes"]}]
        insert(con, table, [rec])
        con.commit()
    return {"result": rec}


@app.patch("/api/now/table/{table}/{sys_id}", dependencies=[Depends(auth)])
async def patch(table: str, sys_id: str, request: Request):
    body = await request.json()
    con = db()
    with LOCK:
        r = con.execute(f"SELECT * FROM {table} WHERE sys_id=? OR number=?", (sys_id, sys_id)).fetchone()
        if not r:
            raise HTTPException(404)
        notes = json.loads(r["work_notes"] or "[]")
        if body.get("work_notes"):
            notes.append({"at": iso(now()), "by": "knowledge-desk", "text": body["work_notes"]})
        con.execute(f"UPDATE {table} SET work_notes=?, sys_updated_on=? WHERE sys_id=?", (json.dumps(notes), iso(now()), r["sys_id"]))
        con.commit()
    return {"result": _public(db().execute(f"SELECT * FROM {table} WHERE sys_id=?", (r["sys_id"],)).fetchone())}
