# PROJECT.md — . Decision Register

Every gate decision lands here as `CONFIRMED` or `ASSUMED`, never silently decided. See
`conversion-runbook.md` §1 for the interview protocol this file supports.

## Current stage

**Stage P — Kickoff**, needs attention — gates passed: none yet (derived by gate-check on 2026-10-14; re-run it rather than editing this line).

Toolkit commit: d16f578
Exec approval: auto
Permission profile: project
Unit tests default: no

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
| 1 | Goal: faithful port of Odoo's data model, or "Odoo-inspired" Mendix-native design? (intake Q3) | Kickoff 2026-10-14 | open |
| 2 | Project driver: POC/demo, or production use? (intake Q2) | Kickoff 2026-10-14 | open |

## Assumptions (ASSUMED, unresolved)

See the ASSUMED rows in Decisions: source committed to git, Mendix patch level 11.15.0, and the four inheritance-mapping rules (confirm at Stage 3).
