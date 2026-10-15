# RESUME.md

**Overwritten, never appended. Hard cap ~60 lines.** Append-only history: `checkpoints.md`.

## Where we are

Stage 5 (Build), 2026-10-15. Done: Phase 0, walking skeleton, demo script, Phase 1 domain, Phases 3 Core / 4 Products /
5 Partners closed (unit tests 10/16/11 with fail control; journeys + positive control 5/7 — trace rungs need Jaeger, absent here;
verify-module conformance/graph/coverage/journeys PASS; LOOK reports in design/ui-reviews/). Phase 6 Sales built: order logic
(600-604, 615), pages (605-612), analysis view entities + report (607/608), seed + startup chain top Sales.ASU_Sales_SeedData (616);
12 unit tests pass + fail control; journey J-SALES-01 21/21. Sales LOOK + verify-module were running at last commit.
Waiting on the user: lint baseline raise for Partners/Sales debt (ARCH001 Account pickers, CONV003 *_Edit, CUSTOM002 ASU_).

- Generators (never hand-edit their output): pipelines/odoo/mdl_domain.py (1-domain), mdl_pages.py <Page...> | --nav (list/form/popup
  pages + VAL/SUB/ACT save + line Add), plan_render.py (plan, ledgers with model-derived status, briefs). Microflows are hand-written.
- Every write: `./bin/exec.sh --commit-first <script>`; JAVA_HOME=/usr/lib/jvm/java-25-openjdk-amd64 (in .claude/settings.json).
- A reshaped microflow: drop + replay owning scripts in ONE _oneoff script (create or modify refuses: MDL-V1-REBUILD).
- LOOK: node tests/e2e/look.js tests/e2e/looks/<module>.json design/ui-reviews/shots/<date> (NODE_PATH=/opt/node22/lib/node_modules
  PW_CHROMIUM=/opt/pw-browsers/chromium), then review-agent writes the report; verify: TEST_USER=<persona> APP_PORT=8080
  MXTK_ROOT=/root/Mendix/mxcli-project-toolkit ./bin/verify-module.sh <Module>.

## Next actions, in order

1. Read the Sales LOOK report + verify log; fix P1/P2; rename verified 6-sales scripts to done-.
2. Coherence pass 1 (process-coherence-pass.md) over Core, Products, Partners, Sales; UserProfile_Edit entry point (P2).
3. Phases 7-9: Purchasing (+ WF_PurchaseOrderApproval), Inventory (replace 800 stubs), Invoicing (+ Sales row 52 create
   invoice); coherence 2 + close; pre-demo cleanup of journey fixtures; gate-check . 5.

## Do not lose

- Container setup each session: `cp /usr/local/bin/mxcli ./mxcli` (or download), clone toolkit to
  `~/Mendix/mxcli-project-toolkit`. **Never re-run `mxcli init`** — it overwrites CLAUDE.md.
- mxbuild 11.15.0 is already cached at `/root/.mxcli/mxbuild/11.15.0/` in this container image.
- BRDs are generated: never hand-edit `brd/*.brd.json`; edit brd_spec.py / brd_content.py and regenerate.
- Re-run extraction any time: `pipelines/odoo/run.sh` (deterministic; exits 1 under 95%).
- Inheritance-mapping rules (Odoo `_inherit`/`_inherits` → Mendix) are ASSUMED rows in PROJECT.md; confirm at Stage 3.
