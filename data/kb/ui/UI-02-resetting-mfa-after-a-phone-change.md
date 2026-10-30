---
id: UI-02
title: Resetting MFA after a phone change
doc_type: ui
owner: Portal Product Team
audience: PROVIDER_NURSE, PROVIDER_OFFICE_MGR, UM_NURSE, REGIONAL_DIRECTOR
screens: Sign in, Help
role_required: PROVIDER_NURSE
permission: intake.view
version: 2.4
effective_date: 2026-06-01
last_reviewed: 2026-08-30
related: WF-10, WF-09, POL-19
---
# Resetting MFA after a phone change

Use this when you have a new phone, or have reinstalled your authenticator app, and need to sign in to the portal. The first sign-in after a phone change needs two codes, and using your old code will lock the account.

## Procedure: Sign in for the first time on a new phone
1. Install the authenticator app on the new phone and add the Northwind portal account using the re-enrolment link sent to your work address.
2. On the **Sign in** screen, enter your **Email** and **Password**, then click **Sign in**.
3. At **Enter the 6-digit code**, type the code from the authenticator app on the **new** phone.
4. The portal then asks for a one-time code. Open your work email and find the message with the one-time code.
5. Type the emailed one-time code and confirm.
6. The portal opens **Home**. From now on, only the new phone's code is needed.

**What you should see:** The **Home** worklist. If you are asked for the emailed code again on your next sign-in, the first attempt did not complete; repeat steps 2 to 5.

Do not type a code from your old phone or an old authenticator entry at any point. An old code is an MFA mismatch, and an MFA mismatch locks the account.

## Procedure: Get help when your account is locked
Lockouts are **not self-service**. There is no unlock button in the portal, and **Forgot password** does not unlock a locked account.
1. Stop trying to sign in. More attempts do not help.
2. Open **Help** from the link on the **Sign in** screen and click **Contact support**. This opens the support assistant.
3. Tell the assistant your account is locked after a phone change. Give your name, your work email and your office; do not include any member information.
4. Note the incident number (`INC00NNNNN`) the assistant gives you.
5. Wait for the Service Desk to unlock the account. Unlocks are done within 2 business hours, 7am–7pm Central.
6. When you are told the account is unlocked, sign in using the new-phone procedure above, with the new code and the emailed one-time code.

**What you should see:** A confirmation from the Service Desk on your ticket, then a normal sign-in ending on **Home**.

## Common errors on this screen
- **"It locked me out right after I got my new phone"**: You typed a code from the old phone or the old app entry, which is an MFA mismatch. Use **Help** > **Contact support** to have it unlocked, then sign in with the new code and the emailed one-time code.
- **"I typed the new code and it asked for another code"**: That is expected. The first sign-in after a phone change also needs the one-time code emailed to your work address.
- **"The one-time code never arrived"**: It goes only to the work address on your account, not a personal address. Check your junk folder before asking for a new one.
- **"Can't I just unlock it myself?"**: No. Lockouts are not self-service; only the Service Desk can unlock an account (UI-18 explains how to follow up on the ticket).
