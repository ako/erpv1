# Process-coherence pass: cluster 1 (Core, Products, Partners, Sales), 2026-10-15

Run per `skills/process-coherence-pass.md` (all five passes). This was a read-only review. The only
file written is this report. Model: `app/erpv1.mpr`. Instruments used: `./mxcli lint`,
`REFRESH CATALOG FULL` + `COMMUNITIES`, `CATALOG.GRAPH_DEAD_ASSETS`, `SHOW REFERENCES TO`, `SHOW CALLERS OF`,
`DESCRIBE MICROFLOW|PAGE|ENTITY|ENUMERATION|NAVIGATION|USER ROLE`, and `jq` over BRDs F001–F004 (plus F007/F008 at the overlaps).
OQL was not used because nothing was listening on :8080.

**What was treated as known, not as findings:** the two Inventory log-only stubs (`Inventory.SUB_SalesOrder_CreateDelivery`,
`Inventory.SUB_SalesOrder_CancelDeliveries`), the deferred "Create invoice" button and `CreateInvoice_Popup` (row 52), the delivery
smart button (row 77), and `QuantityDelivered`/`DeliveryStatus` updates (row 78). Where one of these will cause a dead end, the finding says so.

**Concurrency note:** while this pass ran, uncommitted work appeared in the tree from someone else:
`mdlsource/7-purchasing/*` (new) and `mdlsource/8-inventory/800-*.mdl` (new PO receipt stubs). Nothing in this report depends on it.

## Severity and labels

P1 means a persona dead-ends on a path the demo or a BRD requires. P2 means a BRD postcondition is unmet, or the
data can go wrong. P3 means a gap in the docs or the wiring with low impact. **Measured** means a command's output
directly supports the claim. **Judged** means a view formed from the cited evidence, which a reader can overrule.

## Findings

