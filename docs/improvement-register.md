# Improvement register — one row per P1/P2, append-only (skills/improvement-register.md)

| Date | Module/Cluster | Source pass | Defect class | Severity | Finding | Disposition |
|---|---|---|---|---|---|---|
| 2026-10-14 | Core | module-review §4d (design/ui-reviews/ui-review-2026-10-14-core.html) | blank-render | P2 | Line editors at 390px: inputs unlabeled (caption row hidden on phone) | fixed same session — generator keeps input labels, CSS shows them on phone only (mdl_pages.editable_listview) |
| 2026-10-14 | Core | module-review §4d | other | P2 | Data grid at 390px squeezed to ~30px columns, text unreadable | fixed same session — grids scroll horizontally on phone (core main.scss) |
| 2026-10-14 | Core | module-review §4d | other | P2 | Sequence Code column clipped and editable | fixed same session — weighted column widths, business key read-only |
| 2026-10-14 | Core | module-review §4d | other | P2 | Demo-user switcher overlaps content at 390px | partly — content gets bottom padding; switcher position rule not applied (P3 open) |
| 2026-10-14 | Core | module-review §4c | vocabulary-mismatch | P2 | Company "Users" link unexplained | fixed same session — "Related" heading + caption "User accounts (Administration)" |
| 2026-10-14 | Core | module-review §4c | other | P2 | One-click Remove on numbering sequences | fixed same session — editable list pages have no Remove (rows are configuration) |
