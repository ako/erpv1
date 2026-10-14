# RESUME.md

**Overwritten, never appended. Hard cap ~60 lines.** Append-only history: `checkpoints.md`.

## Where we are

Stage 3 (Architecture & Design) gate PASSES — 2026-10-14; awaiting the user's ✋ sign-off (close-out pasted in chat).

- Architecture (generated): `pipelines/odoo/arch_render.py` → module-design.html + erd.md; `arch_blueprint.py` → modules/*/definition.md,
  blueprint.md/.html, fit-gap.md. Design: `design/ds.css` (ledger tokens), design-system.html, brand.md;
  `pipelines/odoo/wf_render.py` (from `ui_spec.py`) → 46 wireframes + Home, target-ui.md, interaction-model.md;
  `node bin/assemble-prototype.js` → design/prototype.html; `node bin/check-prototype-links.js --brd analysis/odoo/knowledge-base/brd/` = 0 failures.
- Regenerate order after a design change: brd_generator.py → wf_render.py → assemble-prototype.js → check-prototype-links.js → arch_render.py → arch_blueprint.py.
- Open ASSUMED: navigation layout (side rail), OI-6 (no SCSS port; theme = mxcli ledger).

## Next actions, in order

1. On sign-off: flip Stage 3 ASSUMED rows the user accepts to CONFIRMED.
2. Stage 4 (build plan): `skills/brd-to-build-plan.md` + `skills/module-brief.md` — Step 0 marketplace installs,
   `mxcli new` with Mendix 11.15.0, `mxcli theme apply ledger`, module briefs in architecture/modules/<M>/.

## Do not lose

- Container setup each session: `cp /usr/local/bin/mxcli ./mxcli` (or download), clone toolkit to
  `~/Mendix/mxcli-project-toolkit`. **Never re-run `mxcli init`** — it overwrites CLAUDE.md.
- mxbuild 11.15.0 is already cached at `/root/.mxcli/mxbuild/11.15.0/` in this container image.
- BRDs are generated: never hand-edit `brd/*.brd.json`; edit brd_spec.py / brd_content.py and regenerate.
- Re-run extraction any time: `pipelines/odoo/run.sh` (deterministic; exits 1 under 95%).
- Inheritance-mapping rules (Odoo `_inherit`/`_inherits` → Mendix) are ASSUMED rows in PROJECT.md; confirm at Stage 3.
