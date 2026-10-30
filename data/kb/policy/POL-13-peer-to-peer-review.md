---
id: POL-13
title: Peer-to-peer review
doc_type: policy
owner: Utilization Management Operations
audience: PROVIDER_NURSE, PROVIDER_OFFICE_MGR, UM_NURSE
service_types: ALL
version: 2.1
effective_date: 2026-07-01
last_reviewed: 2026-09-15
related: WF-06, WF-07, UI-09, UI-11
---
# Peer-to-peer review

This policy explains when an ordering provider can request a peer-to-peer conversation with a Northwind reviewer after a denial, the deadline, how scheduling works and how a peer-to-peer differs from an appeal.

## What is a peer-to-peer review?
A peer-to-peer review is a conversation between the ordering provider and a Northwind clinical reviewer about a denied request. It lets the ordering provider share clinical context that may not be clear from the documents. The reviewer may change the decision after the conversation or leave it in place. The conversation is clinical, so it is held between clinicians; the service desk and the assistant do not take part.

## Which denials can have a peer-to-peer?
A peer-to-peer is offered only for two denial codes: CR-ND-004, medical necessity criteria not met, and CR-ND-009, requested site of care not approved. For these codes, the **Request peer-to-peer** button appears on the **Decision** tab. Denials with any other code do not offer a peer-to-peer; the next step for those is an appeal or the action listed in POL-11, Denial reason codes.

## What is the deadline to request a peer-to-peer?
A peer-to-peer must be requested within 14 calendar days of the denial date. After 14 days, the **Request peer-to-peer** option is no longer available, and the remaining route is a first-level appeal within 60 calendar days of the denial. The user requesting it needs the `p2p.request` permission, which PROVIDER_NURSE and PROVIDER_OFFICE_MGR users have. The service desk cannot request a peer-to-peer on the office's behalf.

## How is a peer-to-peer scheduled?
After the office selects **Request peer-to-peer**, the conversation is scheduled within 2 business days. The scheduled time appears on the request's **Timeline** tab and in the **Messages** tab. The ordering provider should be available at the scheduled time. The service desk cannot move a peer-to-peer to an earlier slot. The outcome of the peer-to-peer is recorded on the **Decision** tab, and a changed decision comes with a new decision letter.

## Is a peer-to-peer the same as an appeal?
No. A peer-to-peer is not an appeal. Requesting one does not file an appeal and does not pause the appeal clock. The 60-day appeal deadline keeps running from the denial date. If the decision is unchanged after the peer-to-peer, the office can still file a first-level appeal with **Appeal this decision**, as long as it is within the 60 days.
