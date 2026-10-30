---
id: UI-04
title: Creating a new intake request
doc_type: ui
owner: Portal Product Team
audience: PROVIDER_NURSE, PROVIDER_OFFICE_MGR
screens: Home, New Request wizard
role_required: PROVIDER_NURSE
permission: intake.create
version: 5.0
effective_date: 2026-06-15
last_reviewed: 2026-08-30
related: POL-01, POL-08, POL-09, WF-01, WF-02
---
# Creating a new intake request

Use this when you need prior authorization for a service and are starting a new request. The **New Request wizard** has six steps; you can stop at any point with **Save draft**.

## Procedure: Enter the member, service and providers
1. On **Home**, click **New request**.
2. On **1 Member**, enter the member ID (pattern `NW-0000000`) and confirm the member's coverage is found. Click **Next**.
3. On **2 Service**, choose the service type (for example `IMAGING` or `CARDIOLOGY`), the service requested, the diagnosis code, the units and the dates of service. Click **Next**.
4. On **3 Providers**, enter the **Ordering provider** and the **Servicing provider**. The step takes one ordering provider and one servicing provider.
5. Check that the servicing provider's practice location is correct. The review region is taken from the servicing provider's practice location, not from your office.
6. Click **Next**. Use **Back** at any time to correct an earlier step.

**What you should see:** Step **4 Clinical**, with your entries kept. Nothing is sent to a reviewer yet.

## Procedure: Add clinical information and submit
1. On **4 Clinical**, summarise the clinical reason for the request, including any conservative therapy already tried (type, dates, duration, outcome). Click **Next**.
2. On **5 Documents**, add the clinical notes and reports the request needs (see UI-05). Notes must be signed, dated and within 60 days. Click **Next**.
3. On **6 Review & Submit**, read every section.
4. If waiting the standard time could seriously jeopardise the member's life, health or ability to regain maximum function, the treating clinician ticks **Urgent attestation**. Leave it unticked for a standard request.
5. Click **Submit**.

**What you should see:** A confirmation with the request number (`IR-YYYY-NNNNN`) and status `Submitted`. The review clock starts now: 72 hours for STANDARD, 24 hours for URGENT.

## Procedure: Stop part-way and come back later
1. On any step, click **Save draft**.
2. Continue later from the worklist on **Home** (see UI-06).

**What you should see:** The request listed on **Home** with status `Draft`.

## Common errors on this screen
- **"The Submit button isn't there on step 6"**: You do not currently have permission to submit for the office, usually because your delegation lapsed. **Save draft** still works; ask your office manager to renew the delegation (UI-12).
- **"Next is greyed out on step 1"**: The member ID was not found. Check the `NW-` number and try again.
- **"My request went to the wrong region"**: The region comes from the servicing provider's practice location. Check the location entered on **3 Providers**; see WF-08 for misrouted requests.
- **"I ticked Urgent attestation by mistake"**: Untick it before you click **Submit**. After submission, urgency cannot be changed from the wizard.
- **"It was pended straight away for missing notes"**: The notes were missing, unsigned or older than 60 days. Respond through **Respond to Pend** (UI-08).
