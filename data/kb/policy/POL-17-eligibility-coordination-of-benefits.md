---
id: POL-17
title: Member eligibility and coordination of benefits
doc_type: policy
owner: Utilization Management Operations
audience: PROVIDER_NURSE, PROVIDER_OFFICE_MGR, UM_NURSE
service_types: ALL
version: 2.0
effective_date: 2026-07-01
last_reviewed: 2026-09-02
related: WF-01, WF-11, UI-04, UI-18
---
# Member eligibility and coordination of benefits

This policy explains how member eligibility affects a prior-authorization request, how coordination of benefits applies when the member has other coverage, and what the assistant and service desk can and cannot see about a member.

## Why does eligibility matter for prior authorization?
A prior authorization is only valid if the member is eligible with Northwind on the date of service. A request for a date when the member is not eligible is denied with CR-ND-007, "Member not eligible on the date of service". An approval does not guarantee eligibility on a later date; if the member's coverage ends before the service, the authorization does not cover it.

## What should I do after a CR-ND-007 denial?
CR-ND-007 is not appealable. The next step is to verify the member's eligibility for the date of service through the office's usual eligibility check with the plan. If the member was in fact eligible, for example because coverage was granted retroactively, submit a new request; retroactive eligibility allows a retro authorization within 14 calendar days of the service date. If the member was not eligible, the service is not covered by Northwind.

## How does coordination of benefits affect a request?
Coordination of benefits applies when the member has coverage from more than one plan. When Northwind is the secondary plan, Northwind's prior-authorization rules still apply to the services on its list, even if the primary plan has authorized the service. Submit the request through the portal as usual and note the other coverage on step **1 Member**. A primary plan's approval letter can be uploaded as supporting information but does not replace Northwind's review.

## What can the assistant see about a member?
The assistant can see the status, timeline, pend codes and decision codes of requests the signed-in user has access to, and the user's own role and permissions. It cannot see member eligibility, benefits or coordination-of-benefits records, and it never shows another user's data. It cannot confirm whether a member is eligible on a given date. Eligibility questions are answered through the plan's eligibility check, not through a support ticket.

## What should I put in a ticket about an eligibility problem?
A support ticket about an eligibility problem should contain the intake request ID, such as `IR-2026-00517`, the decision code and a short description of the portal problem. It should not contain the member's name, date of birth, diagnosis or other health information. The service desk can investigate portal defects, such as an eligibility date displayed wrongly, but cannot change a member's eligibility or a decision.
