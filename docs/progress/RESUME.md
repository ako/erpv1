# RESUME.md

**Overwritten, never appended. Hard cap ~60 lines.** Append-only history: `checkpoints.md`.

## Where we are

Stage 5 (Build), 2026-10-15. Done: Phase 0 (app/erpv1.mpr, ledger theme, Workflow Commons), walking skeleton (docs/skeleton-proof.md),
demo script (docs/demo-script.md), Phase 1 (43 entities / 27 enums / 109 assocs / 9 roles / 9 demo users), Phase 3 Core and
Phase 4 Products closed (unit tests 10 + 16 pass with fail control; journeys/Core + Products pass + positive control; verify-module:
conformance, graph, coverage, journeys PASS; LOOK reports design/ui-reviews/ui-review-2026-10-14-core.html, -2026-10-15-products.html).
Waiting on the user: lint security-tier acceptance (CONV006, SEC008), SEC014 external roles, demo-data seeding approval.

- Generators (never hand-edit their output): pipelines/odoo/mdl_domain.py (1-domain), mdl_pages.py <Page...> | --nav (list/form/popup
  pages + VAL/SUB/ACT save + line Add), plan_render.py (plan, ledgers with model-derived status, briefs). Microflows are hand-written.
- Every write: `./bin/exec.sh --commit-first <script>`; JAVA_HOME=/usr/lib/jvm/java-25-openjdk-amd64 (in .claude/settings.json).
- A reshaped microflow: drop + replay owning scripts in ONE _oneoff script (create or modify refuses: MDL-V1-REBUILD).
- LOOK: node tests/e2e/look.js tests/e2e/looks/<module>.json design/ui-reviews/shots/<date> (NODE_PATH=/opt/node22/lib/node_modules
  PW_CHROMIUM=/opt/pw-browsers/chromium), then review-agent writes the report; verify: TEST_USER=<persona> APP_PORT=8080
  MXTK_ROOT=/root/Mendix/mxcli-project-toolkit ./bin/verify-module.sh <Module>.

## Next actions, in order

1. Apply the user's answers (lint baseline, SEC014, demo seed).
2. Phase 5 Partners (F001): ACT_Partner_Save/VAL_Partner (replaces skeleton), contact pages, UserProfile; then coherence pass 1.
3. Phases 6–9: Sales, Purchasing (+ WF_PurchaseOrderApproval), Inventory, Invoicing; coherence 2 + close; gate-check . 5.

## Do not lose

- Container setup each session: `cp /usr/local/bin/mxcli ./mxcli` (or download), clone toolkit to
  `~/Mendix/mxcli-project-toolkit`. **Never re-run `mxcli init`** — it overwrites CLAUDE.md.
- mxbuild 11.15.0 is already cached at `/root/.mxcli/mxbuild/11.15.0/` in this container image.
- BRDs are generated: never hand-edit `brd/*.brd.json`; edit brd_spec.py / brd_content.py and regenerate.
- Re-run extraction any time: `pipelines/odoo/run.sh` (deterministic; exits 1 under 95%).
- Inheritance-mapping rules (Odoo `_inherit`/`_inherits` → Mendix) are ASSUMED rows in PROJECT.md; confirm at Stage 3.
