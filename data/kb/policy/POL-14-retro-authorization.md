---
id: POL-14
title: Retro authorization
doc_type: policy
owner: Utilization Management Operations
audience: PROVIDER_NURSE, PROVIDER_OFFICE_MGR, UM_NURSE
service_types: ALL
version: 2.0
effective_date: 2026-07-01
last_reviewed: 2026-08-30
related: WF-01, WF-06, UI-04, UI-10
---
# Retro authorization

This policy explains when Northwind accepts a request for authorization after the service was delivered, the deadline for such a request, and what happens when the deadline is missed. Retro authorization is an exception. It is not a way to authorize planned services that were delivered without a request.

## When is retro authorization allowed?
Retro authorization is allowed in two situations only. The first is an emergency admission, where the member was admitted before a prior-authorization request could be filed. The second is retroactive eligibility, where the member's coverage was granted after the service date and back-dated to cover it. Planned services that were delivered without prior authorization do not qualify for retro authorization.

## What is the deadline for a retro authorization request?
A retro authorization request must be submitted within 14 calendar days of the service date. For an emergency admission, the service date is the admission date. For retroactive eligibility, the service date is still the date the service was delivered, so the office should file as soon as it learns the eligibility was granted. The 14 days include weekends and holidays.

## How do I submit a retro authorization request?
A retro authorization request is submitted through **New request** like any other request. On step **2 Service**, enter the actual dates of service, which are in the past. In the clinical notes or a short signed statement, say whether the request is for an emergency admission or retroactive eligibility. Upload the admission notes or the eligibility confirmation on step **5 Documents**. The normal documentation standards apply.

## What happens if the retro request is late?
A retro authorization request submitted more than 14 calendar days after the service date is denied with CR-ND-008, "Retro request outside the 14-day window". CR-ND-008 is appealable. A first-level appeal must be filed within 60 calendar days of the denial, using **Appeal this decision**, and should explain why the request could not be filed within 14 days. The service desk cannot accept a late retro request or waive the window.

## Does a retro request use the same turnaround times?
Yes. A retro authorization request is reviewed under the same decision turnaround as other requests: 72 hours STANDARD and 24 hours URGENT, counted from submission. Because the service has already been delivered, retro requests are rarely URGENT. The clock pauses if the request is pended for information. Missing admission notes, for example, lead to a pend with PI-DOC-001, and the request waits until the office responds through **Respond to Pend**.
