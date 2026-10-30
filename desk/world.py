"""The fictional world shared by the portal mock, the ServiceNow mock, the generator and the eval (see data/kb/CANON.md).

Everything here is synthetic. Timestamps are computed relative to "now" at call time so the fixture never goes stale.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

REGIONS = ["SOUTH_CENTRAL", "NORTHEAST", "WEST"]
SERVICE_TYPES = ["IMAGING", "ORTHO_SURGERY", "CARDIOLOGY", "ONCOLOGY", "HOME_HEALTH_DME", "BEHAVIORAL_HEALTH",
                 "PHYSICAL_THERAPY", "SLEEP_STUDY"]

ROLE_PERMISSIONS = {
    "PROVIDER_NURSE": ["intake.view", "intake.create", "intake.submit", "intake.attach", "intake.respond_pend",
                       "decision.view", "appeal.create", "p2p.request"],
    "UM_NURSE": ["review.queue.view", "review.claim", "review.pend", "review.recommend", "intake.view"],
    "REGIONAL_DIRECTOR": ["dashboard.region.view", "reports.export", "access.request.approve", "queue.reassign"],
    "PLATFORM_ADMIN": ["config.*"],
}
ROLE_PERMISSIONS["PROVIDER_OFFICE_MGR"] = ROLE_PERMISSIONS["PROVIDER_NURSE"] + ["office.users.manage", "delegation.manage",
                                                                                 "reports.export"]


def now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def users() -> dict[str, dict]:
    n = now()
    u = {
        "u-anita": dict(displayName="Anita Rao, RN", role="PROVIDER_NURSE", org="Lakeside Orthopedics", region="SOUTH_CENTRAL",
                        office="Dallas", mfaState="RESET_PENDING", locked=True, lockedSince=iso(n - timedelta(minutes=50)),
                        failedAttempts=5, delegation={"active": True, "expiresOn": iso(n + timedelta(days=120))}),
        "u-priya": dict(displayName="Priya Shah, RN", role="PROVIDER_NURSE", org="Lakeside Orthopedics", region="SOUTH_CENTRAL",
                        office="Dallas", mfaState="ACTIVE", locked=False, lockedSince=None, failedAttempts=0,
                        delegation={"active": False, "expiresOn": iso(n - timedelta(days=3))}),   # ← lapsed: Submit button gone
        "u-sam": dict(displayName="Sam Whitfield", role="PROVIDER_OFFICE_MGR", org="Lakeside Orthopedics", region="SOUTH_CENTRAL",
                      office="Dallas", mfaState="ACTIVE", locked=False, lockedSince=None, failedAttempts=0,
                      delegation={"active": True, "expiresOn": None}),
        "u-nora": dict(displayName="Nora Walsh, RN", role="PROVIDER_NURSE", org="Harbor Spine Clinic", region="NORTHEAST",
                       office="Boston", mfaState="ACTIVE", locked=False, lockedSince=None, failedAttempts=0,
                       delegation={"active": True, "expiresOn": iso(n + timedelta(days=40))}),
        "u-liam": dict(displayName="Liam Costa, RN", role="PROVIDER_NURSE", org="Sierra Rehab Partners", region="WEST",
                       office="Phoenix", mfaState="ACTIVE", locked=False, lockedSince=None, failedAttempts=0,
                       delegation={"active": True, "expiresOn": iso(n + timedelta(days=90))}),
        "u-maria": dict(displayName="Maria Lopez", role="UM_NURSE", org="Clinical Operations", region="SOUTH_CENTRAL",
                        office="Dallas", mfaState="ACTIVE", locked=False, lockedSince=None, failedAttempts=0, team="IMAGING"),
        "u-grace": dict(displayName="Grace Iyer", role="UM_NURSE", org="Clinical Operations", region="NORTHEAST",
                        office="Boston", mfaState="ACTIVE", locked=False, lockedSince=None, failedAttempts=0, team="ORTHO_SURGERY"),
        "u-owen": dict(displayName="Owen Brooks", role="UM_NURSE", org="Clinical Operations", region="WEST",
                       office="Phoenix", mfaState="ACTIVE", locked=False, lockedSince=None, failedAttempts=0, team="ORTHO_SURGERY"),
        "u-marcus": dict(displayName="Marcus Bell", role="REGIONAL_DIRECTOR", org="Clinical Operations", region="SOUTH_CENTRAL",
                         office="Dallas", mfaState="ACTIVE", locked=False, lockedSince=None, failedAttempts=0),
        "u-elena": dict(displayName="Elena Novak", role="REGIONAL_DIRECTOR", org="Clinical Operations", region="NORTHEAST",
                        office="Boston", mfaState="ACTIVE", locked=False, lockedSince=None, failedAttempts=0),
        "u-tom": dict(displayName="Tom Okafor", role="PLATFORM_ADMIN", org="Platform Engineering", region="ALL",
                      office="Remote", mfaState="ACTIVE", locked=False, lockedSince=None, failedAttempts=0),
    }
    for uid, rec in u.items():
        rec["userId"] = uid
    return u


def effective_permissions(user: dict) -> list[str]:
    """Role permissions, minus intake.submit when a provider user's office delegation has lapsed (CANON: Delegation)."""
    perms = list(ROLE_PERMISSIONS.get(user["role"], []))
    if user["role"] == "PROVIDER_NURSE" and not user.get("delegation", {}).get("active", True):
        perms.remove("intake.submit")
    return perms


