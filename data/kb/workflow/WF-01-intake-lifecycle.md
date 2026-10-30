---
id: WF-01
title: Intake request lifecycle
doc_type: workflow
owner: Utilization Management Operations
audience: PROVIDER_NURSE, PROVIDER_OFFICE_MGR, UM_NURSE, REGIONAL_DIRECTOR
queues: {REGION}-{SERVICE_TYPE}-{URGENCY}, UNASSIGNED, Medical Directors
stages: Draft, Submitted, Pending Clinical Review, Pended (Info Requested), Approved, Denied, Withdrawn
version: 3.1
effective_date: 2026-07-01
last_reviewed: 2026-09-15
related: POL-01, POL-02, UI-03, UI-06
---
# Intake request lifecycle

## Summary
This workflow describes every status an intake request (`IR-YYYY-NNNNN`) passes through in the Northwind Prior Auth Portal, from the first saved draft to a final decision. It starts when a provider office opens **New request** and ends when the request is Approved, Denied or Withdrawn. The decision clock runs 72 hours STANDARD or 24 hours URGENT, paused while pended.

### Step 1: Draft
- **Owner:** PROVIDER_NURSE or PROVIDER_OFFICE_MGR
- **Queue / system:** New Request wizard, the office's Home worklist
- **Time limit:** None. No clock runs on a draft.
- **What happens:** The office works through the wizard steps **1 Member** to **6 Review & Submit** and may press **Save draft** at any point. A draft is visible only to the office; reviewers never see it. Documents attached in step 5 stay with the draft.
- **Exit:** A user with `intake.submit` presses **Submit** on step 6.

### Step 2: Submitted
- **Owner:** The portal (automatic)
- **Queue / system:** Rules engine and routing
- **Time limit:** The decision clock starts at this moment.
- **What happens:** The request receives its identifier and is checked by the rules engine. If the engine's confidence is at least 0.85, the request is approved straight away with code CR-AD-001. Otherwise it is routed to a review queue (see WF-02).
- **Exit:** The request is auto-approved, or it lands in a review queue.

### Step 3: Pending Clinical Review
- **Owner:** UM_NURSE for the routed region
- **Queue / system:** `{REGION}-{SERVICE_TYPE}-{URGENCY}`
- **Time limit:** Within the 72-hour or 24-hour decision clock.
- **What happens:** A UM nurse claims the request and reviews the clinical record (see WF-03). The nurse can recommend approval, recommend denial for Medical Director review, or pend the request for missing information.
- **Exit:** A pend, or a decision.

### Step 4: Pended (Info Requested)
- **Owner:** The provider office
- **Queue / system:** Request detail, **Respond to Pend** panel
- **Time limit:** 14 calendar days to respond. The decision clock is paused.
- **What happens:** The request shows a pend code (PI-DOC-001 to PI-DOC-012) naming what is missing. The office uploads it through **Respond to Pend** (see WF-04).
- **Exit:** On the office's response the request returns to Pending Clinical Review and the clock resumes. With no response in 14 days it closes as Withdrawn with CR-ND-010.

### Step 5: Final status
- **Owner:** UM_NURSE (approvals), Medical Directors (denials), or the office (withdrawals)
- **Queue / system:** Decision tab
- **Time limit:** Final; no further clock.
- **What happens:** Approved requests receive a prior-auth number (`PA-NNNNN`). Denied requests carry a denial code and, where offered, appeal and peer-to-peer options. Withdrawn requests are closed by the office with **Withdraw** or by the 14-day pend rule.
- **Exit:** The decision letter is available under **Download letter**.

## Exceptions
- A request that was auto-approved never enters Pending Clinical Review; its Timeline shows CR-AD-001.
- A request whose servicing provider has no practice location on file is routed to `UNASSIGNED` until the regional director's 24-hour sweep places it.
- An office can **Withdraw** a request at any non-final status; a withdrawn request cannot be reopened, so a new request is needed.
- A request denied with CR-ND-010 (pend not answered) cannot be appealed; the office submits a new request.
- A request denied with CR-ND-006 (duplicate) is not resubmitted; the existing PA number is used instead.

## What the provider office sees
The office follows the status on the Home worklist, filtered by **Status** and **Urgency**. The **Timeline** tab on Request detail records every transition with its time, including clock pauses. **Respond to Pend** appears only while pended, and the **Decision** tab fills in once the request is Approved or Denied.
