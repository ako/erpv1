# sources/odoo — provenance

| Item | Value |
|---|---|
| Upstream | https://github.com/odoo/odoo (Community edition only — no Enterprise code) |
| Branch | `18.0` |
| Commit | `0c430eda706da326d0bc42dc2f8725f2c4b7a5bd` (2026-10-14) |
| Licence | LGPL-3.0 — see `LICENSE` in this folder |
| Imported | 2026-10-14, sparse clone |

## What was taken

`odoo/addons/base` plus these addons from `addons/`, copied into `addons/<name>/`:

| Wave | Addons |
|---|---|
| 1 Core | `base`, `uom`, `product` |
| 2 Sales & purchasing | `sales_team`, `sale`, `sale_management`, `purchase` |
| 3 Inventory | `stock`, `sale_stock`, `purchase_stock` |
| 4 Invoicing | `account`, `analytic`, `stock_account` |

The bridge modules (`sale_stock`, `purchase_stock`, `stock_account`) are included because they
hold the cross-wave flows (delivery from a sales order, receipts from a purchase order,
stock valuation). `sale_management` holds quotation templates and optional lines.

## What was left out, and why

- **Inside the taken addons:** `i18n/` and `*.po`/`*.pot` (translations), `static/` (JS/CSS/
  images, i.e. Odoo's web client), `tests/` and `populate/`. 11 MB / 824 files instead of ~230 MB.
  Re-import from the commit above if tests are wanted later as behavioural ground truth.
- **Dependencies that are not imported** (out of scope per triage): `mail` (chatter,
  `mail.thread`/`mail.activity.mixin`), `portal`, `payment`, `utm`, `web`, `digest`,
  `resource`, `onboarding`, `spreadsheet*`, and every other Odoo addon.
  Fields those modules add to in-scope models (e.g. `message_ids`) are therefore absent here, on purpose.

## Re-import

```bash
git clone --depth 1 --branch 18.0 --filter=blob:none --sparse https://github.com/odoo/odoo.git odoo-src
cd odoo-src && git checkout 0c430eda706da326d0bc42dc2f8725f2c4b7a5bd
git sparse-checkout set odoo/addons/base addons/{uom,product,sales_team,sale,sale_management,purchase,stock,sale_stock,purchase_stock,account,analytic,stock_account}
# then copy each addon excluding i18n, static, tests, populate
```

## Initial inventory (grep-level, Stage 0 homework, not an extraction)

| Addon | New models (`_name`) | of which transient (wizards) | In-place extensions (`_inherit`) |
|---|---|---|---|
| base | 121 | 22 | 34 |
| uom | 2 | 0 | 0 |
| product | 26 | 3 | 8 |
| sales_team | 3 | 0 | 1 |
| sale | 9 | 9 | 26 |
| sale_management | 4 | 1 | 5 |
| purchase | 9 | 2 | 14 |
| stock | 54 | 25 | 15 |
| sale_stock | 0 | 4 | 22 |
| purchase_stock | 3 | 5 | 27 |
| account | 61 | 18 | 34 |
| analytic | 7 | 1 | 4 |
| stock_account | 4 | 5 | 21 |

Delegation (`_inherits`) occurs in: `res.users → res.partner`, `product.product → product.template`,
`account.bank.statement.line → account.move`, `product.document → ir.attachment`, and one account
setup wizard.