| # | Sev | Label | Element(s) | Claimed vs built | Proposed fix | Owner |
|---|---|---|---|---|---|---|
| C1-01 | P1 | Measured (grants), Judged (runtime effect) | `Sales.SalesOrder_Overview` (granted to Sales.Reader); `gridMain` onClick → `Sales.SalesOrder_NewEdit` (granted to Sales.User and Sales.Manager **only**); `btnNew` → `Sales.ACT_SalesOrder_New` (**granted to Sales.Reader**) | Billing, InvoicingManager, InventoryUser and InventoryManager hold Sales.Reader (`DESCRIBE USER ROLE`), so the menu shows them "Quotations & orders". A row click opens a page they cannot view. **New** first commits a numbered quotation (`SUB_SalesOrder_Create` commits, which burns a S000nn number) and only then opens that same page. Row 52 will dead-end because of this. The Sales brief (line 33) has Billing open `CreateInvoice_Popup` "from Create invoice on SalesOrder_NewEdit", which Billing cannot open. The alternative route, "selection on SalesOrder_Overview", needs a selection mode that `gridMain` does not have. Demo beat 1.7 (billing) has no entry point. | Needs a decision before row 52. (a) Give Sales.Reader a read-only order view: either grant `SalesOrder_NewEdit` with every input and action gated, or add a separate `SalesOrder_View`. (b) Revoke `ACT_SalesOrder_New` from Sales.Reader and hide `btnNew` from it. (c) Row 52 must name the page Billing starts from: overview multi-select plus "Create invoice", or a "To invoice" list in Invoicing. | architect (decision), mdl |
| C1-02 | P2 | Measured | `Products.Product.Active`, `Products.Product.CanBeSold`, `Partners.Partner.Active`, `Partners.Partner.IsCustomer`. Pickers: `SalesOrder_NewEdit.cmbSalesOrderCustomer/InvoiceAddress/DeliveryAddress` (`database from Partners.Partner`, no where clause), `lncmbSalesOrderLineProduct`, `QuotationTemplate_NewEdit` product picker, `Pricelist_NewEdit` product picker | F001-UC003 promises "Partner hidden from pickers" and F003-UC004 "Product hidden from pickers". `SUB_Partner_Archive`/`SUB_Product_Archive` write `Active=false`, but `SHOW REFERENCES TO Products.Product.Active` lists only the archive and seed microflows. No picker reads Active, CanBeSold or IsCustomer, so archiving has no visible effect. The customer picker also offers vendors and child addresses, and the product picker offers products that cannot be sold. This is a reachable terminal state that nothing ever queries. | Add XPath constraints to the picker datasources: customer `[Active][IsCustomer]`, addresses scoped to the customer's company, product `[Active][CanBeSold]`. Overviews can get an Active filter. | mdl |
| C1-03 | P2 | Measured | `Sales.SalesOrder.Locked`, `ACT_SalesOrder_Cancel`, `btnCancelorder3`, `btnLock5`, the access rules on `Sales.SalesOrder` and `Sales.SalesOrderLine` | F004-UC005 says "Locked orders cannot be edited". F004-UC004's precondition is "Not locked; no posted invoice". `Locked` is written (`SUB_SalesOrder_SetLocked`) and displayed (`cbLocked`), and nothing else uses it. No widget has an Editable condition, the write rules have no `[Locked=false]`, `ACT_SalesOrder_Cancel` does not check it, and `btnCancelorder3` stays visible on a locked order. `btnLock5` always reads "Lock", even when clicking it unlocks. | Gate the dataview inputs, `lvLines` and template picker on `not(Locked)`. Add a Locked guard to `ACT_SalesOrder_Cancel` and hide Cancel when locked. Make the caption conditional (Lock/Unlock). | mdl |
| C1-04 | P2 | Measured | `cmbSalesOrderQuotationTemplate` OnChange → `SUB_SalesOrder_ApplyTemplate` (`delete $OldLines`); `btnLineDelete` (`Action: delete`); `ACT_SalesOrderLine_Recompute` | A confirmed order (and later an invoiced or delivered one) stays fully editable. Picking a template deletes **every** line, including lines with `QuantityDelivered`/`QuantityInvoiced`, with no status check. **Remove** deletes any line. After line edits on a confirmed order, `SUB_SalesOrder_UpdateInvoiceStatus` is not called again: it runs only from `SUB_SalesOrder_Confirm`, per `SHOW CALLERS`. `InvoiceStatus` therefore goes stale for ordered-quantity products. | Show the template picker only for Quotation/QuotationSent and guard `SUB_SalesOrder_ApplyTemplate` the same way. Replace the delete action with an `ACT_SalesOrderLine_Delete` that refuses delivered or invoiced lines and recomputes. Call `UpdateInvoiceStatus` from the line-recompute path when Status = SalesOrder. | mdl |
| C1-05 | P2 | Measured | `btnLineDelete` (delete, no microflow); header `AmountUntaxed/AmountTax/AmountTotal` | F004-UC001 step 6 says "System recomputes subtotal, tax and total on every line change", and demo beat 1.3 depends on totals updating. Removing a line does not recompute. The header totals stay stale until **Save** (`ACT_SalesOrder_Save` → `RecomputeTotals`), and stay stale for good if the user leaves without saving, because the order was already committed at New. This feeds C1-10. | Same delete ACT as in C1-04, ending in `SUB_SalesOrder_RecomputeTotals`. | mdl |
| C1-06 | P2 | Measured | `lncmbSalesOrderLineUoM` (no OnChange, `database from Products.UoM` unfiltered); `Products.SUB_UoM_ConvertPrice` (QUAL004 and GRAPH_DEAD_ASSETS: 0 callers, and no build-plan row consumes it); `lntxtQuantity` OnChange → `ACT_SalesOrderLine_Recompute` | F002-UC002 says "a line uses a different unit … prices are converted inversely". F003-UC003 says the price is found "when a product/**quantity** is set" (min-quantity rules). As built, changing a line's unit (to Dozens, or even kg on a chair) leaves the per-Unit price, so totals come out wrong. Changing the quantity recomputes totals but never re-runs `SUB_Pricelist_GetPrice`, which was called with qty 1 when the product was picked. The seed has no PriceRule, so the demo is unaffected, but the rule as written is not met. | Add a UoM OnChange ACT that calls `SUB_UoM_ConvertPrice` (from the product UoM), and constrain the picker to the product UoM's category. Quantity OnChange should re-price through `SUB_Pricelist_GetPrice`. Whether a manually typed price should survive the re-price is a question for the human, so record it as ASSUMED or CONFIRMED. | mdl; human decision on price override |
| C1-07 | P2 | Measured (page has no save action), Judged (edits are lost at runtime) | `Core.Sequence_Overview` (`listview lvLines`, Editable: true, no action button anywhere on the page) | F001-UC006 postcondition: "Next documents use the new prefix/number". Admins can type into Prefix, Padding and NextNumber, but nothing commits the changes, so they are lost when the page is left. | Add a Save button (`ACT_Sequence_SaveAll` commits the list) or open a `Sequence_Edit` popup per row. | mdl |
| C1-08 | P2 | Judged | `Sales.SUB_SalesOrder_HasInvoicedLines` (`QuantityInvoiced > 0`, message "has posted invoices"); F008-UC001 step 4 vs F008 post step ("updates sales/purchase invoiced quantities") | The BRDs disagree on when `QuantityInvoiced` moves. If it moves only on Post, an order with an open **draft** invoice stays "To invoice" and a second draft can be created for the same quantities (double invoicing). If it moves when the draft is created, as Odoo does, Cancel is refused with a message that wrongly says "posted". | Decide before row 52 which one it is, record it in PROJECT.md, then align F008 and the Cancel message. | ba + human decision |
| C1-09 | P2 | Measured | Build-plan row 79 "F007-UC003 Changing quantities on a confirmed sales order", which claims to be "carried by the documents of rows 44" | None of row 44's documents implements F007-UC003. Its rules are "decreasing below delivered quantity is refused" and "add the difference to the open delivery". `ACT_SalesOrderLine_Recompute` only recomputes totals. The row has no document, so the behaviour has nowhere to live. | Give row 79 its own documents: a VAL on line quantity against QuantityDelivered (Sales), plus an Inventory hook to adjust the open delivery, wired from the quantity OnChange. Write the claims block in the same edit. | architect |
| C1-10 | P2 | Judged | `Sales.SalesAnalysis_Report`: `dvKpi` "Revenue (confirmed)" = `Sales.SalesKpi` = `sum(SalesOrder.AmountUntaxed)`; the "Revenue per month/salesperson" charts and `gridMain` = `Sales.SalesAnalysis` = `sum(SalesOrderLine.Subtotal)` | One displayed fact (confirmed revenue) has two sources on one page. They agree only while every header total is fresh, and C1-05 is a path where it is not. | Choose one source (line sum, or header with the recompute guaranteed by C1-04/C1-05). Then register it: `Displayed fact: confirmed revenue — source …`. | architect (register), mdl |
| C1-11 | P3 | Measured | `Partners.UserProfile_Edit` (QUAL004, GRAPH_DEAD_ASSETS, no navigation entry); `Partners.SUB_UserProfiles_Ensure` (only caller: `ASU_Partners_SeedData`) | F001-UC005 step 2 says "System creates the Partners.UserProfile". Profiles are created only at startup, so an account created through `Company_Edit` → `Administration.Account_Overview` has no profile until the next restart. The profile page cannot be reached at all. | Decide whether profiles are created lazily at first use or when the account is created (Administration is a marketplace module, so there is no event hook). Add a menu or link to a profile overview for Partners.Admin. | architect (decision), mdl |
| C1-12 | P3 | Measured | `Sales.SUB_SalesOrder_ApplyCustomer`; `Partners.Partner_Salesperson` (read only by Partner pages); `Partners.UserProfile` (no team association) | F004-UC001 step 2 says the customer fills in "salesperson, team". ApplyCustomer sets addresses, pricelist and payment term only. F001-UC005 step 3 says the profile "sets the default sales team", while F001's own UserProfile entity note says "team membership lives on Sales.SalesTeam". The team default has no single source anywhere. | ba reconciles F001/F004 on where the team default comes from. ApplyCustomer then sets the salesperson from the partner when one is set. | ba, mdl |
| C1-13 | P3 | Measured | `Core.Company_DefaultSalesTax`, `Core.Company_DefaultPurchaseTax` (read only by `Company_Edit` and the seed) | F001-UC004 says "Company defaults used by all documents". A new product (`Product_Overview` create object) gets no default taxes. Seeded products get theirs by tax name, not from the company. | Default the taxes in a `ACT_Product_New`, or narrow F001 to say products are not covered. | ba or mdl |
| C1-14 | P3 | Measured | `SalesOrder_NewEdit.lvLines` (no LineType widget); `SalesOrderLine.LineType` (no default) | F004-UC001 step 5 says "Adds section and note lines". On an order they can only come from a template. | Add "+ Section" and "+ Note" link buttons, or record the narrowing. | mdl or ba |
| C1-15 | P3 | Measured | `ACT_SalesOrder_ToggleLock` granted to Sales.User, with `btnLock5` visible to SalesUser; `ACT_Partner_Archive` granted to Partners.Editor (held by SalesUser, Purchaser, Billing) | The BRD actors are narrower: F004-UC005 is SalesManager, F001-UC003 is SalesManager and Administrator. | Human decision: narrow the grants, or widen the BRD actors. | human decision |
| C1-16 | P3 | Judged | `SUB_SalesOrder_Create` (commits and takes a number at **New**); `SalesOrder_NewEdit` has no Discard | F004-UC001 step 7 says "User saves; system assigns the number". Demo beat 1.2 expects the number at New, so the build matches the demo and not the BRD. Each abandoned New leaves an empty numbered quotation. Applying the judgement rule: the working path is real, so correct the BRD rather than rewire. | ba corrects F004-UC001 step 7. Optionally add a Discard action that deletes an empty quotation. | ba |
| C1-17 | P3 | Measured | `btnCancelorder3` (no confirmation) | F004-UC004 step 1 says "system asks for confirmation". | Add a confirmation to the button. | mdl |
| C1-18 | P3 | Judged | `Sales.ENUM_DeliveryStatus.Started` | F007-UC002 lists Started next to PartiallyDelivered and no BRD says what separates them. Row 78 cannot implement it as specified. | ba defines the Started rule, or drops the value, before row 78. | ba |
| — | info | Measured | `Core.SUB_PaymentTerm_ComputeDueDate`, `Products.SUB_UoM_ConvertQuantity` (QUAL004) | Not defects. The consumers are downstream: Invoicing post sets the due date (plan acceptance line 752), and F007-UC002/row 78 for the conversion. They should stop showing as orphans once those rows are built. | none | — |

