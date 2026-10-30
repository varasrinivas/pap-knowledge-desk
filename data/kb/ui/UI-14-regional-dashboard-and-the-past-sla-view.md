---
id: UI-14
title: Regional dashboard and the past-SLA view
doc_type: ui
owner: Portal Product Team
audience: REGIONAL_DIRECTOR
screens: Regional Dashboard
role_required: REGIONAL_DIRECTOR
permission: dashboard.region.view
version: 2.5
effective_date: 2026-06-01
last_reviewed: 2026-08-30
related: POL-08, POL-20, WF-02, WF-08
---
# Regional dashboard and the past-SLA view

Use this if you are a regional director and want to see your region's review workload, find requests that have missed the review SLA, and move misrouted work to the right queue.

## Procedure: Read the dashboard tiles
1. Sign in and open **Regional Dashboard**.
2. Read the four tiles for your region:
   - **Open**: requests submitted and not yet decided.
   - **Past SLA**: requests past the 72-hour (STANDARD) or 24-hour (URGENT) review clock.
   - **Pended**: requests waiting on a provider's response; their clock is paused.
   - **Unassigned**: requests in the `UNASSIGNED` queue because the servicing provider has no location on file.
3. Click any tile to open the list behind it.

**What you should see:** Counts for your own region only, with each tile opening a list of `IR-` numbers, queues and ages.

## Procedure: Work the past-SLA list
1. Click the **Past SLA** tile.
2. Sort the list by urgency so `URGENT` requests are at the top.
3. Open each request and check its queue name, in the form `{REGION}-{SERVICE_TYPE}-{URGENCY}`.
4. If the queue is right, follow up with the reviewer group through your usual escalation route (POL-20).
5. If the queue is wrong, move it with **Reassign queue** (below).

**What you should see:** The **Past SLA** count falls as requests are decided. Time paused in `Pended (Info Requested)` does not count toward SLA.

## Procedure: Reassign a request to the right queue
1. From any list, open the request.
2. Click **Reassign queue**.
3. Choose the correct queue, for example `SOUTH_CENTRAL-CARDIOLOGY-URGENT`.
4. Enter a short reason (for example "Servicing provider is in Dallas").
5. Confirm.

**What you should see:** The request in the new queue. A reassignment does not reset the SLA clock, so a past-SLA request stays past SLA.

## Procedure: Sweep the Unassigned queue
1. Click the **Unassigned** tile. Sweep it at least every 24 hours.
2. For each request, find the servicing provider's practice location.
3. Use **Reassign queue** to move it to the queue for that region.

**What you should see:** The **Unassigned** tile back at zero after the sweep.

## Common errors on this screen
- **"I can't see Reassign queue"**: Reassigning needs `queue.reassign`, which only regional directors hold. Others ask through a Service Desk ticket (category `other`, subcategory `routing`).
- **"A reassigned request still shows Past SLA"**: Expected. Reassignment does not reset the clock.
- **"Requests from one office keep landing in the wrong region"**: The region comes from the servicing provider's practice location. Repeated misroutes for one service type may be a routing-rule problem; report it (WF-08).
- **"The dashboard shows only my region"**: That is by design; each director sees their assigned region.
