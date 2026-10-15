wiring · Sales · 80 of 99 interactive elements swept, 7 of 7 pages   (N = DOM + unshown conditional; N/A and UNREACHED are in N but not swept)
  0 failed (no observable effect), 0 error-on-click, 1 not interactable (overlay), 79 passed,
  19 N/A by design (state recorded), 0 unreached (condition shown)
  Read as: these elements are wired to something. Not that the something is correct.
  Shell (side-nav items + Sign out, listed separately, not in the totals above): 23 of 23 PASS

Users: sales.manager (Sales.Manager) for Quotation templates, Sales teams, Sales analysis (Manager-only grants); sales.user for Sales orders. Orders state machine swept on ONE fresh order S00050 (created by New), one state-changing button per pass, each in a state that satisfies its Visible: condition:
  Visible conditions on SalesOrder_NewEdit: btnSendmarkassent1 (Quotation) swept; btnConfirm2 (Quotation|QuotationSent) swept in QuotationSent; btnCancelorder3 (Quotation|QuotationSent|SalesOrder) swept in Quotation (-> Cancelled); btnSettoquotation4 (Cancelled) swept (-> Quotation); btnLock5 (SalesOrder) swept on journey order S00048 and restored to Locked; cmbSalesOrderQuotationTemplate (Quotation|QuotationSent) swept in Quotation. State pill verified before/after each pass (Quotation -> Cancelled -> Quotation -> Quotation sent; Confirm refused: no customer).
  Side effects, all on records this sweep created: orders S00049 (blank, from the overview New sweep) and S00050 (left in "Quotation sent"); plus blank quotation template / sales team records never saved. Row clicks on fixture templates/teams only open them.
FINDING: the Order date filter calendar button on the Sales order overview is not clickable (covered by the neighbouring column header) - see the FAIL row.
SalesAnalysis_Report: KPI cards (3 read-only textboxes) and the two column charts have no click affordances in the model; the report grid has filters/sort/column selector only.

### Sales.QuotationTemplate_Overview

