---
id: POL-20
title: Escalation and SLA breach policy
doc_type: policy
owner: Service Desk
audience: PROVIDER_NURSE, PROVIDER_OFFICE_MGR, UM_NURSE, REGIONAL_DIRECTOR, PLATFORM_ADMIN
service_types: ALL
version: 3.1
effective_date: 2026-07-01
last_reviewed: 2026-09-28
related: WF-05, WF-08, WF-11, WF-12, UI-14, UI-18
---
# Escalation and SLA breach policy

This policy sets out how the service desk prioritises support tickets, how a review at risk of breaching its SLA is escalated, how reports of a known outage are linked to a major incident, and how often users are updated.

## How is a ticket's priority set?
Ticket priority is impact multiplied by urgency, which gives P1 to P4.

| Priority | Meaning | Example |
|---|---|---|
| P1 | Outage affecting a region | No one in a region can sign in or submit |
| P2 | A single office blocked, or a review SLA at risk | An office cannot submit any request |
| P3 | One user impeded, with a workaround | One user's Excel export fails but CSV works |
| P4 | A question or minor issue | How to export a report |

The desk sets the priority; the caller describes the impact.

## What happens when a review is at risk of breaching its SLA?
A review SLA at risk is a P2. The review SLA is the 72-hour STANDARD or 24-hour URGENT decision turnaround, counted from Submitted and paused while pended. When a request is close to breaching, the desk opens a P2 ticket so the regional review team is aware. The desk cannot expedite or decide the request, and it does not promise a decision time. Regional directors see breached requests on the **Past SLA** tile of the Regional Dashboard.

## How are misrouted requests escalated?
A request sitting in the wrong review queue can be reassigned only by a REGIONAL_DIRECTOR using **Reassign queue**, or through a Service Desk ticket with category `other` and subcategory `routing`. If the misrouting puts the review SLA at risk, the ticket is a P2. A reassignment does not reset the SLA clock. Requests in `UNASSIGNED` are swept every 24 hours by the regional director.

## What happens when I report a known outage?
When an outage is already open as a major incident, a new report about the same issue is linked to it with a `parent_incident` instead of opening a separate investigation. A report with the same category and the same region or user within 4 hours, or matching an open P1 or P2 on the same issue, is a duplicate; the oldest open match receives a work note. The caller is told the major incident number and the update cadence.

## How often will I get updates?
For a P1, the service desk posts an update every 60 minutes until the incident is resolved, even when there is no new information. For P2 to P4 tickets, the caller is updated when the ticket's status changes and when it is resolved. Updates appear under **Help > Your tickets** and in email. The assistant does not promise a fix time it does not control.
