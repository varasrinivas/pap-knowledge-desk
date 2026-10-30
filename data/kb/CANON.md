# CANON: the facts every document, mock and generator must agree on

This file is the single source of truth for the Knowledge Desk's fictional world. It is not indexed into RAG. When a document and this file disagree, this file wins, except for the deliberately planted defects listed in `PLANTED.md`.

## The world

- **Payer:** Northwind Health Plan (fictional). The portal is the **Northwind Prior Auth Portal**, called "the portal".
- **Regions:** `SOUTH_CENTRAL` (Dallas, Houston), `NORTHEAST` (Boston, Hartford), `WEST` (Phoenix, Denver).
- **Users, all fictional:**
  - Anita Rao, RN (PROVIDER_NURSE, Lakeside Orthopedics, Dallas)
  - Priya Shah, RN (PROVIDER_NURSE, Lakeside Orthopedics)
  - Sam Whitfield (PROVIDER_OFFICE_MGR, Lakeside)
  - Nora Walsh, RN (PROVIDER_NURSE, Harbor Spine Clinic, Boston)
  - Liam Costa, RN (PROVIDER_NURSE, Sierra Rehab Partners, Phoenix)
  - Maria Lopez (UM_NURSE, SOUTH_CENTRAL)
  - Grace Iyer (UM_NURSE, NORTHEAST)
  - Owen Brooks (UM_NURSE, WEST)
  - Marcus Bell (REGIONAL_DIRECTOR, SOUTH_CENTRAL)
  - Elena Novak (REGIONAL_DIRECTOR, NORTHEAST)
  - Tom Okafor (PLATFORM_ADMIN)
  - Devika Menon (service-desk analyst)
- **Teams:**
  - Clinical Policy Desk: clinical-criteria questions, which the assistant never answers.
  - Appeals Unit: a separate process, never a ticket.
  - Service Desk: Devika's queue.
  - Platform Engineering: Tom's team.
  - Medical Directors: second-level clinical review.
- **No PHI anywhere.** Members are referred to only as "the member". Member IDs, if shown, use the pattern `NW-0000000` and are always fictional.

## Identifiers and statuses

- **Intake request:** `IR-YYYY-NNNNN` (for example `IR-2026-00517`).
- **Prior-auth number:** `PA-NNNNN`.
- **Intake status:** `Draft → Submitted → Pending Clinical Review → Pended (Info Requested) → Approved | Denied | Withdrawn`.
  - `Draft` is never visible to reviewers.
  - A `Pended (Info Requested)` request goes back to `Pending Clinical Review` when the provider responds.
- **Urgency:** `STANDARD` or `URGENT`.
- **Decision turnaround (the review SLA):** 72 hours STANDARD and 24 hours URGENT. The clock starts at `Submitted`, pauses while `Pended (Info Requested)`, and resumes on the provider's response.
- **URGENT means:** waiting the standard time could seriously jeopardise the member's life, health or ability to regain maximum function. A treating clinician must attest to this in the wizard (the **Urgent attestation** checkbox).

## Service types (policy documents filter on these)

`IMAGING` (MRI, CT, PET), `ORTHO_SURGERY`, `CARDIOLOGY`, `ONCOLOGY`, `HOME_HEALTH_DME`, `BEHAVIORAL_HEALTH`, `PHYSICAL_THERAPY`, `SLEEP_STUDY`.

## Reason codes

**Pend codes**, shown on `Pended (Info Requested)`. Each is cleared by uploading what it names, through the **Respond to Pend** panel:

| Code | Meaning |
|---|---|
| PI-DOC-001 | Clinical notes missing |
| PI-DOC-002 | Clinical notes older than 60 days |
| PI-DOC-003 | Imaging report missing |
| PI-DOC-004 | Conservative-therapy history missing (type, dates, duration, outcome) |
| PI-DOC-005 | Ordering-provider signature missing |
| PI-DOC-006 | Units or dates of service unclear |
| PI-DOC-007 | Diagnosis code does not match the requested service |
| PI-DOC-008 | Face-to-face encounter note missing (HOME_HEALTH_DME) |
| PI-DOC-009 | Treatment plan missing (ONCOLOGY, BEHAVIORAL_HEALTH) |
| PI-DOC-010 | Servicing provider NPI missing or invalid |
| PI-DOC-011 | Prior test results missing (CARDIOLOGY, SLEEP_STUDY) |
| PI-DOC-012 | Illegible document |

A pend with no response in 14 calendar days closes as `Withdrawn`.

**Denial codes:**

