# PROJECT.md — . Decision Register

Every gate decision lands here as `CONFIRMED` or `ASSUMED`, never silently decided. See
`conversion-runbook.md` §1 for the interview protocol this file supports.

## Current stage

**Stage 5 — Build**, needs attention — gates passed: P, 0, 1, 2, 3, 4 (derived by gate-check on 2026-10-15; re-run it rather than editing this line).

Toolkit commit: 99ef8f5
Interview mode: assist
Exec approval: auto
Permission profile: project
Unit tests default: yes

<!-- The bold line above is a READOUT: bin/gate-check.sh rewrites it on every full run from the
     verdicts it just produced (first stage neither PASS nor WAIVED). Do not edit it by hand.
     Where this project joins the pipeline: nothing recorded, so it starts at Stage P — the
     usual case. If work was already done outside the toolkit, record it once and the earlier
     stages report WAIVED instead of a red row nobody can clear:
       bin/gate-check.sh <project> --adopt 5 --reason "..."     every stage before 5
       bin/gate-check.sh <project> --waive 2 --reason "..."     just that one (one line per stage)
     Intake Q10 asks this. Never infer it from what happens to be on disk. (No example line is
     written out here on purpose: gate-check reads these labels back out of this file, and a
     sample value would waive stages in every project that never deleted it.) -->

## Decisions

Opt-in artifact erd: user asked for the target-domain ERD at Stage 2 close (chat 2026-10-14)

