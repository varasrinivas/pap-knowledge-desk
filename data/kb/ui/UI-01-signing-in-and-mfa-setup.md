---
id: UI-01
title: Signing in and MFA setup
doc_type: ui
owner: Portal Product Team
audience: PROVIDER_NURSE, PROVIDER_OFFICE_MGR, UM_NURSE, REGIONAL_DIRECTOR
screens: Sign in, Home
role_required: PROVIDER_NURSE
permission: intake.view
version: 3.2
effective_date: 2026-05-01
last_reviewed: 2026-08-30
related: WF-09, WF-10, POL-19
---
# Signing in and MFA setup

Use this when you sign in to the Northwind Prior Auth Portal for the first time, or on any day you start work in the portal. Every account uses multi-factor authentication (MFA) with an authenticator app on your phone.

## Procedure: Sign in to the portal for the first time and set up MFA
1. Open the portal in a supported browser (current Chrome or Edge).
2. On the **Sign in** screen, type your work address in **Email** and the temporary password from your welcome email in **Password**.
3. Click **Sign in**. The portal asks you to choose a new password; enter it twice and confirm.
4. The portal shows a QR code. Open the authenticator app on your phone, add a new account and scan the code.
5. At **Enter the 6-digit code**, type the code the app is showing now and confirm before it refreshes.
6. The portal confirms MFA is set up and opens the **Home** screen.

**What you should see:** Your worklist on **Home**, with the **New request** and **Search** buttons at the top. If your worklist is empty on day one, that is normal.

## Procedure: Sign in on a normal working day
1. On the **Sign in** screen, enter your **Email** and **Password**.
2. Click **Sign in**.
3. At **Enter the 6-digit code**, open your authenticator app and type the current code for the Northwind portal.
4. Confirm. The portal opens **Home**.

**What you should see:** The **Home** worklist with your saved filters. Sessions end automatically after a period of inactivity, and you sign in again the same way.

## Procedure: Reset a forgotten password
1. On the **Sign in** screen, click **Forgot password**.
2. Enter your work **Email** and confirm.
3. Open the reset email sent to your work address and follow the link.
4. Choose a new password, then sign in as usual, including **Enter the 6-digit code**.

**What you should see:** The **Home** screen after the MFA prompt. Your MFA setup does not change when you reset your password.

## Common errors on this screen
- **"My code is always rejected"**: The phone's clock is out of sync, or you are typing a code that has just refreshed. Set the phone to automatic time and type the code as soon as it appears.
- **"I got a new phone and the code doesn't work"**: The authenticator on your new phone is not registered yet. Follow UI-02, Resetting MFA after a phone change; do not keep trying the old code.
- **"It says my account is locked"**: The account locks after 5 failed attempts or an MFA mismatch. Lockouts are not self-service; see UI-02 for how to get it unlocked.
- **"I never received the reset email"**: The reset email only goes to the work address on your account. Check your junk folder; if it is not there, use **Help** > **Contact support** (UI-18).