| element | action | verdict | observation |
|---|---|---|---|
| button "New" (btnNew) | click | PASS | dom changed; 2 xas req; title New |
| div[button] "sort Name" (gridMain) | click | PASS | dom changed; 1 xas req |
| button[combobox] "Contains" (fName) | click | PASS | dom changed [Contains ⏎ Starts with ⏎ Ends with ⏎ Greater than ⏎ Greater than or ] |
| div[button] "sort Validity days" (gridMain) | click | PASS | dom changed; 1 xas req |
| button[combobox] "Equal" (fValidityDays) | click | PASS | dom changed [/Greater than ⏎ Greater than or equal ⏎ Equal ⏎ Not equal ⏎ Smaller ] |
| div[button] "sort Active" (gridMain) | click | PASS | dom changed; 1 xas req |
| div[combobox] "filter" (fActive) | click | PASS | dom changed [//Yes ⏎ No] |
| button "Column selector" (gridMain) | click | PASS | dom changed |
| div[gridcell] "Office starter pack" (gridMain) | click | PASS | dom changed [/////]; 7 xas req; title Office starter pack |
| button "Go to first page" (gridMain) | click | N/A (by design) | disabled; pager status: 1 to 1 of 1 |
| button "Go to previous page" (gridMain) | click | N/A (by design) | disabled; pager status: 1 to 1 of 1 |
| button "Go to next page" (gridMain) | click | N/A (by design) | disabled; pager status: 1 to 1 of 1 |
| button "Go to last page" (gridMain) | click | N/A (by design) | disabled; pager status: 1 to 1 of 1 |

### Sales.QuotationTemplate_NewEdit (fresh record via New, one line added)

| element | action | verdict | observation |
|---|---|---|---|
| button "Save" (btnSave0) | click | PASS | dom changed [Name is required.///]; 1 xas req |
| input[combobox] "" (lncmbLineType) | click | PASS | dom changed [Product line ⏎ Section ⏎ Note//] |
| input[combobox] "" (lncmbQuotationTemplateLineProduct) | click | PASS | dom changed [/Cable Pack ⏎ Desk Combination ⏎ Installation ⏎ Journey Chair ⏎ Jour] |
| input[combobox] "" (lncmbQuotationTemplateLineUoM) | click | PASS | dom changed [//Days ⏎ Dozens ⏎ Hours ⏎ Units ⏎ g ⏎ kg] |
| a[button] "Remove" (btnLineDelete) | click | PASS | dom changed; title New [dialog] |
| a[button] "+ Add a line" (btnAddLine) | click | PASS | dom changed [/////]; 4 xas req |

### Sales.SalesTeam_Overview

| element | action | verdict | observation |
|---|---|---|---|
| button "New" (btnNew) | click | PASS | dom changed; 3 xas req; title New |
| div[button] "sort Name" (gridMain) | click | PASS | dom changed; 1 xas req |
| button[combobox] "Contains" (fName) | click | PASS | dom changed [Contains ⏎ Starts with ⏎ Ends with ⏎ Greater than ⏎ Greater than or ] |
| div[button] "sort Leader" (gridMain) | click | PASS | dom changed; 1 xas req |
| div[button] "sort Invoicing target" (gridMain) | click | PASS | dom changed; 1 xas req |
| button[combobox] "Equal" (fInvoicingTarget) | click | PASS | dom changed [/Greater than ⏎ Greater than or equal ⏎ Equal ⏎ Not equal ⏎ Smaller ] |
| button "Column selector" (gridMain) | click | PASS | dom changed |
| div[gridcell] "Direct sales" (gridMain) | click | PASS | dom changed; 3 xas req; title Direct sales |
| button "Go to first page" (gridMain) | click | N/A (by design) | disabled; pager status: 1 to 1 of 1 |
| button "Go to previous page" (gridMain) | click | N/A (by design) | disabled; pager status: 1 to 1 of 1 |
| button "Go to next page" (gridMain) | click | N/A (by design) | disabled; pager status: 1 to 1 of 1 |
| button "Go to last page" (gridMain) | click | N/A (by design) | disabled; pager status: 1 to 1 of 1 |

### Sales.SalesTeam_NewEdit (fresh record via New)

| element | action | verdict | observation |
|---|---|---|---|
| button "Save" (btnSave0) | click | PASS | dom changed [Name is required.//]; 1 xas req |
| input[combobox] "" (cmbSalesTeamLeader) | click | PASS | dom changed [Ada Admin ⏎ Bea Billing ⏎ Ingrid Warehouse ⏎ Ivan Ledger ⏎ Marc Demo] |
| input[combobox] "" (cmbSalesTeamMembers) | click | PASS | dom changed [/Ada Admin ⏎ Bea Billing ⏎ Ingrid Warehouse ⏎ Ivan Ledger ⏎ Marc Dem] |

### Sales.SalesAnalysis_Report

| element | action | verdict | observation |
|---|---|---|---|
| div[button] "sort Month" (gridMain) | click | PASS | dom changed |
| button[combobox] "Contains" (fPeriod) | click | PASS | dom changed [Contains ⏎ Starts with ⏎ Ends with ⏎ Greater than ⏎ Greater than or ] |
| div[button] "sort Customer" (gridMain) | click | PASS | dom changed; 1 xas req |
| button[combobox] "Contains" (fCustomerName) | click | PASS | dom changed [/Contains ⏎ Starts with ⏎ Ends with ⏎ Greater than ⏎ Greater than or] |
| div[button] "sort Product" (gridMain) | click | PASS | dom changed; 1 xas req |
| button[combobox] "Contains" (fProductName) | click | PASS | dom changed [//Contains ⏎ Starts with ⏎ Ends with ⏎ Greater than ⏎ Greater than o] |
| div[button] "sort Salesperson" (gridMain) | click | PASS | dom changed; 1 xas req |
| button[combobox] "Contains" (fSalespersonName) | click | PASS | dom changed [///Contains ⏎ Starts with ⏎ Ends with ⏎ Greater than ⏎ Greater than ] |
| div[button] "sort Quantity" (gridMain) | click | PASS | dom changed; 1 xas req |
| button[combobox] "Equal" (fQuantity) | click | PASS | dom changed [////Greater than ⏎ Greater than or equal ⏎ Equal ⏎ Not equal ⏎ Small] |
| div[button] "sort Untaxed" (gridMain) | click | PASS | dom changed; 1 xas req |
| button[combobox] "Equal" (fUntaxed) | click | PASS | dom changed [/////Greater than ⏎ Greater than or equal ⏎ Equal ⏎ Not equal ⏎ Smal] |
| button "Column selector" (gridMain) | click | PASS | dom changed |
| div[gridcell] "2026-10" (gridMain) | click | N/A (by design) | grid has no onClick in its page definition (DESCRIBE PAGE) - read-only report/lines grid, a data cell is not an affordance; click correctly does nothing |
| button "Go to first page" (gridMain) | click | N/A (by design) | disabled; pager status: 1 to 1 of 1 |
| button "Go to previous page" (gridMain) | click | N/A (by design) | disabled; pager status: 1 to 1 of 1 |
| button "Go to next page" (gridMain) | click | N/A (by design) | disabled; pager status: 1 to 1 of 1 |
| button "Go to last page" (gridMain) | click | N/A (by design) | disabled; pager status: 1 to 1 of 1 |

### Sales.SalesOrder_Overview

| element | action | verdict | observation |
|---|---|---|---|
| button "New" (btnNew) | click | PASS | dom changed [/////////]; 11 xas req; title S00049 |
| div[button] "sort Number" (gridMain) | click | PASS | dom changed; 1 xas req |
| button[combobox] "Contains" (fNumber) | click | PASS | dom changed [Contains ⏎ Starts with ⏎ Ends with ⏎ Greater than ⏎ Greater than or ] |
| div[button] "sort Order date" (gridMain) | click | PASS | dom changed; 1 xas req |
| button[combobox] "Equal" (fOrderDate) | click | PASS | dom changed [/Between ⏎ Greater than ⏎ Greater than or equal ⏎ Equal ⏎ Not equal ⏎ ] |
| button "Show calendar" (fOrderDate) | click | FAIL (not interactable) | Playwright: locator.click timeout 4000ms - <div class="column-container" id="DataGrid7-column2"> from the Customer columnheader subtree intercepts pointer events. The Order date filter's calendar button (x 486-534px) is clipped under the next column header: not clickable with the mouse. |
| div[button] "sort Customer" (gridMain) | click | PASS | dom changed; 1 xas req |
| div[button] "sort Salesperson" (gridMain) | click | PASS | dom changed; 1 xas req |
| div[button] "sort Amount total" (gridMain) | click | PASS | dom changed; 1 xas req |
| button[combobox] "Equal" (fAmountTotal) | click | PASS | dom changed [//Greater than ⏎ Greater than or equal ⏎ Equal ⏎ Not equal ⏎ Smaller] |
| div[button] "sort Status" (gridMain) | click | PASS | dom changed; 1 xas req |
| div[combobox] "filter" (fStatus) | click | PASS | dom changed [///Quotation ⏎ Quotation sent ⏎ Sales order ⏎ Cancelled//] |
| div[button] "sort Invoice status" (gridMain) | click | PASS | dom changed; 1 xas req |
| div[combobox] "filter" (fInvoiceStatus) | click | PASS | dom changed [////Nothing to invoice ⏎ To invoice ⏎ Fully invoiced/] |
| div[button] "sort Delivery status" (gridMain) | click | PASS | dom changed; 1 xas req |
| div[combobox] "filter" (fDeliveryStatus) | click | PASS | dom changed [/////Not delivered ⏎ Started ⏎ Partially delivered ⏎ Fully deliver] |
| button "Column selector" (gridMain) | click | PASS | dom changed |
| div[gridcell] "S00001" (gridMain) | click | PASS | dom changed [///////////]; 20 xas req; title S00001 |
| button "Go to first page" (gridMain) | click | N/A (by design) | disabled; pager status: 1 to 15 of 15 |
| button "Go to previous page" (gridMain) | click | N/A (by design) | disabled; pager status: 1 to 15 of 15 |
| button "Go to next page" (gridMain) | click | N/A (by design) | disabled; pager status: 1 to 15 of 15 |
| button "Go to last page" (gridMain) | click | N/A (by design) | disabled; pager status: 1 to 15 of 15 |

### Sales.SalesOrder_NewEdit — state Quotation (fresh order S00050, one line added)

| element | action | verdict | observation |
|---|---|---|---|
| button "Save" (btnSave6) | click | PASS | dom changed [/////]; 2 xas req; title Quotations & sales orders | OBSERVATION: Save on a blank order (no customer) succeeded and returned to the overview - no customer-required check at Save, only at Confirm |
| input[combobox] "" (cmbSalesOrderCustomer) | click | PASS | dom changed [Azure Interior ⏎ Azure Interior, Accounts ⏎ Brandon Freeman ⏎ Deco] |
| input[combobox] "" (cmbSalesOrderInvoiceAddress) | click | PASS | dom changed [/Ada Admin ⏎ Azure Interior ⏎ Azure Interior, Accounts ⏎ Bea Billi] |
| input[combobox] "" (cmbSalesOrderDeliveryAddress) | click | PASS | dom changed [//Ada Admin ⏎ Azure Interior ⏎ Azure Interior, Accounts ⏎ Bea Bill] |
| input[combobox] "" (cmbSalesOrderQuotationTemplate) | click | PASS | dom changed [///Office starter pack/////////] |
| button "Show date picker" (dpExpirationDate) | click | PASS | dom changed |
| input[combobox] "" (cmbSalesOrderPricelist) | click | PASS | dom changed [////Public Pricelist////////] |
| input[combobox] "" (cmbSalesOrderPaymentTerm) | click | PASS | dom changed [/////15 Days ⏎ 30 Days ⏎ Immediate Payment///////] |
| button "Show date picker" (dpOrderDate) | click | PASS | dom changed |
| input[combobox] "" (cmbSalesOrderSalesperson) | click | PASS | dom changed [//////Ada Admin ⏎ Bea Billing ⏎ Ingrid Warehouse ⏎ Ivan Ledger ⏎ Mar]; 1 xas req |
| button "Clear selection" (cmbSalesOrderSalesperson) | click | PASS | dom changed; 1 xas req |
| input[combobox] "" (cmbSalesOrderSalesTeam) | click | PASS | dom changed [///////Direct sales/////] |
| button "Show date picker" (dpDeliveryDate) | click | PASS | dom changed |
| input[combobox] "" (cmbInvoiceStatus) | click | N/A (by design) | disabled |
| input[combobox] "" (cmbDeliveryStatus) | click | N/A (by design) | disabled |
| input[combobox] "" (lncmbSalesOrderLineProduct) | click | PASS | dom changed [//////////Cable Pack ⏎ Desk Combination ⏎ Installation ⏎ Journey C] |
| input[combobox] "" (lncmbSalesOrderLineUoM) | click | PASS | dom changed [///////////Days ⏎ Dozens ⏎ Hours ⏎ Units ⏎ g ⏎ kg/] |
| input[combobox] "" (lncmbSalesOrderLineTaxes) | click | PASS | dom changed [////////////21% (purchase) ⏎ 21% (sales) ⏎ 9% (sales) ⏎ Journey ta] |
| a[button] "Remove" (btnLineDelete) | click | PASS | dom changed [/////////]; 2 xas req |
| a[button] "+ Add a line" (btnAddLine) | click | PASS | dom changed [////////////]; 5 xas req |

### Sales.SalesOrder_NewEdit — Cancel order (Quotation -> Cancelled)

| element | action | verdict | observation |
|---|---|---|---|
| button "Cancel order" (btnCancelorder3) | click | PASS | dom changed [///////////]; 2 xas req |

### Sales.SalesOrder_NewEdit — Set to quotation (Cancelled -> Quotation)

| element | action | verdict | observation |
|---|---|---|---|
| button "Set to quotation" (btnSettoquotation4) | click | PASS | dom changed [////////////]; 3 xas req |

### Sales.SalesOrder_NewEdit — Send (mark as sent) (Quotation -> QuotationSent)

| element | action | verdict | observation |
|---|---|---|---|
| button "Send (mark as sent)" (btnSendmarkassent1) | click | PASS | dom changed; 2 xas req |

### Sales.SalesOrder_NewEdit — Confirm (QuotationSent -> ?)

| element | action | verdict | observation |
|---|---|---|---|
| button "Confirm" (btnConfirm2) | click | PASS | dom changed; 1 xas req; title S00050 [dialog] | dialog text: "Warning - Choose a customer before confirming." (blank order, QuotationSent unchanged) = wired, validation |

### Sales.SalesOrder_NewEdit — Lock/Cancel visibility on journey order S00048 (SalesOrder state)

| element | action | verdict | observation |
|---|---|---|---|
| button "Lock" (btnLock5) | click | PASS | no DOM-hash change (checkbox is a property) but 2 requests; verified separately: on S00048 Locked true -> false after one click, restored to true with a second click. Button caption stays "Lock" in both states. |

### Shell: side navigation tree (sales.manager)

| element | action | verdict | observation |
|---|---|---|---|
| nav item "Home" | click | PASS | -> /p/home title=Welcome |
| nav item "Sales" | click | PASS | group toggle; dom true |
| nav item "Quotations & orders" | click | PASS | -> /p/sales-order-overview title=Quotations & sales orders |
| nav item "Quotation templates" | click | PASS | -> /p/quotation-template-overview title=Quotation templates |
| nav item "Sales teams" | click | PASS | -> /p/sales-team-overview title=Sales teams |
| nav item "Contacts" | click | PASS | group toggle; dom true |
| nav item "Contacts" | click | PASS | -> /p/partner-overview title=Contacts |
| nav item "Products" | click | PASS | group toggle; dom true |
| nav item "Products" | click | PASS | -> /p/product-overview title=Products |
| nav item "Pricelists" | click | PASS | -> /p/pricelist-overview title=Pricelists |
| nav item "Reporting" | click | PASS | group toggle; dom true |
| nav item "Sales analysis" | click | PASS | -> /p/sales-analysis-report title=Sales analysis |
| nav item "Configuration" | click | PASS | group toggle; dom true |
| nav item "Units of measure" | click | PASS | -> /p/uo-m-category-overview title=Units of measure |
| nav item "Product categories" | click | PASS | -> /p/product-category-overview title=Product categories |
| Sign out (btnSignOut) | click | PASS | session ended, next login for same user succeeded |

### Shell: side navigation tree (sales.user)

| element | action | verdict | observation |
|---|---|---|---|
| nav item "Home" | click | PASS | -> /p/home title=Welcome |
| nav item "Sales" | click | PASS | group toggle; dom true |
| nav item "Quotations & orders" | click | PASS | -> /p/sales-order-overview title=Quotations & sales orders |
| nav item "Contacts" | click | PASS | group toggle; dom true |
| nav item "Contacts" | click | PASS | -> /p/partner-overview title=Contacts |
| nav item "Products" | click | PASS | group toggle; dom true |
| nav item "Products" | click | PASS | -> /p/product-overview title=Products |
| Sign out (btnSignOut) | click | PASS | session ended, next login for same user succeeded |