| Code | Meaning | Appealable |
|---|---|---|
| CR-ND-001 | Missing conservative-therapy documentation | yes |
| CR-ND-002 | Clinical notes not current | yes |
| CR-ND-003 | Service not covered under the member's plan | yes (coverage appeal) |
| CR-ND-004 | Medical necessity criteria not met | yes; peer-to-peer offered |
| CR-ND-005 | Out-of-network without an approved exception | yes |
| CR-ND-006 | Duplicate request (an approved authorization already exists) | no; use the existing PA |
| CR-ND-007 | Member not eligible on the date of service | no; verify eligibility |
| CR-ND-008 | Retro request outside the 14-day window | yes |
| CR-ND-009 | Requested site of care not approved (an alternative site is approved) | yes |
| CR-ND-010 | Pend not answered in 14 days | no; submit a new request |

**Approval code:** CR-AD-001, approved on auto-adjudication. The rules engine confidence was at least 0.85.

## Appeals and peer-to-peer

- **Appeals** are filed within **60 calendar days** of the denial date, from the decision screen (**Appeal this decision**).
  - Who may file: the ordering provider, the provider office on the member's behalf, or the member.
  - Decision time: 30 days for a standard appeal, 72 hours for an expedited appeal.
  - The service desk cannot file, expedite or change an appeal.
- **Peer-to-peer:** offered for CR-ND-004 and CR-ND-009 only.
  - It must be requested within **14 calendar days** of the denial, using **Request peer-to-peer** on the decision screen.
  - It is scheduled within 2 business days.
  - A peer-to-peer is not an appeal; the appeal clock keeps running.
- **Retro authorization** is allowed for emergency admissions and for retroactive eligibility only. It must be requested within **14 calendar days** of the service date.

## Documentation standards

- **Clinical notes:**
  - legible, signed and dated by the ordering provider;
  - dated within **60 days** of submission.
- **Accepted file types:** PDF, JPG, PNG, TIFF, DOCX. ZIP is not accepted.
- **Size limit:** **25 MB** per file, up to 20 files per request. (`PLANTED.md`: UI-05 wrongly says 20 MB.)
- **Missing uploads:** attachments appear on the **Documents** tab within 2 minutes. If one is missing after 10 minutes, re-upload it. Never email documents.

## Roles and permissions (portal mock `GET /api/v1/users/{id}/access` and `/permissions/check`)

| Role | Permissions |
|---|---|
| PROVIDER_NURSE | `intake.view`, `intake.create`, `intake.submit`, `intake.attach`, `intake.respond_pend`, `decision.view`, `appeal.create`, `p2p.request` |
| PROVIDER_OFFICE_MGR | everything PROVIDER_NURSE has, plus `office.users.manage`, `delegation.manage`, `reports.export` |
| UM_NURSE | `review.queue.view`, `review.claim`, `review.pend`, `review.recommend`, `intake.view` (assigned region only) |
| REGIONAL_DIRECTOR | `dashboard.region.view`, `reports.export`, `access.request.approve`, `queue.reassign` |
| PLATFORM_ADMIN | `config.*` |

- **Delegation:** a PROVIDER_OFFICE_MGR can grant a nurse `intake.submit` on behalf of the office, on **My Office > Delegation**. A nurse whose delegation lapsed (delegations expire after 180 days) loses the **Submit** button but keeps **Save draft**. *This is the hidden cause behind many "Submit button disappeared" incidents.*
- **Access changes** (role, region, approver group) go through the ServiceNow access catalog (`sc_request`), with a manager or regional director as approver. Provisioning takes one business day after approval. The assistant drafts the request and asks for confirmation before submitting it.
- **Lockout:** an account locks after 5 failed attempts or an MFA mismatch.
  - Lockouts are **not self-service**. The Service Desk unlocks within 2 business hours, 7am–7pm Central (ticket category `portal_access`).
  - **MFA reset after a phone change:** the first sign-in needs the new authenticator code *and* the one-time code emailed to the work address. Using the old code locks the account.

## Routing (portal mock `GET /api/v1/routing/rules`, `GET /api/v1/routing/explain/{request_id}`)

A submitted request is routed to a **review queue** named `{REGION}-{SERVICE_TYPE}-{URGENCY}` (for example `SOUTH_CENTRAL-CARDIOLOGY-URGENT`).
- The region comes from the **servicing provider's practice location**, not from the submitting office and not from the member's address.
- When the servicing provider has no location on file, the request falls to `UNASSIGNED`, which is swept every 24 hours by the regional director.
- Misrouted requests can be reassigned only by a REGIONAL_DIRECTOR (`queue.reassign`) or by a Service Desk ticket of category `other`, subcategory `routing`. A reassignment does not reset the SLA clock.

