---
id: UI-05
title: Adding attachments
doc_type: ui
owner: Portal Product Team
audience: PROVIDER_NURSE, PROVIDER_OFFICE_MGR
screens: Request detail, Documents tab
role_required: PROVIDER_NURSE
permission: intake.attach
version: 4.1
effective_date: 2026-06-15
last_reviewed: 2026-08-30
related: POL-09, WF-04
---
# Adding attachments

Use this when you need to add clinical notes, imaging reports or other documents to a request, either while creating it or after it has been submitted. All documents go through the **Documents** tab; never email documents.

## Procedure: Upload clinical notes to a request
1. Open the request from the worklist on **Home**. The **Request detail** screen opens.
2. Click the **Documents** tab.
3. Click **Upload files**.
4. Choose one or more files. Accepted types are PDF, JPG, PNG, TIFF and DOCX. ZIP files are not accepted.
5. Check each file is no larger than **20 MB**. You can add up to 20 files per request.
6. Confirm the upload and watch the progress bar until it completes.
7. Find your file in the file list. It shows **Uploaded by**, **Size** and **Status**.

**What you should see:** Your file in the list with **Status** `Scanning`, changing to `Available` within 2 minutes. Only `Available` files can be seen by the reviewer.

## Procedure: Check that an upload arrived
1. Open the request and click the **Documents** tab.
2. Find the file by name and check **Uploaded by** shows your name.
3. Read the **Status** column:
   - `Scanning`: the file is being checked. Wait.
   - `Available`: the file is attached and visible to the reviewer.
   - `Rejected`: the file was not accepted. Fix it and upload again.
4. If the file is not in the list at all after 10 minutes, upload it again with **Upload files**.

**What you should see:** Every file you uploaded marked `Available`.

## Before you upload
- Clinical notes must be legible, signed and dated by the ordering provider, and dated within 60 days of submission.
- Name files plainly (for example "clinical-notes-ortho-consult.pdf"). Do not put member details in file names.
- Scan pages straight and at a readable resolution; an illegible document is pended with PI-DOC-012.

## Common errors on this screen
- **"My file says Rejected"**: The file type is not accepted (for example a ZIP) or it is over the **20 MB** limit. Convert it to PDF, split it into smaller files if needed, and upload again.
- **"I uploaded it but it's not on the Documents tab"**: Attachments appear within 2 minutes. If it is still missing after 10 minutes, re-upload it.
- **"The progress bar stopped part-way"**: The connection dropped during the upload. Refresh the page, check the file list, and upload the file again if it is not listed.
- **"Can I just email the notes to the reviewer?"**: No. Never email documents; only files on the **Documents** tab are part of the request.
- **"The reviewer says they can't see my notes"**: The file may still show `Scanning`. Wait until it shows `Available`; if it is not listed after 10 minutes, re-upload it.
