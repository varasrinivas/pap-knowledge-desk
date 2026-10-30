---
id: UI-03
title: Home dashboard and worklist filters
doc_type: ui
owner: Portal Product Team
audience: PROVIDER_NURSE, PROVIDER_OFFICE_MGR
screens: Home
role_required: PROVIDER_NURSE
permission: intake.view
version: 2.1
effective_date: 2026-04-15
last_reviewed: 2026-08-30
related: WF-01, POL-08
---
# Home dashboard and worklist filters

The **Home** screen is where you land after signing in. It shows your office's worklist of intake requests, and it is the fastest way to find a request that needs your attention, such as one that has been pended.

## Procedure: Find the requests that need action today
1. Sign in. The portal opens **Home**.
2. Open the **Status** filter and select `Pended (Info Requested)`.
3. Open the **Urgency** filter and select `URGENT` if you want to work urgent requests first.
4. Leave **Submitted by** empty to see the whole office, or choose your own name to see only your requests.
5. Set **Date range** to cover the period you care about, for example the last 30 days.
6. Click a row in the worklist to open the request detail.

**What you should see:** A shorter worklist showing only matching requests, each with its request number (`IR-YYYY-NNNNN`), status and urgency. Filters stay set until you change them.

## Procedure: Look up a specific request
1. On **Home**, click **Search**.
2. Type the intake request number (for example `IR-2026-00517`) or the prior-auth number (`PA-NNNNN`).
3. Press Enter and click the matching result.

**What you should see:** The **Request detail** screen for that request, opening on the **Summary** tab.

## Procedure: Start a new request from Home
1. On **Home**, click **New request**.
2. The **New Request wizard** opens at step **1 Member**. Continue with UI-04.

**What you should see:** Step 1 of the wizard. Nothing appears in the worklist until you save a draft.

## Reading the worklist
- Each row shows the request number, status, urgency, who submitted it and when.
- Your own drafts appear with status `Draft`. Drafts are never visible to reviewers until you submit them.
- A request in `Pended (Info Requested)` is waiting on your office; the review clock is paused until you respond (UI-08).

## Common errors on this screen
- **"My worklist is empty but I know we have requests"**: A filter is still set from an earlier session. Clear **Status**, **Urgency**, **Submitted by** and **Date range** and look again.
- **"I can't find a request my colleague submitted"**: **Submitted by** is set to your own name. Clear it to see the whole office's requests.
- **"Search finds nothing for the PA number"**: A `PA-NNNNN` number exists only once a request is approved. Search by the `IR-` number instead.
- **"The worklist shows an old status"**: The page was left open for a long time. Refresh it; if the problem persists after a long session, see UI-17.
