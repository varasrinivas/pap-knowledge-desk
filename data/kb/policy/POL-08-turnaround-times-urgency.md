---
id: POL-08
title: Turnaround times and urgency
doc_type: policy
owner: Utilization Management Operations
audience: PROVIDER_NURSE, PROVIDER_OFFICE_MGR, UM_NURSE
service_types: ALL
version: 3.2
effective_date: 2026-07-01
last_reviewed: 2026-09-15
related: WF-01, WF-05, WF-08, UI-04, UI-07
---
# Turnaround times and urgency

This policy defines how long Northwind takes to decide a prior-authorization request, when the clock starts and pauses, and what makes a request urgent. The turnaround time is the review SLA. The service desk cannot shorten it for an individual request.

## How long does a standard review take?
A STANDARD prior-authorization request is decided within 72 hours. An URGENT request is decided within 24 hours. These are the decision turnaround times, also called the review SLA. They apply to every service type. The time is counted from when the request reaches Submitted, not from when the draft was started, and it excludes any time the request spends pended for information.

## When does the turnaround clock start and pause?
The turnaround clock starts when the request moves from Draft to Submitted. It pauses when a reviewer pends the request and the status becomes Pended (Info Requested). It resumes when the provider responds through **Respond to Pend** and the request returns to Pending Clinical Review. A Draft is never visible to reviewers, so time spent in Draft does not count. Reassigning a misrouted request to another queue does not reset the clock.

## What counts as urgent?
A request is URGENT when waiting the standard time could seriously jeopardise the member's life, health or ability to regain maximum function. Convenience, a scheduled date that is close, or an office backlog do not make a request urgent. Every other request is STANDARD. Whether a member's condition meets the urgent standard is a clinical judgement made by the treating clinician, not by the service desk.

## What is the urgent attestation?
The urgent attestation is the **Urgent attestation** checkbox on step **6 Review & Submit** of the New Request wizard. A treating clinician ticks it to confirm that the request meets the urgent standard. A request submitted as URGENT without the attestation is reviewed as STANDARD. The attestation is part of the request record and is visible to the reviewer. The service desk cannot add or remove the attestation after submission.

## Can the service desk speed up a request?
No. The service desk and the assistant cannot change, expedite or override a decision, and cannot promise a decision time beyond the published turnaround. If a request is close to breaching its 72-hour or 24-hour turnaround, the desk can open a P2 ticket for an SLA at risk so that the review team is aware. The request's status and history are on the **Timeline** tab of the request detail screen.