There are no findings on Core tax configuration (InvoicingManager → Taxes), Products UoM/category/pricelist maintenance, or
Partners create-company/add-contact. Those paths are clean on every hop checked.

## Pass 1: call-graph trace per persona

`./mxcli lint -p app/erpv1.mpr`: 387 issues (0 errors, 123 warnings, 264 info). **QUAL004: 4**: `Core.SUB_PaymentTerm_ComputeDueDate`,
`Partners.UserProfile_Edit`, `Products.SUB_UoM_ConvertPrice`, `Products.SUB_UoM_ConvertQuantity`. `GRAPH_DEAD_ASSETS` lists the same 4 for
these modules (the other 45 rows are marketplace or System). The catalog reference graph does **not** record expression reads
(for example `$Company/QuotationValidityDays` in `SUB_SalesOrder_Create` is missing from `SHOW REFERENCES TO`). Every "never read" claim
above was therefore cross-checked by grepping `mdlsource/` (excluding `_oneoff`) or with DESCRIBE.

| Persona | Path walked | Result |
|---|---|---|
| SalesUser (Act 1 beats 1.1–1.4) | home `SalesOrder_Overview` → `btnNew` → `ACT_SalesOrder_New` → `SalesOrder_NewEdit` → customer OnChange `ACT_SalesOrder_ChangeCustomer` → `SUB_SalesOrder_ApplyCustomer` (payment term from commercial partner) → `+ Add a line` → product OnChange `ACT_SalesOrderLine_ChangeProduct` (price `SUB_Pricelist_GetPrice`, taxes `Product_CustomerTaxes` = "21% (sales)" seeded) → `btnSendmarkassent1` → `btnConfirm2` → `SUB_SalesOrder_Confirm` → stub delivery → `UpdateInvoiceStatus` → `btnSave6` | Every hop is reachable and granted. Beat 1.4's "delivery smart button" waits on row 77, which is known. Defects on the edit paths that sit beside the demo route: C1-03, C1-04, C1-05, C1-06. |
| SalesManager | above, plus Lock, Sales analysis, templates, teams | Lock has no effect (C1-03). Two revenue sources on the report (C1-10). |
| Billing / InvoicingManager / InventoryUser / InventoryManager (Sales.Reader) | menu → `SalesOrder_Overview` → row or New | Dead end (C1-01). This becomes the entry point for beat 1.7 once row 52 is built. |
| InvoicingManager (Core journey) | Configuration → Taxes → `Tax_NewEdit` (Core.Config) | Clean. |
| Administrator | home `Company_Edit` → `Administration.Account_Overview`; Configuration → Numbering | Profiles are not created for new accounts (C1-11). Numbering edits are never saved (C1-07). |
| SalesManager / InventoryManager / PurchaseManager (Products.Manager) | Products, Pricelists, UoM, Categories | Clean. Archiving is ineffective downstream (C1-02). |
| SalesUser / Purchaser / Billing (Partners.Editor) | Contacts → company → add contact | Clean. Archive is wider than the BRD (C1-15) and has no effect (C1-02). |