| Stage | Decision | Status | Notes |
|---|---|---|---|
| P | Entry mode: **Migration** (source Odoo 18.0 Community → Mendix) | CONFIRMED | Chat 2026-10-14 |
| P | Source: Odoo `18.0` @ `0c430eda`, Community only, subset in `sources/odoo/` (no i18n/static/tests) | CONFIRMED | Chat 2026-10-14; provenance in `sources/odoo/SOURCE.md` |
| P | Target Mendix version: **11.15** (mxbuild 11.15.0 available in the container) | CONFIRMED | Chat 2026-10-14; patch level 11.15.0 is ASSUMED until `mxcli new` at Stage 5 |
| P | Scope slicing: W1 Core (base, uom, product) → W2 Sales & Purchasing → W3 Inventory → W4 Invoicing; out: website, POS, MRP, HR, mail/chatter, portal, payment, QWeb reports, multi-company | CONFIRMED | Chat 2026-10-14 |
| P | Project driver: **POC / demo / test**, never production; no hard date | CONFIRMED | Intake Q2, chat 2026-10-14. Implies: no Odoo data migration, Stage 7 cutover reduces to "demo-ready" |
| P | Fidelity: **Odoo-inspired, Mendix-native** — do what makes most sense in Mendix; Odoo is the functional reference, not the model to copy | CONFIRMED | Intake Q3, chat 2026-10-14. Stage 3 fit-gap findings are opportunities, not gaps to close |
| P | Interview mode: steering (interactive); SME = the user, in chat; nothing outside scope must stay as-is; starting from scratch (no adopt/waive) | CONFIRMED | Intake Q5, Q7–Q10, chat 2026-10-14 |
| P | Exec approval auto; permission profile project; unit tests default **yes** | CONFIRMED | Intake Q11–Q13, chat 2026-10-14 |
| 0 | Extraction approach: **Build new pipeline** — project-local Odoo extractor (Python ast + XML/CSV), validated on 5 ground-truth models | CONFIRMED | Stage 0 gate, chat 2026-10-14 (triage.md) |
| 0 | Missing dependencies (mail, portal, account_payment/payment, utm, barcodes_gs1_nomenclature, digest, onboarding, base_setup): **declare not implemented**; manual payment registration stays in scope | CONFIRMED | Stage 0 gate, chat 2026-10-14 |
| 0 | Interview mode switched steering → **assist** (sufficiency report: SPECIFICATION, 0 contradictions) — questions batched at gates, low-consequence ones assumed and reported | CONFIRMED | Stage 0 gate, chat 2026-10-14 |
| 0 | Scope (CAC-1): C1–C8 in scope in waves 1–4, C9 ledger / C10 analytic / C11 valuation / C12 framework deferred; one Mendix app; size tier full (≈115 in-scope models, far over small-tier bounds) | CONFIRMED | Stage 0 gate, chat 2026-10-14 — user accepted the map without additions |
| 1 | Path A (code): project-local Odoo extractor `pipelines/odoo/` — quality **100%** on 9 Odoo-shaped dimensions (3557 fields, 1223 relations, 132 static enumerations, 712 views, 223 menus, 759 security records, 43 routes, 7 crons); independent regex validator; one correlated blind spot found by a 3rd probe and fixed (annotated fields) | CONFIRMED | `analysis/odoo/knowledge-base/extracted/extraction-quality.json`, method log `pipelines/odoo/SESSION-NOTES.md` |
| 1 | Path B (documents): the 24 non-code files (READMEs, licence, anglo-saxon PDF/ODS, framework assets) read by hand | CONFIRMED | `analysis/odoo/non-code-sources.md`; source ledger 825/825 name-verified, 0 waivers |
| 1 | Path C (SME): no open questions that code + docs cannot answer at this point; behavioural questions are raised at the Stage 2 interview gate (SME = user, assist mode) | ASSUMED | Agent, 2026-10-14 — reported in chat |
| 1 | Extraction scope (CAC-1b): extraction covers all 13 imported addons; **BRDs only for C1–C8** (89 entities, 56 structures, 504 views in scope). C9–C12 output (76 entities, 68 structures, 208 views) stays in the KB as reference, no BRDs. Nothing missing for an in-scope capability | ASSUMED | Follows from the CAC-1 decision; stated in chat 2026-10-14 (assist mode) |
| 2 | BRD set F001–F008 (one per capability C1–C8), generated from `pipelines/odoo/brd_spec.py` + `brd_content.py` by `brd_generator.py`: 7 modules (Core, Partners, Products, Sales, Purchasing, Inventory, Invoicing), 43 entities, 27 enumerations, 4 view entities, 48 use cases, 60 microflows, 1 workflow (PO approval); 338 of 358 members traced to Odoo fields; 89/89 in-scope Odoo models mapped (39) or dropped with reason (50); validation clean | CONFIRMED | User accepted all 15 Stage 2 questions as proposed, chat 2026-10-14 (no variants, no lots/packages/multi-step, no ledger, single currency, 9 roles, PO approval workflow, on-screen documents, view-entity reports, templates + reorder rules in, returns/scrap/down payments out) |
| 2 | Mendix conventions in BRDs: system members (createdDate/changedDate/owner/changedBy) instead of hand-made audit attributes; `Active` only where Odoo archives; document numbers via Core.Sequence | ASSUMED | Deviation from brd-generation.md template, recorded in brd_spec.py header |
| 3 | Module boundaries: 7 modules in a strict layer stack Core → Products → Partners → Sales/Purchasing → Inventory/Invoicing; associations only point down (acyclic, checked by brd_generator.py); upward calls only Sales/Purchasing → Inventory/Invoicing bridge microflows. Tax/PaymentTerm → Core, UserProfile → Partners, VendorPrice → Purchasing, PO deliver-to dropped, reorder-rule link reversed. Rationale: `architecture/module-design.html` | CONFIRMED | User 2026-10-14 ("A–D as proposed"); Step 1: one owner, no reuse intent, no independent cadence, no segregation beyond the 9 roles |
| 3 | ERD (opt-in) generated: `architecture/erd.md`, 8 Mermaid diagrams, all render (mermaid-cli 11.4.2) | CONFIRMED | Accepted with the module design, user 2026-10-14 |
| 3 | One Mendix app (Stage 0 flag not raised) | CONFIRMED | triage.md Architecture Scale Flag: no concern; user 2026-10-14 |
| 3 | Role model: 9 user roles mapped from Odoo groups (Q-F001-2); no anonymous/guest access; no PII/regulatory segregation | CONFIRMED | User 2026-10-14 (Q-F001-2 + "A–D as proposed") |
| 3 | Volumes / NFRs: demo data (tens–hundreds of rows per entity), ≤ 5 concurrent users, no SLA → paged data grids, indexes only on number/date/status attributes, no batching | CONFIRMED | User 2026-10-14 ("B as proposed") |
| 3 | Integrations: none live; email, portal, payment providers, EDI and barcodes declared not implemented | CONFIRMED | Stage 0 decision; user 2026-10-14 ("C as proposed") |
| 3 | Marketplace: Buy Administration, Atlas Core, Data Widgets, Charts, Workflow Commons; build everything else | CONFIRMED | User 2026-10-14 ("D as proposed") |
| 3 | Branding: no client brand; design direction = mxcli built-in theme **ledger** (warm paper, hairline rules, Source Serif headings / Source Sans body, 2px radius, 30px rows, light + dark) — ideation library not used | CONFIRMED | User 2026-10-14: "use the ledger theme provided by mxcli, no branding" |
| 3 | Navigation layout: side rail (ledger's --mxt-rail tokens), one menu group per app area (Sales, Purchase, Inventory, Invoicing, Contacts, Products, Reporting, Configuration), filtered by role | CONFIRMED | User 2026-10-14 (Stage 3 sign-off, "all as proposed") |
| 3 | Stage 3 ✋ sign-off: blueprint, fit-gap, ledger design system, 46 wireframes + prototype, interaction model approved | CONFIRMED | User 2026-10-14: "all as proposed" |
| P | Source is committed to git (`sources/` tracked) | ASSUMED | LGPL-3.0 public code; container is ephemeral so an ignored copy would be lost (cloud-dev-environment.md step 5) |
| 3 | Odoo in-place extension (`_inherit` without new `_name`): fields go into the owning Mendix entity; 1–1 extension entity only where the module must stay optional; method overrides → explicit sub-microflow hooks | CONFIRMED | User 2026-10-14 (Stage 3 sign-off, \"all as proposed\") |
| 3 | Odoo mixins (`_inherit` with new `_name`, e.g. `mail.thread`): no multiple inheritance in Mendix; at most one shared generalization (e.g. `Core.BusinessDocument`), otherwise associations; chatter out of scope | CONFIRMED | User 2026-10-14 (Stage 3 sign-off, \"all as proposed\") |
| 3 | Odoo delegation (`_inherits`): always an **association**, never a Mendix generalization (e.g. product.product → product.template is 1–n; res.users → res.partner can be created later) | CONFIRMED | User 2026-10-14 (Stage 3 sign-off, \"all as proposed\") |
| 3 | Mendix generalization only for true, fixed-at-creation is-a (e.g. account → `System.User`, attachments → `System.FileDocument`) | CONFIRMED | User 2026-10-14 (Stage 3 sign-off, \"all as proposed\") |
| 4 | Model location: two-tree layout, app at `app/erpv1.mpr` (`mxcli new --output-dir app`), repo tooling at the root; CLAUDE.local.md Wiring updated; 6 dev-process agents completed (build-ready PASS) | CONFIRMED | User 2026-10-14: "all as proposed" (PD question 7) |
| 4 | PD-1 Acceptance criteria per module: verify-module.sh no FAULT · every use case walked as its demo user with data effect asserted by OQL · unit tests pass · every page LOOKed at 1280/390 px vs its wireframe · coverage ledger clean | CONFIRMED | User 2026-10-14: "all as proposed" |
| 4 | PD-2 Environment: local only (`mxcli run --local`, `--hub` preview URL for the demo); no Mendix Cloud, no DTAP | CONFIRMED | User 2026-10-14: "all as proposed" |
| 4 | PD-3 StyleGallery UI module: No — ledger theme recipe classes + design/design-system.html are the reference | CONFIRMED | User 2026-10-14: "all as proposed" |
| 4 | PD-4 Generation strategy: phase-by-phase in dependency order (draft + exec + verify a phase before the next); security in layer 1, grants co-located in every script | CONFIRMED | User 2026-10-14: "all as proposed" |
| 4 | PD-5 Priority: none — pure dependency order Core → … → Invoicing | CONFIRMED | User 2026-10-14: "all as proposed" |
| 4 | PD-6 Demo script: yes, written before phase 3 | CONFIRMED | User 2026-10-14: "all as proposed" |
| 4 | Stage 4 ✋ sign-off: architecture/build-plan.md (95 rows, 10 phases), per-BRD coverage ledgers (8 clean), 7 module briefs approved | CONFIRMED | User 2026-10-14: "all as proposed, continue with stage 5" |
| 5 (build) | Lint security tier accepted: CONV006 (create/delete rights per the approved access tables) and SEC008 (email on Company/Partner readable by internal roles) — single-company internal demo; baseline updated --approved-in-chat | CONFIRMED | User 2026-10-15: "all as proposed" |
| 5 (build) | SEC014 external roles: none (no portal, guest or external users) — .claude/lint-config.yaml | CONFIRMED | User 2026-10-15: "all as proposed" |
| 5 (build) | Demo data: the docs/demo-script.md fixtures are seeded by idempotent startup microflows (per module, business-key guarded, behind constant Core.SeedDemoData); journey leftovers are cleaned before a demo | CONFIRMED | User 2026-10-15: "all as proposed" |
| 5 (build) | Startup chain: each module's ASU_<M>_SeedData calls the module below it first; the after-startup setting points at the highest module built (layering-safe, no upward call) | ASSUMED | Agent 2026-10-14 — replaces the plan's single Core seed, which would have referenced Products/Inventory upward |
| 5 (build) | Displayed fact: confirmed revenue — source Sales.SalesAnalysis / Sales.SalesKpi, both the sum of SalesOrderLine.Subtotal over confirmed orders; SalesOrder.AmountUntaxed is never summed for reporting | CONFIRMED | coherence 2026-10-15 C1-10 (user: "continue with coherence pass") |
| 5 (build) | Displayed fact: confirmed purchases — source Purchasing.PurchaseAnalysis / Purchasing.PurchaseKpi, both the sum of PurchaseOrderLine.Subtotal over confirmed orders; PurchaseOrder.AmountUntaxed is never summed for reporting | CONFIRMED | same pattern as confirmed revenue, 2026-10-15 |
| 5 (build) | Sales.ENUM_DeliveryStatus.Started is not used: delivery status is NotDelivered / PartiallyDelivered / FullyDelivered (coherence C1-18) | CONFIRMED | User 2026-10-15: "Yes, go with proposed assumptions" |
| 5 (build) | Quantity change on a confirmed sales order: a decrease below QuantityDelivered is refused; an increase is added to the open delivery (or a new one). Row 79 gets its own scripts (coherence C1-09) | CONFIRMED | User 2026-10-15: "Yes, go with proposed assumptions" |
| 5 (build) | Billing's entry to invoicing: Sales.Reader gets a read-only SalesOrder_View page with Create invoice on it (row 52); Sales.Reader does not get SalesOrder_NewEdit (coherence C1-01) | CONFIRMED | User 2026-10-15: "Yes, go with proposed assumptions" |
| 5 (build) | SalesOrderLine.QuantityInvoiced / PurchaseOrderLine.QuantityBilled move when the draft invoice/bill is created (Odoo), not on post; the Cancel refusal message says 'invoiced' (coherence C1-08) | CONFIRMED | User 2026-10-15: "Yes, go with proposed assumptions" |
| 5 (build) | Re-pricing: a sales line's quantity or unit change re-prices through the pricelist (unit converted via SUB_UoM_ConvertPrice) only while its price is still the pricelist price; a hand-typed price is kept (coherence C1-06) | CONFIRMED | User 2026-10-15: "Yes, go with proposed assumptions" |
| 5 (build) | Manager-only actions: lock/unlock orders (Sales, Purchasing), archive contacts, and maintain vendor prices are limited to the Manager module roles (coherence C1-15) | CONFIRMED | User 2026-10-15: "Yes, go with proposed assumptions" |
| 5 (build) | Lint baseline raised for Purchasing: ARCH001 Account pickers, CONV003 page names, CUSTOM002 ASU_, CONV010 on ACT_PurchaseApproval_Open (open user task is navigation; rule false positive) | CONFIRMED | User 2026-10-15: "Yes, go with proposed assumptions" |
| 5 (build) | Inventory coverage checklist (12 items, posted in chat 2026-10-15) confirmed as the module's definition of done | CONFIRMED | User 2026-10-15: "Yes, go with proposed assumptions" |
| 5 (build) | Lint baseline raised for Inventory: ARCH001 cross-module pickers (+8), CONV003 ValidateTransfer_Popup / Warehouse_Edit (+2), CUSTOM002 ASU_Inventory_SeedData and SCE_ReorderRules_Run — the BRD's name (+2) | CONFIRMED | User 2026-10-16: "1. ok" |
| 5 (build) | Order lists get the wireframe's tabs and filters: Quotations & sales orders, RFQs & purchase orders (and Transfers, whose spec carries tabs too) — LOOK 2026-10-16 P2 intent | CONFIRMED | User 2026-10-16: "2 yes" |
| 5 (build) | Lint baseline (security tier): SEC010 1->4 — the row-scoped Sales order list now has one grid per tab (gridMain, gridQuotations, gridSalesOrders, gridToInvoice); same intended scoping as accepted 2026-10-15 | CONFIRMED | User 2026-10-16: "ok, baseline the SEC010 ones too" |
| 5 (build) | Validation: Odoo uniqueness constraints become entity unique rules, enforced in the database (composite Odoo keys via a stored key attribute filled on commit); value ranges become entity range rules; form-level required/conditional checks stay in VAL_ microflows (inline lists included). Odoo constraints are carried into the BRDs first. Supersedes the mdl_domain.py note "no NOT NULL / UNIQUE validation rules" for uniqueness and ranges | CONFIRMED | User 2026-10-16: "For unique validation this needs to happen in the database, so defined as entity validations." (ranges/VAL_ split as proposed, not objected) |
| 5 (build) | Lint baseline: CONV015 +13 (entity unique/range rules), CONV016 +2 and CUSTOM002 +2 (BCo_ composite-key handlers) — rationale in FINDINGS.md "Why the lint baseline accepts entity validation rules and two event handlers"; duplicate journey taxes removed directly in the dev database | CONFIRMED | User 2026-10-16: "Clear them in the database, and you may change lint baseline, but document a finding why" |

Skeleton proven 2026-10-14: exec pass, journey pass/fail-control, look done (docs/skeleton-proof.md, 6 of 6 rows)

Opt-in artifact demo-script: PD-6 — the POC ends in a demo (user, 2026-10-14)

## Change log

Feedback and change requests, one row each, written BEFORE any edit (`skills/change-intake.md`). Status: open → refined → agreed → applied → proven, or rejected (reason); Closed-by cites the commit, journey or test. Escape a `|` inside the ask as `\|`.

| CR | Date | Source | Verbatim ask | Class | Size | Entry artifact | Status | Closed-by |
|---|---|---|---|---|---|---|---|---|

## Dependencies & open issues

Carried into the build plan (architecture-blueprint.md Step 5). Numbered OI-n on purpose (gate-check reads a bare number as a stage).

| ID | Item | Type | Resolution / owner |
|---|---|---|---|
| OI-1 | BRD openQuestions | Decision | none open — all 15 answered 2026-10-14 |
| OI-2 | 53 cross-module associations (list in `analysis/odoo/knowledge-base/brd/module-graph.json`) | Scripted via mxcli | each created in the referencing module's domain-model script; build order Core → Products → Partners → Sales → Purchasing → Inventory → Invoicing |
| OI-3 | Marketplace Buy: Administration, Atlas Core, Data Widgets, Charts, Workflow Commons | Dependency | CONFIRMED; install at build-plan Step 0, versions matching Mendix 11.15 |
| OI-4 | mxcli known bugs on this app's shape (workflows, view entities, Data Grid 2 inline edit) | Handoff | check `bin/bug-lookup.sh` per module at Stage 4/5 |
| OI-5 | Behaviour changes vs Odoo (simplifications listed per BRD; no ledger, no variants, single warehouse one-step, explicit recomputation) | Faithful-rebuild risk | documented in BRDs + fit-gap; signed off via the 15 Stage 2 answers |
| OI-6 | Theme: no SCSS port of ds.css; app styled by `mxcli theme apply ledger` (portability check findings apply to a port that will not happen) | Decision | CONFIRMED by user 2026-10-14 (Stage 3 sign-off); StyleGallery (design-artifacts 5b) to be decided at Stage 4 |

## Open questions

| # | Question | Raised at | Status |
|---|---|---|---|
| 1 | Goal: faithful port of Odoo's data model, or "Odoo-inspired" Mendix-native design? (intake Q3) | Kickoff 2026-10-14 | answered — Odoo-inspired, Mendix-native (see Decisions) |
| 3 | Stage 2 BRD questions Q-F001-1..3, Q-F003-1..2, Q-F004-1..3, Q-F005-1, Q-F006-1..3, Q-F008-1..3 (15) | Stage 2, 2026-10-14 | answered — all as proposed (user, 2026-10-14) |
| 2 | Project driver: POC/demo, or production use? (intake Q2) | Kickoff 2026-10-14 | answered — POC/demo (see Decisions) |
| 4 | Stage 4 ✋ build-plan sign-off + PD-1..PD-6 (acceptance criteria, environment, StyleGallery, generation strategy/security timing, priority, demo-script opt-in) — proposals in architecture/build-plan.md §Pending decisions | Stage 4, 2026-10-14 | answered — all as proposed (user, 2026-10-14) |

## Assumptions (ASSUMED, unresolved)

See the ASSUMED rows in Decisions: source committed to git, Mendix patch level 11.15.0, and the four inheritance-mapping rules (confirm at Stage 3).
