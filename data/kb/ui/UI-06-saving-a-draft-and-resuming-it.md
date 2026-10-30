---
id: UI-06
title: Saving a draft and resuming it
doc_type: ui
owner: Portal Product Team
audience: PROVIDER_NURSE, PROVIDER_OFFICE_MGR
screens: New Request wizard, Home
role_required: PROVIDER_NURSE
permission: intake.create
version: 2.0
effective_date: 2026-03-01
last_reviewed: 2026-08-30
related: WF-01, POL-09
---
# Saving a draft and resuming it

Use this when you cannot finish a new request in one sitting, for example while you wait for signed clinical notes. A draft keeps everything you have entered so far, and nothing in it is reviewed until you submit.

## Procedure: Save a request part-way through the wizard
1. In the **New Request wizard**, complete as many steps as you can.
2. On the step you are on, click **Save draft**.
3. Note the request number (`IR-YYYY-NNNNN`) shown in the confirmation.
4. Close the wizard or go back to **Home**.

**What you should see:** The request in the worklist on **Home** with status `Draft`. A draft is never visible to reviewers, and the review clock has not started.

## Procedure: Find and resume a draft
1. On **Home**, open the **Status** filter and select `Draft`.
2. Optionally set **Submitted by** to your own name to see only your drafts.
3. Click the draft in the worklist. The **New Request wizard** reopens at the step where you saved.
4. Use **Back** and **Next** to review earlier steps; your entries are kept.
5. Complete the remaining steps, through **6 Review & Submit**.
6. Click **Submit**, or click **Save draft** again if you still need to stop.

**What you should see:** After **Submit**, the status changes from `Draft` to `Submitted` and the review clock starts.

## Procedure: Hand a draft to a colleague to submit
1. Save the draft as above and tell your colleague the `IR-` number.
2. Your colleague opens **Home**, sets **Status** to `Draft` and clears **Submitted by**.
3. Your colleague opens the draft, checks **6 Review & Submit** and clicks **Submit**.

**What you should see:** The request moves to `Submitted`. The colleague must have permission to submit for the office.

## Things to know about drafts
- Saving a draft is not submitting. Until you click **Submit**, nobody at Northwind can see or review the request.
- Clinical notes must still be within 60 days of submission, not of when you started the draft. Check note dates before you submit an old draft.

## Common errors on this screen
- **"I saved it days ago and nothing has happened"**: A draft is not reviewed. Open it and click **Submit**.
- **"I can only see Save draft, there's no Submit"**: You do not currently have permission to submit for the office, often because a delegation lapsed. Ask your office manager to renew it (UI-12).
- **"My draft isn't in the worklist"**: The **Status** or **Date range** filter is hiding it. Set **Status** to `Draft` and widen **Date range**.
- **"The draft was pended for old notes after I submitted it"**: The notes were older than 60 days by the time you submitted. Upload current notes through **Respond to Pend** (UI-08).
