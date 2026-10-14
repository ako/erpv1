# RESUME.md

**Overwritten, never appended. Hard cap ~60 lines.** Append-only history: `checkpoints.md`.

## Where we are

Stage 2 (Requirements) gate PASSES — 2026-10-14; 15 BRD questions raised in chat, awaiting answers.

- BRDs: `analysis/odoo/knowledge-base/brd/F001..F008` — regenerate with `python3 -I pipelines/odoo/brd_generator.py`
  (design in `pipelines/odoo/brd_spec.py`, narrative in `brd_content.py`; generator fails on any unresolved Odoo ref).
- Validation: `analysis/odoo/knowledge-base/reports/validation-report.md` (Clean). Surface: `analysis/brd-report.html`.

## Next actions, in order

1. Record the answers: set each question's status to `Resolved` + `answer` in brd_content.py, regenerate,
   flip the Stage 2 ASSUMED rows in PROJECT.md to CONFIRMED; apply any design change to brd_spec.py first.
2. Stage 3: modularize (7 modules as in the BRDs), blueprint + fit-gap, security model, CAC-4 design brainstorm,
   design system + one wireframe per screen (38 pages) + prototype.

## Do not lose

- Container setup each session: `cp /usr/local/bin/mxcli ./mxcli` (or download), clone toolkit to
  `~/Mendix/mxcli-project-toolkit`. **Never re-run `mxcli init`** — it overwrites CLAUDE.md.
- mxbuild 11.15.0 is already cached at `/root/.mxcli/mxbuild/11.15.0/` in this container image.
- BRDs are generated: never hand-edit `brd/*.brd.json`; edit brd_spec.py / brd_content.py and regenerate.
- Re-run extraction any time: `pipelines/odoo/run.sh` (deterministic; exits 1 under 95%).
- Inheritance-mapping rules (Odoo `_inherit`/`_inherits` → Mendix) are ASSUMED rows in PROJECT.md; confirm at Stage 3.
