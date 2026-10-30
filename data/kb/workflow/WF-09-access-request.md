---
id: WF-09
title: Access request workflow
doc_type: workflow
owner: Service Desk
audience: PROVIDER_NURSE, PROVIDER_OFFICE_MGR, UM_NURSE, REGIONAL_DIRECTOR
queues: ServiceNow access catalog (sc_request), Service Desk
stages: n/a (access request)
version: 2.3
effective_date: 2026-07-01
last_reviewed: 2026-09-15
related: POL-14, POL-16, UI-13, UI-14
---
# Access request workflow

## Summary
This workflow covers changes to a user's portal access: role, region or approver group, plus office delegation of submit rights. Access changes go through the ServiceNow access catalog (`sc_request`), are approved by a manager or regional director, and are provisioned one business day after approval. Delegation is granted by a PROVIDER_OFFICE_MGR on My Office and expires after 180 days.

### Step 1: Identify what is needed
- **Owner:** The requesting user
- **Queue / system:** **My Access** (**Your role**, **Your regions**)
- **Time limit:** None.
- **What happens:** The user checks the current role and regions. A missing **Submit** button for a provider nurse is often a lapsed delegation rather than a role problem; the nurse can still **Save draft**. Delegation is handled in Step 5, not through the catalog.
- **Exit:** A role, region or approver-group change is needed.

### Step 2: Draft the catalog request
- **Owner:** The requesting user, or the assistant on the user's behalf
- **Queue / system:** **Request a change**, which opens the access catalog form (`sc_request`)
- **Time limit:** None.
- **What happens:** The request names the user, the change and the reason. When the assistant drafts it, the assistant shows the draft and asks the user to confirm before it is submitted.
- **Exit:** The request is submitted.

### Step 3: Approve
- **Owner:** The user's manager, or a REGIONAL_DIRECTOR (`access.request.approve`)
- **Queue / system:** ServiceNow approvals
- **Time limit:** Approvers act as soon as practical; provisioning time counts from approval.
- **What happens:** The approver confirms the change fits the user's job. A UM nurse's region change is approved by the director of the region being added.
- **Exit:** Approved or rejected.

### Step 4: Provision
- **Owner:** Service Desk
- **Queue / system:** `sc_request` fulfilment
- **Time limit:** One business day after approval.
- **What happens:** The change is applied and the request is closed with a note. The user signs out and back in to see the change on **My Access**.
- **Exit:** The new access is visible.

### Step 5: Office delegation
- **Owner:** PROVIDER_OFFICE_MGR (`delegation.manage`)
- **Queue / system:** **My Office > Delegation**, **Add delegate**, **Expires on**
- **Time limit:** Immediate on save; expires after 180 days.
- **What happens:** The office manager grants a nurse `intake.submit` on behalf of the office. The **Expires on** date shows when it lapses. When it lapses, the nurse loses **Submit** but keeps **Save draft**, and the manager renews it on the same screen.
- **Exit:** The nurse can submit for the office.

## Exceptions
- A lapsed delegation is not a defect and is not fixed by a catalog request; the office manager renews it.
- The Service Desk does not change roles without an approved `sc_request`.
- A user cannot approve a request for their own access.
- Region changes for UM nurses change which queues they see; requests already claimed stay with them.
- PLATFORM_ADMIN (`config.*`) access is granted only by Platform Engineering.

## What the provider office sees
Users see their access on **My Access** under **Your role** and **Your regions**, and start changes with **Request a change**. Office managers see **Users**, **Delegation**, **Add delegate** and **Expires on** on **My Office**. Open access requests are listed under Help, **Your tickets**.
