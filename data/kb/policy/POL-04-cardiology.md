---
id: POL-04
title: Cardiology diagnostics and procedures
doc_type: policy
owner: Utilization Management Operations
audience: PROVIDER_NURSE, PROVIDER_OFFICE_MGR, UM_NURSE
service_types: CARDIOLOGY
version: 2.2
effective_date: 2026-07-01
last_reviewed: 2026-08-28
related: WF-01, WF-02, WF-04, WF-08, UI-04, UI-08
---
# Cardiology diagnostics and procedures

This policy sets out what an office submits for cardiology diagnostic tests and procedures under the CARDIOLOGY service type, with a focus on prior test results. It also explains how cardiology requests are routed. Questions about the clinical criteria for a test go to the Clinical Policy Desk.

## What must a cardiology request include?
A CARDIOLOGY request needs the cardiologist's or ordering provider's clinical notes, signed and dated within 60 days of submission, the results of earlier cardiac tests, a diagnosis code that matches the requested service, and the servicing provider's valid NPI. Missing notes are pended with PI-DOC-001, notes older than 60 days with PI-DOC-002, and a missing or invalid servicing provider NPI with PI-DOC-010.

## Which prior test results are needed for cardiology?
Prior test results means the reports of cardiac testing the member already had that relate to the requested service, for example an ECG, an echocardiogram or a stress test. Upload the reports, not the raw tracings. When the clinical notes mention a prior test but the result is not attached, the request is pended with PI-DOC-011, "Prior test results missing". The pend is cleared by uploading the result through the **Respond to Pend** panel.

## What if the member has had no prior cardiac testing?
If the member has had no earlier cardiac testing related to the request, say so in the clinical notes or in a short signed statement from the ordering provider, and upload it on step **5 Documents**. A clear statement that no prior testing exists avoids a PI-DOC-011 pend. Whether the requested test is appropriate without earlier testing is a clinical question for the reviewer, and criteria questions go to the Clinical Policy Desk.

## How is a cardiology request routed?
A submitted cardiology request goes to the review queue named `{REGION}-CARDIOLOGY-{URGENCY}`, for example `SOUTH_CENTRAL-CARDIOLOGY-URGENT`. The region comes from the servicing provider's practice location, not from the submitting office and not from the member's address. If the servicing provider has no location on file, the request falls to `UNASSIGNED`, which the regional director sweeps every 24 hours. Keeping the servicing provider's practice location current is the simplest way to make sure a cardiology request reaches the right region.

## What if a cardiology request lands in the wrong region?
A cardiology request routed to the wrong region can be reassigned only by a REGIONAL_DIRECTOR or through a Service Desk ticket with category `other` and subcategory `routing`. Include the intake request ID, such as `IR-2026-00517`, and the servicing provider's practice location in the ticket. A reassignment does not reset the review SLA clock, so the original 72-hour or 24-hour turnaround still applies. Do not resubmit the cardiology request to move it, because a second request for the same service can be denied as a duplicate.
