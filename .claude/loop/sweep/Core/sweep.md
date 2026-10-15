wiring · Core · 45 of 54 interactive elements swept, 7 of 7 pages   (N = DOM + unshown conditional; N/A and UNREACHED are in N but not swept)
  0 failed (no observable effect), 0 error-on-click, 0 not interactable (overlay), 45 passed,
  8 N/A by design (state recorded), 1 unreached (condition shown)
  Read as: these elements are wired to something. Not that the something is correct.
  Shell (side-nav items + Sign out, listed separately, not in the totals above): 13 of 13 PASS

Users: invoicing.manager (Core.Config) for Tax / Payment term pages and the nav shell; admin.user for Core.Company_Edit and Core.Sequence_Overview, which are granted to Core.Admin ONLY (no nav entry or grant for invoicing.manager - by the grant, not a routing-around). Each NewEdit page was entered via the overview's New button (fresh unsaved record) and swept there; Save on the blank record returned the model's required-field messages (Name is required) = wired. Row-click on a fixture only opens it; nothing saved. Company_Edit Save = UNREACHED (would commit the company fixture); the combobox "Clear selection" clicks there only change client state - verified afterwards: currency EUR, country Netherlands, sales tax 21% (sales), purchase tax 21% (purchase) unchanged.
FINDING (not in Core): Company_Edit's lnk0 "User accounts (Administration)" opens Administration.Account_Overview, whose Roles column filter renders the error text "Unable to get filter store. Check parent widget configuration."; console shows "Failed to fetch" x3. The link itself is wired.

### Core.Home_Web

| element | action | verdict | observation |
|---|---|---|---|
| (none) | - | N/A (0 elements) | page is a heading + paragraph; 0 interactive elements in model and DOM |

### Core.Company_Edit (admin.user; Core.Admin-only page)