Routing rule table (fixture): one rule per region × service type. Two rules are **deliberately misconfigured** in the fixture, and they are the cause of the routing incidents:
- `CARDIOLOGY` providers whose ZIP prefix is `750–753` (Dallas) map to `NORTHEAST`. This is a bad rule (`RR-0412`) added in release 24.2.
- `ONCOLOGY` URGENT in WEST falls back to the ortho reviewer group `WEST-ORTHO_SURGERY-URGENT` (rule `RR-0577`).

## ServiceNow

- **Incidents:** `INC00NNNNN`.
- **Categories** (as the desk sets them): `portal_access`, `portal_defect`, `data_issue`, `performance`, `other`. Subcategories include `login`, `mfa`, `permissions`, `upload`, `routing`, `report`, `status_mismatch`, `slowness`, `outage`, `how_to`.
- **Close codes:** `Solved (Work Around)`, `Solved (Permanently)`, `Solved Remotely (Permanently)`, `Not Solved (Not Reproducible)`, `Not Solved (Too Costly)`, `Closed/Resolved by Caller`, `Duplicate`, `Known Error`.
- **Priority** = impact × urgency, giving P1–P4. P1 is an outage affecting a region, and P2 is a single office blocked or an SLA at risk.
- **Dedup** (the desk's rule): the same caller plus the same category within 4 hours, **or** an open P1/P2 with the same category and subcategory in the caller's region or platform-wide, makes the new report a duplicate. The oldest open match wins, and the duplicate gets a work note instead of a new ticket.
- **Major incidents** are linked with a `parent_incident`. Users who report a known outage are told the number and the update cadence, which is every 60 minutes for a P1.

## Assistant never-list (the assistant must refuse)

The assistant never:
- changes, expedites or overrides a decision;
- promises an outcome or a time it does not control;
- answers clinical-criteria or medical-necessity questions;
- gives clinical advice;
- closes or merges tickets;
- shows another user's data;
- sends PHI to a model that is not covered by a BAA.

## Portal screens and labels (UI documents use exactly these)

| Screen | Main labels |
|---|---|
| Sign in | **Email**, **Password**, **Sign in**, **Forgot password**; the MFA prompt is **Enter the 6-digit code** |
| Home | Worklist with filters **Status**, **Urgency**, **Submitted by**, **Date range**; buttons **New request** and **Search** |
| New Request wizard | Steps **1 Member**, **2 Service**, **3 Providers**, **4 Clinical**, **5 Documents**, **6 Review & Submit**. Buttons **Save draft**, **Back**, **Next**, **Submit**; the **Urgent attestation** checkbox is on step 6 |
| Request detail | Tabs **Summary**, **Documents**, **Timeline**, **Messages**, **Decision**. Buttons **Respond to Pend** (when pended) and **Withdraw** |
| Documents tab | **Upload files**, the progress bar, the file list with **Uploaded by**, **Size**, **Status** (`Scanning`, `Available`, `Rejected`) |
| Decision tab | **Download letter**, **Appeal this decision**, **Request peer-to-peer** (when offered) |
| My Access | **Your role**, **Your regions**, **Request a change** (opens the access catalog form) |
| My Office (managers) | **Users**, **Delegation**, **Add delegate**, **Expires on** |
| Regional Dashboard (directors) | Tiles **Open**, **Past SLA**, **Pended**, **Unassigned**; **Reassign queue** |
| Reports | **Export**, with the formats **CSV** and **Excel** |
| Notifications | **Email me when**, with **Pended**, **Decided**, **Message received** |
| Help | **Contact support** (opens the assistant), **Your tickets** |

The **Providers** step (3) has **Ordering provider** and **Servicing provider**. Only **one** servicing provider can be entered in the wizard. Adding a second servicing provider to an existing request has no screen, and is a planted knowledge gap.

## Live-incident fixture (the last 12 hours, regenerated relative to now)

These are the planted active issues, with their trigger keywords:

| Issue | Priority | Opened | Status | Workaround | Keywords |
|---|---|---|---|---|---|
| "Fax-to-portal intake not creating requests (NORTHEAST)" | P1 | about 3 hours ago | In Progress | Use **New request** in the portal | fax, intake |
| "Uploads failing with 'Scanning' stuck after release 24.3" | P2 | about 6 hours ago | In Progress | Uploads under 10 MB succeed | upload, scanning, attachment |

Plus about 120 routine incidents in the window.
