---
id: UI-08
title: Responding to a pend
doc_type: ui
owner: Portal Product Team
audience: PROVIDER_NURSE, PROVIDER_OFFICE_MGR
screens: Request detail, Summary tab, Documents tab
role_required: PROVIDER_NURSE
permission: intake.respond_pend
version: 3.3
effective_date: 2026-06-01
last_reviewed: 2026-08-30
related: POL-10, POL-09, WF-04
---
# Responding to a pend

Use this when a request shows `Pended (Info Requested)`. The reviewer needs something specific, named by a pend code, and the review clock is paused until you respond. You have 14 calendar days.

## Procedure: Find out what the reviewer needs
1. On **Home**, set the **Status** filter to `Pended (Info Requested)` and open the request.
2. On the **Summary** tab, read the pend code (for example `PI-DOC-003`) and its description.
3. Note the date the request was pended. The response is due within 14 calendar days of that date.
4. Gather exactly what the code names. Common codes:
   - `PI-DOC-001`: clinical notes missing.
   - `PI-DOC-002`: clinical notes older than 60 days.
   - `PI-DOC-003`: imaging report missing.
   - `PI-DOC-004`: conservative-therapy history (type, dates, duration, outcome).
   - `PI-DOC-005`: ordering-provider signature missing.
   - `PI-DOC-012`: illegible document.

**What you should see:** One pend code and its meaning on the **Summary** tab. POL-10 lists all twelve codes.

## Procedure: Send the missing information through Respond to Pend
1. Open the request and click **Respond to Pend**. The panel opens with the pend code shown at the top.
2. Click **Upload files** in the panel and add the document the code asks for (accepted types: PDF, JPG, PNG, TIFF, DOCX).
3. Wait for the progress bar to finish.
4. Add a short note saying what you uploaded, for example "Imaging report attached." Do not add member details beyond what the reviewer needs.
5. Click to submit your response.
6. Open the **Documents** tab and check the new file shows `Available`.

**What you should see:** The status returns to `Pending Clinical Review`, and the **Timeline** shows your response. The review clock resumes.

## Common errors on this screen
- **"There's no Respond to Pend button"**: The button only appears while the status is `Pended (Info Requested)`. If the request is already back in review or decided, there is nothing to respond to.
- **"We uploaded on the Documents tab but it's still pended"**: Uploading alone does not answer the pend. Click **Respond to Pend** and submit the response from the panel.
- **"It was pended again for the same code"**: The upload did not clear it, for example notes that are still over 60 days old or unsigned. Upload what the code names exactly.
- **"The request went to Withdrawn"**: The pend had no response within 14 calendar days. Submit a new request with the missing documents included.
- **"Can I email the documents instead?"**: No. Never email documents; respond only through the portal.
