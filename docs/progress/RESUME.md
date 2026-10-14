# RESUME.md

**Overwritten, never appended. Hard cap ~60 lines.** Append-only history: `checkpoints.md`.

## Where we are

Stage 4 (Build Plan) built — 2026-10-14; gate FAILS only on the missing ✋ sign-off (PD-1..PD-6 asked in chat). build-ready PASS.

- Plan (generated): `python3 -I pipelines/odoo/plan_render.py` → architecture/build-plan.md (95 rows, 66 BUILD / 49 use cases = 1.35,
  10 phases), per-BRD ledgers `architecture/modules/<Home>/coverage-ledger/<F>.md` + index, 7 module-brief.md, design/wireframes/PAGE-MAP.tsv.
  `bin/build-plan-status.sh . --html` → build-plan.html; toolkit `project-bin/build-plan-status.sh . --json` → build-plan.json (gitignored).
- Coverage: all 8 BRDs 0 UNCLAIMED / 0 PHANTOM / 0 DOUBLE / 0 COUNT-MISMATCH (`~/Mendix/mxcli-project-toolkit/bin/coverage-check.sh --summary`).
- Regenerate order: brd_generator → wf_render → assemble-prototype → check-prototype-links → arch_render → arch_blueprint → plan_render.
- Model will live at `app/erpv1.mpr` (two-tree; ASSUMED row). .claude/agents/* completed.

## Next actions, in order

1. On sign-off: add Stage 4 CONFIRMED rows (sign-off + PD-1..PD-6), close open question 4, re-run `gate-check.sh . 4`.
2. Stage 5 phase 0: `./mxcli new erpv1 --version 11.15.0 --output-dir app`, theme ledger, marketplace modules, verify + boot
   (walking-skeleton.md), then phase 1 domain scripts via `./bin/exec.sh`.

## Do not lose

- Container setup each session: `cp /usr/local/bin/mxcli ./mxcli` (or download), clone toolkit to
  `~/Mendix/mxcli-project-toolkit`. **Never re-run `mxcli init`** — it overwrites CLAUDE.md.
- mxbuild 11.15.0 is already cached at `/root/.mxcli/mxbuild/11.15.0/` in this container image.
- BRDs are generated: never hand-edit `brd/*.brd.json`; edit brd_spec.py / brd_content.py and regenerate.
- Re-run extraction any time: `pipelines/odoo/run.sh` (deterministic; exits 1 under 95%).
- Inheritance-mapping rules (Odoo `_inherit`/`_inherits` → Mendix) are ASSUMED rows in PROJECT.md; confirm at Stage 3.
