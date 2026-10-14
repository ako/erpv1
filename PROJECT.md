# PROJECT.md — . Decision Register

Every gate decision lands here as `CONFIRMED` or `ASSUMED`, never silently decided. See
`conversion-runbook.md` §1 for the interview protocol this file supports.

## Current stage

**Stage 2 — Requirements**, in progress — gates passed: P, 0, 1 (derived by gate-check on 2026-10-14; re-run it rather than editing this line).

Toolkit commit: d16f578
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
| P | Source is committed to git (`sources/` tracked) | ASSUMED | LGPL-3.0 public code; container is ephemeral so an ignored copy would be lost (cloud-dev-environment.md step 5) |
| 3 | Odoo in-place extension (`_inherit` without new `_name`): fields go into the owning Mendix entity; 1–1 extension entity only where the module must stay optional; method overrides → explicit sub-microflow hooks | ASSUMED | Discussed in chat 2026-10-14, to confirm at Stage 3 |
| 3 | Odoo mixins (`_inherit` with new `_name`, e.g. `mail.thread`): no multiple inheritance in Mendix; at most one shared generalization (e.g. `Core.BusinessDocument`), otherwise associations; chatter out of scope | ASSUMED | Chat 2026-10-14 |
| 3 | Odoo delegation (`_inherits`): always an **association**, never a Mendix generalization (e.g. product.product → product.template is 1–n; res.users → res.partner can be created later) | ASSUMED | Chat 2026-10-14 |
| 3 | Mendix generalization only for true, fixed-at-creation is-a (e.g. account → `System.User`, attachments → `System.FileDocument`) | ASSUMED | Chat 2026-10-14 |

## Change log

Feedback and change requests, one row each, written BEFORE any edit (`skills/change-intake.md`). Status: open → refined → agreed → applied → proven, or rejected (reason); Closed-by cites the commit, journey or test. Escape a `|` inside the ask as `\|`.

| CR | Date | Source | Verbatim ask | Class | Size | Entry artifact | Status | Closed-by |
|---|---|---|---|---|---|---|---|---|

## Open questions

| # | Question | Raised at | Status |
|---|---|---|---|
| 1 | Goal: faithful port of Odoo's data model, or "Odoo-inspired" Mendix-native design? (intake Q3) | Kickoff 2026-10-14 | answered — Odoo-inspired, Mendix-native (see Decisions) |
| 2 | Project driver: POC/demo, or production use? (intake Q2) | Kickoff 2026-10-14 | answered — POC/demo (see Decisions) |

## Assumptions (ASSUMED, unresolved)

See the ASSUMED rows in Decisions: source committed to git, Mendix patch level 11.15.0, and the four inheritance-mapping rules (confirm at Stage 3).
