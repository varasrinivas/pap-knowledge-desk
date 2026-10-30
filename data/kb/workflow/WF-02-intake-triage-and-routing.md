---
id: WF-02
title: Intake triage and routing
doc_type: workflow
owner: Utilization Management Operations
audience: PROVIDER_NURSE, PROVIDER_OFFICE_MGR, UM_NURSE, REGIONAL_DIRECTOR
queues: {REGION}-{SERVICE_TYPE}-{URGENCY}, UNASSIGNED, Service Desk
stages: Submitted, Pending Clinical Review
version: 2.4
effective_date: 2026-07-01
last_reviewed: 2026-09-15
related: POL-08, POL-12, UI-07, UI-15
---
# Intake triage and routing

## Summary
This workflow explains how a submitted intake request reaches a review queue. It starts at Submitted and ends when the request sits in a queue named `{REGION}-{SERVICE_TYPE}-{URGENCY}` with status Pending Clinical Review. The region always comes from the servicing provider's practice location. Requests without a location wait in `UNASSIGNED` for the regional director's 24-hour sweep.

### Step 1: Confirm the request is routable
- **Owner:** The portal (automatic)
- **Queue / system:** Rules engine
- **Time limit:** Seconds after **Submit**; the decision clock has already started.
- **What happens:** Requests the rules engine approves at a confidence of 0.85 or more (code CR-AD-001) skip routing. Every other request moves on to triage.
- **Exit:** The request needs human review.

### Step 2: Determine the region
- **Owner:** The portal (routing rules)
- **Queue / system:** Routing rule table
- **Time limit:** Immediate.
- **What happens:** The region is taken from the **servicing provider's practice location**, as entered on wizard step **3 Providers**. It is not taken from the submitting office's address, and not from the member's address. The three regions are SOUTH_CENTRAL (Dallas, Houston), NORTHEAST (Boston, Hartford) and WEST (Phoenix, Denver).
- **Exit:** A region is found, or no location is on file.

### Step 3: Determine service type and urgency
- **Owner:** The portal (routing rules)
- **Queue / system:** Routing rule table
- **Time limit:** Immediate.
- **What happens:** The service type is the one chosen on step **2 Service**, for example IMAGING or CARDIOLOGY. Urgency is URGENT only when the **Urgent attestation** checkbox was ticked on step 6; otherwise it is STANDARD (see WF-05).
- **Exit:** All three parts of the queue name are known.

### Step 4: Place the request in its queue
- **Owner:** The portal (automatic)
- **Queue / system:** `{REGION}-{SERVICE_TYPE}-{URGENCY}`, for example `SOUTH_CENTRAL-CARDIOLOGY-URGENT`
- **Time limit:** Immediate.
- **What happens:** The request's status becomes Pending Clinical Review and it appears in the queue for UM nurses assigned to that region. The routing decision is recorded on the request and can be inspected through the routing explanation.
- **Exit:** A UM nurse can claim it (WF-03).

### Step 5: Sweep UNASSIGNED
- **Owner:** REGIONAL_DIRECTOR
- **Queue / system:** `UNASSIGNED`, Regional Dashboard tile **Unassigned**
- **Time limit:** Swept every 24 hours.
- **What happens:** Requests whose servicing provider has no practice location on file fall to `UNASSIGNED`. The regional director reviews the tile, identifies the correct region and uses **Reassign queue** to place each request. The decision clock keeps running while a request waits.
- **Exit:** The request is in a regional queue.

## Exceptions
- A request that appears to be in the wrong region is handled through WF-08; only a REGIONAL_DIRECTOR or a Service Desk ticket (category `other`, subcategory `routing`) can move it.
- Reassignment never resets the decision clock.
- If the servicing provider's NPI is missing or invalid, the reviewer may pend with PI-DOC-010 once the request is in a queue.
- An office that wants faster routing for an UNASSIGNED request should ask for the servicing provider's location to be added to the provider record, not resubmit, since a second request can be denied as a duplicate.

## What the provider office sees
The office does not see queue names. Request detail shows the status Pending Clinical Review on the **Summary** tab, and the **Timeline** tab shows when the request was submitted and routed. Offices check the servicing provider on step **3 Providers** before pressing **Submit**, because that choice decides the region.
