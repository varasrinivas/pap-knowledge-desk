---
id: WF-08
title: Misrouted request correction
doc_type: workflow
owner: Utilization Management Operations
audience: PROVIDER_NURSE, PROVIDER_OFFICE_MGR, UM_NURSE, REGIONAL_DIRECTOR
queues: {REGION}-{SERVICE_TYPE}-{URGENCY}, UNASSIGNED, Service Desk, Platform Engineering
stages: Pending Clinical Review
version: 1.9
effective_date: 2026-07-01
last_reviewed: 2026-09-15
related: POL-08, POL-12, UI-07, UI-15, UI-18
---
# Misrouted request correction

## Summary
This workflow corrects a request that landed in the wrong review queue. It starts when an office, a UM nurse or a director notices the queue does not match the servicing provider's practice location, and ends when the request is in the right queue and, if a routing rule caused it, a defect is raised. Reassignment never resets the decision clock.

### Step 1: Confirm the request is misrouted
- **Owner:** Whoever notices it (office, UM_NURSE, REGIONAL_DIRECTOR or Service Desk)
- **Queue / system:** Routing explanation for the request
- **Time limit:** As soon as it is noticed; the decision clock is running.
- **What happens:** Compare the queue `{REGION}-{SERVICE_TYPE}-{URGENCY}` with the expected one. The correct region comes from the servicing provider's practice location, not from the submitting office or the member's address. A request that matches that rule is not misrouted, even if the office is in another city.
- **Exit:** The queue is confirmed wrong.

### Step 2: Choose the reassignment path
- **Owner:** The person who confirmed it
- **Queue / system:** Regional Dashboard or Service Desk
- **Time limit:** Same business day.
- **What happens:** Only two paths can move a request. A REGIONAL_DIRECTOR with `queue.reassign` can move it directly. Anyone else, including offices and UM nurses, raises a Service Desk ticket with category `other` and subcategory `routing`, giving the IR number and the expected queue.
- **Exit:** A director acts, or a ticket is open.

### Step 3: Reassign
- **Owner:** REGIONAL_DIRECTOR
- **Queue / system:** Regional Dashboard, **Reassign queue**
- **Time limit:** Prompt; URGENT requests first.
- **What happens:** The director selects the request and the correct queue. For a ticket, the Service Desk routes the work to the director of the correct region, who performs the reassignment. The request stays Pending Clinical Review.
- **Exit:** The request is in the correct queue.

### Step 4: Keep the clock
- **Owner:** The portal (automatic)
- **Queue / system:** Decision clock
- **Time limit:** Unchanged.
- **What happens:** The decision clock continues from the original Submitted time. A reassigned STANDARD request still has 72 hours from submission, an URGENT request still has 24. Directors check the **Past SLA** tile for reassigned requests near their limit.
- **Exit:** A UM nurse in the correct region claims it.

### Step 5: Report a routing-rule defect
- **Owner:** Service Desk
- **Queue / system:** ServiceNow incident, category `portal_defect`, subcategory `routing`, assigned to Platform Engineering
- **Time limit:** When the same pattern appears more than once.
- **What happens:** If several requests with the same service type and provider area land in the same wrong region, the cause is likely a routing rule rather than data entry. The Service Desk raises one incident with the IR numbers, the expected and actual queues, and the routing explanation output. Platform Engineering owns the rule table; only PLATFORM_ADMIN can change it.
- **Exit:** The defect is logged and linked to the routing tickets.

## Exceptions
- Requests in `UNASSIGNED` are not misrouted; they wait for the regional director's 24-hour sweep (WF-02).
- An office must not withdraw and resubmit to fix routing; the new request can be denied as a duplicate and the clock restarts on the new request only.
- A UM nurse cannot reassign a request, even within the nurse's own region.
- If several offices report the same misrouting at once, new reports become work notes on the oldest open ticket under the dedup rule (WF-11).

## What the provider office sees
Offices do not see queue names, so a misroute usually shows as a slow review. The **Summary** and **Timeline** tabs show status and submission time, which do not change on reassignment. Offices raise the routing ticket from Help, **Contact support**, and follow it under **Your tickets**.
