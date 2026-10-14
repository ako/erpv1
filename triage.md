# Source Triage: erpv1 (Odoo 18.0 Community → Mendix 11.15)

**Stage 0 — migration mode.** Follows `skills/source-triage.md`. Source: `sources/odoo/` (13 addons,
825 files, provenance in `sources/odoo/SOURCE.md`). Source grade: `analysis/source-sufficiency.html`
— band **SPECIFICATION**, 7/10 dimensions specified or better, 0 contradictions, 0 shape-changing gaps.

Framing from Stage P: **POC/demo**, **Odoo-inspired, Mendix-native** (Odoo is the functional
reference, not the model to copy). Sizes below are Odoo's; the Mendix model will be smaller by design.

---

## Extraction Approach

| Decision | Chosen? | Which pipeline / what has to be built |
|---|---|---|
| **Reuse existing pipeline** | no | No toolkit pipeline reads Python/Odoo: `pipelines/` has `outsystems`, `java-angular`, `node-express-react` only, and none of their layout assumptions (OML/XML, Java/TS source trees) fit an Odoo addon tree. |
| **Build new pipeline** | **yes** | A small `pipelines/odoo/` extractor in this project: Python `ast` over `models/`, `wizard/`, `report/*.py` → models, fields (type, required, relation, compute/depends, selection values), `_inherit`/`_inherits`, `_sql_constraints`, `@api.constrains`, `action_*` methods; XML over `views/` → views per model, menus, actions; `security/` → ACL matrix (model × group × CRUD) and `ir.rule` domains; `__manifest__.py` → dependency graph. Output JSON into `analysis/odoo/knowledge-base/`. Validated against hand-built ground truth for 5 models (`res.partner`, `product.template`, `sale.order`, `sale.order.line`, `stock.picking`) per `qa-loop-goal-pattern.md`. |

Reasoning: Odoo is unusually extractor-friendly — models, fields, relations, security and menus are
all declarative, so a few hundred lines of Python cover the structure. What it cannot extract is
method *behaviour* (what `action_confirm` does); that is read per method at Stage 1/2 for the
in-scope flows only. ~300 models × ~20 fields each is far beyond a reliable hand read.

Who chose it, and when: the user, Stage 0 gate in chat, 2026-10-14 (recorded in PROJECT.md).

---

## Business Capability Map

| # | Business capability | Source components (Odoo addon → models) | Rough size in Odoo (models / wizards / form views) | Owner / team |
|---|---|---|---|---|
| C1 | Contacts, companies & users | `base` → res.partner (+category, industry, title), res.company, res.users, res.currency(+rate), res.country(+state), res.bank, res.partner.bank | 20 / 8 / ~6 relevant | user (SME) |
| C2 | Units of measure | `uom` → uom.category, uom.uom | 2 / 0 / 2 | user |
| C3 | Product catalogue & pricing | `product` → product.template, product.product (variants), product.category, attributes/values, product.pricelist(+item), product.supplierinfo, product.packaging, product.tag | 24 / 2 / 18 | user |
| C4 | Sales (quotations → orders) | `sales_team` → crm.team(+member); `sale` → sale.order, sale.order.line, cancel/discount/advance-payment wizards; `sale_management` → sale.order.template(+line, option) | 11 / 5 / 15 | user |
| C5 | Purchasing (RFQ → PO, approval) | `purchase` → purchase.order, purchase.order.line, purchase.report, bill matching | 8 / 1 / 4 | user |
| C6 | Inventory & warehouse operations | `stock` → stock.warehouse, stock.location, stock.picking(+type), stock.move, stock.move.line, stock.quant, stock.lot, stock.route/rule, stock.warehouse.orderpoint, scrap, packages, backorder/return/inventory wizards | 31 / 23 / 42 | user |
| C7 | Order fulfilment (sales → delivery, purchase → receipt) | `sale_stock`, `purchase_stock` → extensions of sale.order(.line), purchase.order(.line), stock.move/picking, procurement | 3 / 0 / 0 (extension-only: 22 + 27 `_inherit`s) | user |
| C8 | Customer invoices, vendor bills & payments | `account` → account.move (invoice/bill types), account.move.line, account.tax(+group, repartition), account.payment.term, account.payment, account.payment.register, account.journal (sales/purchase/bank only) | ~15 of 47 / 4 / ~12 | user |
| C9 | General ledger & accounting core | `account` → account.account, chart template, reconciliation (full/partial, reconcile models), bank statements, fiscal positions, lock dates, hash integrity, account.report | ~32 of 47 / 10 / ~26 | user |
| C10 | Analytic accounting | `analytic` → account.analytic.plan/account/line/distribution model | 7 / 0 / 4 | user |
| C11 | Stock valuation | `stock_account` → stock.valuation.layer, revaluation, accounting entries on moves | 3 / 1 / 2 | user |
| C12 | Platform / framework | `base` → ir.* (models, views, actions, cron, sequences, attachments, rules), res.config.settings, res.lang, res.groups, modules, QWeb, translations | 96 / ~8 / ~70 | n/a — Mendix platform provides the equivalents |

---

## Coverage Matrix