## Pass 2: state-machine coherence

| Enum / flag | Values reachable now | Writers (Measured) | Who queries the end states | Verdict |
|---|---|---|---|---|
| `Sales.ENUM_SalesOrderStatus` | 4 of 4 | `SUB_SalesOrder_Create` (Quotation), `ACT_SalesOrder_MarkSent` (QuotationSent), `SUB_SalesOrder_Confirm` (SalesOrder), `SUB_SalesOrder_Cancel` (Cancelled), `ACT_SalesOrder_SetToQuotation` (Cancelled→Quotation) | Cancelled: SetToQuotation guard, overview filter. SalesOrder: Lock guard, `UpdateInvoiceStatus`, SalesKpi/SalesAnalysis | The edges match the blueprint diagram one to one. Missing guard: Locked (C1-03). |
| `Core.ENUM_InvoiceStatus` | NothingToInvoice; ToInvoice now only for ordered-quantity products at Confirm; FullyInvoiced not until Invoicing writes `QuantityInvoiced` | `SUB_SalesOrder_Create`, `SUB_SalesOrder_Cancel`, `SUB_SalesOrder_UpdateInvoiceStatus` (Confirm only) | Overview `fInvoiceStatus` dropdown filter (F004-UC006) | Coherent. Recomputation is too narrow (C1-04), and the definition of "invoiced" is unsettled (C1-08). Beat 1.6 ("To invoice" for Office Chair, DeliveredQuantities) depends on row 78 calling `UpdateInvoiceStatus` as F007-UC002 step 3 says. |
| `Sales.ENUM_DeliveryStatus` | 1 of 4 (NotDelivered) | `SUB_SalesOrder_Create` only | Overview `fDeliveryStatus` | This is expected until row 78. Started is undefined (C1-18). |
| `Core.ENUM_LineType` | Product (ApplyProduct); Section/Note only via template | `SUB_SalesOrderLine_ApplyProduct`, `SUB_SalesOrder_ApplyTemplate` | `RecomputeTotals`, `UpdateInvoiceStatus`, `LinesReadyToConfirm` | Manual lines start with an empty LineType, which every reader handles as Product correctly. C1-14. |
| `Products.ENUM_InvoicePolicy` | 2 of 2 (seed: tracked goods → Delivered, else Ordered) | `SUB_Product_EnsureDemo`, `Product_NewEdit` | `UpdateInvoiceStatus` | Coherent. |
| `Partners.ENUM_AddressType` | 4 of 4 (Partner pages) | pages | `SUB_Partner_GetAddress` (Invoice, Delivery) | Coherent. |
| `Active` flags (Partner, Product; Tax, PaymentTerm, UoM, Currency, SalesTeam, QuotationTemplate, Pricelist) | true/false | archive microflows (Partner, Product); others are seed only | Pickers: none (C1-02); only `SUB_Partner_GetAddress` and the UoM reference check | false is a terminal state that nothing queries (C1-02). |
| `SalesOrder.Locked` | true/false | `SUB_SalesOrder_SetLocked` | none apart from display | No downstream reader (C1-03). |

