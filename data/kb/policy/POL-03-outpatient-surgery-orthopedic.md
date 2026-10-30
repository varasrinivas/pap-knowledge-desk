---
id: POL-03
title: Outpatient surgery and orthopedic procedures
doc_type: policy
owner: Utilization Management Operations
audience: PROVIDER_NURSE, PROVIDER_OFFICE_MGR, UM_NURSE
service_types: ORTHO_SURGERY, PHYSICAL_THERAPY
version: 2.4
effective_date: 2026-07-01
last_reviewed: 2026-09-12
related: WF-01, WF-03, WF-07, UI-04, UI-11
---
# Outpatient surgery and orthopedic procedures

This policy covers the documentation an office submits for outpatient surgery and orthopedic procedures under the ORTHO_SURGERY service type, and the site-of-care rule. It also notes how physical therapy history supports a surgical request. Clinical criteria questions go to the Clinical Policy Desk.

## What documents does an orthopedic surgery request need?
An ORTHO_SURGERY request needs the surgeon's clinical notes signed and dated within 60 days of submission, the report of the imaging that supports the procedure, and the member's conservative-therapy history. The request must name the procedure, the planned date of service and the site where it will be performed. Missing notes are pended with PI-DOC-001, a missing imaging report with PI-DOC-003 and a missing therapy history with PI-DOC-004. An unsigned order is pended with PI-DOC-005.

## What counts as conservative therapy before orthopedic surgery?
For an orthopedic surgery request, conservative therapy means the non-surgical treatment the member tried first, such as physical therapy, medication, injections or bracing. For each therapy, list the type, dates, duration and outcome. Physical therapy records from a PHYSICAL_THERAPY authorization can be uploaded as part of this history. A request decided without the history is denied with CR-ND-001, which is appealable.

## What is the site-of-care rule?
The site-of-care rule means Northwind reviews where a procedure is performed as well as whether it is authorized. A procedure that can be done safely in an ambulatory surgery center or office setting may not be approved at a hospital outpatient department. When the requested site is not approved but another site is, the decision is denied with CR-ND-009, "Requested site of care not approved (an alternative site is approved)". The decision letter names the approved alternative site.

## What can an office do after a CR-ND-009 site-of-care denial?
After a CR-ND-009 denial, the office has three options. It can schedule the procedure at the approved alternative site named in the decision letter. It can request a peer-to-peer within 14 calendar days of the denial, using **Request peer-to-peer** on the Decision tab. Or it can file an appeal within 60 calendar days of the denial, using **Appeal this decision**. A peer-to-peer is not an appeal, and the appeal clock keeps running during it.

## How should multiple procedures be entered?
When one surgery includes more than one procedure, enter each procedure as a separate service line on step **2 Service** of the wizard, with its own units. Use one planned date of service for procedures done in the same session. Unclear units or dates lead to a pend with PI-DOC-006, and a diagnosis code that does not match a procedure leads to a pend with PI-DOC-007.
