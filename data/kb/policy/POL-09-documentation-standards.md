---
id: POL-09
title: Documentation standards
doc_type: policy
owner: Utilization Management Operations
audience: PROVIDER_NURSE, PROVIDER_OFFICE_MGR, UM_NURSE
service_types: ALL
version: 5.1
effective_date: 2026-07-01
last_reviewed: 2026-09-22
related: WF-04, UI-05, UI-08, UI-17
---
# Documentation standards

This policy sets the standards every document attached to a prior-authorization request must meet: legibility, signature, date, file type and size. It applies to all service types. Documents that do not meet these standards lead to a pend and pause the decision clock.

## What makes clinical notes acceptable?
Clinical notes attached to a prior-authorization request must be legible, signed by the ordering provider and dated. They must be dated within 60 days of submission. Notes older than 60 days are pended with PI-DOC-002. Notes without the ordering provider's signature are pended with PI-DOC-005. A scan that the reviewer cannot read is pended with PI-DOC-012. Typed notes with an electronic signature and date are acceptable.

## Which file types can be uploaded?
The portal accepts PDF, JPG, PNG, TIFF and DOCX files. ZIP files are not accepted, and neither are other compressed or archive formats. Scan multi-page documents into a single PDF where possible, so the reviewer sees the pages in order. Password-protected files cannot be opened by the reviewer and are treated as illegible. A file in an unsupported format shows the status `Rejected` on the **Documents** tab and must be uploaded again as PDF, JPG, PNG, TIFF or DOCX.

## What is the file size limit for attachments?
The file size limit is 25 MB per file, with up to 20 files per request. A file larger than 25 MB is rejected at upload; split it into smaller PDFs or scan at a lower resolution. If a request needs more than 20 files, combine related pages into one PDF. Each file appears on the **Documents** tab with **Uploaded by**, **Size** and **Status**.

## What if an uploaded document does not appear?
Uploaded attachments appear on the **Documents** tab within 2 minutes. A new file first shows the status `Scanning`, then `Available`. A file marked `Rejected` did not pass the checks and must be uploaded again in an accepted format. If a file is still missing after 10 minutes, re-upload it. Never email documents to Northwind or to the service desk; documents are accepted only through the portal.

## How should documents be named and organised?
Give each file a short descriptive name such as "clinical notes" or "MRI report", without the member's name or date of birth. Upload the documents that support the request on step **5 Documents** of the wizard, or through **Respond to Pend** when answering a pend. Upload only what the request needs; extra unrelated records slow the review and do not meet the minimum-necessary rule in POL-18.
