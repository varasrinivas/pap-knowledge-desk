---
id: UI-16
title: Notifications and email preferences
doc_type: ui
owner: Portal Product Team
audience: PROVIDER_NURSE, PROVIDER_OFFICE_MGR
screens: Notifications
role_required: PROVIDER_NURSE
permission: intake.view
version: 1.6
effective_date: 2026-03-15
last_reviewed: 2026-08-30
related: WF-04, POL-18
---
# Notifications and email preferences

Use this to choose which request events send an email to your work address. Turning on the **Pended** notification is the simplest way to avoid missing the 14-day window to respond to a pend.

## Procedure: Choose which events email you
1. Sign in and open **Notifications**.
2. Find **Email me when**.
3. Tick the events you want:
   - **Pended**: a request you submitted has moved to `Pended (Info Requested)`.
   - **Decided**: a request you submitted has been `Approved` or `Denied`.
   - **Message received**: a reviewer has posted on the **Messages** tab of one of your requests.
4. Untick any you do not want.
5. Save your preferences.

**What you should see:** A confirmation that your preferences are saved. Emails go only to the work address on your account.

## Procedure: Act on a notification email
1. Read the email. It names the event and the request number (`IR-YYYY-NNNNN`), but no member details.
2. Sign in to the portal directly; do not reply to the email.
3. On **Home**, click **Search** and enter the `IR-` number.
4. Go to the tab the event relates to: **Summary** and **Respond to Pend** for a pend, **Decision** for a decision, **Messages** for a message.

**What you should see:** The request with the change the email described.

## Things to know
- Notification emails never contain clinical details or attachments. Everything is read inside the portal.
- Do not reply to notification emails with documents. Never email documents; upload them on the **Documents** tab or through **Respond to Pend**.
- Your preferences apply to requests you submitted. To keep track of the whole office, use the worklist filters on **Home** (UI-03).

## Common errors on this screen
- **"We missed a pend and the request was withdrawn"**: The **Pended** notification was not turned on, or the email went to junk. Turn it on in **Email me when** and add the portal's sender to your safe list.
- **"I'm not getting any emails"**: Check that at least one box is ticked under **Email me when** and that the address on your account is your current work address.
- **"I'm getting emails for requests I didn't submit"**: You may be listed as the submitter on drafts a colleague finished. Check **Submitted by** on **Home**.
- **"I replied to the email with the notes"**: Replies are not read. Upload the notes in the portal through **Respond to Pend** (UI-08).
