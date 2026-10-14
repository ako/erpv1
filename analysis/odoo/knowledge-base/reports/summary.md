# Odoo extraction summary

Source: `/home/user/erpv1/sources/odoo/addons` (addons in dependency order: base, uom, product, analytic, account, purchase, stock, stock_account, purchase_stock, sales_team, sale, sale_management, sale_stock)

| Type | File | Items | In scope (C1–C8) |
|---|---|---|---|
| Entities (persistent models) | `entities.json` | 165 | 89 |
| Structures (transient + abstract models) | `structures.json` | 124 | 56 |
| Static entities (selection enumerations) | `staticEntities.json` | 292 | 191 |
| Logic (model methods) | `logics.json` | 5095 | 3542 |
| Screens (views) | `screens.json` | 712 | 504 |
| Workflows (state machines) | `workflows.json` | 27 | 16 |
| Roles (groups) | `roles.json` | 57 | — |
| Timers (ir.cron) | `timers.json` | 7 | — |
| Service APIs (http routes) | `serviceApis.json` | 43 | 0 |
| External entities (not imported) | `extEntities.json` | 15 | — |

Extras: 223 menus, 253 window actions, 8 sequences, 42 server actions, 131 record rules, 572 ACL rows.

Parse errors: 1
- `sources/odoo/addons/base/models/ir_model.py`: non-literal _name in class CustomModel: model_data['model']

## Per capability

| Capability | Entities | Structures | Enumerations | Logic | Screens |
|---|---|---|---|---|---|
| C1 Contacts, companies & users | 17 | 5 | 30 | 504 | 78 |
| C2 Units of measure | 2 | 0 | 1 | 22 | 7 |
| C3 Product catalogue & pricing | 17 | 9 | 28 | 498 | 112 |
| C4 Sales | 10 | 5 | 22 | 416 | 62 |
| C5 Purchasing | 5 | 1 | 13 | 194 | 30 |
| C6 Inventory & warehouse | 23 | 31 | 51 | 923 | 132 |
| C7 Order fulfilment bridges | 1 | 0 | 0 | 3 | 2 |
| C8 Invoices, bills & payments | 14 | 5 | 46 | 982 | 81 |
| C9 General ledger core (deferred) | 22 | 15 | 36 | 414 | 39 |
| C10 Analytic accounting (deferred) | 5 | 2 | 5 | 107 | 25 |
| C11 Stock valuation (deferred) | 1 | 1 | 1 | 23 | 8 |
| C12 Platform / framework (deferred) | 48 | 50 | 59 | 1009 | 136 |
