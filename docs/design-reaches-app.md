21 of 47 framework knobs bound · tokens 16 of 19 (15 of 19 valued) · classes 2 of 68 — build 2026-10-14, app/deployment/web/theme.compiled.css

# Design reaches app — B0 report (before the first page)

Instrument: `bin/check-design-reaches-app.sh` (defaults: design/ds.css → app/deployment/web/theme.compiled.css,
knob file app/theme/web/custom-variables.scss, `$use-css-variables: true`). Verdict: clean, 2 warnings.

## Reading the numbers

- **Tokens 16 of 19 / valued 15 of 19.** design/ds.css is the ledger theme's `--mxt-*` token set copied
  verbatim (Stage 3, OI-6), so the tokens arrive because `mxcli theme apply ledger` wrote the same set into
  app/theme/web/_mxcli-ledger.scss. The one "differing" value (`--mxt-tint-neutral`, designed #2b2723) is the
  instrument reading ds.css's dark-mode block last; the light value in ds.css line 28 is #ebe5d9 = built. Not a defect.
- **Knobs 21 of 47.** The ledger atlas-map binds Atlas's knobs (topbar, sidebar, navigation, buttons, brand) to
  `--mxt-*`; the unbound remainder are knobs ds.css never set. Rail and brand verified by name in
  _mxcli-atlas-map.scss (--sidebar-bg, --navigation-bg → --mxt-rail).
- **Classes 2 of 68 — expected, by decision.** The 66 absent classes are the prototype's `lg-*` / `is-*` /
  `bind` presentation classes, which exist only to draw the wireframes. PROJECT.md OI-6 (CONFIRMED): no SCSS
  port of ds.css; pages use the theme's own recipe classes, which are in the built sheet:
  `num`, `num-right`, `pill`, `pill-ok|info|warn|risk|danger`, `stat`, `stat-label`, `stat-value`,
  `stat-delta(-up|-down)`, `density-compact`, `th`.
- **Model classes 0 of 4 undefined** — every class the model already asks for exists.

## Rule for page scripts

Only the recipe classes above, Atlas classes present in theme.compiled.css, and `Core`'s promoted classes (none
yet) may appear in a `Class:`. An `lg-*` class on a widget resolves to nothing.
