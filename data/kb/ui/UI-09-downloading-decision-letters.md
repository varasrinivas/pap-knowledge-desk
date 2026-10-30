---
id: UI-09
title: Downloading decision letters
doc_type: ui
owner: Portal Product Team
audience: PROVIDER_NURSE, PROVIDER_OFFICE_MGR
screens: Request detail, Decision tab
role_required: PROVIDER_NURSE
permission: decision.view
version: 2.2
effective_date: 2026-04-01
last_reviewed: 2026-08-30
related: POL-11, POL-18, WF-01
---
# Downloading decision letters

Use this when a request has been decided (`Approved` or `Denied`) and you need the decision letter for your records or to explain the outcome. Every decision has a letter on the **Decision** tab.

## Procedure: Download the letter for a decided request
1. On **Home**, set the **Status** filter to `Approved` or `Denied`, or use **Search** with the `IR-` number.
2. Open the request. The **Request detail** screen opens.
3. Click the **Decision** tab.
4. Read the decision summary: the outcome, the reason code and, for approvals, the prior-auth number (`PA-NNNNN`).
5. Click **Download letter**.
6. If your browser asks, allow the pop-up or download for the portal.
7. Save the PDF to your office's secure document store.

**What you should see:** A PDF letter that shows the decision, the reason code and the date. For an approval on auto-adjudication the code is `CR-AD-001`; denials show a `CR-ND-` code.

## Procedure: Read the reason code on a denial
1. On the **Decision** tab, find the code beginning `CR-ND-`.
2. Look the code up in POL-11, which explains each denial code and whether it can be appealed.
3. If the code can be appealed, use **Appeal this decision** (UI-10).
4. If **Request peer-to-peer** is shown, a peer-to-peer is available for this denial (UI-11).

**What you should see:** The decision letter and the **Decision** tab show the same code. If the code is `CR-ND-006` (duplicate), use the existing prior-auth number instead of appealing.

## Handling letters safely
- Decision letters contain member information. Store them only in your office's approved system.
- Do not email letters outside your organisation or paste their contents into tickets or chat. If you need help with a letter, quote the `IR-` number only.

## Common errors on this screen
- **"I click Download letter and nothing happens"**: Your browser's pop-up blocker stopped the letter. Allow pop-ups for the portal and click again (UI-17).
- **"There's no Decision tab content"**: The request has not been decided yet. Check the status on **Summary**; a letter only exists for `Approved` or `Denied` requests.
- **"The letter shows a different code from what we expected"**: The letter is the decision of record. Use POL-11 to read the code; the Service Desk cannot change a decision.
- **"The PDF opens blank"**: The download was interrupted. Clear site data and sign in again if the page has been open a long time, then download again (UI-17).
