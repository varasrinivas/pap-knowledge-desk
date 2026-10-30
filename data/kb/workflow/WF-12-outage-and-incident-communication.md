---
id: WF-12
title: Outage and incident communication
doc_type: workflow
owner: Service Desk
audience: PROVIDER_NURSE, PROVIDER_OFFICE_MGR, UM_NURSE, REGIONAL_DIRECTOR
queues: Service Desk, Platform Engineering
stages: New, In Progress, Resolved, Closed
version: 2.0
effective_date: 2026-07-01
last_reviewed: 2026-09-15
related: POL-18, POL-20, UI-16, UI-18
---
# Outage and incident communication

## Summary
This workflow covers how a portal outage is declared, linked and communicated. It starts when reports point to an outage affecting a region, which is a P1 major incident, and ends when the incident is resolved and users are told. Every related report is linked with `parent_incident`, and users are given the incident number, the workaround and an update every 60 minutes.

### Step 1: Recognise the pattern
- **Owner:** Service Desk
- **Queue / system:** ServiceNow
- **Time limit:** As soon as reports cluster.
- **What happens:** Several reports in one category from the same region within a short time suggest an outage rather than separate problems. The analyst checks for an open P1 or P2 on the same issue before creating anything new. Portal features at risk include sign-in, uploads, routing and intake channels such as fax intake.
- **Exit:** No open major incident exists, and the issue affects a region.

### Step 2: Declare the major incident
- **Owner:** Service Desk, with Platform Engineering
- **Queue / system:** ServiceNow incident, priority P1
- **Time limit:** At once.
- **What happens:** The analyst raises a P1 incident, names the affected region and feature, and assigns it to Platform Engineering. The first public update states what is affected, what is not, and the workaround if one exists.
- **Exit:** The P1 is open and In Progress.

### Step 3: Link related reports
- **Owner:** Service Desk
- **Queue / system:** `parent_incident` field
- **Time limit:** For every new report until resolution.
- **What happens:** Existing tickets on the same issue are linked to the P1 as children using `parent_incident`. New reports are treated as duplicates of the open P1 and recorded as work notes, so one ticket holds the history.
- **Exit:** All related reports point to the parent.

### Step 4: Post the banner
- **Owner:** Platform Engineering
- **Queue / system:** Portal status banner
- **Time limit:** Within the first update cycle.
- **What happens:** A banner on the portal names the affected feature and region, the incident number and the workaround. The banner is updated with each public update and removed at resolution.
- **Exit:** The banner is live.

### Step 5: Update every 60 minutes
- **Owner:** Service Desk
- **Queue / system:** ServiceNow public updates
- **Time limit:** Every 60 minutes while the P1 is open.
- **What happens:** Each update states the current position and the next update time, even if nothing has changed. Users who report the outage are told the incident number, the workaround and that updates come every 60 minutes. The desk does not promise a fix time it does not control.
- **Exit:** Platform Engineering confirms a fix.

### Step 6: Resolve and close
- **Owner:** Service Desk and Platform Engineering
- **Queue / system:** ServiceNow
- **Time limit:** After the fix is confirmed.
- **What happens:** A final update explains what happened and whether anything needs action from users. Child incidents are resolved with the parent, and the banner is removed.
- **Exit:** The P1 and its children are Closed.

## Exceptions
- A problem that blocks one office rather than a region is a P2, not a major incident; it is still linked if it turns out to share a cause.
- A P2 affecting many users, such as uploads failing, follows the same linking and workaround steps, but the 60-minute cadence is required only for P1.
- An outage that delays review decisions does not change any decision clock or decision; questions about specific requests go to the reviewing region.
- The assistant tells users about the open incident and its workaround, and never closes or merges tickets.

## What the provider office sees
The office sees the status banner on the portal with the incident number and workaround. Under Help, **Your tickets** shows the office's own report linked to the parent incident with its latest update. If **New request** or **Upload files** is named as the workaround, the office continues there.
