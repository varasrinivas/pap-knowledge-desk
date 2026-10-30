---
id: WF-03
title: Clinical review
doc_type: workflow
owner: Utilization Management Operations
audience: UM_NURSE, REGIONAL_DIRECTOR, PROVIDER_NURSE, PROVIDER_OFFICE_MGR
queues: {REGION}-{SERVICE_TYPE}-{URGENCY}, Medical Directors, Clinical Policy Desk
stages: Submitted, Pending Clinical Review, Pended (Info Requested), Approved, Denied
version: 2.2
effective_date: 2026-07-01
last_reviewed: 2026-09-15
related: POL-03, POL-04, POL-05, UI-12
---
# Clinical review

## Summary
This workflow covers how a routed request is reviewed and decided. It starts when the rules engine scores a submitted request and ends with an approval, a denial or a pend. Auto-adjudication approves at confidence 0.85 or above (CR-AD-001); otherwise a UM nurse claims the request, and any denial needs Medical Director second-level review.

### Step 1: Auto-adjudication
- **Owner:** The portal (rules engine)
- **Queue / system:** Rules engine
- **Time limit:** At submission.
- **What happens:** The rules engine scores the request against the criteria for its service type. At a confidence of at least 0.85 the request is approved with code CR-AD-001 and a PA number is issued. The engine only approves; it never pends or denies.
- **Exit:** Approved (CR-AD-001), or routed to a review queue (WF-02).

### Step 2: Claim from the queue
- **Owner:** UM_NURSE (permission `review.claim`)
- **Queue / system:** `{REGION}-{SERVICE_TYPE}-{URGENCY}`
- **Time limit:** URGENT queues are worked before STANDARD; all work stays inside the 24-hour or 72-hour clock.
- **What happens:** A UM nurse assigned to the region opens the queue and claims the oldest request first. Claiming locks the request to that nurse so that two reviewers do not work it at once. Nurses see only requests in their assigned region.
- **Exit:** The request is claimed.

### Step 3: First-pass review
- **Owner:** UM_NURSE
- **Queue / system:** Request detail, **Documents** tab
- **Time limit:** Within the decision clock.
- **What happens:** The nurse checks the documentation standards: notes legible, signed, dated by the ordering provider and within 60 days of submission, plus anything the service type needs. If something is missing, the nurse pends with the matching code (permission `review.pend`, see WF-04).
- **Exit:** The record is complete, or the request is pended.

### Step 4: Recommend
- **Owner:** UM_NURSE (permission `review.recommend`)
- **Queue / system:** Review panel
- **Time limit:** Within the decision clock.
- **What happens:** When the criteria are met, the nurse records an approval and a PA number is issued. When the nurse believes the criteria are not met, the nurse recommends denial with a reason; a UM nurse cannot issue a denial alone.
- **Exit:** Approved, or sent to the Medical Directors.

### Step 5: Medical Director second-level review
- **Owner:** Medical Directors
- **Queue / system:** Medical Directors review list
- **Time limit:** Within the remaining decision clock.
- **What happens:** A Medical Director reviews the nurse's recommendation and the record. The director either approves or denies with a denial code from CR-ND-001 to CR-ND-009. The decision letter is generated for the **Decision** tab.
- **Exit:** Approved or Denied.

## Exceptions
- Requests that look like duplicates of an existing approval are denied with CR-ND-006 and the office is pointed to the existing PA number.
- If the member is not eligible on the date of service, the denial is CR-ND-007 and is not appealable; the office verifies eligibility.
- Questions from offices about clinical criteria or medical necessity go to the Clinical Policy Desk, never to the Service Desk.
- A UM nurse who finds the request in the wrong region does not review it; the nurse flags it to the regional director for reassignment (WF-08).
- The Service Desk cannot change, expedite or override a decision at any step.

## What the provider office sees
While the request is in review, the **Summary** tab shows Pending Clinical Review. Auto-approvals show CR-AD-001 on the **Decision** tab within moments of **Submit**. Every decision appears on the **Decision** tab with **Download letter**, and denials add **Appeal this decision** and, where offered, **Request peer-to-peer**.
