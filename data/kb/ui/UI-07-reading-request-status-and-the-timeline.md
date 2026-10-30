---
id: UI-07
title: Reading request status and the timeline
doc_type: ui
owner: Portal Product Team
audience: PROVIDER_NURSE, PROVIDER_OFFICE_MGR
screens: Request detail, Summary tab, Timeline tab
role_required: PROVIDER_NURSE
permission: intake.view
version: 3.0
effective_date: 2026-05-15
last_reviewed: 2026-08-30
related: WF-01, POL-08, POL-10
---
# Reading request status and the timeline

Use this when you want to know where a request is, whether the review clock is running, and what happens next. The **Summary** tab shows the current status; the **Timeline** tab shows every change with its date and time.

## Procedure: Check the current status of a request
1. On **Home**, click the request in the worklist, or use **Search** with the `IR-` number.
2. The **Request detail** screen opens on the **Summary** tab.
3. Read the status at the top of **Summary**.
4. Read the urgency (`STANDARD` or `URGENT`) and the review SLA shown next to it.
5. If the status is `Pended (Info Requested)`, note the pend code and go to UI-08.
6. If the status is `Approved` or `Denied`, open the **Decision** tab (UI-09).

**What you should see:** One of these statuses: `Draft`, `Submitted`, `Pending Clinical Review`, `Pended (Info Requested)`, `Approved`, `Denied` or `Withdrawn`.

## What each status means
- `Draft`: saved but not submitted. Reviewers cannot see it.
- `Submitted`: received. The review clock has started.
- `Pending Clinical Review`: a clinical reviewer is assessing the request. You do not need to do anything; the clock is running.
- `Pended (Info Requested)`: the reviewer needs something from your office, named by a pend code. The clock is paused.
- `Approved` / `Denied`: a decision has been made; the letter is on the **Decision** tab.
- `Withdrawn`: the request was withdrawn, or a pend was not answered within 14 calendar days.

## Procedure: Read the timeline and the SLA clock
1. Open the request and click the **Timeline** tab.
2. Read the entries from top to bottom. Each shows the date, time and event (submitted, pended, responded, decided).
3. Find the **Submitted** entry. The review clock starts here: 72 hours for STANDARD, 24 hours for URGENT.
4. Find any **Pended** entry and the response that followed it. The clock was paused between them and resumed on your response.

**What you should see:** A complete history of the request. After you respond to a pend, the timeline shows the status returning to `Pending Clinical Review`.

## Common errors on this screen
- **"It's been Pending Clinical Review for days, is it stuck?"**: Check the **Timeline**. Time spent in `Pended (Info Requested)` does not count toward the 72-hour or 24-hour clock, so the clock may have run for less time than the calendar suggests.
- **"The status changed to Withdrawn and we didn't withdraw it"**: A pend that gets no response within 14 calendar days closes as `Withdrawn`. Submit a new request.
- **"The status here doesn't match what the reviewer told us"**: Refresh the page. If it still differs, use **Help** > **Contact support** and quote the `IR-` number.
- **"Where are the reviewer's questions?"**: Pend details are on **Summary** and in the **Respond to Pend** panel; general notes are on the **Messages** tab.
