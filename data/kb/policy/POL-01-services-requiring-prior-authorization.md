---
id: POL-01
title: Services requiring prior authorization
doc_type: policy
owner: Utilization Management Operations
audience: PROVIDER_NURSE, PROVIDER_OFFICE_MGR, UM_NURSE
service_types: ALL
version: 4.0
effective_date: 2026-07-01
last_reviewed: 2026-09-15
related: WF-01, WF-02, UI-04, UI-12
---
# Services requiring prior authorization

This policy lists the service types that need prior authorization from Northwind Health Plan before the service is delivered, the situations that are exempt, and how the list changes. It is an administrative policy. Questions about medical-necessity criteria go to the Clinical Policy Desk.

## Which services need prior authorization at Northwind?
Northwind Health Plan requires prior authorization for eight service types. Each one is a choice on step **2 Service** of the New Request wizard in the Northwind Prior Auth Portal, and each one routes to its own review queue.

| Service type | Covers |
|---|---|
| IMAGING | MRI, CT and PET |
| ORTHO_SURGERY | Outpatient surgery and orthopedic procedures |
| CARDIOLOGY | Cardiology diagnostics and procedures |
| ONCOLOGY | Oncology drugs and radiation therapy |
| HOME_HEALTH_DME | Home health services and durable medical equipment |
| BEHAVIORAL_HEALTH | Behavioral health inpatient and intensive outpatient |
| PHYSICAL_THERAPY | Physical therapy |
| SLEEP_STUDY | Sleep studies |

A service outside these eight types does not need a prior-authorization request through the portal.

## Are emergency services exempt from prior authorization?
Emergency services do not need prior authorization before they are delivered. The provider should never delay emergency care to submit a portal request. When an emergency leads to an admission that would otherwise need prior authorization, the office submits a retro authorization request within 14 calendar days of the service date. A retro request filed after the 14-day window is denied with CR-ND-008, which is appealable. Retro authorization is also allowed when the member's eligibility is granted retroactively. The full retro rules are in POL-14.

## Who can submit a prior-authorization request?
A prior-authorization request is created and submitted in the portal by a user with the `intake.create` and `intake.submit` permissions. PROVIDER_NURSE and PROVIDER_OFFICE_MGR users have both. A nurse may also submit on behalf of the office through a delegation granted on **My Office > Delegation**. Delegations expire after 180 days; a nurse whose delegation lapsed keeps **Save draft** but loses the **Submit** button. UM_NURSE users review requests and do not submit them.

## How does the list of services change?
Northwind gives providers 90 days' notice before a service type is added to the prior-authorization list or a new rule takes effect. The notice appears on the portal home page and in the office manager's email. Removals take effect on the date announced, without a notice period, because they reduce the office's work. A request already submitted is reviewed under the list that was in force on its submission date.

## What if I am unsure whether a service needs authorization?
If an office is unsure whether a service falls under one of the eight service types, the office can ask the assistant through **Help > Contact support**. The assistant answers administrative questions about the list and the portal. It does not decide coverage for a specific member and does not answer clinical-criteria or medical-necessity questions; those go to the Clinical Policy Desk. Submitting a request when unsure is safe: a service that does not need authorization is not penalised.
