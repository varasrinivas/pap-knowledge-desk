---
id: UI-15
title: Exporting reports
doc_type: ui
owner: Portal Product Team
audience: PROVIDER_OFFICE_MGR, REGIONAL_DIRECTOR
screens: Reports
role_required: PROVIDER_OFFICE_MGR
permission: reports.export
version: 2.0
effective_date: 2026-04-15
last_reviewed: 2026-08-30
related: POL-18, WF-09
---
# Exporting reports

Use this when you need a list of requests outside the portal, for example a monthly count of approvals for your office or a regional review summary. Exports are available as **CSV** or **Excel** and need the `reports.export` permission, which office managers and regional directors have.

## Procedure: Export a report as CSV or Excel
1. Sign in and open **Reports**.
2. Choose the report you need, for example your office's requests by status.
3. Set the filters: date range, status, urgency or service type.
4. Click **Export**.
5. Choose the format: **CSV** for importing into another system, or **Excel** for reading and sorting.
6. Wait for the download to finish and open the file.
7. Save it in your organisation's approved secure location.

**What you should see:** A downloaded file containing the rows that matched your filters, with request numbers (`IR-YYYY-NNNNN`), statuses and dates.

## Procedure: Check whether you can export
1. Open **My Access** and read **Your role**.
2. If your role is PROVIDER_OFFICE_MGR or REGIONAL_DIRECTOR, you have `reports.export`.
3. If your role is PROVIDER_NURSE, you can view requests but not export. Ask your office manager to run the export, or request a role change (UI-13).

**What you should see:** The **Export** button on **Reports** if you have permission. Without it, the button is not shown.

## Choosing a format
- **CSV**: plain text with commas. Best for loading into another system or a script. Open it in a spreadsheet program if you just want to look.
- **Excel**: a workbook ready for sorting and filtering by hand.
- PDF is not an export format. If you need a decision letter as PDF, use **Download letter** on the **Decision** tab (UI-09).

## Handling exports safely
- Exports can contain member identifiers. Keep them inside your organisation's approved systems.
- Do not attach exports to support tickets or emails. If you need help with a report, describe the filters you used and quote request numbers only.

## Common errors on this screen
- **"There's no Export button"**: Your role does not include `reports.export`. Nurses do not have it; ask your office manager.
- **"The CSV opens as one long column"**: Your spreadsheet program did not split on commas. Use its import option, or export as **Excel** instead.
- **"The export is missing recent requests"**: Your date range or status filter excludes them. Widen the filters and export again.
- **"I need a PDF report"**: Exports are **CSV** or **Excel** only. Export to **Excel** and print from there if you need paper.
