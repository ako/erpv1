# RESUME.md

**Overwritten, never appended. Hard cap ~60 lines.** Append-only history: `checkpoints.md`.

## Where we are

Stage 5 (Build), 2026-10-16. All seven modules built: Core, Products, Partners, Sales, Purchasing, Inventory, Invoicing.
Unit tests 116 pass (Core 10, Products 16, Partners 11, Sales 16, Purchasing 15, Inventory 14, Constraints 17, Invoicing 17);
14 journeys pass incl. J-INV-B1 quote-to-cash (journeys/Invoicing.journey.json) and J-INV-B2 procure-to-pay (Billing persona);
positive control 5/7 everywhere (trace rungs need Jaeger). LOOK 2026-10-16d PASS (all modules, 0 P1, P2s fixed and re-shot;
design/ui-reviews/ui-review-2026-10-16d.html + addendum). Lint gate PASS at baseline 442 (Invoicing rises accepted, SEC010 approved
in chat). gate-check 5: 49/49 pages accounted (UserProfile_Edit waived, C1-11); rest of Stage 5 manual. verify-module Invoicing:
conformance/graph/coverage/journeys PASS; design audit instrument FAULT (persona cannot reach other modules' pages; informational).
Startup chain head: Invoicing.ASU_Invoicing_SeedData. Decided and built today: C1-01 read-only order views (SUB_*_Show picks form or
view by user role), C1-06 re-pricing (IsPriceManual), C1-08 invoiced qty incl. drafts, C1-15 manager-only actions (Partners.Manager).
ASSUMED today (PROJECT.md): sales/purchase users (Invoicing.Creator) open Invoice_NewEdit, edit draft lines only.
App on a trial licence: each browser login uses a session; after ~5, logins hang — ./bin/app-restart.sh.

- Generators (never hand-edit their output): pipelines/odoo/mdl_domain.py (1-domain), mdl_pages.py <Page...> | --nav. Do NOT run
  plan_render.py to refresh ledgers: it rewrites the module briefs (access rows) — fix ledger counts in place (FINDINGS 2026-10-16).
- Every write: `./bin/exec.sh --commit-first <script>`. A reshaped microflow: drop + replay in ONE _oneoff script (MDL-V1-REBUILD).
- LOOK: node tests/e2e/look.js tests/e2e/looks/<module>.json design/ui-reviews/shots/<date> (options: openRow, rowText, click, url),
  then review-agent; verify: TEST_USER=<persona> APP_PORT=8080 MXTK_ROOT=/root/Mendix/mxcli-project-toolkit ./bin/verify-module.sh <M>.

## Next actions, in order

1. User: C1-11 (profile creation + an entry point for Partners.UserProfile_Edit); confirm or reverse the Creator invoice-form access.
2. Coherence pass 2 over Purchasing, Inventory, Invoicing (quote-to-cash and procure-to-pay end to end; audit form buttons reading
   their own objects by XPath — register P2); then Stage 5 manual sign-off and gate-check . 6.
3. Pre-demo cleanup of journey/sweep data; configure WALKTHROUGH; docs/demo-script.md acts 1-4 rehearsal.

## Do not lose

- Container setup each session: `cp /usr/local/bin/mxcli ./mxcli` (or download), clone toolkit to
  `~/Mendix/mxcli-project-toolkit`. **Never re-run `mxcli init`** — it overwrites CLAUDE.md.
- mxbuild 11.15.0 is already cached at `/root/.mxcli/mxbuild/11.15.0/` in this container image.
- BRDs are generated: never hand-edit `brd/*.brd.json`; edit brd_spec.py / brd_content.py and regenerate.
- Re-run extraction any time: `pipelines/odoo/run.sh` (deterministic; exits 1 under 95%).
- Inheritance-mapping rules (Odoo `_inherit`/`_inherits` → Mendix) are ASSUMED rows in PROJECT.md; confirm at Stage 3.
