# RESUME.md

**Overwritten, never appended. Hard cap ~60 lines.** Append-only history: `checkpoints.md`.

## Where we are

Stage 0 (Triage) drafted, awaiting sign-off — 2026-10-14. Stage P PASSED (all 13 intake answers).

- `analysis/source-sufficiency.json/.html`: pass-1 inventory (825 rows) + pass-2 grade → SPECIFICATION, 7/10.
- `triage.md` (+ `analysis/triage.html`): build-new Odoo extractor proposed, 12 capabilities, C1–C8 in scope
  (waves 1–4), C9–C12 deferred, missing-dependency policies proposed, one app.

## Next actions, in order

1. Stage 0 gate (asked in chat 2026-10-14): user confirms extraction approach, missing-dependency
   policies, interview mode (report recommends `assist`; intake said `steering`), CAC-1 scope brainstorm.
   Then fill triage.md sign-off + PROJECT.md rows, run `gate-check.sh . 0`.
2. Stage 1: build the Odoo extractor (see triage.md Extraction Approach), validate on 5 ground-truth models,
   write `analysis/odoo/knowledge-base/`, then source-ledger dispositions for all 825 rows.

## Do not lose

- Container setup each session: `cp /usr/local/bin/mxcli ./mxcli` (or download), clone toolkit to
  `~/Mendix/mxcli-project-toolkit`. **Never re-run `mxcli init`** — it overwrites CLAUDE.md.
- mxbuild 11.15.0 is already cached at `/root/.mxcli/mxbuild/11.15.0/` in this container image.
- Inheritance-mapping rules (Odoo `_inherit`/`_inherits` → Mendix) are ASSUMED rows in PROJECT.md; confirm at Stage 3.
