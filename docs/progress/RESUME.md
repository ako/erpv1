# RESUME.md

**Overwritten, never appended. Hard cap ~60 lines.** Append-only history: `checkpoints.md`.

## Where we are

Stage 5 (Build), 2026-10-16. Built: Core, Products, Partners, Sales, Purchasing, Inventory (unit tests 10/16/12/15/14;
journeys incl. Inventory J-INV-01 backorder walk, -02 receipt, -03 reorder, -04 count, -05 manual transfer; positive control
5/7 — trace rungs need Jaeger). Inventory close: sweep done (.claude/loop/sweep/Inventory), verify conformance/graph/coverage/
journeys PASS, fidelity rows logged; consolidated LOOK re-shoot in progress (shots/2026-10-16b, model 63626bc) after the
P1 fixes below — the review-agent writes design/ui-reviews/ui-review-2026-10-16b.html.
P1s fixed 2026-10-16: form Saves now commit their lines; transfer state buttons save lines first; Validate reads moves over the
association; stock count Apply is per row; identity pickers editable only while empty. Startup chain head:
Inventory.ASU_Inventory_SeedData. Waiting on the user: lint baseline for Inventory (ARCH001 +8, CONV003 +2, CUSTOM002 +2);
order-list tabs/filters (LOOK P2 intent); C1-06 / C1-15 implementation (decided).
App on a trial licence (~5 sessions): never leave a browser script running; restart the app if logins are refused.

- Generators (never hand-edit their output): pipelines/odoo/mdl_domain.py (1-domain), mdl_pages.py <Page...> | --nav (list/form/popup
  pages + VAL/SUB/ACT save + line Add), plan_render.py (plan, ledgers with model-derived status, briefs). Microflows are hand-written.
- Every write: `./bin/exec.sh --commit-first <script>`; JAVA_HOME=/usr/lib/jvm/java-25-openjdk-amd64 (in .claude/settings.json).
- A reshaped microflow: drop + replay owning scripts in ONE _oneoff script (create or modify refuses: MDL-V1-REBUILD).
- LOOK: node tests/e2e/look.js tests/e2e/looks/<module>.json design/ui-reviews/shots/<date> (NODE_PATH=/opt/node22/lib/node_modules
  PW_CHROMIUM=/opt/pw-browsers/chromium), then review-agent writes the report; verify: TEST_USER=<persona> APP_PORT=8080
  MXTK_ROOT=/root/Mendix/mxcli-project-toolkit ./bin/verify-module.sh <Module>.

## Next actions, in order

1. Review the 2026-10-16b shots (review-agent, all six modules, one file), then rename 8-inventory scripts to done-, gate-check.
2. Invoicing phase: read-only SalesOrder_View / PurchaseOrder_View with Create invoice (C1-01), rows 52/64, QuantityInvoiced
   on draft (C1-08); restore the transfer Open order links to those views. C1-06 re-pricing, C1-15 manager-only actions.
3. Coherence pass 2 (incl. Purchasing + Inventory; audit form buttons reading their own objects by XPath — register P2);
   configure WALKTHROUGH; pre-demo cleanup of journey/sweep data; gate-check . 5.

## Do not lose

- Container setup each session: `cp /usr/local/bin/mxcli ./mxcli` (or download), clone toolkit to
  `~/Mendix/mxcli-project-toolkit`. **Never re-run `mxcli init`** — it overwrites CLAUDE.md.
- mxbuild 11.15.0 is already cached at `/root/.mxcli/mxbuild/11.15.0/` in this container image.
- BRDs are generated: never hand-edit `brd/*.brd.json`; edit brd_spec.py / brd_content.py and regenerate.
- Re-run extraction any time: `pipelines/odoo/run.sh` (deterministic; exits 1 under 95%).
- Inheritance-mapping rules (Odoo `_inherit`/`_inherits` → Mendix) are ASSUMED rows in PROJECT.md; confirm at Stage 3.
