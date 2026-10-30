---
id: UI-12
title: "Delegation: letting a nurse submit for the office"
doc_type: ui
owner: Portal Product Team
audience: PROVIDER_OFFICE_MGR, PROVIDER_NURSE
screens: My Office, Delegation
role_required: PROVIDER_OFFICE_MGR
permission: delegation.manage
version: 3.4
effective_date: 2026-06-01
last_reviewed: 2026-08-30
related: WF-09, POL-19
---
# Delegation: letting a nurse submit for the office

Use this if you are an office manager and a nurse needs to submit requests on behalf of the office. Delegation grants submit rights for a limited time; every delegation expires after at most **180 days** and must be renewed.

## Procedure: Add a delegate
1. Sign in and open **My Office**.
2. Click **Delegation**.
3. Click **Add delegate**.
4. Choose the nurse from the list of your office's **Users**.
5. Set **Expires on**. The latest date you can choose is 180 days from today.
6. Save the delegation.
7. Tell the nurse to sign out and sign in again.

**What you should see:** The nurse listed on **Delegation** with the **Expires on** date. After signing in again, the nurse sees **Submit** on step **6 Review & Submit** of the wizard.

## Procedure: Renew a delegation before it lapses
1. Open **My Office** > **Delegation**.
2. Sort or scan the list by **Expires on** to find delegations ending soon.
3. Open the nurse's delegation and set a new **Expires on** date, up to 180 days from today.
4. Save the change.

**What you should see:** The new **Expires on** date in the list. The nurse keeps **Submit** without interruption.

## Procedure: Check why a nurse lost the Submit button
1. Open **My Office** > **Delegation**.
2. Find the nurse. If they are missing, or **Expires on** is in the past, the delegation has lapsed.
3. Renew it with **Add delegate** (or a new **Expires on** date) as above.
4. Ask the nurse to sign out and sign in again.

**What you should see:** The nurse can submit again. Drafts they saved while the delegation was lapsed are still in the worklist, ready to submit.

## What a lapsed delegation looks like to the nurse
- The **Submit** button is missing on step **6 Review & Submit**.
- **Save draft** is still there, so the nurse can keep working but cannot send anything for review.
- Nothing else about their account changes. This is the most common cause of "the Submit button disappeared".

## Common errors on this screen
- **"A nurse says the Submit button disappeared"**: Their delegation lapsed after its **Expires on** date. Renew it on **My Office** > **Delegation**.
- **"I can't see My Office"**: Only office managers (PROVIDER_OFFICE_MGR) have **My Office**. Ask your office manager, or request a role change (UI-13).
- **"I can't set Expires on further out"**: Delegations are limited to 180 days. Set a reminder to renew before the date.
- **"I renewed it but the nurse still can't submit"**: The nurse's session started before the change. Ask them to sign out and sign in again.
