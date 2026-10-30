---
id: POL-10
title: Pend reason codes
doc_type: policy
owner: Utilization Management Operations
audience: PROVIDER_NURSE, PROVIDER_OFFICE_MGR, UM_NURSE
service_types: ALL
version: 4.2
effective_date: 2026-07-01
last_reviewed: 2026-09-15
related: WF-04, UI-07, UI-08, UI-16
---
# Pend reason codes

This policy lists the twelve pend reason codes a reviewer can set when a request needs more information, what clears each one, and what happens when a pend is not answered. A pended request shows the status Pended (Info Requested), and the decision clock is paused.

## What do the pend reason codes mean and what clears them?
Each pend code is cleared by uploading what it names through the **Respond to Pend** panel.

| Code | Meaning | What clears it |
|---|---|---|
| PI-DOC-001 | Clinical notes missing | Signed, dated notes within 60 days |
| PI-DOC-002 | Clinical notes older than 60 days | Notes dated within 60 days |
| PI-DOC-003 | Imaging report missing | The imaging report |
| PI-DOC-004 | Conservative-therapy history missing | Type, dates, duration, outcome |
| PI-DOC-005 | Ordering-provider signature missing | A signed copy |
| PI-DOC-006 | Units or dates of service unclear | Corrected units or dates |
| PI-DOC-007 | Diagnosis code does not match the service | A matching code with support |
| PI-DOC-008 | Face-to-face encounter note missing | The face-to-face note |
| PI-DOC-009 | Treatment plan missing | The signed treatment plan |
| PI-DOC-010 | Servicing provider NPI missing or invalid | A valid NPI |
| PI-DOC-011 | Prior test results missing | The prior test reports |
| PI-DOC-012 | Illegible document | A legible copy |

## How do I respond to a pend?
To respond to a pend, open the request, select **Respond to Pend** on the request detail screen, upload the document the pend code names, and submit the response. The request returns to Pending Clinical Review and the decision clock resumes. Upload the specific item requested; a response without it usually leads to a second pend. The **Messages** tab can carry a short note to the reviewer, but a message alone does not clear a document pend.

## Which pend codes apply to specific service types?
Three pend codes apply to specific service types. PI-DOC-008, face-to-face encounter note missing, applies to HOME_HEALTH_DME. PI-DOC-009, treatment plan missing, applies to ONCOLOGY and BEHAVIORAL_HEALTH. PI-DOC-011, prior test results missing, applies to CARDIOLOGY and SLEEP_STUDY. The other nine pend codes can apply to any service type. Each pend is cleared the same way, by uploading the named item through **Respond to Pend** on the request detail screen.

## What happens if a pend is not answered?
A pend with no response in 14 calendar days closes as Withdrawn. The decision record shows CR-ND-010, "Pend not answered in 14 days", which is not appealable. To continue, the office submits a new request with the missing information. The closed request cannot be reopened. Turning on the **Pended** notification under **Email me when** helps the office see pends quickly.

## Does a pend affect the turnaround time?
Yes. While a request is Pended (Info Requested), the 72-hour STANDARD or 24-hour URGENT decision clock is paused. It resumes when the provider responds. A pend therefore lengthens the total elapsed time to a decision. Submitting complete, current documentation with the first submission is the most reliable way to avoid a pend. The status history, including each pend and response, is shown on the **Timeline** tab.
