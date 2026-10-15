wiring · Inventory · 78 of 112 interactive elements swept, 7 of 7 pages   (N = DOM + unshown conditional; N/A and UNREACHED are in N but not swept)
  0 failed (no observable effect), 0 error-on-click, 0 not interactable, 78 passed,
  15 N/A by design (state recorded), 19 unreached (condition shown)
  Read as: these elements are wired to something. Not that the something is correct.
  Shell (side-nav items + Sign out, listed separately, not in the totals above): 30 of 30 PASS

Users: warehouse.user (Inventory.User) for Overview (dashboard), Transfers, Stock; inventory.manager (Inventory.Manager) for Reorder rules and Configuration > Warehouse (and the manager-only Remove link on transfer lines); sales.user on Sales.SalesOrder_NewEdit (Delivery smart button) and purchaser on Purchasing.PurchaseOrder_NewEdit (Receipt smart button). One browser at a time, signed out between users. Transfer_NewEdit swept per state: Draft (WH/INT/00002), Ready (WH/INT/00002..00004), Waiting (WH/OUT/00054..56 from three Sales journey runs); Visible conditions: Mark as to do (Draft), Check availability (Waiting), Validate (Waiting|Ready), Cancel transfer (Draft|Waiting|Ready) - each swept in a satisfying state (Draft Cancel is the same widget, not clicked separately). A Done/Cancelled transfer shows no header buttons (observed on WH/OUT/00054 after Done).
Side effects on records created by this sweep: internal transfers WH/INT/00002 (left Ready, line has product Office Chair, demand 0), WH/INT/00003 (Ready, its line removed by the Remove sweep), WH/INT/00004 (Cancelled); three confirmed sales orders S00068/S00069/S00070 from the Sales journey with deliveries WH/OUT/00054 (Waiting -> Done via Create backorder, processed 2), WH/OUT/00055 (Waiting -> Done via No backorder, processed 2), WH/OUT/00056 (Cancelled), plus backorder WH/OUT/00057 (Waiting); one operation type line added to Main warehouse and removed again (3 types remain: Receipts, Delivery orders, Internal transfers); Run scheduler clicked twice, each time "1 rule(s) added to an RFQ" (an RFQ to Gemini Furniture was created/extended - not identified further); Apply on Desk Combination with counted 26 = quantity 26 ("0 stock level(s) corrected", no change). No Clear selection was clicked on any seeded row; the only Clear selection clicks were on the Draft transfer WH/INT/00002 and were not saved (reopened: values unchanged).
STOCK CONSEQUENCE (caused by this sweep, disclosed): validating WH/OUT/00054 and WH/OUT/00055 (2 processed each, only 2 chairs on hand) moved the seeded Office Chair / WH/Stock quantity from 2 to -2; Validate does not stop at zero on-hand. Desk Combination unchanged (26). Please re-seed or count the chair row if a positive balance matters to journeys.
FINDING: Transfer_NewEdit has no Save and edits to a line are not persisted by the header buttons. On WH/INT/00004 I typed Demand quantity 9,999.00 on the line (field showed 9,999.00), clicked Mark as to do (status -> Ready), and OQL then showed StockMove.DemandQuantity = 0. The typed Quantity/Demand is therefore lost unless something commits the line - Validate after typing a processed quantity may be reading the old value (the popup path only fired here because the Sales delivery already had Quantity 2 < Demand 5 from reservation). Worth a journey that types a quantity in the UI and then validates.
FINDING: Warehouse_Edit Save did not persist typed values on a newly added operation-type line: I added a line, typed Name "Sweep test type" and Sequence code "SWP", clicked Save (went to the dashboard); on reopening the new line's Name was empty (the line itself had been created by + Add a line). Same pattern as above; the Save microflow gets the Warehouse only.
FINDING: warehouse.user (Inventory.User) has no Remove link on transfer lines (0 in the DOM; present for inventory.manager) - the same entity-delete-access pattern as the Purchaser on vendor prices; confirm against the brief.
FINDING: Inventory overview shows 1 tile (Delivery orders) of 3 operation types: the TransferSummary view returns only types with ready/waiting transfers, so Receipts and Internal transfers have no tile and no "Open transfers" link when idle.
Dashboard stock grid: no onClick (data cell reclassified N/A by design). Reorder rules page has only Run scheduler and the row editors - there is no "Order once" button, and no way to add/remove a rule. Validate with demand 0 shows a warning dialog and leaves the transfer Ready (wired, correct refusal).

