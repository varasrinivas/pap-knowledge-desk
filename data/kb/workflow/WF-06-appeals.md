---
id: WF-06
title: Appeals workflow
doc_type: workflow
owner: Appeals Unit
audience: PROVIDER_NURSE, PROVIDER_OFFICE_MGR, UM_NURSE, REGIONAL_DIRECTOR
queues: Appeals Unit
stages: Denied
version: 2.1
effective_date: 2026-07-01
last_reviewed: 2026-09-15
related: POL-10, POL-11, UI-09
---
# Appeals workflow

## Summary
This workflow describes how a denied request is appealed. It starts when someone presses **Appeal this decision** on the Decision tab within 60 calendar days of the denial date, and ends with an appeal decision from an independent reviewer: within 30 days for a standard appeal or 72 hours for an expedited one. Appeals are handled by the Appeals Unit, never by a ticket.

### Step 1: Confirm the denial can be appealed
- **Owner:** PROVIDER_NURSE, PROVIDER_OFFICE_MGR or the member
- **Queue / system:** **Decision** tab, decision letter
- **Time limit:** 60 calendar days from the denial date.
- **What happens:** The filer checks the denial code. Most codes are appealable. CR-ND-006 (duplicate), CR-ND-007 (member not eligible) and CR-ND-010 (pend not answered) are not; each has its own next step instead.
- **Exit:** The code is appealable and the 60 days have not passed.

### Step 2: File the appeal
- **Owner:** The ordering provider, the provider office on the member's behalf, or the member (permission `appeal.create` for office users)
- **Queue / system:** **Appeal this decision**
- **Time limit:** Before day 60.
- **What happens:** The filer states why the decision should change and attaches supporting documents, for example the conservative-therapy history behind a CR-ND-001 denial. The filer chooses standard or expedited. Expedited is for cases where the standard appeal time could seriously jeopardise the member's life, health or ability to regain maximum function.
- **Exit:** The appeal is submitted and acknowledged.

### Step 3: Intake by the Appeals Unit
- **Owner:** Appeals Unit
- **Queue / system:** Appeals Unit work list
- **Time limit:** The appeal clock starts on receipt.
- **What happens:** The Appeals Unit confirms the appeal is complete and in time, and assembles the original request, the decision and the new material. Coverage appeals (CR-ND-003) follow the same path with a plan-coverage reviewer.
- **Exit:** The case is assigned to a reviewer.

### Step 4: Independent review
- **Owner:** Independent reviewer appointed by the Appeals Unit
- **Queue / system:** Appeals Unit
- **Time limit:** 30 days standard; 72 hours expedited.
- **What happens:** A clinician who took no part in the original decision reviews the whole record afresh. The original UM nurse and Medical Director do not decide the appeal.
- **Exit:** The decision is upheld or overturned.

### Step 5: Communicate the outcome
- **Owner:** Appeals Unit
- **Queue / system:** **Decision** tab, decision letter
- **Time limit:** At the decision.
- **What happens:** An appeal letter is issued and available from **Download letter**. An overturned denial becomes an approval with a PA number.
- **Exit:** The appeal is closed.

## Exceptions
- A peer-to-peer (WF-07) is not an appeal; the 60-day appeal clock keeps running while a peer-to-peer is requested or held.
- Appeals filed after 60 calendar days are not accepted; the office may submit a new request if circumstances have changed.
- The Service Desk cannot file, expedite or change an appeal; questions about an appeal's progress go to the Appeals Unit.
- Retro requests denied with CR-ND-008 (outside the 14-day window) are appealable through this same workflow.
- Questions about the clinical criteria behind a denial go to the Clinical Policy Desk.

## What the provider office sees
The **Decision** tab shows the denial code, **Download letter** and **Appeal this decision**. After filing, the **Timeline** tab shows the appeal and its type, and the outcome letter appears on the **Decision** tab. Users who chose **Decided** under **Email me when** are notified when the appeal is decided.
