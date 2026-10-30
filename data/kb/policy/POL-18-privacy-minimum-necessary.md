---
id: POL-18
title: Privacy and minimum-necessary (PHI)
doc_type: policy
owner: Privacy Office
audience: PROVIDER_NURSE, PROVIDER_OFFICE_MGR, UM_NURSE, REGIONAL_DIRECTOR, PLATFORM_ADMIN
service_types: ALL
version: 3.0
effective_date: 2026-07-01
last_reviewed: 2026-09-30
related: WF-11, UI-05, UI-18
---
# Privacy and minimum-necessary (PHI)

This policy sets out what protected health information (PHI) may appear in support conversations and tickets, and how it is redacted. The rule is minimum necessary: share only what is needed to solve the problem. Clinical documents belong in the portal, never in a ticket.

## What may I put in a support ticket?
A support ticket or a message to the assistant may contain the identifiers needed to find the problem: the intake request ID (for example `IR-2026-00517`), the PA number (for example `PA-10482`), the user's own portal user ID, the service type, the region, any pend or denial code, and a description of what happened on screen. These identifiers are enough for the service desk to look up the request. A screenshot is acceptable if it shows no member details.

## What must never go in a support ticket?
A support ticket must never contain the member's name, date of birth, address, phone number, diagnosis, diagnosis code with a description, clinical notes or test results. Refer to the patient only as "the member". Do not attach clinical documents to a ticket and never email them; clinical documents are uploaded only on the request's **Documents** tab. If you are unsure whether a detail is needed, leave it out and the desk will ask.

## What happens if PHI is included by mistake?
If a message to the assistant contains PHI, the assistant redacts it before anything leaves the organization's boundary. Member names, dates of birth and member IDs are replaced with stable placeholders such as "the member". The identifiers the portal needs, `IR-…`, `PA-…` and the user ID, are kept because they are not PHI on their own. If a ticket already contains PHI, the service desk removes it from the ticket record.

## Can the assistant send PHI to an AI model?
The assistant never sends PHI to a model that is not covered by a business associate agreement (BAA). Any third-party model used with PHI needs a BAA and a security review. Messages are redacted before they are sent to any model. The audit log records each outbound call's destination and token counts, never the message content. Users do not need to redact identifiers such as `IR-…` themselves, but should still avoid typing member details.

## Does minimum necessary apply to portal uploads too?
Yes. When uploading documents to a prior-authorization request, include only the records that support the requested service. Extra unrelated records slow the review and share more PHI than needed. Name files descriptively, such as "clinical notes" or "MRI report", without the member's name or date of birth. The documentation standards are in POL-09. A document uploaded to the wrong request should be reported to the service desk by request ID, without describing its clinical content.
