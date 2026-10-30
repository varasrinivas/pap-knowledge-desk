---
id: UI-10
title: Starting an appeal from the decision screen
doc_type: ui
owner: Portal Product Team
audience: PROVIDER_NURSE, PROVIDER_OFFICE_MGR
screens: Request detail, Decision tab
role_required: PROVIDER_NURSE
permission: appeal.create
version: 3.1
effective_date: 2026-05-01
last_reviewed: 2026-08-30
related: POL-12, POL-11, WF-06
---
# Starting an appeal from the decision screen

Use this when a request has been denied and you want Northwind to reconsider it. Appeals are filed from the **Decision** tab within **60 calendar days** of the denial date. An appeal is handled by the Appeals Unit; it is not a support ticket.

## Procedure: File an appeal on a denied request
1. Open the denied request and click the **Decision** tab.
2. Check the denial date and the reason code (`CR-ND-`). You have 60 calendar days from the denial date.
3. Click **Appeal this decision**.
4. Choose who is filing: the ordering provider, or the provider office on the member's behalf.
5. Choose standard or expedited. Expedited is for cases where the standard appeal time could seriously jeopardise the member's health.
6. Write the reason for the appeal and attach the supporting documents with **Upload files**.
7. Review the appeal and submit it.

**What you should see:** A confirmation, and an appeal entry on the **Timeline** tab. A standard appeal is decided within 30 days; an expedited appeal within 72 hours.

## Procedure: Check whether a denial can be appealed
1. On the **Decision** tab, read the reason code.
2. Look it up in POL-11:
   - Most codes, such as `CR-ND-001`, `CR-ND-002`, `CR-ND-004` and `CR-ND-005`, can be appealed.
   - `CR-ND-006` (duplicate) cannot; use the existing prior-auth number.
   - `CR-ND-007` (member not eligible) cannot; verify eligibility instead.
   - `CR-ND-010` (pend not answered) cannot; submit a new request.
3. If the code cannot be appealed, **Appeal this decision** does not apply; follow the action POL-11 gives.

**What you should see:** A clear next step for the denial: an appeal, a new request, or using an existing authorization.

## Things to know
- A peer-to-peer (UI-11) is not an appeal. If you request one, the 60-day appeal clock keeps running.
- The member can also file an appeal themselves.
- The Service Desk cannot file, expedite or change an appeal. Questions about an appeal in progress go to the Appeals Unit.

## Common errors on this screen
- **"Appeal this decision is missing"**: The request is not denied, or the 60-day window has passed. Check the status and the denial date.
- **"We did a peer-to-peer, so we thought the appeal deadline was paused"**: It was not. The appeal clock runs from the denial date regardless of a peer-to-peer.
- **"Can support speed up our appeal?"**: No. The Service Desk cannot expedite an appeal; choose expedited when you file, if it applies.
- **"Can we appeal a CR-ND-010 denial?"**: No. The pend was not answered in 14 days; submit a new request with the documents included.