## Pass 3: cross-document consistency (F001/F002/F003/F004, with the F007/F008 seams)

The enum vocabularies agree across the BRDs and the model: `Core.ENUM_InvoiceStatus` has the same 3 values and captions in F004, F005 and the model,
and `ENUM_SalesOrderStatus`/`ENUM_DeliveryStatus` have the same 4 values and captions. F003's `ENUM_InvoicePolicy` is consumed by
F004's invoice-status rule exactly as F003 defines it. Where the documents disagree:
- F001 ↔ F004: where the salesperson and team defaults come from (C1-12); the archive actors (C1-15); the "hidden from pickers" contract that no F004 picker honours (C1-02).
- F002 ↔ F004: the line-unit price conversion is owned by no F004 use case and no plan row (C1-06).
- F003 ↔ F004: re-pricing on a quantity change (C1-06).
- F004 internal: when the number is assigned (C1-16).
- F004 ↔ F007: row 79 has no home (C1-09); Started is undefined (C1-18).
- F004 ↔ F008: what `QuantityInvoiced` means (C1-08).

## Pass 4: goal-to-outcome traceability (all Judged; evidence cited)

| UC | Postcondition | Verdict | Evidence |
|---|---|---|---|
| F001-UC001 | Partner visible in customer/vendor pickers | Met, but over-broad: every partner is visible, not only customers | C1-02 picker datasources |
| F001-UC002 | Child linked to company | Met | `ACT_Partner_AddToPartner`, Partners journey |
| F001-UC003 | Hidden from pickers, history kept | **Not met** (history kept: yes; hidden: no) | C1-02 |
| F001-UC004 | Company defaults used by all documents | Partly: validity days and terms are used; default taxes are not | `SUB_SalesOrder_Create`; C1-13 |
| F001-UC005 | User can log in with roles (profile created) | Partly: login works; profile only at startup | C1-11 |
| F001-UC006 | Next documents use new prefix/number | **Not met**: edits are not saved | C1-07 |
| F002-UC001 | Unit usable on products and lines | Met | `UoMCategory_NewEdit`, line UoM picker |
| F002-UC002 | Stock and prices computed in product unit | **Not met** on sales lines; stock side waits on row 78 | C1-06 |
| F003-UC001 | Product sellable/purchasable as flagged | Partly: the flag is stored, but the sales picker ignores CanBeSold | C1-02 |
| F003-UC002 | Customers on pricelist get its prices | Met for the pick-time price | `ApplyCustomer` → `Partner_Pricelist`, `ApplyProduct` → `GetPrice` |
| F003-UC003 | Line unit price set | Partly: set when the product is picked, not on a quantity change | C1-06 |
| F003-UC004 | Product hidden from pickers | **Not met** | C1-02 |
| F004-UC001 | Quotation with number S000nn | Met (number at New, see C1-16) | Sales journey, `SUB_SalesOrder_Create` |
| F004-UC002 | Status QuotationSent | Met | `ACT_SalesOrder_MarkSent` |
| F004-UC003 | SalesOrder, order date, delivery created | Met apart from the delivery, which is the known stub | `SUB_SalesOrder_Confirm` |
| F004-UC004 | Cancelled / back to Quotation | Met, without the lock precondition or the confirmation | C1-03, C1-17 |
| F004-UC005 | Locked orders cannot be edited | **Not met** | C1-03 |
| F004-UC006 | Follow up to invoice/deliver | Met as a filter; the values become meaningful only after rows 52/78 | Overview dropdown filters |
| F004-UC007 | Analyse sales | Met, with two revenue sources | C1-10 |
| F004-UC008 | Templates/teams available on quotations | Met; applying a template is destructive on confirmed orders | C1-04 |

