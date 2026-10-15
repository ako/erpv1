wiring · Products · 66 of 82 interactive elements swept, 8 of 8 pages   (N = DOM + unshown conditional; N/A and UNREACHED are in N but not swept)
  0 failed (no observable effect), 0 error-on-click, 0 not interactable (overlay), 66 passed,
  16 N/A by design (state recorded), 0 unreached (condition shown)
  Read as: these elements are wired to something. Not that the something is correct.
  Shell (side-nav items + Sign out, listed separately, not in the totals above): 16 of 16 PASS

User: sales.manager (Products.Manager). Every NewEdit swept on a fresh record from New. Remove (btnLineDelete) swept only on the line I added to the fresh record (confirmation dialog appears = DOM change). Archive on the blank fresh product closed the page back to Products (2 requests) - a blank, never-saved record, no fixture touched; row click on fixtures opens, nothing saved.

### Products.Product_Overview

| element | action | verdict | observation |
|---|---|---|---|
| button "New" (btnNew) | click | PASS | dom changed [////////]; 7 xas req; title New |
| div[button] "sort Internal reference" (gridMain) | click | PASS | dom changed; 1 xas req |
| button[combobox] "Contains" (fInternalReference) | click | PASS | dom changed [Contains ⏎ Starts with ⏎ Ends with ⏎ Greater than ⏎ Greater than or ] |
| div[button] "sort Name" (gridMain) | click | PASS | dom changed; 1 xas req |
| button[combobox] "Contains" (fName) | click | PASS | dom changed [/Contains ⏎ Starts with ⏎ Ends with ⏎ Greater than ⏎ Greater than or] |
| div[button] "sort Product type" (gridMain) | click | PASS | dom changed; 1 xas req |
| div[combobox] "filter" (fProductType) | click | PASS | dom changed [//Goods ⏎ Service//] |
| div[button] "sort Category" (gridMain) | click | PASS | dom changed; 1 xas req |
| div[button] "sort Sales price" (gridMain) | click | PASS | dom changed; 1 xas req |
| button[combobox] "Equal" (fSalesPrice) | click | PASS | dom changed [///Greater than ⏎ Greater than or equal ⏎ Equal ⏎ Not equal ⏎ Smalle] |
| div[button] "sort Cost" (gridMain) | click | PASS | dom changed; 1 xas req |
| button[combobox] "Equal" (fCost) | click | PASS | dom changed [////Greater than ⏎ Greater than or equal ⏎ Equal ⏎ Not equal ⏎ Small] |
| div[button] "sort Unit" (gridMain) | click | PASS | dom changed; 1 xas req |
| button "Column selector" (gridMain) | click | PASS | dom changed |
| div[gridcell] "CONS_0001" (gridMain) | click | PASS | dom changed [////////]; 10 xas req; title Cable Pack |
| button "Go to first page" (gridMain) | click | N/A (by design) | disabled; pager status: 1 to 13 of 13 |
| button "Go to previous page" (gridMain) | click | N/A (by design) | disabled; pager status: 1 to 13 of 13 |
| button "Go to next page" (gridMain) | click | N/A (by design) | disabled; pager status: 1 to 13 of 13 |
| button "Go to last page" (gridMain) | click | N/A (by design) | disabled; pager status: 1 to 13 of 13 |

### Products.Product_NewEdit (fresh record via New)

| element | action | verdict | observation |
|---|---|---|---|
| button "Save" (btnSave0) | click | PASS | dom changed [Name is required./////////Unit of measure is required./]; 1 xas req |
| button "Archive" (btnArchive1) | click | PASS | dom changed [////]; 2 xas req; title Products |
| input[combobox] "" (cmbProductType) | click | PASS | dom changed [Goods ⏎ Service////////] |
| button "Clear selection" (cmbProductType) | click | PASS | dom changed |
| input[combobox] "" (cmbProductCategory) | click | PASS | dom changed [/All ⏎ Office ⏎ Saleable///////] |
| input[combobox] "" (cmbProductTags) | click | PASS | dom changed |
| input[combobox] "" (cmbProductCustomerTaxes) | click | PASS | dom changed [///21% (purchase) ⏎ 21% (sales) ⏎ 9% (sales) ⏎ Journey tax 5% ⏎ Jour] |
| input[combobox] "" (cmbInvoicePolicy) | click | PASS | dom changed [////Ordered quantities ⏎ Delivered quantities////] |
| input[combobox] "" (cmbProductVendorTaxes) | click | PASS | dom changed [/////21% (purchase) ⏎ 21% (sales) ⏎ 9% (sales) ⏎ Journey tax 5% ⏎ Jo] |
| input[combobox] "" (cmbBillPolicy) | click | PASS | dom changed [//////On ordered quantities ⏎ On received quantities//] |
| input[combobox] "" (cmbProductPurchaseUoM) | click | PASS | dom changed [///////Days ⏎ Dozens ⏎ Hours ⏎ Units ⏎ g ⏎ kg/] |
| input[combobox] "" (cmbProductUoM) | click | PASS | dom changed [////////Days ⏎ Dozens ⏎ Hours ⏎ Units ⏎ g ⏎ kg] |

### Products.ProductCategory_Overview

| element | action | verdict | observation |
|---|---|---|---|
| button "New" (btnNew) | click | PASS | dom changed [/]; 2 xas req; title Product categories [dialog] |
| div[button] "sort Full name" (gridMain) | click | PASS | dom changed; 1 xas req |
| button[combobox] "Contains" (fFullName) | click | PASS | dom changed [Contains ⏎ Starts with ⏎ Ends with ⏎ Greater than ⏎ Greater than or ] |
| button "Column selector" (gridMain) | click | PASS | dom changed |
| div[gridcell] "All" (gridMain) | click | PASS | dom changed [/]; 2 xas req; title Product categories [dialog] |
| button "Go to first page" (gridMain) | click | N/A (by design) | disabled; pager status: 1 to 3 of 3 |
| button "Go to previous page" (gridMain) | click | N/A (by design) | disabled; pager status: 1 to 3 of 3 |
| button "Go to next page" (gridMain) | click | N/A (by design) | disabled; pager status: 1 to 3 of 3 |
| button "Go to last page" (gridMain) | click | N/A (by design) | disabled; pager status: 1 to 3 of 3 |

### Products.ProductCategory_NewEdit (fresh record via New)

| element | action | verdict | observation |
|---|---|---|---|
| button "close" | click | PASS | dom changed; 2 xas req; title Product categories |
| input[combobox] "" (pcmbProductCategoryParent) | click | PASS | dom changed [/All ⏎ Office ⏎ Saleable] |
| button "Save" (pbtnSave0) | click | PASS | dom changed [/Name is required./]; 1 xas req |
| button "Cancel" (pbtnCancel) | click | PASS | dom changed; 2 xas req; title Product categories |

### Products.UoMCategory_Overview

| element | action | verdict | observation |
|---|---|---|---|
| button "New" (btnNew) | click | PASS | dom changed; 2 xas req; title New |
| div[button] "sort Name" (gridMain) | click | PASS | dom changed; 1 xas req |
| button[combobox] "Contains" (fName) | click | PASS | dom changed [Contains ⏎ Starts with ⏎ Ends with ⏎ Greater than ⏎ Greater than or ] |
| button "Column selector" (gridMain) | click | PASS | dom changed |
| div[gridcell] "Unit" (gridMain) | click | PASS | dom changed [/]; 2 xas req; title Unit |
| button "Go to first page" (gridMain) | click | N/A (by design) | disabled; pager status: 1 to 3 of 3 |
| button "Go to previous page" (gridMain) | click | N/A (by design) | disabled; pager status: 1 to 3 of 3 |
| button "Go to next page" (gridMain) | click | N/A (by design) | disabled; pager status: 1 to 3 of 3 |
| button "Go to last page" (gridMain) | click | N/A (by design) | disabled; pager status: 1 to 3 of 3 |

### Products.UoMCategory_NewEdit (fresh record via New, one UoM line added)

| element | action | verdict | observation |
|---|---|---|---|
| button "Save" (btnSave0) | click | PASS | dom changed [Name is required./Unit name is required./]; 1 xas req |
| input[combobox] "" (lncmbUoMType) | click | PASS | dom changed [Reference unit for this category ⏎ Bigger than the reference u] |
| button "Clear selection" (lncmbUoMType) | click | PASS | dom changed |
| a[button] "Remove" (btnLineDelete) | click | PASS | dom changed; title New [dialog] |
| a[button] "+ Add a line" (btnAddLine) | click | PASS | dom changed [/]; 2 xas req |

### Products.Pricelist_Overview

| element | action | verdict | observation |
|---|---|---|---|
| button "New" (btnNew) | click | PASS | dom changed; 3 xas req; title New |
| div[button] "sort Name" (gridMain) | click | PASS | dom changed; 1 xas req |
| button[combobox] "Contains" (fName) | click | PASS | dom changed [Contains ⏎ Starts with ⏎ Ends with ⏎ Greater than ⏎ Greater than or ] |
| div[button] "sort Currency" (gridMain) | click | PASS | dom changed; 1 xas req |
| div[button] "sort Active" (gridMain) | click | PASS | dom changed; 1 xas req |
| div[combobox] "filter" (fActive) | click | PASS | dom changed [/Yes ⏎ No] |
| button "Column selector" (gridMain) | click | PASS | dom changed |
| div[gridcell] "Public Pricelist" (gridMain) | click | PASS | dom changed; 4 xas req; title Public Pricelist |
| button "Go to first page" (gridMain) | click | N/A (by design) | disabled; pager status: 1 to 1 of 1 |
| button "Go to previous page" (gridMain) | click | N/A (by design) | disabled; pager status: 1 to 1 of 1 |
| button "Go to next page" (gridMain) | click | N/A (by design) | disabled; pager status: 1 to 1 of 1 |
| button "Go to last page" (gridMain) | click | N/A (by design) | disabled; pager status: 1 to 1 of 1 |

### Products.Pricelist_NewEdit (fresh record via New, one rule added)

| element | action | verdict | observation |
|---|---|---|---|
| button "Save" (btnSave0) | click | PASS | dom changed [Name is required./Currency is required./////]; 1 xas req |
| input[combobox] "" (cmbPricelistCurrency) | click | PASS | dom changed [EUR ⏎ USD////] |
| input[combobox] "" (lncmbAppliesTo) | click | PASS | dom changed [/All products ⏎ Product category ⏎ Product///] |
| button "Clear selection" (lncmbAppliesTo) | click | PASS | dom changed |
| input[combobox] "" (lncmbPriceRuleCategory) | click | PASS | dom changed [//All ⏎ Office ⏎ Saleable//] |
| input[combobox] "" (lncmbPriceRuleProduct) | click | PASS | dom changed [///Cable Pack ⏎ Desk Combination ⏎ Installation ⏎ Journey Chair ⏎ Jo] |
| input[combobox] "" (lncmbComputation) | click | PASS | dom changed [////Fixed price ⏎ Discount (%)] |
| button "Clear selection" (lncmbComputation) | click | PASS | dom changed |
| button "Show date picker" (lndpValidFrom) | click | PASS | dom changed |
| button "Show date picker" (lndpValidTo) | click | PASS | dom changed |
| a[button] "Remove" (btnLineDelete) | click | PASS | dom changed; title New [dialog] |
| a[button] "+ Add a line" (btnAddLine) | click | PASS | dom changed [////////]; 4 xas req |

### Shell: side navigation tree (this user)

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

