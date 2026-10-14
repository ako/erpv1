# RESUME.md

**Overwritten, never appended. Hard cap ~60 lines.** Append-only history: `checkpoints.md`.

## Where we are

Stage P (Kickoff), partly done — 2026-10-14. Run `<toolkit>/bin/gate-check.sh .` for the live verdict.

- Workspace bootstrapped: `mxcli init` (mxcli nightly-20261014), then toolkit `init-project.sh --track-sources`
  at toolkit commit `d16f578`.
- Odoo 18.0 Community subset imported into `sources/odoo/` (provenance, scope and inventory: `sources/odoo/SOURCE.md`).
- Confirmed: entry mode Migration, target Mendix 11.15, 4-wave scope slicing (PROJECT.md Decisions).

## Next actions, in order

1. Finish the kickoff interview: intake Q2, Q3, Q5, Q7–Q13 are still unasked (Q3 = PROJECT.md open question 1).
2. Stage 0: fill `triage.md` (extraction approach — no existing Odoo pipeline, so "build new" is
   the expected call; capability map from SOURCE.md's inventory), run `bin/source-sufficiency.sh`, get sign-off.
3. Stage 1: Odoo extractor (Python AST over `_name`/`_inherit`/`_inherits`/`fields.*`, XML views/security)
   → `analysis/odoo/knowledge-base/`.

## Do not lose

- Container setup each session: `cp /usr/local/bin/mxcli ./mxcli` (or download), clone toolkit to
  `~/Mendix/mxcli-project-toolkit`. **Never re-run `mxcli init`** — it overwrites CLAUDE.md.
- mxbuild 11.15.0 is already cached at `/root/.mxcli/mxbuild/11.15.0/` in this container image.
- Inheritance-mapping rules (Odoo `_inherit`/`_inherits` → Mendix) are ASSUMED rows in PROJECT.md; confirm at Stage 3.
