# RESUME.md

**Overwritten, never appended. Hard cap ~60 lines.** Append-only history: `checkpoints.md`.

## Where we are

Stage 5 (Build), 2026-10-15. Closed: Core, Products, Partners, Sales, Purchasing (unit tests 10/16/11/12/15 with fail
control; journeys incl. Purchasing approve + reject; positive control 5/7 everywhere — trace rungs need Jaeger, absent here;
verify-module conformance/graph/coverage/journeys PASS; LOOK reports in design/ui-reviews/). Coherence pass 1 done
(docs/coherence/coherence-2026-10-15-cluster1.md; fixes applied; cadence recorded). Startup chain head:
Purchasing.ASU_Purchasing_SeedData. Approval workflow Purchasing.WF_PurchaseOrderApproval (decisions synchronous in the task SUBs).
Waiting on the user: coherence decisions C1-01 (read-only order view / Billing entry for row 52), C1-06 (typed price vs
re-price), C1-08 (QuantityInvoiced on draft or post), C1-15 (lock/archive actors); lint baseline for Purchasing debt;
toolkit update a503c30 -> 95bf240 (8 guidance files).

- Generators (never hand-edit their output): pipelines/odoo/mdl_domain.py (1-domain), mdl_pages.py <Page...> | --nav (list/form/popup
  pages + VAL/SUB/ACT save + line Add), plan_render.py (plan, ledgers with model-derived status, briefs). Microflows are hand-written.
- Every write: `./bin/exec.sh --commit-first <script>`; JAVA_HOME=/usr/lib/jvm/java-25-openjdk-amd64 (in .claude/settings.json).
- A reshaped microflow: drop + replay owning scripts in ONE _oneoff script (create or modify refuses: MDL-V1-REBUILD).
- LOOK: node tests/e2e/look.js tests/e2e/looks/<module>.json design/ui-reviews/shots/<date> (NODE_PATH=/opt/node22/lib/node_modules
  PW_CHROMIUM=/opt/pw-browsers/chromium), then review-agent writes the report; verify: TEST_USER=<persona> APP_PORT=8080
  MXTK_ROOT=/root/Mendix/mxcli-project-toolkit ./bin/verify-module.sh <Module>.

## Next actions, in order

1. Apply the user's answers above (C1-01 shapes row 52; C1-08 before Invoicing).
2. Phase 8 Inventory: replace the 800 stubs (deliveries, receipts), stock, reorder rules; Inventory ASU heads the startup chain;
   C1-09 (row 79) and C1-18 (DeliveryStatus.Started) first.
3. Phase 9 Invoicing (+ Sales row 52, Purchasing row 64); coherence pass 2 (incl. Purchasing + Inventory); configure
   tests/e2e/project.config.js WALKTHROUGH for erpv1 (still the toolkit template); pre-demo cleanup; gate-check . 5.

## Do not lose

- Container setup each session: `cp /usr/local/bin/mxcli ./mxcli` (or download), clone toolkit to
  `~/Mendix/mxcli-project-toolkit`. **Never re-run `mxcli init`** — it overwrites CLAUDE.md.
- mxbuild 11.15.0 is already cached at `/root/.mxcli/mxbuild/11.15.0/` in this container image.
- BRDs are generated: never hand-edit `brd/*.brd.json`; edit brd_spec.py / brd_content.py and regenerate.
- Re-run extraction any time: `pipelines/odoo/run.sh` (deterministic; exits 1 under 95%).
- Inheritance-mapping rules (Odoo `_inherit`/`_inherits` → Mendix) are ASSUMED rows in PROJECT.md; confirm at Stage 3.
