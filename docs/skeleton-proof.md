Skeleton proven 2026-10-14: exec pass, journey pass/fail-control, look done — 6 of 6 rows

# Walking skeleton — proof (walking-skeleton.md)

| # | Row | Evidence |
|---|---|---|
| 1 | exec.sh gate pass for `mdlsource/00-skeleton.mdl` | docs/BUILD-LOG.md rows 2026-10-14 (mxbuild 0 errors; lint rose — ARCH003/CONV007/CONV008/SEC008, see below) |
| 2 | App up | `./bin/app-restart.sh` → "serving on :8080", `curl /login.html` → 200; snapshot taken before first boot (.mpr-snapshots/pre-first-boot) |
| 3 | Journey passes, broken copy fails | `node tests/e2e/journeys/00-skeleton.journey.js "<name>"` → PASS, exit 0; same journey with menu "Contactz" → `FAIL menu item "Contactz" not found`, exit 1, 0 rows written |
| 4 | Data assertion names the row | `mxcli oql "SELECT p.Name FROM Partners.Partner AS p WHERE p.Name = 'Skeleton Co 210300'"` → 1 row `Skeleton Co 210300` (typed by the journey as sales.user) |
| 5 | Screenshot + four ui-loop answers | docs/looks/00-skeleton.png (1280px), answers below |
| 6 | Register line | PROJECT.md "Skeleton proven 2026-10-14" |

## Look (docs/looks/00-skeleton.png, 1280px)

1. **Is it logical?** Yes — Contacts list reached from the rail as sales.user; New creates, Save returns to the list with the row present.
2. **Does it look right?** After one fix round, yes: first screenshot had an invisible app name (dark on rail), no content gutter, and New under the title. Fixed in the shell (layout `spacing-inner-layout` gutter, `.app-name`) and the page-head pattern (`.page-head` flex row) — promoted to themesource/core/web/main.scss.
3. **Does it match the design?** Shell matches the wireframe (ledger rail, serif H1, warm paper). Two gaps carried into module build: grid rows ~73px vs ledger's 30px (use the `density-compact` recipe class), and the wireframe opens a row via the name link, not an Edit button.
4. **What would a user trip on?** The Feedback module's floating button overlaps the grid's column chooser at the right edge.
