---
id: WF-04
title: Pend and resubmission loop
doc_type: workflow
owner: Utilization Management Operations
audience: PROVIDER_NURSE, PROVIDER_OFFICE_MGR, UM_NURSE
queues: {REGION}-{SERVICE_TYPE}-{URGENCY}
stages: Pending Clinical Review, Pended (Info Requested), Withdrawn
version: 2.0
effective_date: 2026-07-01
last_reviewed: 2026-09-15
related: POL-06, POL-09, UI-05, UI-08
---
# Pend and resubmission loop

## Summary
This workflow covers what happens when a reviewer needs more information. It starts when a UM nurse pends a request with a PI-DOC code and ends when the office responds and review resumes, or when 14 calendar days pass without a response and the request closes as Withdrawn. The decision clock pauses while the request is pended.

### Step 1: Pend the request
- **Owner:** UM_NURSE (permission `review.pend`)
- **Queue / system:** Review panel
- **Time limit:** Within the decision clock.
- **What happens:** The nurse selects one or more pend codes, for example PI-DOC-001 (clinical notes missing) or PI-DOC-004 (conservative-therapy history missing). Each code names exactly what is needed. The status changes to Pended (Info Requested) and the decision clock pauses.
- **Exit:** The office is notified.

### Step 2: Notify the office
- **Owner:** The portal (automatic)
- **Queue / system:** Notifications, **Messages** tab
- **Time limit:** At the time of the pend.
- **What happens:** Users who chose **Pended** under **Email me when** receive an email. The request shows the pend code on its **Summary** tab and the **Respond to Pend** button appears.
- **Exit:** The office opens the request.

### Step 3: Gather what the code names
- **Owner:** PROVIDER_NURSE or PROVIDER_OFFICE_MGR
- **Queue / system:** The office's own records
- **Time limit:** 14 calendar days from the pend.
- **What happens:** The office collects the item each code names, such as notes dated within 60 days for PI-DOC-002 or the servicing provider NPI for PI-DOC-010. Files must be PDF, JPG, PNG, TIFF or DOCX, no larger than 25 MB each, and up to 20 files per request. ZIP files are not accepted.
- **Exit:** The documents are ready.

### Step 4: Respond to Pend
- **Owner:** PROVIDER_NURSE (permission `intake.respond_pend`)
- **Queue / system:** **Respond to Pend** panel
- **Time limit:** Before day 14.
- **What happens:** The office uploads the items through **Respond to Pend** and submits the response. Uploads appear on the **Documents** tab within 2 minutes; a file still missing after 10 minutes should be uploaded again. Documents are never emailed.
- **Exit:** The response is submitted.

### Step 5: Resume review
- **Owner:** The portal, then the UM_NURSE
- **Queue / system:** The original queue
- **Time limit:** The decision clock resumes from where it paused.
- **What happens:** The request returns to Pending Clinical Review in the same queue, and the reviewer continues from the point of the pend. If the response does not clear the code, the reviewer may pend again with the remaining code.
- **Exit:** A decision (WF-03) or another pend.

## Exceptions
- No response in 14 calendar days: the request closes as Withdrawn with CR-ND-010. That code is not appealable; the office submits a new request.
- A file shown as `Rejected` on the **Documents** tab does not clear a pend; the office uploads an accepted file type.
- A file stuck at `Scanning` should be checked against the Service Desk's open incidents before raising a new ticket.
- PI-DOC-012 (illegible document) is cleared only by a clearer copy of the same document, not by an explanation in **Messages**.
- The Service Desk cannot clear a pend or extend the 14-day window.

## What the provider office sees
The **Summary** tab shows Pended (Info Requested) with the pend code and its meaning. The **Respond to Pend** button is on Request detail, and responses appear on the **Documents** tab with **Uploaded by**, **Size** and **Status**. The **Timeline** tab records when the clock paused and resumed.
