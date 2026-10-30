---
id: WF-05
title: Urgent and expedited handling
doc_type: workflow
owner: Utilization Management Operations
audience: PROVIDER_NURSE, PROVIDER_OFFICE_MGR, UM_NURSE, REGIONAL_DIRECTOR
queues: {REGION}-{SERVICE_TYPE}-URGENT, {REGION}-{SERVICE_TYPE}-STANDARD
stages: Draft, Submitted, Pending Clinical Review, Approved, Denied
version: 1.8
effective_date: 2026-07-01
last_reviewed: 2026-09-15
related: POL-02, POL-07, UI-03, UI-04
---
# Urgent and expedited handling

## Summary
This workflow explains how a request becomes URGENT and what changes when it does. It starts on wizard step 6, where a treating clinician ticks the **Urgent attestation** checkbox, and ends with a decision inside 24 hours. A request without the attestation is handled as STANDARD with the 72-hour clock.

### Step 1: Decide whether the request is urgent
- **Owner:** Treating clinician at the provider office
- **Queue / system:** New Request wizard
- **Time limit:** Before **Submit**.
- **What happens:** A request is URGENT only when waiting the standard time could seriously jeopardise the member's life, health or ability to regain maximum function. Convenience, scheduling pressure or a booked procedure date do not by themselves meet this definition.
- **Exit:** The clinician confirms the definition is met.

### Step 2: Attest
- **Owner:** Treating clinician (entered by a PROVIDER_NURSE with `intake.submit`)
- **Queue / system:** Step **6 Review & Submit**, **Urgent attestation** checkbox
- **Time limit:** At submission.
- **What happens:** The **Urgent attestation** checkbox records that a treating clinician attests to the urgency. The attestation is stored with the request and shown to the reviewer.
- **Exit:** **Submit** is pressed.

### Step 3: Check for the attestation
- **Owner:** The portal (automatic)
- **Queue / system:** Routing
- **Time limit:** At submission.
- **What happens:** If URGENT was indicated but the **Urgent attestation** checkbox was not ticked, the request is downgraded to STANDARD and routed to the STANDARD queue with a 72-hour clock. The **Timeline** tab records the downgrade.
- **Exit:** The request is routed as URGENT or STANDARD.

### Step 4: Route and prioritise
- **Owner:** The portal, then UM_NURSE
- **Queue / system:** `{REGION}-{SERVICE_TYPE}-URGENT`
- **Time limit:** 24-hour decision clock from Submitted.
- **What happens:** The request goes to the URGENT queue for its region and service type. UM nurses work URGENT queues before STANDARD queues. Regional directors watch the **Past SLA** tile for any URGENT request close to its limit.
- **Exit:** A nurse claims it.

### Step 5: Decide within 24 hours
- **Owner:** UM_NURSE, with Medical Directors for denials
- **Queue / system:** Review panel
- **Time limit:** 24 hours, paused only while pended.
- **What happens:** Review follows WF-03. If information is missing the request can still be pended; the clock pauses, and the office should respond as quickly as possible because the 24-hour limit resumes on the response.
- **Exit:** Approved or Denied.

## Exceptions
- A missing attestation cannot be added after submission, so the request is decided on the 72-hour STANDARD clock. The Service Desk cannot expedite a request.
- Ticking the attestation for a request that does not meet the definition is a compliance issue and is reviewed by the regional director.
- An urgent request denied by a Medical Director can be appealed as an expedited appeal, decided within 72 hours (WF-06).
- A request routed to the wrong URGENT queue keeps its 24-hour clock through reassignment (WF-08).

## What the provider office sees
On step **6 Review & Submit** the office sees the **Urgent attestation** checkbox above **Submit**. The Home worklist can be filtered by **Urgency**, and Request detail shows URGENT or STANDARD on the **Summary** tab. The **Timeline** tab shows any downgrade and the time the decision clock started.
