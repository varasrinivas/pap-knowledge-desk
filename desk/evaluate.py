"""Run the labelled scenarios through the Agno workflow and score each one.

    python -m desk eval            # all scenarios        python -m desk eval --only R-01

Per scenario: route (one of the acceptable routes), sources (required RAG collections searched), tools (required tool calls
made), citations (at least one expected id cited), redaction (PHI kind masked). A scenario passes when every check passes.
Raised tickets in scenarios marked confirm are confirmed, so the dedup scenario that follows has something to find.
"""
from __future__ import annotations

import json
import time

import httpx

from desk import config
from desk.stats import bootstrap_ci
from desk.workflow import ask, confirm

SCEN = json.loads((config.EVAL_DIR / "scenarios.json").read_text(encoding="utf-8"))["scenarios"]


def clear_desk_tickets():
    httpx.post(f"{config.SERVICENOW_API}/admin/clear-desk", auth=(config.SERVICENOW_USER, config.SERVICENOW_PASS), timeout=30, trust_env=False)
    (config.RUNTIME_DIR / "gaps.jsonl").unlink(missing_ok=True)


def check(s: dict, r: dict) -> dict:
    tools_called = " ".join(r.get("tools_called") or [])
    searched = set((r.get("sources_searched") or {}).keys())
    c = {"route": r["route"] in s["route"],
         "sources": all(x in searched for x in s["sources"]),
         "tools": all(t in tools_called for t in s["tools"]),
         "cite": (not s["cite"]) or any(x in (r.get("citations") or []) for x in s["cite"]),
         "redaction": (not s.get("redacted")) or (s["redacted"] in (r.get("redacted") or []) and "NW-1234567" not in json.dumps(r))}
    c["pass"] = all(c.values())
    return c


def drafts_present() -> bool:
    try:
        from desk.rag.index import get_collection
        return get_collection("kb_drafts").count() > 0
    except Exception:
        return False


def run(only: str | None = None) -> dict:
    clear_desk_tickets()
    rows, t0 = [], time.time()
    fixed = drafts_present()
    if fixed:
        print("kb_drafts has approved articles: gap scenarios use their after_fix expectations\n")
    print(f"{'id':5s} {'route':12s} {'want':22s} {'src':>3s} {'tool':>4s} {'cite':>4s} {'ms':>6s}  result")
    for s in SCEN:
        if only and s["id"] != only:
            continue
        if fixed and s.get("after_fix"):
            s = {**s, **s["after_fix"]}
        r = ask(s["user"], s["message"], thread_id=f"eval-{s['id']}")
        if s.get("confirm") and r.get("pending"):
            r["confirmed"] = confirm(r["pending"])
        c = check(s, r)
        rows.append({"id": s["id"], **c, "got": r["route"], "latency_ms": r["latency_ms"], "answer": r["answer"],
                     "citations": r.get("citations"), "tools_called": r.get("tools_called"), "searched": list((r.get("sources_searched") or {}).keys())})
        mark = lambda b: "ok" if b else "--"
        print(f"{s['id']:5s} {r['route']:12s} {'/'.join(s['route']):22s} {mark(c['sources']):>3s} {mark(c['tools']):>4s} "
              f"{mark(c['cite']):>4s} {r['latency_ms']:6d}  {'PASS' if c['pass'] else 'FAIL'}")
    n = len(rows)
    passed = [1.0 if x["pass"] else 0.0 for x in rows]
    lo, hi = bootstrap_ci(passed) if n > 1 else (0, 0)
    route_acc = sum(x["route"] for x in rows) / max(1, n)
    lat = sorted(x["latency_ms"] for x in rows)
    out = {"n": n, "pass_rate": sum(passed) / max(1, n), "ci": [lo, hi], "route_accuracy": route_acc,
           "p50_ms": lat[len(lat) // 2] if lat else 0, "rows": rows}
    (config.RUNTIME_DIR / "eval.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    fails = [x for x in rows if not x["pass"]]
    for f in fails:
        print(f"  FAIL {f['id']}: got {f['got']} · " + ", ".join(k for k in ("route", "sources", "tools", "cite", "redaction") if not f[k]) + " failed")
    print(f"\ndesk_eval: {sum(passed):.0f}/{n} pass ({out['pass_rate']:.0%}, 95% CI {lo:.0%}-{hi:.0%}) · route accuracy {route_acc:.0%} · "
          f"p50 latency {out['p50_ms']} ms · model {'live' if config.live_llm() else 'fixture'} · {time.time() - t0:.0f}s")
    return out