# Servicing providers: the routing region comes from the servicing provider's practice location (CANON: Routing).
PROVIDERS = {
    "P-2001": dict(name="Lakeside Orthopedics", npi="1902837465", zip="75201", city="Dallas"),
    "P-2050": dict(name="North Texas Heart Associates", npi="1548203391", zip="75230", city="Dallas"),
    "P-2077": dict(name="Plano Surgical Center", npi="1673002918", zip=None, city=None),          # no location on file
    "P-3010": dict(name="Harbor Spine Clinic", npi="1215098834", zip="02115", city="Boston"),
    "P-4120": dict(name="Sierra Rehab Partners", npi="1386650021", zip="85004", city="Phoenix"),
    "P-4188": dict(name="Desert Oncology Group", npi="1720045583", zip="85006", city="Phoenix"),
}

ZIP_REGION = [("750", "753", "SOUTH_CENTRAL"), ("770", "772", "SOUTH_CENTRAL"), ("021", "022", "NORTHEAST"),
              ("061", "061", "NORTHEAST"), ("850", "853", "WEST"), ("802", "802", "WEST")]


def region_for_zip(z: str | None) -> str | None:
    if not z:
        return None
    for lo, hi, region in ZIP_REGION:
        if lo <= z[:3] <= hi:
            return region
    return None


def routing_rules() -> list[dict]:
    """One rule per region × service type, plus the two deliberately misconfigured rules (CANON: Routing)."""
    rules, n = [], 400
    for region in REGIONS:
        for st in SERVICE_TYPES:
            n += 1
            rules.append({"rule_id": f"RR-0{n}", "match": {"region": region, "service_type": st}, "queue_region": region,
                          "queue_service_type": st, "priority": 100, "added_in": "23.1", "note": "standard rule"})
    rules.append({"rule_id": "RR-0412", "match": {"zip_prefix": ["750", "751", "752", "753"], "service_type": "CARDIOLOGY"},
                  "queue_region": "NORTHEAST", "queue_service_type": "CARDIOLOGY", "priority": 10, "added_in": "24.2",
                  "note": "cardiology overflow pilot"})                                    # ← the bad rule behind R-01
    rules.append({"rule_id": "RR-0577", "match": {"region": "WEST", "service_type": "ONCOLOGY", "urgency": "URGENT"},
                  "queue_region": "WEST", "queue_service_type": "ORTHO_SURGERY", "priority": 10, "added_in": "24.1",
                  "note": "temporary staffing fallback"})                                  # ← the bad rule behind R-02
    return rules


def route(provider_id: str, service_type: str, urgency: str) -> dict:
    """Apply the rule table the way the portal does: most specific (lowest priority number) matching rule wins."""
    prov = PROVIDERS.get(provider_id, {})
    region = region_for_zip(prov.get("zip"))
    if region is None:
        return {"queue": "UNASSIGNED", "rule_id": None, "derived_region": None,
                "reason": "servicing provider has no practice location on file"}
    candidates = []
    for r in routing_rules():
        m = r["match"]
        if m.get("service_type") and m["service_type"] != service_type:
            continue
        if m.get("region") and m["region"] != region:
            continue
        if m.get("urgency") and m["urgency"] != urgency:
            continue
        if m.get("zip_prefix") and (prov.get("zip") or "")[:3] not in m["zip_prefix"]:
            continue
        candidates.append(r)
    rule = sorted(candidates, key=lambda r: r["priority"])[0]
    return {"queue": f"{rule['queue_region']}-{rule['queue_service_type']}-{urgency}", "rule_id": rule["rule_id"],
            "derived_region": region, "reason": rule["note"]}


def intake_requests() -> dict[str, dict]:
    n = now()
    reqs = {
        "IR-2026-00517": dict(submittedBy="u-anita", providerId="P-2001", serviceType="IMAGING", service="MRI lumbar spine",
                              urgency="STANDARD", status="Pended (Info Requested)", pendCode="PI-DOC-004",
                              submittedAt=iso(n - timedelta(days=3)), pendedAt=iso(n - timedelta(days=2))),
        "IR-2026-00588": dict(submittedBy="u-priya", providerId="P-2050", serviceType="CARDIOLOGY", service="Stress echocardiogram",
                              urgency="STANDARD", status="Pending Clinical Review", submittedAt=iso(n - timedelta(hours=40))),
        "IR-2026-00602": dict(submittedBy="u-anita", providerId="P-2050", serviceType="CARDIOLOGY", service="Cardiac catheterization",
                              urgency="URGENT", status="Pending Clinical Review", submittedAt=iso(n - timedelta(hours=30))),
        "IR-2026-00631": dict(submittedBy="u-anita", providerId="P-2077", serviceType="ORTHO_SURGERY", service="Knee arthroscopy",
                              urgency="STANDARD", status="Pending Clinical Review", submittedAt=iso(n - timedelta(days=2, hours=2))),
        "IR-2026-00540": dict(submittedBy="u-priya", providerId="P-2001", serviceType="ORTHO_SURGERY", service="Rotator cuff repair",
                              urgency="STANDARD", status="Approved", decisionCode="CR-AD-001", letterStatus="Pended",
                              submittedAt=iso(n - timedelta(days=6)), decidedAt=iso(n - timedelta(days=4))),
        "IR-2026-00660": dict(submittedBy="u-liam", providerId="P-4188", serviceType="ONCOLOGY", service="Radiation therapy plan",
                              urgency="URGENT", status="Pending Clinical Review", submittedAt=iso(n - timedelta(hours=10))),
    }
    for rid, r in reqs.items():
        r["requestId"] = rid
        r["region"] = users()[r["submittedBy"]]["region"]
        r["routing"] = route(r["providerId"], r["serviceType"], r["urgency"])
    return reqs


def expected_queue(req: dict) -> str | None:
    """The queue the CANON rule says a request should land in (region of the servicing provider, own service type)."""
    region = region_for_zip(PROVIDERS[req["providerId"]].get("zip"))
    return f"{region}-{req['serviceType']}-{req['urgency']}" if region else None
