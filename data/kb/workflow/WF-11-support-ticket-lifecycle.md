---
id: WF-11
title: Support ticket lifecycle
doc_type: workflow
owner: Service Desk
audience: PROVIDER_NURSE, PROVIDER_OFFICE_MGR, UM_NURSE, REGIONAL_DIRECTOR
queues: Service Desk, Platform Engineering
stages: New, In Progress, On Hold, Resolved, Closed
version: 3.0
effective_date: 2026-07-01
last_reviewed: 2026-09-15
related: POL-18, POL-19, UI-17, UI-18
---
# Support ticket lifecycle

## Summary
This workflow describes how a Service Desk incident (`INC00NNNNN`) moves from New to Closed. It covers categorisation, priority (impact × urgency, P1 to P4), the duplicate check, work notes and how users follow up. It starts when a user contacts support and ends when the ticket is closed with a close code.

### Step 1: New
- **Owner:** Service Desk, or the assistant when it raises a ticket
- **Queue / system:** ServiceNow incident
- **Time limit:** Categorised on arrival.
- **What happens:** The ticket gets a category (`portal_access`, `portal_defect`, `data_issue`, `performance` or `other`) and a subcategory such as `login`, `upload`, `routing` or `how_to`. Only fictional identifiers such as IR and PA numbers are recorded; no member details are entered.
- **Exit:** Categorised.

### Step 2: Duplicate check
- **Owner:** Service Desk
- **Queue / system:** ServiceNow
- **Time limit:** Before work starts.
- **What happens:** A report is a duplicate if it has the same category and the same region or user as a ticket from the last 4 hours, or if an open P1 or P2 covers the same issue. The oldest open match wins: the new report becomes a work note on that ticket instead of a new ticket, and the user is given its number.
- **Exit:** A new ticket proceeds, or the report is attached to the existing one.

### Step 3: Set priority
- **Owner:** Service Desk
- **Queue / system:** ServiceNow impact and urgency fields
- **Time limit:** At triage.
- **What happens:** Priority is impact × urgency. P1 is an outage affecting a region. P2 is a single office blocked, or a review SLA at risk. P3 and P4 cover narrower problems and questions, such as one user with a working alternative.
- **Exit:** Priority set.

### Step 4: In Progress
- **Owner:** Devika Menon's Service Desk queue, or Platform Engineering for defects
- **Queue / system:** ServiceNow
- **Time limit:** By priority.
- **What happens:** The analyst works the issue and records every action as a work note: what was checked, what was found and what the user was told. Defects in the portal go to Platform Engineering.
- **Exit:** Resolved, or waiting on someone outside the desk.

### Step 5: On Hold
- **Owner:** Service Desk
- **Queue / system:** ServiceNow
- **Time limit:** Until the awaited input arrives.
- **What happens:** A ticket is placed On Hold when it waits on the user, a vendor or a change. The reason is recorded in a work note, and the ticket returns to In Progress when the input arrives.
- **Exit:** Back to In Progress.

### Step 6: Resolved and Closed
- **Owner:** Service Desk
- **Queue / system:** ServiceNow close codes
- **Time limit:** Resolved when fixed; Closed after the user confirms or the confirmation period passes.
- **What happens:** The analyst picks a close code, for example `Solved (Work Around)`, `Solved (Permanently)`, `Known Error` or `Duplicate`, and writes the resolution in plain words.
- **Exit:** Closed.

## Exceptions
- Clinical-criteria questions go to the Clinical Policy Desk and appeals go to the Appeals Unit; neither becomes a ticket.
- The assistant can raise tickets and add work notes, but never closes or merges them.
- A ticket whose issue becomes a regional outage is linked to the major incident with `parent_incident` (WF-12).
- Requests to change a review decision are declined; the desk cannot change, expedite or override decisions.

## What the provider office sees
Users raise tickets from Help, **Contact support**, and follow them under **Your tickets**, which shows the number, status and latest public update. To follow up, the user opens the existing ticket rather than raising a new one; a second report within 4 hours is attached to the first anyway.