## Pass 5: one displayed fact, one source

`grep -n 'Displayed fact:' PROJECT.md` returns nothing: **0 displayed facts registered.**
Unregistered facts found on screen: order status (`txtStatus` pill and the overview column), invoice status (`cmbInvoiceStatus` and the overview column),
delivery status (`cmbDeliveryStatus` and the overview column), order totals (NewEdit totals and the overview AmountTotal), and confirmed revenue
(SalesAnalysis_Report KPI and charts). Each of the first four is read from one stored attribute on every page that shows it, so those are consistent today.
Confirmed revenue has two sources (C1-10). Registration question for the main session: should C1-10's fix, and row 78's change to how delivery and invoice
status are computed, be logged as `Displayed fact:` rows before Inventory and Invoicing start writing these attributes?

## Completion

- Passes run: 5 of 5. Modules in scope: 4 of 4 (Core, Products, Partners, Sales).
- Findings: 18 (1 P1, 9 P2, 8 P3), plus 1 informational row. 14 Measured (two of them, C1-01 and C1-07, also have a Judged runtime part), 4 Judged.
- QUAL004: 4 of 4 resolved (2 awaiting planned consumers, 1 with no planned consumer → C1-06, 1 unreachable page → C1-11).
- Use cases traced: 20 of 20 (F001 6, F002 2, F003 4, F004 8). Met 11, partly met 4, not met 5 (F001-UC003, F001-UC006, F002-UC002 on the sales-line side, F003-UC004, F004-UC005).
- Lifecycle enums/flags checked: 8 of 8.
- **0 of 0 registered facts checked, 6 page references to raw status/total attributes (all single-source), 1 fact with two sources.**
- Workflows in scope: 0 (Purchasing approval is outside this cluster).
- Still owed, not done here because this pass may write only this report: `coherence-cadence.sh /home/user/erpv1 --record` after
  `node tests/e2e/full-app-walkthrough.js --built-only` (the cadence script reports **DUE** for this cluster).
