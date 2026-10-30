---
id: WF-07
title: Peer-to-peer scheduling workflow
doc_type: workflow
owner: Utilization Management Operations
audience: PROVIDER_NURSE, PROVIDER_OFFICE_MGR, UM_NURSE, REGIONAL_DIRECTOR
queues: Medical Directors
stages: Denied
version: 1.5
effective_date: 2026-07-01
last_reviewed: 2026-09-15
related: POL-11, POL-13, UI-09
---
# Peer-to-peer scheduling workflow

## Summary
This workflow covers a peer-to-peer conversation that a provider office requests after a denial. It applies only to denials CR-ND-004 (medical necessity not met) and CR-ND-009 (site of care not approved). It starts when the office presses **Request peer-to-peer** within 14 calendar days of the denial and ends when the outcome is recorded on the request.

### Step 1: Check eligibility
- **Owner:** PROVIDER_NURSE or PROVIDER_OFFICE_MGR
- **Queue / system:** **Decision** tab
- **Time limit:** 14 calendar days from the denial date.
- **What happens:** The office confirms the denial code is CR-ND-004 or CR-ND-009. The **Request peer-to-peer** button appears only for those codes. For every other code a peer-to-peer is not offered, and the route is an appeal or the code's own next step.
- **Exit:** The button is shown and the 14 days have not passed.

### Step 2: Request
- **Owner:** PROVIDER_NURSE (permission `p2p.request`)
- **Queue / system:** **Request peer-to-peer**
- **Time limit:** Before day 14.
- **What happens:** The office names the ordering provider who will take part and gives the times that provider is available. The request is logged on the **Timeline** tab.
- **Exit:** The request reaches the Medical Directors.

### Step 3: Schedule
- **Owner:** Medical Directors
- **Queue / system:** Medical Directors scheduling list
- **Time limit:** Scheduled within 2 business days of the request.
- **What happens:** A Medical Director is assigned and a time is agreed from the availability given. The confirmed date and time are sent to the office through the **Messages** tab.
- **Exit:** A confirmed appointment.

### Step 4: Hold the conversation
- **Owner:** Ordering provider and the assigned Medical Director
- **Queue / system:** Telephone or video, as confirmed
- **Time limit:** At the scheduled time.
- **What happens:** The ordering provider explains the clinical picture and the Medical Director explains the basis for the denial. For CR-ND-009, the discussion is about the requested site of care against the approved alternative.
- **Exit:** The conversation ends with an outcome.

### Step 5: Record the outcome
- **Owner:** Medical Directors
- **Queue / system:** Request detail, **Decision** tab
- **Time limit:** At the end of the conversation.
- **What happens:** The Medical Director records one of two outcomes: the denial is reversed and the request is approved with a PA number, or the denial stands. Either way the outcome is noted on the **Timeline** tab and a letter is available on the **Decision** tab.
- **Exit:** Outcome recorded; the workflow ends.

## Exceptions
- A peer-to-peer is not an appeal. The 60-day appeal clock keeps running from the original denial date, so an office that may appeal should not wait for the peer-to-peer to finish before preparing it.
- A request made after 14 calendar days is not accepted; the office can still appeal within 60 days (WF-06).
- If the ordering provider cannot attend the confirmed time, the office asks to reschedule through **Messages**; rescheduling does not extend the appeal deadline.
- The Service Desk cannot schedule, expedite or change a peer-to-peer; it can only explain this workflow.
- Questions about the medical-necessity criteria themselves go to the Clinical Policy Desk.

## What the provider office sees
On the **Decision** tab the office sees **Download letter**, **Appeal this decision** and, for CR-ND-004 and CR-ND-009 only, **Request peer-to-peer**. The confirmed time arrives on the **Messages** tab, and users who chose **Message received** under **Email me when** are notified. The outcome appears on the **Timeline** and **Decision** tabs.