No extractor exists yet, so nothing can be **Ready** today: every in-scope capability is
**Unknown** until the new Odoo extractor has run and been checked against ground truth (it then
moves to Ready or Extract-only). Out-of-scope capabilities are **Defer**.

| Capability | Extractable? | Mapper → BRD? | Reliable? | Verdict |
|---|---|---|---|---|
| C1 Contacts, companies & users | Yes, once built (declarative ORM) | Build with extractor (fields → entity tables) | Untested | **Unknown** — extractor spike |
| C2 Units of measure | Yes, once built | as C1 | Untested | **Unknown** — extractor spike |
| C3 Product catalogue & pricing | Yes, once built | as C1; pricelist rules need a method read | Untested | **Unknown** — extractor spike |
| C4 Sales | Structure yes; flow from `action_*` methods needs reading | as C1 + state machine listing | Untested | **Unknown** — extractor spike |
| C5 Purchasing | as C4 | as C4 | Untested | **Unknown** — extractor spike |
| C6 Inventory & warehouse | Structure yes; routes/rules/reservation logic is method-heavy | as C4 | Untested | **Unknown** — extractor spike |
| C7 Order fulfilment bridges | Yes (extension-only addons, read through `_inherit`) | as C4 | Untested | **Unknown** — extractor spike |
| C8 Invoices, bills & payments | Structure yes; tax computation is method-heavy | as C4 | Untested | **Unknown** — extractor spike |
| C9 General ledger core | Yes | — | — | **Defer** — POC needs invoices, not a ledger |
| C10 Analytic accounting | Yes | — | — | **Defer** |
| C11 Stock valuation | Yes | — | — | **Defer** |
| C12 Platform / framework | Yes | — | — | **Defer** — replaced by Mendix platform features (security, scheduled events, sequences as microflows/auto-number), never ported |

### Missing dependencies (imported addons depend on addons NOT imported)

Each needs a policy — **acquire / stub / declare-not-implemented** — signed off at the gate.

| Missing addon | Needed by | What it provides | Policy (CONFIRMED 2026-10-14) |
|---|---|---|---|
| `mail` | product, sales_team, analytic (and `mail.thread`/`mail.activity.mixin` on most documents) | Chatter, followers, activities, email templates | **Declare not implemented** (chatter out of scope) |
| `portal` | account (portal.mixin on sale/purchase/invoices) | Customer/vendor self-service pages | **Declare not implemented** |
| `account_payment` → `payment` | sale | Online payment providers, payment links | **Declare not implemented**; manual payment registration (C8) stays |
| `utm` | sale | Marketing campaign/source/medium tags on orders | **Declare not implemented** |
| `barcodes_gs1_nomenclature` | stock | Barcode scanning rules | **Declare not implemented** |
| `digest`, `onboarding`, `base_setup` | account, sale_management, stock | KPI digest emails, setup tours, settings UI | **Declare not implemented** (no functional content) |

---

## Recommended Scope Subset

Order confirmed at Stage P (four waves); this records it per capability. A slice is an ordering —
deferred capabilities are not dropped from the source, only from this POC's build.

- C1 Contacts, companies & users → **Unknown** → **yes, wave 1** → everything references partners; single company only.
- C2 Units of measure → **Unknown** → **yes, wave 1** → products and order lines need it; tiny.
- C3 Product catalogue & pricing → **Unknown** → **yes, wave 1** → prerequisite of every document; variants/pricelists simplified at Stage 3.
- C4 Sales → **Unknown** → **yes, wave 2** → highest demo value (quote → order); templates optional.
- C5 Purchasing → **Unknown** → **yes, wave 2** → mirror of sales; approval step is a natural Mendix workflow.
- C6 Inventory & warehouse → **Unknown** → **yes, wave 3** → one warehouse, receipts/deliveries/stock levels; routes, lots, packages, multi-step flows simplified or deferred at Stage 3.
- C7 Order fulfilment bridges → **Unknown** → **yes, wave 3** → connects waves 2 and 3 (confirm order → delivery/receipt).
- C8 Invoices, bills & payments → **Unknown** → **yes, wave 4** → closes quote-to-cash and procure-to-pay; simplified taxes.
- C9 General ledger core → **Defer** → deferred → not needed to demo order-to-invoice.
- C10 Analytic accounting → **Defer** → deferred.
- C11 Stock valuation → **Defer** → deferred.
- C12 Platform / framework → **Defer** → never ported; Mendix equivalents used.

---

## Architecture Scale Flag

| Trigger | Fired? | Evidence |
|---|---|---|
| Capabilities with clearly independent release cadences, ownership, or security/regulatory domains | no | One owner (the user), one POC, one release cadence. |
| In-scope entity/screen count large enough that `modularize-domain.md` would still land on 8–10+ modules after its own merge criteria | no | In-scope Odoo models ≈ 115 (C1–C8, excl. wizards), expected to shrink to roughly 40–60 Mendix entities under "Mendix-native"; that suggests ~6–7 modules (Core/Partners, Products, Sales, Purchasing, Inventory, Invoicing). |

Verdict: **No concern** — one Mendix app.

---

## Sign-off

Confirmed by: user, in chat on 2026-10-14 (extraction approach, missing-dependency policies, interview mode assist, scope).
