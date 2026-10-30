"""Health of every service, and one call of every tool (the m41 lab's verify command)."""
from __future__ import annotations

import json
import time

import httpx

from desk import config, tools


def health() -> dict:
    out = {}
    for name, url in [("portal", f"{config.PORTAL_API}/health"), ("servicenow", f"{config.SERVICENOW_API}/health"),
                      ("chroma", f"http://{config.CHROMA_HOST}:{config.CHROMA_PORT}/api/v2/heartbeat")]:
        try:
            r = httpx.get(url, timeout=5)
            out[name] = r.json() if r.status_code == 200 else {"status": r.status_code}
        except httpx.HTTPError as e:
            out[name] = {"status": "down", "error": str(e)[:80]}
    try:
        from desk.rag.index import client
        out["collections"] = {c.name: c.count() for c in client().list_collections()}
    except Exception as e:
        out["collections"] = {"error": str(e)[:80]}
    return out


def tools_smoke():
    calls = [
        ("get_user_access", lambda: tools.get_user_access("u-anita")),
        ("check_permission", lambda: tools.check_permission("u-priya", "intake.submit")),
        ("get_intake_request", lambda: tools.get_intake_request("IR-2026-00602")),
        ("explain_routing", lambda: tools.explain_routing("IR-2026-00588")),
        ("get_routing_rules", lambda: {"rules": len(tools.get_routing_rules(region="WEST", service_type="ONCOLOGY")["rules"])}),
        ("sn_live_incidents", lambda: tools.sn_live_incidents("fax")),
        ("sn_region_status", lambda: tools.sn_region_status("SOUTH_CENTRAL")),
        ("sn_find_open_duplicate", lambda: tools.sn_find_open_duplicate("u-priya", "other", "SOUTH_CENTRAL", "routing")),
    ]
    ok = 0
    for name, fn in calls:
        t0 = time.time()
        r = fn()
        ms = int((time.time() - t0) * 1000)
        good = "error" not in r
        ok += good
        print(f"{'ok ' if good else 'ERR'} {name:24s} {ms:5d} ms  {json.dumps(r, default=str)[:150]}")
    print(f"\ntools_ok: {ok}/{len(calls)}")
