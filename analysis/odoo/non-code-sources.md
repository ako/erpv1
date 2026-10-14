# Non-code source files — read by hand (Stage 1, Path B)

The Odoo extractor (`pipelines/odoo/`) reads every model, view, data, security, manifest and
controller file and names each one with its yield in
`analysis/odoo/knowledge-base/extracted/source-files.json`. These 24 files are not code the
extractor parses. Each was opened and read on 2026-10-14; one finding per file, and where it lands.

| File | What it is | Finding | Consequence for the build |
|---|---|---|---|
| `sources/odoo/LICENSE` | Licence text | Odoo is published under LGPLv3; "some external libraries … may be published under other GPL-compatible licenses". | Confirms the Stage P ASSUMED row: committing this subset is allowed. |
| `sources/odoo/SOURCE.md` | Our provenance note | Records branch 18.0 @ `0c430eda`, the 13 addons taken and the i18n/static/tests exclusion. | Basis for the `testCoverage` dimension being unscored (extraction-quality.json). |
| `sources/odoo/addons/account/README.md` | App store blurb | Positions Accounting as invoices, payments, follow-ups and bank sync, with analytic/budget/assets/consolidation "on demand". | Supports C8 (invoices/payments) in scope, C9/C10 deferred. |
| `sources/odoo/addons/purchase/README.md` | App store blurb | "Automate requisition-to-pay": procurement propositions → RFQ → PO → receipt → vendor bill control. | Confirms the C5 + C7 + C8 procure-to-pay story for the POC. |
| `sources/odoo/addons/sale/README.md` | App store blurb | "From quotes to invoices": quotation → (email/PDF) → one-click sales order → invoicing. | Confirms the C4 + C8 quote-to-cash demo story; email sending is not implemented (mail). |
| `sources/odoo/addons/account/doc/account_anglo_saxon.pdf` | 1-page worked example (OpenERP era) | Purchase 1 product at cost 9 / supplier price 10, sell at 20, 19% tax: shows entries on stock input 2800, output 2801, valuation 3000, payable/receivable, expense 7000, income 8000. | Stock valuation and Anglo-Saxon accounting → C9/C11, deferred. No impact on waves 1–4. |
| `sources/odoo/addons/account/doc/account_anglo_saxon.ods` | Spreadsheet behind the PDF (187 cells, 1 sheet "Feuille1") | Same 8-step scenario (purchase, receive, supplier invoice, pay supplier, sell, deliver, customer invoice, customer payment) as a debit/credit grid per account. | Deferred with C9/C11; usable as a test scenario if valuation is ever built. |
| `sources/odoo/addons/base/data/base_data.sql` | Bootstrap SQL | Creates `ir_actions` and its `INHERITS` child tables (`ir_act_window`, `ir_act_report_xml`, …) and other ORM bootstrap tables. | Framework (C12) — Mendix platform; nothing to port. |
| `sources/odoo/addons/base/data/neutralize.sql` | DB neutralisation script | Deactivates mail servers and blanks SMTP credentials so a copied DB cannot send mail. | Framework/ops (C12); no Mendix equivalent needed for a POC. |
| `sources/odoo/addons/base/data/rtlcss.json` | Web asset build config | RTL CSS conversion options for the web client (`autoRename: false`, blacklist rules). | Web client only (C12); not ported. |
| `sources/odoo/addons/base/report/corporate_defaults.xsl` | Legacy RML report stylesheet | Defines corporate header/footer variables for the pre-QWeb RML report engine. | Superseded by QWeb in Odoo itself; not ported. |
| `sources/odoo/addons/base/report/custom_default_printscreen.xsl` | Legacy RML stylesheet | Default "print screen" list-to-PDF layout for the RML engine. | Not ported (C12). |
| `sources/odoo/addons/base/report/custom_new.xsl` | Legacy RML stylesheet | Imports `custom_default_printscreen.xsl` and `custom_rml_printscreen.xsl` and composes the print-screen report. | Not ported (C12). |
| `sources/odoo/addons/base/report/custom_rml_printscreen.xsl` | Legacy RML stylesheet | Table/row templates of the print-screen report. | Not ported (C12). |
| `sources/odoo/addons/base/report/mako_footer.html` | Legacy Mako report footer | Prints company address/contact fields in the footer of Mako reports. | Not ported; Mendix document templates if reports are added later. |
| `sources/odoo/addons/base/report/mako_header.html` | Legacy Mako report header | Shows `company.logo` as base64 image plus company name in the header. | Same as above. |
| `sources/odoo/addons/base/report/mako_template.css` | CSS for Mako reports | Print styles for the legacy Mako report header/footer. | Not ported. |
| `sources/odoo/addons/base/rng/activity_view.rng` | RelaxNG schema | Grammar of Odoo's `<activity>` view type. | View grammar only; actual views are in screens.json. Activity views depend on mail → not implemented. |
| `sources/odoo/addons/base/rng/calendar_view.rng` | RelaxNG schema | Grammar of `<calendar>` views (date_start/date_stop/color attributes). | Grammar only; Mendix calendar widget if a calendar view is wanted. |
| `sources/odoo/addons/base/rng/common.rng` | RelaxNG schema | Shared grammar: `field`, `button`, `group`, `notebook/page`, modifiers. | Explains the element vocabulary the extractor reads in screens.json. |
| `sources/odoo/addons/base/rng/graph_view.rng` | RelaxNG schema | Grammar of `<graph>` views (type bar/line/pie, measures). | Grammar only; Mendix charts at Stage 3 if reporting is in scope. |
| `sources/odoo/addons/base/rng/list_view.rng` | RelaxNG schema | Grammar of `<list>` views: `groupby`, `field`, `button`, `expand`, editable lists. | Grammar only; list views map to Mendix data grids. |
| `sources/odoo/addons/base/rng/pivot_view.rng` | RelaxNG schema | Grammar of `<pivot>` views (row/col/measure fields). | Grammar only; pivot analyses → view entities / data grids at Stage 3. |
| `sources/odoo/addons/base/rng/search_view.rng` | RelaxNG schema | Grammar of `<search>` views: `filter` (domain), `group`/`groupby`, `searchpanel`. | Grammar only; search filters → Mendix data grid filters. |