DATA INTEGRITY (OQL after the sweep): SELECT l.Quantity, product, location FROM Inventory.StockLevel ->
| p                | loc      | Quantity |
| Office Chair     | WH/Stock | -2       |
| Desk Combination | WH/Stock | 26       |
(2 rows) - every row still has a product and a location. Also intact: reorder rule Office Chair / WH/Stock / Gemini Furniture 10..30; warehouse Main warehouse with stock location WH/Stock and its 3 operation types.

### Inventory.Inventory_Dashboard (warehouse.user)

| element | action | verdict | observation |
|---|---|---|---|
| a[button] "Open transfers" (btnOpenTransfers) | click | PASS | url->/p/transfer-overview; dom changed; 1 xas req; title Transfers |
| div[button] "sort Reference" (gridStock) | click | PASS | dom changed; 1 xas req |
| button[combobox] "Contains" (fProductReference) | click | PASS | dom changed [Contains ⏎ Starts with ⏎ Ends with ⏎ Greater than ⏎ Greater than or ] |
| div[button] "sort Product" (gridStock) | click | PASS | dom changed; 1 xas req |
| button[combobox] "Contains" (fProductName) | click | PASS | dom changed [/Contains ⏎ Starts with ⏎ Ends with ⏎ Greater than ⏎ Greater than or] |
| div[button] "sort Location" (gridStock) | click | PASS | dom changed; 1 xas req |
| button[combobox] "Contains" (fLocationName) | click | PASS | dom changed [//Contains ⏎ Starts with ⏎ Ends with ⏎ Greater than ⏎ Greater than o] |
| div[button] "sort On hand" (gridStock) | click | PASS | dom changed; 1 xas req |
| button[combobox] "Equal" (fOnHand) | click | PASS | dom changed [///Greater than ⏎ Greater than or equal ⏎ Equal ⏎ Not equal ⏎ Smalle] |
| button "Column selector" (gridStock) | click | PASS | dom changed |
| div[gridcell] "FURN_7800" (gridStock) | click | N/A (by design) | grid has no onClick in its page definition (DESCRIBE PAGE) - read-only summary grid, a data cell is not an affordance; click correctly does nothing |
| button "Go to first page" (gridStock) | click | N/A (by design) | disabled; pager status: 1 to 2 of 2 |
| button "Go to previous page" (gridStock) | click | N/A (by design) | disabled; pager status: 1 to 2 of 2 |
| button "Go to next page" (gridStock) | click | N/A (by design) | disabled; pager status: 1 to 2 of 2 |
| button "Go to last page" (gridStock) | click | N/A (by design) | disabled; pager status: 1 to 2 of 2 |
| a[button] "Open transfers" (btnOpenTransfers) on the other operation-type tiles | click | UNREACHED | TransferSummary view returns 1 row (Delivery orders) - the tile list only shows operation types with ready/waiting transfers, so the 2 other tiles do not exist; same widget as the PASS above |

### Inventory.Transfer_Overview (warehouse.user)

| element | action | verdict | observation |
|---|---|---|---|
| button "New" (btnNew) | click | PASS | dom changed [/////]; 11 xas req; title WH/INT/00002 |
| div[button] "sort Number" (gridMain) | click | PASS | dom changed |
| button[combobox] "Contains" (fNumber) | click | PASS | dom changed [Contains ⏎ Starts with ⏎ Ends with ⏎ Greater than ⏎ Greater than or ] |
| div[button] "sort Partner" (gridMain) | click | PASS | dom changed; 1 xas req |
| div[button] "sort Scheduled date" (gridMain) | click | PASS | dom changed; 1 xas req |
| button[combobox] "Equal" (fScheduledDate) | click | PASS | dom changed [/Between ⏎ Greater than ⏎ Greater than or equal ⏎ Equal ⏎ Not equal ⏎ ] |
| button "Show calendar" (fScheduledDate) | click | PASS | dom changed [//27282930123 ⏎ 45678910 ⏎ 11121314151617 ⏎ 18192021222324 ⏎ 2526272] |
| div[button] "sort Source document" (gridMain) | click | PASS | dom changed; 1 xas req |
| button[combobox] "Contains" (fSourceDocument) | click | PASS | dom changed [//Contains ⏎ Starts with ⏎ Ends with ⏎ Greater than ⏎ Greater than o] |
| div[button] "sort Operation type" (gridMain) | click | PASS | dom changed; 1 xas req |
| div[button] "sort Status" (gridMain) | click | PASS | dom changed; 1 xas req |
| div[combobox] "filter" (fStatus) | click | PASS | dom changed [///Draft ⏎ Waiting ⏎ Ready ⏎ Done ⏎ Cancelled] |
| button "Column selector" (gridMain) | click | PASS | dom changed |
| div[gridcell] "WH/OUT/00053" (gridMain) | click | PASS | dom changed [////////]; 17 xas req; title WH/OUT/00053 |
| button "Go to first page" (gridMain) | click | N/A (by design) | disabled; pager status: 1 to 20 of 27 |
| button "Go to previous page" (gridMain) | click | N/A (by design) | disabled; pager status: 1 to 20 of 27 |
| button "Go to next page" (gridMain) | click | PASS | dom changed; 1 xas req |
| button "Go to last page" (gridMain) | click | PASS | dom changed; 1 xas req |

### Inventory.Transfer_NewEdit — header, state Draft (WH/INT/00002 created by New)

| element | action | verdict | observation |
|---|---|---|---|
| input[combobox] "" (cmbTransferPartner) | click | PASS | dom changed [Ada Admin ⏎ Azure Interior ⏎ Azure Interior, Accounts ⏎ Bea Billin] |
| input[combobox] "" (cmbTransferOperationType) | click | PASS | dom changed [/Delivery orders ⏎ Internal transfers ⏎ Receipts////]; 1 xas req |
| button "Clear selection" (cmbTransferOperationType) | click | PASS | dom changed; 1 xas req |
| input[combobox] "" (cmbTransferSourceLocation) | click | PASS | dom changed [//Customers ⏎ Inventory adjustment ⏎ Vendors ⏎ WH/Stock///]; 1 xas req |
| button "Clear selection" (cmbTransferSourceLocation) | click | PASS | dom changed; 1 xas req |
| input[combobox] "" (cmbTransferDestinationLocation) | click | PASS | dom changed [///Customers ⏎ Inventory adjustment ⏎ Vendors ⏎ WH/Stock//]; 1 xas req |
| button "Clear selection" (cmbTransferDestinationLocation) | click | PASS | dom changed; 1 xas req |
| button "Show date picker" (dpScheduledDate) | click | PASS | dom changed |
| button "Show date picker" (dpDeadline) | click | PASS | dom changed |
| button "Show date picker" (dpDateDone) | click | N/A (by design) | disabled |
| input[combobox] "" (cmbTransferBackorder) | click | PASS | dom changed [////WH/IN/00012 ⏎ WH/IN/00013 ⏎ WH/INT/00001 ⏎ WH/INT/00002 ⏎ WH/OUT] |
| input[combobox] "" (cmbTransferResponsible) | click | PASS | dom changed [/////Ada Admin ⏎ Bea Billing ⏎ Ingrid Warehouse ⏎ Ivan Ledger ⏎ Marc] |
| button "Mark as to do" (btnMarkastodo1) on WH/INT/00002 (Draft, one line) | click | PASS | dom changed; 3 xas req; status Draft -> Ready (repeated on WH/INT/00003 and 00004, same result). Visible only in Draft. |
| button "Cancel transfer" (btnCanceltransfer3) on WH/INT/00004 (Ready) | click | PASS | dom changed; 3 xas req; status Ready -> Cancelled |
| button "Cancel transfer" (btnCanceltransfer3) on WH/OUT/00056 (Waiting) | click | PASS | dom changed; 3 xas req; status Waiting -> Cancelled. (Draft state satisfied by the same widget; not clicked separately.) |
| button "Check availability" (btnCheckavailability2) on WH/OUT/00054 (Waiting) | click | PASS | dom changed; 3 xas req; status stayed Waiting (stock short: 2 of 5 reserved) |
| button "Validate" (btnValidate0) on WH/OUT/00054 (Waiting, processed 2 < demand 5) | click | PASS | dom changed; 1 xas req; opened ValidateTransfer_Popup |
| button "Validate" (btnValidate0) on WH/INT/00002 (Ready, demand 0) | click | PASS | dom changed; 1 xas req; warning dialog "Enter a quantity on at least one operation before validating." ; status stayed Ready |
| button "OK" in that warning dialog | click | PASS | dom changed; dialog closed |
| button "Validate" (btnValidate0) on a transfer with processed = demand (no popup, completes) | click | UNREACHED | would move 5 chairs off the seeded Office Chair stock row; the popup path (Validate -> Create backorder / No backorder) already completes the transfer to Done |

### Inventory.Transfer_NewEdit — lines (+ Add a line, line widgets, Remove)

| element | action | verdict | observation |
|---|---|---|---|
| a[button] "+ Add a line" (btnAddLine) | click | PASS | dom changed [////////]; 4 xas req |
| input[combobox] "" (lncmbStockMoveProduct) | click | PASS | dom changed [//////Cable Pack ⏎ Desk Combination ⏎ Installation ⏎ Journey Chair] |
| input[combobox] "" (lncmbStockMoveUoM) | click | PASS | dom changed [///////Days ⏎ Dozens ⏎ Hours ⏎ Units ⏎ g ⏎ kg/] |
| input[combobox] "" (lncmbStatus) | click | N/A (by design) | disabled |
| a[button] "Remove" (btnLineDelete) as warehouse.user | click | UNREACHED | not rendered for warehouse.user (0 in the DOM on a transfer that has a line); delete access is Inventory.Manager only - swept as inventory.manager below |
| a[button] "Remove" (btnLineDelete) as inventory.manager on WH/INT/00003 line | click | PASS | dom changed; 2 xas req; line rows 1 -> 0 |

### Inventory.ValidateTransfer_Popup (reached by Validate on WH/OUT/00054 and 00055; processed 2 < demand 5)

| element | action | verdict | observation |
|---|---|---|---|
| button "Cancel" (pbtnCancel) on WH/OUT/00054 | click | PASS | dom changed; 1 xas req; popup closed, transfer stayed Waiting |
| button "Create backorder" (pbtnCreatebackorder) on WH/OUT/00054 | click | PASS | dom changed; 3 xas req; transfer -> Done; backorder WH/OUT/00057 (Waiting) created |
| button "×" (close) on WH/OUT/00055 | click | PASS | dom changed; 1 xas req; popup closed, transfer stayed Waiting |
| button "No backorder" (pbtnNobackorder) on WH/OUT/00055 | click | PASS | dom changed; 3 xas req; transfer -> Done, no backorder |

### Order-form smart buttons that open Transfer_NewEdit

| element | action | verdict | observation |
|---|---|---|---|
| a[button] "Delivery" (lnkSmartDelivery) on Sales.SalesOrder_NewEdit, confirmed order S00067, as sales.user | click | PASS | dom changed; 15 xas req; opened transfer WH/OUT/00050 (Transfer_NewEdit) |
| a[button] "Receipt" (lnkSmartReceipt) on Purchasing.PurchaseOrder_NewEdit, confirmed PO P00033, as purchaser | click | PASS | dom changed; 14 xas req; opened receipt WH/IN/00012 (Transfer_NewEdit) |
| a[button] "Receipt" (lnkSmartReceipt) on confirmed PO P00018 (no goods to receive), as purchaser | click | PASS | dom changed; 1 xas req; information dialog "This order has no receipt (it has no goods to receive)." - wired, correct refusal |

### Inventory.StockLevel_Overview (warehouse.user)

| element | action | verdict | observation |
|---|---|---|---|
| input[combobox] "" (lncmbStockLevelProduct) | click | N/A (by design) | disabled |
| input[combobox] "" (lncmbStockLevelLocation) | click | N/A (by design) | disabled |
| button "Show date picker" (lndpScheduledCountDate) | click | PASS | dom changed |
| input[combobox] "" (lncmbStockLevelProduct) | click | N/A (by design) | disabled |
| input[combobox] "" (lncmbStockLevelLocation) | click | N/A (by design) | disabled |
| button "Show date picker" (lndpScheduledCountDate) | click | PASS | dom changed |
| a[button] "Apply" (btnRowAction) on Desk Combination / WH/Stock, counted 26 typed = current quantity 26 | click | PASS | dom changed; 2 xas req; dialog "Counts applied: 0 stock level(s) corrected." (no stock change; quantity still 26) |
| button "OK" in the "Counts applied" dialog | click | PASS | dom changed; dialog closed |
| a[button] "Apply" (btnRowAction) on Office Chair / WH/Stock | click | UNREACHED | no count typed; same widget as the PASS above; not clicked so the seeded row is left alone |

### Inventory.ReorderRule_Overview (inventory.manager)

| element | action | verdict | observation |
|---|---|---|---|
| button "Run scheduler" (btnRunscheduler1) | click | PASS | dom changed; 1 xas req; dialog "Reorder rules run: 1 rule(s) added to an RFQ." (clicked twice) |
| button "OK" in the Run scheduler dialog | click | PASS | dom changed; dialog closed |
| input[combobox] "" (lncmbReorderRuleProduct) | click | N/A (by design) | disabled |
| input[combobox] "" (lncmbReorderRuleLocation) | click | N/A (by design) | disabled |
| input[combobox] "" (lncmbReorderRuleVendor) | click | PASS | dom changed [//Ada Admin ⏎ Azure Interior ⏎ Azure Interior, Accounts ⏎ Bea Bill]; 1 xas req |
| button "Clear selection" (lncmbReorderRuleVendor) | click | UNREACHED | SEEDED row (Office Chair WH/Stock) - OnChange saves, clearing would wipe the vendor; same widget type proven by opening the vendor combobox |
| checkbox "Automatic" (lncbAutomatic) on rule Office Chair WH/Stock | click | UNREACHED | OnChange: save changes on the SEEDED rule - toggling would change a seeded value; the page has no "Order once" button and no add/remove for rules |

### Inventory.Warehouse_Edit (inventory.manager)

| element | action | verdict | observation |
|---|---|---|---|
| button "Save" (btnSave0) | click | PASS | dom changed; 3 xas req; url->/p/inventory-dashboard (clicked after adding a line on the seeded warehouse; no seeded value edited) |
| input[combobox] "" (cmbWarehouseAddress) | click | PASS | dom changed [Ada Admin ⏎ Azure Interior ⏎ Azure Interior, Accounts ⏎ Bea Billin] |
| input[combobox] "" (cmbWarehouseStockLocation) | click | PASS | dom changed [/Customers ⏎ Inventory adjustment ⏎ Vendors ⏎ WH/Stock/////////]; 1 xas req |
| button "Clear selection" (cmbWarehouseStockLocation) | click | UNREACHED | SEEDED warehouse "Main warehouse" / its operation types - Clear selection would blank a required pick; Save/Add/Remove swept below on a line created by this sweep |
| input[combobox] "" (lncmbKind) | click | PASS | dom changed [//Receipt ⏎ Delivery ⏎ Internal transfer////////] |
| button "Clear selection" (lncmbKind) | click | UNREACHED | SEEDED warehouse "Main warehouse" / its operation types - Clear selection would blank a required pick; Save/Add/Remove swept below on a line created by this sweep |
| input[combobox] "" (lncmbOperationTypeDefaultSource) | click | PASS | dom changed [///Customers ⏎ Inventory adjustment ⏎ Vendors ⏎ WH/Stock///////]; 1 xas req |
| button "Clear selection" (lncmbOperationTypeDefaultSource) | click | UNREACHED | SEEDED warehouse "Main warehouse" / its operation types - Clear selection would blank a required pick; Save/Add/Remove swept below on a line created by this sweep |
| input[combobox] "" (lncmbOperationTypeDefaultDestination) | click | PASS | dom changed [////Customers ⏎ Inventory adjustment ⏎ Vendors ⏎ WH/Stock//////]; 1 xas req |
| button "Clear selection" (lncmbOperationTypeDefaultDestination) | click | UNREACHED | SEEDED warehouse "Main warehouse" / its operation types - Clear selection would blank a required pick; Save/Add/Remove swept below on a line created by this sweep |
| a[button] "Remove" (btnLineDelete) | click | UNREACHED | SEEDED operation type row; same widget proven on the line created by this sweep (PASS below) |
| input[combobox] "" (lncmbKind) | click | PASS | dom changed [/////Receipt ⏎ Delivery ⏎ Internal transfer/////] |
| button "Clear selection" (lncmbKind) | click | UNREACHED | SEEDED warehouse "Main warehouse" / its operation types - Clear selection would blank a required pick; Save/Add/Remove swept below on a line created by this sweep |
| input[combobox] "" (lncmbOperationTypeDefaultSource) | click | PASS | dom changed [//////Customers ⏎ Inventory adjustment ⏎ Vendors ⏎ WH/Stock////]; 1 xas req |
| button "Clear selection" (lncmbOperationTypeDefaultSource) | click | UNREACHED | SEEDED warehouse "Main warehouse" / its operation types - Clear selection would blank a required pick; Save/Add/Remove swept below on a line created by this sweep |
| input[combobox] "" (lncmbOperationTypeDefaultDestination) | click | PASS | dom changed [///////Customers ⏎ Inventory adjustment ⏎ Vendors ⏎ WH/Stock///]; 1 xas req |
| button "Clear selection" (lncmbOperationTypeDefaultDestination) | click | UNREACHED | SEEDED warehouse "Main warehouse" / its operation types - Clear selection would blank a required pick; Save/Add/Remove swept below on a line created by this sweep |
| a[button] "Remove" (btnLineDelete) | click | UNREACHED | SEEDED operation type row; same widget proven on the line created by this sweep (PASS below) |
| input[combobox] "" (lncmbKind) | click | PASS | dom changed [////////Receipt ⏎ Delivery ⏎ Internal transfer//] |
| button "Clear selection" (lncmbKind) | click | UNREACHED | SEEDED warehouse "Main warehouse" / its operation types - Clear selection would blank a required pick; Save/Add/Remove swept below on a line created by this sweep |
| input[combobox] "" (lncmbOperationTypeDefaultSource) | click | PASS | dom changed [/////////Customers ⏎ Inventory adjustment ⏎ Vendors ⏎ WH/Stock/]; 1 xas req |
| button "Clear selection" (lncmbOperationTypeDefaultSource) | click | UNREACHED | SEEDED warehouse "Main warehouse" / its operation types - Clear selection would blank a required pick; Save/Add/Remove swept below on a line created by this sweep |
| input[combobox] "" (lncmbOperationTypeDefaultDestination) | click | PASS | dom changed [//////////Customers ⏎ Inventory adjustment ⏎ Vendors ⏎ WH/Stock]; 1 xas req |
| button "Clear selection" (lncmbOperationTypeDefaultDestination) | click | UNREACHED | SEEDED warehouse "Main warehouse" / its operation types - Clear selection would blank a required pick; Save/Add/Remove swept below on a line created by this sweep |
| a[button] "Remove" (btnLineDelete) | click | UNREACHED | SEEDED operation type row; same widget proven on the line created by this sweep (PASS below) |
| a[button] "+ Add a line" (btnAddLine) | click | PASS | dom changed; 4 xas req; operation-type rows 3 -> 4 (line created by this sweep) |
| a[button] "Remove" (btnLineDelete) on the operation-type line created by this sweep | click | PASS | dom changed; confirmation dialog; Remove-button count 4 -> 3 |
| button "Cancel" in the Remove confirmation dialog | click | PASS | dom changed; dialog closed, row kept (rows still 4) |
| button "OK" in the Remove confirmation dialog | click | PASS | dom changed; 2 xas req; rows 4 -> 3 |

### Shell: side navigation tree (warehouse.user)

| element | action | verdict | observation |
|---|---|---|---|
| nav item "Home" | click | PASS | -> /p/home title=Welcome |
| nav item "Sales" | click | PASS | group toggle; dom true |
| nav item "Quotations & orders" | click | PASS | -> /p/sales-order-overview title=Quotations & sales orders |
| nav item "Purchase" | click | PASS | group toggle; dom true |
| nav item "RFQs & orders" | click | PASS | -> /p/purchase-order-overview title=Requests for quotation & purchase orders |
| nav item "Inventory" | click | PASS | group toggle; dom true |
| nav item "Overview" | click | PASS | -> /p/inventory-dashboard title=Inventory overview |
| nav item "Transfers" | click | PASS | -> /p/transfer-overview title=Transfers |
| nav item "Stock" | click | PASS | -> /p/stock-level-overview title=Stock |
| nav item "Products" | click | PASS | group toggle; dom true |
| nav item "Products" | click | PASS | -> /p/product-overview title=Products |
| Sign out (btnSignOut) | click | PASS | session ended; next login for the same user succeeded |

### Shell: side navigation tree (inventory.manager)

| element | action | verdict | observation |
|---|---|---|---|
| nav item "Home" | click | PASS | -> /p/home title=Welcome |
| nav item "Sales" | click | PASS | group toggle; dom true |
| nav item "Quotations & orders" | click | PASS | -> /p/sales-order-overview title=Quotations & sales orders |
| nav item "Purchase" | click | PASS | group toggle; dom true |
| nav item "RFQs & orders" | click | PASS | -> /p/purchase-order-overview title=Requests for quotation & purchase orders |
| nav item "Inventory" | click | PASS | group toggle; dom true |
| nav item "Overview" | click | PASS | -> /p/inventory-dashboard title=Inventory overview |
| nav item "Transfers" | click | PASS | -> /p/transfer-overview title=Transfers |
| nav item "Stock" | click | PASS | -> /p/stock-level-overview title=Stock |
| nav item "Reorder rules" | click | PASS | -> /p/reorder-rule-overview title=Reorder rules |
| nav item "Products" | click | PASS | group toggle; dom true |
| nav item "Products" | click | PASS | -> /p/product-overview title=Products |
| nav item "Pricelists" | click | PASS | -> /p/pricelist-overview title=Pricelists |
| nav item "Configuration" | click | PASS | group toggle; dom true |
| nav item "Warehouse" | click | PASS | -> /p/warehouse-edit title=Main warehouse |
| nav item "Units of measure" | click | PASS | -> /p/uo-m-category-overview title=Units of measure |
| nav item "Product categories" | click | PASS | -> /p/product-category-overview title=Product categories |
| Sign out (btnSignOut) | click | PASS | session ended; next login for the same user succeeded |

