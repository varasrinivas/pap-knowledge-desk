---
id: WF-10
title: Account lockout and MFA reset workflow
doc_type: workflow
owner: Service Desk
audience: PROVIDER_NURSE, PROVIDER_OFFICE_MGR, UM_NURSE, REGIONAL_DIRECTOR
queues: Service Desk (category portal_access)
stages: n/a (account access)
version: 2.6
effective_date: 2026-07-01
last_reviewed: 2026-09-15
related: POL-17, UI-01, UI-02
---
# Account lockout and MFA reset workflow

## Summary
This workflow covers unlocking a portal account and resetting MFA after a phone change. An account locks after 5 failed sign-in attempts or an MFA mismatch. Unlocking is not self-service: the Service Desk unlocks within 2 business hours, 7am to 7pm Central, under ticket category `portal_access`. It ends when the user signs in successfully.

### Step 1: Recognise the lockout
- **Owner:** The user
- **Queue / system:** **Sign in** screen
- **Time limit:** None.
- **What happens:** After 5 failed attempts at **Password**, or a wrong code at **Enter the 6-digit code**, the account locks. Further attempts do not help and **Forgot password** does not unlock a locked account.
- **Exit:** The user contacts the Service Desk.

### Step 2: Raise the ticket
- **Owner:** The user, or a colleague on the user's behalf
- **Queue / system:** Help, **Contact support**; ServiceNow category `portal_access`, subcategory `login` or `mfa`
- **Time limit:** At once.
- **What happens:** The ticket names the user and says whether the cause was passwords, an MFA mismatch or a new phone. If the same user already has an open lockout ticket from the last 4 hours, the new report is added as a work note to that ticket instead.
- **Exit:** The ticket is in the Service Desk queue.

### Step 3: Verify identity
- **Owner:** Service Desk
- **Queue / system:** ServiceNow, portal user record
- **Time limit:** Inside the 2-business-hour target.
- **What happens:** The analyst confirms the caller is the account holder using the organisation's identity check. The analyst does not read out or share any other user's details.
- **Exit:** Identity confirmed.

### Step 4: Unlock or reset
- **Owner:** Service Desk
- **Queue / system:** Portal admin tools
- **Time limit:** Within 2 business hours of the ticket, 7am to 7pm Central.
- **What happens:** For a password lockout, the analyst unlocks the account. For a phone change, the analyst also resets MFA so a new authenticator can be enrolled. Tickets raised after 7pm Central are worked from 7am the next business day.
- **Exit:** The user is told the account is ready.

### Step 5: First sign-in after an MFA reset
- **Owner:** The user
- **Queue / system:** **Sign in**, **Enter the 6-digit code**
- **Time limit:** At the next sign-in.
- **What happens:** The first sign-in needs two codes: the code from the new authenticator *and* the one-time code emailed to the work address. Entering the code from the old phone causes an MFA mismatch and locks the account again.
- **Exit:** Successful sign-in; the ticket is resolved.

## Exceptions
- A user locked again after a reset usually entered the old authenticator code; the workflow restarts at Step 2 under the same ticket where it is still open.
- If the one-time email does not arrive, the user checks the work address only; codes are never sent to personal email.
- A lockout that blocks a whole office from submitting may be raised as P2 (single office blocked).
- Many lockouts at once in one region may indicate an outage; the Service Desk checks for an open P1 before treating them separately (WF-12).
- The assistant cannot unlock accounts; it raises the ticket and explains the steps.

## What the provider office sees
The **Sign in** screen shows **Email**, **Password**, **Sign in** and **Forgot password**, then **Enter the 6-digit code**. After an MFA reset the user also receives the emailed one-time code. Ticket progress is visible under Help, **Your tickets**.
