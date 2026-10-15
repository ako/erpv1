wiring · Purchasing · 99 of 126 interactive elements swept, 6 of 6 pages   (N = DOM + unshown conditional; N/A and UNREACHED are in N but not swept)
  0 failed (no observable effect), 0 error-on-click, 1 not interactable (overlay), 98 passed,
  25 N/A by design (state recorded), 2 unreached (condition shown)
  Read as: these elements are wired to something. Not that the something is correct.
  Shell (side-nav items + Sign out, listed separately, not in the totals above): 24 of 24 PASS

Users: purchaser (Purchasing.User) for RFQs & orders and Vendor prices; purchase.manager (Purchasing.Manager) for Approvals inbox, Approval task, Purchase analysis (Manager-only grants) and for the VendorPrice Remove link. RFQ state machine swept on ONE fresh order P00032 (created by New): RFQ -> Cancelled -> RFQ -> RFQ sent; Confirm refused by a dialog (no vendor), state stayed RFQ sent. Lock swept on journey order P00018 and restored (unlocked). The approval task page needs a "To approve" journey PO: opened from the inbox; Approve swept on P00025 (-> Purchase order, left approved), Reject swept on P00024 (asks for a reason, state unchanged). Visible conditions on PurchaseOrder_NewEdit: Send (RFQ), Confirm (RFQ|RFQSent), Cancel (RFQ|RFQSent|PurchaseOrder), Set to RFQ (Cancelled), Lock (PurchaseOrder) - all swept in a satisfying state; dpConfirmationDate disabled N/A.
Side effects on records created by this sweep: POs P00031 (blank, overview New sweep) and P00032 (left in RFQ sent); P00025 approved; extra blank vendor-price rows were created by the "+ Add a line" sweeps and removed by the 3 Remove sweeps.
DATA INCIDENT (caused by this sweep, disclosed): on Purchasing.VendorPrice_Overview the vendor/product comboboxes use OnChange: save changes, and my first sweeps clicked their "Clear selection" buttons on the SEEDED rows, which saved immediately - the 3 existing vendor-price rows lost their vendor/product. I re-selected them through the UI afterwards (Gemini Furniture + Office Chair 65/5, Gemini Furniture + Desk Combination 420/7, and a third 65/5 row restored as Gemini Furniture + Office Chair - the original of that third row is a best guess from the seed SUB_VendorPrice_EnsureDemo and the earlier screenshot). Please re-run the seed / inspect those 3 rows.
FINDING: purchaser has no Remove link on the vendor-price lines at all (page is granted to Purchasing.User; the link is only rendered for purchase.manager) - may be intended (entity delete access), worth confirming against the brief.
FINDING: Order deadline calendar button on the PO overview is not clickable (clipped under the Vendor header).
Approval task page: the products grid has no onClick (data cells reclassified N/A by design).

### Purchasing.PurchaseOrder_Overview

