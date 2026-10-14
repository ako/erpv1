# Brand & design basis — erpv1

**Decision (PROJECT.md, Stage 3, CONFIRMED 2026-10-14):** no client branding; the look is mxcli's built-in
theme **ledger** ("warm paper, hairline rules instead of cards, serif headings, 30px rows"). User: *"use the ledger
theme provided by mxcli, no branding"*. The ui-ux-pro-max ideation library was not used (nothing fetched).

## How the theme reaches the app

- Build: `./mxcli theme apply ledger -p <App>.mpr` writes `theme/web/custom-variables.scss`, `_mxcli-atlas-map.scss`,
  `_mxcli-ledger.scss`, `_mxcli-recipes.scss`, `_mxcli-widgets.scss`, `main.scss` and the vendored fonts. Atlas Core is untouched;
  the model is not touched. Light/dark follows the OS (`--variant auto`); `mxcli theme switcher install` adds a toggle if wanted.
- Design: `design/ds.css` carries the **same `--mxt-*` values** (copied verbatim from that apply, 2026-10-14) so wireframes
  paint exactly like the app. ds.css is the wireframe/showcase source; it is **not ported to SCSS** — the app's styling is
  the theme mxcli writes. `bin/check-design-portability.sh design/ds.css` reports 15 violations / 9 warnings
  (element selectors such as `table`/`th`/`td`, `label`, `h1`): they concern a port that will not happen. The intent they
  encode (30px rows, hairline rules, uppercase grid headers, tabular numerals) is what ledger's own widget layer already
  applies to Data Grid 2 and Atlas.
- If the palette ever changes: edit the `--mxt-*` block in `ds.css`, then `mxcli theme create erpv1 --from design/ds.css`
  (light from bare declarations, dark from the `.theme-dark` / `prefers-color-scheme` blocks) — one source, no hand edit of
  `custom-variables.scss`.

## Palette (ledger, light / dark)

| Token | Light | Dark | Use for |
|---|---|---|---|
| `--mxt-brand` | #1f3a5f | #7fa3cc | primary buttons, current status step, links |
| `--mxt-accent` | #b4531f | #e08a4f | active rail item marker, active tab underline (sparingly) |
| `--mxt-ground` | #f7f4ee | #171614 | page background ("paper") |
| `--mxt-surface` | #fffdf9 | #1f1d1a | sheets, grids, dialogs |
| `--mxt-ink` / `-muted` / `-faint` | #1c1917 / #6b6257 / #9b9082 | #ede8df / #a69c8d / #7a7164 | text, labels, hints |
| `--mxt-line` | #e2dbce | #35302a | hairline rules (no card shadows) |
| `--mxt-rail` | #211e1a | #12110f | side navigation |
| ok / warn / risk / info tints + tones | ledger pairs | ledger pairs | status pills (see tone mapping below) |

**Status tone mapping** (pills): ok = Sales order, Purchase order, Posted, Done, Paid, Fully …, Ready · warn = To approve,
Partially …, Waiting, To invoice · risk = Cancelled, Not paid (overdue), Reversed, Late · info = Quotation sent, RFQ sent,
payment direction · neutral = Quotation, RFQ, Draft, Nothing to invoice.

**Chart series** colours are not hand-picked: report pages use the `dataviz` skill's validated palette at build time;
wireframes only draw the chart frame in `--mxt-brand`.

## Typography

Source Serif 4 (headings, document numbers, KPI values) over Source Sans 3 (body, 14px, line-height 1.5), vendored with the
theme under SIL OFL 1.1 (`design/fonts/OFL-ledger.txt`) — no CDN at runtime.

## Shape & density

2px radius, 30px rows and controls, no shadows, 1px rules; spacing 8/16/24/32/48 px (`design-spacing.md`). All sizes in px
(Atlas sets `html { font-size: 10px }`).

## Atlas mapping

Handled by mxcli: `_mxcli-atlas-map.scss` wires the `--mxt-*` tokens onto ~60 Atlas variables (brand-primary, backgrounds,
font colours, borders, radii, spacing, success/warning/danger, data grid). Nothing to map by hand.

## Navigation layout

Side rail (ledger's `--mxt-rail` tokens), grouped Sales · Purchase · Inventory · Invoicing · Contacts · Products ·
Reporting · Configuration, filtered by role — ASSUMED in PROJECT.md (reported for veto, 2026-10-14).