| element | action | verdict | observation |
|---|---|---|---|
| button "Save" (btnSave0) | click | UNREACHED | Save would commit changes to the company fixture |
| input[combobox] "" (cmbCompanyCurrency) | click | PASS | dom changed [EUR ⏎ USD///]; 1 xas req |
| button "Clear selection" (cmbCompanyCurrency) | click | PASS | dom changed; 1 xas req |
| input[combobox] "" (cmbCompanyCountry) | click | PASS | dom changed [/Belgium ⏎ France ⏎ Germany ⏎ Netherlands ⏎ United Kingdom ⏎ United St]; 1 xas req |
| button "Clear selection" (cmbCompanyCountry) | click | PASS | dom changed; 1 xas req |
| input[combobox] "" (cmbCompanyDefaultSalesTax) | click | PASS | dom changed [//21% (purchase) ⏎ 21% (sales) ⏎ 9% (sales) ⏎ Journey tax 5% ⏎ Journ]; 1 xas req |
| button "Clear selection" (cmbCompanyDefaultSalesTax) | click | PASS | dom changed; 1 xas req |
| input[combobox] "" (cmbCompanyDefaultPurchaseTax) | click | PASS | dom changed [///21% (purchase) ⏎ 21% (sales) ⏎ 9% (sales) ⏎ Journey tax 5% ⏎ Jour]; 1 xas req |
| button "Clear selection" (cmbCompanyDefaultPurchaseTax) | click | PASS | dom changed; 1 xas req |
| a[button] "User accounts (Administration)" (lnk0) | click | PASS | dom changed [//Unable to get filter store. Check parent widget configurat]; 3 xas req; title undefined | NOTE: target Administration.Account_Overview renders, but its Roles column filter shows "Unable to get filter store. Check parent widget configuration." (Administration module widget config) and 3 console "Failed to fetch" errors |

### Core.Tax_Overview

| element | action | verdict | observation |
|---|---|---|---|
| button "New" (btnNew) | click | PASS | dom changed [///////]; 1 xas req; title Taxes [dialog] |
| div[button] "sort Name" (gridMain) | click | PASS | dom changed; 1 xas req |
| button[combobox] "Contains" (fName) | click | PASS | dom changed [Contains ⏎ Starts with ⏎ Ends with ⏎ Greater than ⏎ Greater than or ] |
| div[button] "sort Scope" (gridMain) | click | PASS | dom changed; 1 xas req |
| div[combobox] "filter" (fScope) | click | PASS | dom changed [/Sales ⏎ Purchases////] |
| div[button] "sort Computation" (gridMain) | click | PASS | dom changed; 1 xas req |
| div[combobox] "filter" (fComputation) | click | PASS | dom changed [//Percentage of price ⏎ Fixed amount per unit///] |
| div[button] "sort Amount" (gridMain) | click | PASS | dom changed; 1 xas req |
| button[combobox] "Equal" (fAmount) | click | PASS | dom changed [///Greater than ⏎ Greater than or equal ⏎ Equal ⏎ Not equal ⏎ Smalle] |
| div[button] "sort Included in price" (gridMain) | click | PASS | dom changed; 1 xas req |
| div[combobox] "filter" (fIncludedInPrice) | click | PASS | dom changed [////Yes ⏎ No/] |
| div[button] "sort Active" (gridMain) | click | PASS | dom changed; 1 xas req |
| div[combobox] "filter" (fActive) | click | PASS | dom changed [/////Yes ⏎ No] |
| button "Column selector" (gridMain) | click | PASS | dom changed |
| div[gridcell] "21% (purchase)" (gridMain) | click | PASS | dom changed [///////]; 1 xas req; title Taxes [dialog] |
| button "Go to first page" (gridMain) | click | N/A (by design) | disabled; pager status: 1 to 17 of 17 |
| button "Go to previous page" (gridMain) | click | N/A (by design) | disabled; pager status: 1 to 17 of 17 |
| button "Go to next page" (gridMain) | click | N/A (by design) | disabled; pager status: 1 to 17 of 17 |
| button "Go to last page" (gridMain) | click | N/A (by design) | disabled; pager status: 1 to 17 of 17 |

### Core.Tax_NewEdit (fresh record via New)

| element | action | verdict | observation |
|---|---|---|---|
| button "close" | click | PASS | dom changed [/////]; 2 xas req; title Taxes |
| input[combobox] "" (pcmbScope) | click | PASS | dom changed [//////Sales ⏎ Purchases/] |
| button "Clear selection" (pcmbScope) | click | PASS | dom changed |
| input[combobox] "" (pcmbComputation) | click | PASS | dom changed [///////Percentage of price ⏎ Fixed amount per unit] |
| button "Clear selection" (pcmbComputation) | click | PASS | dom changed |
| button "Save" (pbtnSave0) | click | PASS | dom changed [//////Name is required.//]; 1 xas req |
| button "Cancel" (pbtnCancel) | click | PASS | dom changed [/////]; 2 xas req; title Taxes |

### Core.PaymentTerm_Overview

| element | action | verdict | observation |
|---|---|---|---|
| button "New" (btnNew) | click | PASS | dom changed; 2 xas req; title New |
| div[button] "sort Name" (gridMain) | click | PASS | dom changed; 1 xas req |
| button[combobox] "Contains" (fName) | click | PASS | dom changed [Contains ⏎ Starts with ⏎ Ends with ⏎ Greater than ⏎ Greater than or ] |
| div[button] "sort Note" (gridMain) | click | PASS | dom changed; 1 xas req |
| button[combobox] "Contains" (fNote) | click | PASS | dom changed [/Contains ⏎ Starts with ⏎ Ends with ⏎ Greater than ⏎ Greater than or] |
| button "Column selector" (gridMain) | click | PASS | dom changed |
| div[gridcell] "15 Days" (gridMain) | click | PASS | dom changed; 2 xas req; title 15 Days |
| button "Go to first page" (gridMain) | click | N/A (by design) | disabled; pager status: 1 to 3 of 3 |
| button "Go to previous page" (gridMain) | click | N/A (by design) | disabled; pager status: 1 to 3 of 3 |
| button "Go to next page" (gridMain) | click | N/A (by design) | disabled; pager status: 1 to 3 of 3 |
| button "Go to last page" (gridMain) | click | N/A (by design) | disabled; pager status: 1 to 3 of 3 |

### Core.PaymentTerm_NewEdit (fresh record via New, one line added)

| element | action | verdict | observation |
|---|---|---|---|
| button "Save" (btnSave0) | click | PASS | dom changed [Name is required.//]; 1 xas req |
| input[combobox] "" (lncmbValue) | click | PASS | dom changed [Percent ⏎ Fixed amount/] |
| button "Clear selection" (lncmbValue) | click | PASS | dom changed |
| input[combobox] "" (lncmbDelayType) | click | PASS | dom changed [/Days after invoice date ⏎ Days after end of month] |
| button "Clear selection" (lncmbDelayType) | click | PASS | dom changed |
| a[button] "Remove" (btnLineDelete) | click | PASS | dom changed; title New [dialog] |
| a[button] "+ Add a line" (btnAddLine) | click | PASS | dom changed [///]; 2 xas req |

### Core.Sequence_Overview (admin.user; Core.Admin-only page)

| element | action | verdict | observation |
|---|---|---|---|
| (none) - 4 inline textboxes per row (lntxtPrefix/Padding/NextNumber OnChange: save changes) | - | N/A (0 elements) | 0 clickable elements in model and DOM; text inputs are monkey-test territory and were deliberately not typed into (sequence fixtures) |

### Shell: side navigation tree (this user)

| element | action | verdict | observation |
|---|---|---|---|
| nav item "Home" | click | PASS | -> /p/home title=Welcome |
| nav item "Sales" | click | PASS | group toggle; dom true |
| nav item "Quotations & orders" | click | PASS | -> /p/sales-order-overview title=Quotations & sales orders |
| nav item "Purchase" | click | PASS | group toggle; dom true |
| nav item "RFQs & orders" | click | PASS | -> /p/purchase-order-overview title=Requests for quotation & purchase orders |
| nav item "Contacts" | click | PASS | group toggle; dom true |
| nav item "Contacts" | click | PASS | -> /p/partner-overview title=Contacts |
| nav item "Products" | click | PASS | group toggle; dom true |
| nav item "Products" | click | PASS | -> /p/product-overview title=Products |
| nav item "Configuration" | click | PASS | group toggle; dom true |
| nav item "Taxes" | click | PASS | -> /p/tax-overview title=Taxes |
| nav item "Payment terms" | click | PASS | -> /p/payment-term-overview title=Payment terms |
| Sign out (btnSignOut) | click | PASS | session ended, next login for same user succeeded |

