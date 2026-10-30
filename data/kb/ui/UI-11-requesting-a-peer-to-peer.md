---
id: UI-11
title: Requesting a peer-to-peer
doc_type: ui
owner: Portal Product Team
audience: PROVIDER_NURSE, PROVIDER_OFFICE_MGR
screens: Request detail, Decision tab
role_required: PROVIDER_NURSE
permission: p2p.request
version: 2.0
effective_date: 2026-05-01
last_reviewed: 2026-08-30
related: POL-13, POL-12, WF-07
---
# Requesting a peer-to-peer

Use this when a request was denied and the ordering provider wants to discuss the decision with a Northwind physician reviewer. A peer-to-peer is offered only for certain denials, and you must request it within **14 calendar days** of the denial.

## Procedure: Request a peer-to-peer from the Decision tab
1. Open the denied request and click the **Decision** tab.
2. Check that **Request peer-to-peer** is shown. It appears only when a peer-to-peer is offered, which is for `CR-ND-004` (medical necessity criteria not met) and `CR-ND-009` (requested site of care not approved).
3. Check the denial date. You must request within 14 calendar days of it.
4. Click **Request peer-to-peer**.
5. Enter the ordering provider who will take part and the times they are available.
6. Give a direct phone number for the provider's office.
7. Submit the request.

**What you should see:** A confirmation and a peer-to-peer entry on the **Timeline** tab. The conversation is scheduled within 2 business days, and you are contacted with the time.

## Procedure: Decide between a peer-to-peer and an appeal
1. Read the reason code on the **Decision** tab.
2. If **Request peer-to-peer** is not shown, a peer-to-peer is not available; use **Appeal this decision** if the code can be appealed (UI-10).
3. If it is shown, you may request a peer-to-peer, file an appeal, or both.
4. Track the appeal deadline separately: 60 calendar days from the denial date.

**What you should see:** A plan with both dates noted: 14 days for the peer-to-peer, 60 days for the appeal.

## Things to know
- A peer-to-peer is not an appeal. The appeal clock keeps running while you wait for or take part in a peer-to-peer.
- The peer-to-peer is between the ordering provider and a physician reviewer. Office staff can request it, but the clinical discussion is for the provider.
- The Service Desk cannot schedule, move or change a peer-to-peer, and cannot answer clinical-criteria questions.

## Common errors on this screen
- **"There's no Request peer-to-peer button"**: The denial code is not one for which a peer-to-peer is offered, or the 14-day window has passed. Consider an appeal instead (UI-10).
- **"We requested a peer-to-peer and missed the appeal deadline"**: The appeal clock does not stop for a peer-to-peer. File the appeal within 60 days of the denial regardless.
- **"Nobody has contacted us yet"**: Scheduling takes up to 2 business days. Check the **Messages** tab for the scheduled time before chasing.
- **"Can support tell us whether the peer-to-peer will overturn it?"**: No. Nobody can promise an outcome before the discussion.
