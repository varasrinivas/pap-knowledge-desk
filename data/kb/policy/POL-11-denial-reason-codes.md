---
id: POL-11
title: Denial reason codes
doc_type: policy
owner: Utilization Management Operations
audience: PROVIDER_NURSE, PROVIDER_OFFICE_MGR, UM_NURSE
service_types: ALL
version: 4.0
effective_date: 2026-07-01
last_reviewed: 2026-09-15
related: WF-03, WF-06, WF-07, UI-09, UI-10, UI-11
---
# Denial reason codes

This policy lists the ten denial reason codes and the auto-approval code, whether each denial can be appealed, and the next step for the office. The code appears on the **Decision** tab and in the decision letter, which is downloaded with **Download letter**.

## What do the denial reason codes mean?
Each denied request carries one denial code on the **Decision** tab.

| Code | Meaning | Appealable | Next step |
|---|---|---|---|
| CR-ND-001 | Missing conservative-therapy documentation | Yes | Appeal with the therapy history |
| CR-ND-002 | Clinical notes not current | Yes | Appeal with notes within 60 days |
| CR-ND-003 | Service not covered under the member's plan | Yes (coverage appeal) | File a coverage appeal |
| CR-ND-004 | Medical necessity criteria not met | Yes | Peer-to-peer or appeal |
| CR-ND-005 | Out-of-network without an approved exception | Yes | Appeal, or use an in-network provider |
| CR-ND-006 | Duplicate request | No | Use the existing PA |
| CR-ND-007 | Member not eligible on the date of service | No | Verify eligibility |
| CR-ND-008 | Retro request outside the 14-day window | Yes | Appeal |
| CR-ND-009 | Requested site of care not approved | Yes | Use the approved site, peer-to-peer or appeal |
| CR-ND-010 | Pend not answered in 14 days | No | Submit a new request |

## Which denials cannot be appealed?
Three denial codes are not appealable. CR-ND-006 means an approved authorization already exists for the same service; use the existing PA number instead of a new request. CR-ND-007 means the member was not eligible on the date of service; verify eligibility before taking any other step. CR-ND-010 means a pend was not answered within 14 calendar days and the request closed as Withdrawn; submit a new request with the missing information.

## Which denials offer a peer-to-peer?
A peer-to-peer is offered only for CR-ND-004, medical necessity criteria not met, and CR-ND-009, requested site of care not approved. When it is offered, the **Request peer-to-peer** button appears on the **Decision** tab. It must be requested within 14 calendar days of the denial. A peer-to-peer is not an appeal; the 60-day appeal clock keeps running while it is scheduled and held.

## What is CR-AD-001?
CR-AD-001 is the approval code for a request approved on auto-adjudication. The rules engine approved the request automatically because its confidence was at least 0.85. A CR-AD-001 approval is a full approval with a PA number, the same as one made by a reviewer. Requests below the 0.85 confidence threshold go to a UM nurse for clinical review instead. The CR-AD-001 code appears on the **Decision** tab and in the approval letter.

## Who can explain why a request was denied?
The decision letter states the reason and the denial code. The assistant and the service desk can explain what a code means administratively and what the next step is. They cannot change, expedite or override a decision, and they do not answer medical-necessity or clinical-criteria questions. Those go to the Clinical Policy Desk, or are raised through a peer-to-peer or an appeal.
