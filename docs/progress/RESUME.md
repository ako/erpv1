# RESUME.md

**Overwritten, never appended. Hard cap ~60 lines.** Append-only history: `checkpoints.md`.

## Where we are

Stage 1 (Analysis) PASSED — 2026-10-14. Stages P, 0, 1 done. Interview mode: assist.

- Extractor `pipelines/odoo/run.sh` (ast extractor + regex validator) → `analysis/odoo/knowledge-base/` at 100%
  quality; surface `analysis/odoo/knowledge-base/extraction-report.html`. Source ledger 825/825.
- CAC-1b: BRDs only for C1–C8 (inScope flag on every KB item); C9–C12 kept as reference.

## Next actions, in order

1. Stage 2 (Requirements): read runbook §Stage 2 + `skills/brd-generation.md`; generate one BRD per in-scope
   capability (C1–C8) from the KB (Odoo-inspired, Mendix-native: simplify, don't transliterate), validate
   (`skills/brd-validation.md`), render `bin/brd-report.sh`, interview gate (batched, assist mode).
2. Stage 3: modularize (≈6–7 modules), blueprint, fit-gap, design system + wireframes.

## Do not lose

- Container setup each session: `cp /usr/local/bin/mxcli ./mxcli` (or download), clone toolkit to
  `~/Mendix/mxcli-project-toolkit`. **Never re-run `mxcli init`** — it overwrites CLAUDE.md.
- mxbuild 11.15.0 is already cached at `/root/.mxcli/mxbuild/11.15.0/` in this container image.
- Re-run extraction any time: `pipelines/odoo/run.sh` (deterministic; exits 1 under 95%).
- Inheritance-mapping rules (Odoo `_inherit`/`_inherits` → Mendix) are ASSUMED rows in PROJECT.md; confirm at Stage 3.