| element | action | verdict | observation |
|---|---|---|---|
| button "New" (btnNew) | click | PASS | dom changed; 8 xas req; title P00031 |
| div[button] "sort Number" (gridMain) | click | PASS | dom changed; 1 xas req |
| button[combobox] "Contains" (fNumber) | click | PASS | dom changed [Contains ⏎ Starts with ⏎ Ends with ⏎ Greater than ⏎ Greater than or ] |
| div[button] "sort Order deadline" (gridMain) | click | PASS | dom changed; 1 xas req |
| button[combobox] "Equal" (fOrderDeadline) | click | PASS | dom changed [/Between ⏎ Greater than ⏎ Greater than or equal ⏎ Equal ⏎ Not equal ⏎ ] |
| button "Show calendar" (fOrderDeadline) | click | FAIL (not interactable) | Playwright: click timeout - the Vendor column header subtree (DataGrid7-column2) intercepts pointer events; the Order deadline filter calendar button is clipped under the next header (screenshot confirmed). Not clickable with the mouse. |
| div[button] "sort Vendor" (gridMain) | click | PASS | dom changed; 1 xas req |
| div[button] "sort Buyer" (gridMain) | click | PASS | dom changed; 1 xas req |
| div[button] "sort Amount total" (gridMain) | click | PASS | dom changed; 1 xas req |
| button[combobox] "Equal" (fAmountTotal) | click | PASS | dom changed [//Greater than ⏎ Greater than or equal ⏎ Equal ⏎ Not equal ⏎ Smaller] |
| div[button] "sort Status" (gridMain) | click | PASS | dom changed; 1 xas req |
| div[combobox] "filter" (fStatus) | click | PASS | dom changed [///Request for quotation ⏎ RFQ sent ⏎ To approve ⏎ Purchase order ⏎ ] |
| div[button] "sort Receipt status" (gridMain) | click | PASS | dom changed; 1 xas req |
| div[combobox] "filter" (fReceiptStatus) | click | PASS | dom changed [////Not received ⏎ Partially received ⏎ Fully received/] |
| div[button] "sort Billing status" (gridMain) | click | PASS | dom changed; 1 xas req |
| div[combobox] "filter" (fBillingStatus) | click | PASS | dom changed [/////Nothing to invoice ⏎ To invoice ⏎ Fully invoiced] |
| button "Column selector" (gridMain) | click | PASS | dom changed |
| div[gridcell] "P00018" (gridMain) | click | PASS | dom changed [////////]; 15 xas req; title P00018 |
| button "Go to first page" (gridMain) | click | N/A (by design) | disabled; pager status: 1 to 14 of 14 |
| button "Go to previous page" (gridMain) | click | N/A (by design) | disabled; pager status: 1 to 14 of 14 |
| button "Go to next page" (gridMain) | click | N/A (by design) | disabled; pager status: 1 to 14 of 14 |
| button "Go to last page" (gridMain) | click | N/A (by design) | disabled; pager status: 1 to 14 of 14 |

### Purchasing.PurchaseOrder_NewEdit — state RFQ (fresh order P00032, one line added)

| element | action | verdict | observation |
|---|---|---|---|
| button "Save" (btnSave6) | click | PASS | dom changed [/////]; 2 xas req; title Requests for quotation & purchase orders | OBSERVATION: Save on a blank RFQ (no vendor) succeeded and returned to the overview |
| input[combobox] "" (cmbPurchaseOrderVendor) | click | PASS | dom changed [Gemini Furniture ⏎ Ready Mat ⏎ Wood Corner////////] |
| input[combobox] "" (cmbPurchaseOrderCurrency) | click | PASS | dom changed [/EUR ⏎ USD///////]; 1 xas req |
| button "Clear selection" (cmbPurchaseOrderCurrency) | click | PASS | dom changed; 1 xas req |
| button "Show date picker" (dpOrderDeadline) | click | PASS | dom changed |
| button "Show date picker" (dpExpectedArrival) | click | PASS | dom changed |
| input[combobox] "" (cmbPurchaseOrderBuyer) | click | PASS | dom changed [//Ada Admin ⏎ Bea Billing ⏎ Ingrid Warehouse ⏎ Ivan Ledger ⏎ Marc De]; 1 xas req |
| button "Clear selection" (cmbPurchaseOrderBuyer) | click | PASS | dom changed; 1 xas req |
| input[combobox] "" (cmbPurchaseOrderPaymentTerm) | click | PASS | dom changed [///15 Days ⏎ 30 Days ⏎ Immediate Payment/////] |
| input[combobox] "" (cmbReceiptStatus) | click | N/A (by design) | disabled |
| input[combobox] "" (cmbBillingStatus) | click | N/A (by design) | disabled |
| input[combobox] "" (lncmbPurchaseOrderLineProduct) | click | PASS | dom changed [//////Cable Pack ⏎ Desk Combination ⏎ Journey Chair ⏎ Journey Chai] |
| input[combobox] "" (lncmbPurchaseOrderLineUoM) | click | PASS | dom changed [///////Days ⏎ Dozens ⏎ Hours ⏎ Units ⏎ g ⏎ kg/] |
| input[combobox] "" (lncmbPurchaseOrderLineTaxes) | click | PASS | dom changed [////////21% (purchase) ⏎ 21% (sales) ⏎ 9% (sales) ⏎ Journey tax 5%] |
| a[button] "Remove" (btnLineDelete) | click | PASS | dom changed [/////]; 2 xas req |
| a[button] "+ Add a line" (btnAddLine) | click | PASS | dom changed [////////]; 5 xas req |

### Purchasing.PurchaseOrder_NewEdit — Cancel order (RFQ -> Cancelled)

| element | action | verdict | observation |
|---|---|---|---|
| button "Cancel order" (btnCancelorder3) | click | PASS | dom changed; 2 xas req |

### Purchasing.PurchaseOrder_NewEdit — Set to RFQ (Cancelled -> RFQ)

| element | action | verdict | observation |
|---|---|---|---|
| button "Set to RFQ" (btnSettoRFQ4) | click | PASS | dom changed; 2 xas req |

### Purchasing.PurchaseOrder_NewEdit — Send (mark as sent) (RFQ -> RFQ sent)

| element | action | verdict | observation |
|---|---|---|---|
| button "Send (mark as sent)" (btnSendmarkassent0) | click | PASS | dom changed; 2 xas req |

### Purchasing.PurchaseOrder_NewEdit — Confirm order (RFQ sent -> ?)

| element | action | verdict | observation |
|---|---|---|---|
| button "Confirm order" (btnConfirmorder1) | click | PASS | dom changed; 1 xas req; title P00032 [dialog] | a dialog appeared and the status stayed "RFQ sent" (blank order: no vendor) = wired, validation |
| button "Show date picker" (dpConfirmationDate) | click | N/A (by design) | disabled |

### Purchasing.PurchaseOrder_NewEdit — Lock on journey order P00018 (Purchase order state)

| element | action | verdict | observation |
|---|---|---|---|
| button "Lock" (btnLock5) | click | PASS | no DOM-hash change but 2 requests; verified on P00018: Locked false -> true after one click, restored to false with a second click |

### Purchasing.VendorPrice_Overview (purchaser)

| element | action | verdict | observation |
|---|---|---|---|
| input[combobox] "" (lncmbVendorPriceVendor) | click | PASS | dom changed [Gemini Furniture ⏎ Ready Mat ⏎ Wood Corner/////////]; 1 xas req |
| button "Clear selection" (lncmbVendorPriceVendor) | click | PASS | dom changed; 3 xas req |
| input[combobox] "" (lncmbVendorPriceProduct) | click | PASS | dom changed [/Cable Pack ⏎ Desk Combination ⏎ Journey Chair ⏎ Journey Chair ⏎ Jou] |
| button "Show date picker" (lndpValidFrom) | click | PASS | dom changed |
| button "Show date picker" (lndpValidTo) | click | PASS | dom changed |
| input[combobox] "" (lncmbVendorPriceVendor) | click | PASS | dom changed [//Gemini Furniture ⏎ Ready Mat ⏎ Wood Corner///////] |
| input[combobox] "" (lncmbVendorPriceProduct) | click | PASS | dom changed [///Cable Pack ⏎ Desk Combination ⏎ Journey Chair ⏎ Journey Chair ⏎ J] |
| button "Show date picker" (lndpValidFrom) | click | PASS | dom changed |
| button "Show date picker" (lndpValidTo) | click | PASS | dom changed |
| input[combobox] "" (lncmbVendorPriceVendor) | click | PASS | dom changed [////Gemini Furniture ⏎ Ready Mat ⏎ Wood Corner/////] |
| input[combobox] "" (lncmbVendorPriceProduct) | click | PASS | dom changed [/////Cable Pack ⏎ Desk Combination ⏎ Journey Chair ⏎ Journey Chair]; 1 xas req |
| button "Clear selection" (lncmbVendorPriceProduct) | click | PASS | dom changed; 3 xas req |
| button "Show date picker" (lndpValidFrom) | click | PASS | dom changed |
| button "Show date picker" (lndpValidTo) | click | PASS | dom changed |
| input[combobox] "" (lncmbVendorPriceVendor) | click | PASS | dom changed [//////Gemini Furniture ⏎ Ready Mat ⏎ Wood Corner///] |
| input[combobox] "" (lncmbVendorPriceProduct) | click | PASS | dom changed [///////Cable Pack ⏎ Desk Combination ⏎ Journey Chair ⏎ Journey Cha] |
| button "Show date picker" (lndpValidFrom) | click | PASS | dom changed |
| button "Show date picker" (lndpValidTo) | click | PASS | dom changed |
| input[combobox] "" (lncmbVendorPriceVendor) | click | PASS | dom changed [////////Gemini Furniture ⏎ Ready Mat ⏎ Wood Corner/] |
| input[combobox] "" (lncmbVendorPriceProduct) | click | PASS | dom changed [/////////Cable Pack ⏎ Desk Combination ⏎ Journey Chair ⏎ Journey C] |
| button "Show date picker" (lndpValidFrom) | click | PASS | dom changed |
| button "Show date picker" (lndpValidTo) | click | PASS | dom changed |
| a[button] "+ Add a line" (btnAddLine) | click | PASS | dom changed [///////////]; 4 xas req |
| a[button] "Remove" (btnLineDelete) | click | UNREACHED | not rendered for purchaser (0 in the DOM; present x6 for purchase.manager) - delete access on VendorPrice; swept as purchase.manager below |

### Purchasing.PurchaseApproval_Inbox

| element | action | verdict | observation |
|---|---|---|---|
| div[button] "sort Number" (gridMain) | click | PASS | dom changed; 1 xas req |
| button[combobox] "Contains" (fNumber) | click | PASS | dom changed [Contains ⏎ Starts with ⏎ Ends with ⏎ Greater than ⏎ Greater than or ] |
| div[button] "sort Vendor" (gridMain) | click | PASS | dom changed; 1 xas req |
| div[button] "sort Buyer" (gridMain) | click | PASS | dom changed; 1 xas req |
| div[button] "sort Total" (gridMain) | click | PASS | dom changed; 1 xas req |
| button[combobox] "Equal" (fAmountTotal) | click | PASS | dom changed [/Greater than ⏎ Greater than or equal ⏎ Equal ⏎ Not equal ⏎ Smaller ] |
| div[button] "sort Order deadline" (gridMain) | click | PASS | dom changed; 1 xas req |
| button[combobox] "Equal" (fOrderDeadline) | click | PASS | dom changed [//Between ⏎ Greater than ⏎ Greater than or equal ⏎ Equal ⏎ Not equal] |
| button "Show calendar" (fOrderDeadline) | click | PASS | dom changed [///27282930123 ⏎ 45678910 ⏎ 11121314151617 ⏎ 18192021222324 ⏎ 252627] |
| button "Column selector" (gridMain) | click | PASS | dom changed |
| div[gridcell] "P00022" (gridMain) | click | PASS | dom changed [/]; 6 xas req; title P00022 |
| button "Go to first page" (gridMain) | click | N/A (by design) | disabled; pager status: 1 to 5 of 5 |
| button "Go to previous page" (gridMain) | click | N/A (by design) | disabled; pager status: 1 to 5 of 5 |
| button "Go to next page" (gridMain) | click | N/A (by design) | disabled; pager status: 1 to 5 of 5 |
| button "Go to last page" (gridMain) | click | N/A (by design) | disabled; pager status: 1 to 5 of 5 |

### Purchasing.PurchaseApproval_Task (opened from inbox via P00023, a journey PO)

| element | action | verdict | observation |
|---|---|---|---|
| input[combobox] "" (cmbPurchaseOrderVendor) | click | N/A (by design) | disabled; pager status: 1 to 1 of 1 |
| input[combobox] "" (cmbPurchaseOrderBuyer) | click | N/A (by design) | disabled; pager status: 1 to 1 of 1 |
| button "Show date picker" (dpOrderDeadline) | click | N/A (by design) | disabled; pager status: 1 to 1 of 1 |
| button "Show date picker" (dpExpectedArrival) | click | N/A (by design) | disabled; pager status: 1 to 1 of 1 |
| a[button] "Open order" (lnkOpenOrder) | click | PASS | dom changed [////////]; 15 xas req |
| div[button] "sort Product" (gridProducts) | click | PASS | dom changed; 1 xas req |
| div[button] "sort Description" (gridProducts) | click | PASS | dom changed; 1 xas req |
| div[button] "sort Quantity" (gridProducts) | click | PASS | dom changed; 1 xas req |
| div[button] "sort Unit" (gridProducts) | click | PASS | dom changed; 1 xas req |
| div[button] "sort Unit price" (gridProducts) | click | PASS | dom changed; 1 xas req |
| div[button] "sort Subtotal" (gridProducts) | click | PASS | dom changed; 1 xas req |
| button "Column selector" (gridProducts) | click | PASS | dom changed |
| div[gridcell] "Desk Combination" (gridProducts) | click | N/A (by design) | grid has no onClick in its page definition (DESCRIBE PAGE) - read-only report/lines grid, a data cell is not an affordance; click correctly does nothing |
| button "Go to first page" (gridProducts) | click | N/A (by design) | disabled; pager status: 1 to 1 of 1 |
| button "Go to previous page" (gridProducts) | click | N/A (by design) | disabled; pager status: 1 to 1 of 1 |
| button "Go to next page" (gridProducts) | click | N/A (by design) | disabled; pager status: 1 to 1 of 1 |
| button "Go to last page" (gridProducts) | click | N/A (by design) | disabled; pager status: 1 to 1 of 1 |

### Purchasing.PurchaseApproval_Task — Approve (P00025)

| element | action | verdict | observation |
|---|---|---|---|
| button "Approve" (btnApprove) | click | PASS | dom changed [//]; 3 xas req; title Purchase approvals |

### Purchasing.PurchaseApproval_Task — Reject (P00024)

| element | action | verdict | observation |
|---|---|---|---|
| button "Reject" (btnReject) | click | PASS | dom changed [//Give the purchaser a reason for the rejection.]; 1 xas req | click shows "Give the purchaser a reason for the rejection." (reason required; state not changed) |

### Purchasing.PurchaseAnalysis_Report

| element | action | verdict | observation |
|---|---|---|---|
| div[button] "sort Month" (gridMain) | click | PASS | dom changed |
| button[combobox] "Contains" (fPeriod) | click | PASS | dom changed [Contains ⏎ Starts with ⏎ Ends with ⏎ Greater than ⏎ Greater than or ] |
| div[button] "sort Vendor" (gridMain) | click | PASS | dom changed; 1 xas req |
| button[combobox] "Contains" (fVendorName) | click | PASS | dom changed [/Contains ⏎ Starts with ⏎ Ends with ⏎ Greater than ⏎ Greater than or] |
| div[button] "sort Product" (gridMain) | click | PASS | dom changed; 1 xas req |
| button[combobox] "Contains" (fProductName) | click | PASS | dom changed [//Contains ⏎ Starts with ⏎ Ends with ⏎ Greater than ⏎ Greater than o] |
| div[button] "sort Ordered" (gridMain) | click | PASS | dom changed; 1 xas req |
| button[combobox] "Equal" (fOrdered) | click | PASS | dom changed [///Greater than ⏎ Greater than or equal ⏎ Equal ⏎ Not equal ⏎ Smalle] |
| div[button] "sort Received" (gridMain) | click | PASS | dom changed; 1 xas req |
| button[combobox] "Equal" (fReceived) | click | PASS | dom changed [////Greater than ⏎ Greater than or equal ⏎ Equal ⏎ Not equal ⏎ Small] |
| div[button] "sort Billed" (gridMain) | click | PASS | dom changed; 1 xas req |
| button[combobox] "Equal" (fBilled) | click | PASS | dom changed [/////Greater than ⏎ Greater than or equal ⏎ Equal ⏎ Not equal ⏎ Smal] |
| div[button] "sort Untaxed" (gridMain) | click | PASS | dom changed; 1 xas req |
| button[combobox] "Equal" (fUntaxed) | click | PASS | dom changed [//////Greater than ⏎ Greater than or equal ⏎ Equal ⏎ Not equal ⏎ Sma] |
| button "Column selector" (gridMain) | click | PASS | dom changed |
| div[gridcell] "2026-10" (gridMain) | click | N/A (by design) | grid has no onClick in its page definition (DESCRIBE PAGE) - read-only report/lines grid, a data cell is not an affordance; click correctly does nothing |
| button "Go to first page" (gridMain) | click | N/A (by design) | disabled; pager status: 1 to 1 of 1 |
| button "Go to previous page" (gridMain) | click | N/A (by design) | disabled; pager status: 1 to 1 of 1 |
| button "Go to next page" (gridMain) | click | N/A (by design) | disabled; pager status: 1 to 1 of 1 |
| button "Go to last page" (gridMain) | click | N/A (by design) | disabled; pager status: 1 to 1 of 1 |

### Purchasing.VendorPrice_Overview (purchase.manager: Remove link is only rendered for this role)

| element | action | verdict | observation |
|---|---|---|---|
| a[button] "Remove" (btnLineDelete) on a blank sweep-created row | click | PASS | Remove-button count 6 -> 5 |
| a[button] "Remove" (btnLineDelete) on a blank sweep-created row | click | PASS | Remove-button count 5 -> 4 |
| a[button] "Remove" (btnLineDelete) on a blank sweep-created row | click | PASS | Remove-button count 4 -> 3 |
| a[button] "Remove" (btnLineDelete) on the pre-existing vendor price rows | click | UNREACHED | would delete seeded/journey vendor-price data; same widget proven on the blank rows |

### Shell: side navigation tree (purchaser)

| element | action | verdict | observation |
|---|---|---|---|
| nav item "Home" | click | PASS | -> /p/home title=Welcome |
| nav item "Purchase" | click | PASS | group toggle; dom true |
| nav item "RFQs & orders" | click | PASS | -> /p/purchase-order-overview title=Requests for quotation & purchase orders |
| nav item "Vendor prices" | click | PASS | -> /p/vendor-price-overview title=Vendor prices |
| nav item "Contacts" | click | PASS | group toggle; dom true |
| nav item "Contacts" | click | PASS | -> /p/partner-overview title=Contacts |
| nav item "Products" | click | PASS | group toggle; dom true |
| nav item "Products" | click | PASS | -> /p/product-overview title=Products |
| Sign out (btnSignOut) | click | PASS | session ended, next login for same user succeeded |

### Shell: side navigation tree (purchase.manager)

| element | action | verdict | observation |
|---|---|---|---|
| nav item "Home" | click | PASS | -> /p/home title=Welcome |
| nav item "Purchase" | click | PASS | group toggle; dom true |
| nav item "RFQs & orders" | click | PASS | -> /p/purchase-order-overview title=Requests for quotation & purchase orders |
| nav item "Approvals" | click | PASS | -> /p/purchase-approval-inbox title=Purchase approvals |
| nav item "Vendor prices" | click | PASS | -> /p/vendor-price-overview title=Vendor prices |
| nav item "Contacts" | click | PASS | group toggle; dom true |
| nav item "Contacts" | click | PASS | -> /p/partner-overview title=Contacts |
| nav item "Products" | click | PASS | group toggle; dom true |
| nav item "Products" | click | PASS | -> /p/product-overview title=Products |
| nav item "Pricelists" | click | PASS | -> /p/pricelist-overview title=Pricelists |
| nav item "Reporting" | click | PASS | group toggle; dom true |
| nav item "Purchase analysis" | click | PASS | -> /p/purchase-analysis-report title=Purchase analysis |
| nav item "Configuration" | click | PASS | group toggle; dom true |
| nav item "Units of measure" | click | PASS | -> /p/uo-m-category-overview title=Units of measure |
| nav item "Product categories" | click | PASS | -> /p/product-category-overview title=Product categories |
| Sign out (btnSignOut) | click | PASS | session ended, next login for same user succeeded |

