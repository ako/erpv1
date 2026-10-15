wiring · Partners · 41 of 51 interactive elements swept, 4 of 4 pages   (N = DOM + unshown conditional; N/A and UNREACHED are in N but not swept)
  0 failed (no observable effect), 0 error-on-click, 0 not interactable (overlay), 41 passed,
  6 N/A by design (state recorded), 4 unreached (condition shown)
  Read as: these elements are wired to something. Not that the something is correct.
  Shell (side-nav items + Sign out, listed separately, not in the totals above): 8 of 8 PASS

User: sales.user (Partners.Editor). PartnerChild_NewEdit was reached through Partner_NewEdit's "+ Add" on a fresh parent (ACT_Partner_AddToPartner). Partners.UserProfile_Edit is an orphan page (nothing opens it) - finding, its 4 elements are UNREACHED, never swept. Partner_NewEdit's Archive on the blank fresh partner is swept (blank record). Pager "N/A" rows: Partner overview 1 to 20 of 35 (first/previous disabled on page 1); the contacts grid on a fresh record 0 to 0 of 0.

### Partners.Partner_Overview

| element | action | verdict | observation |
|---|---|---|---|
| button "New" (btnNew) | click | PASS | dom changed [//////]; 9 xas req; title New |
| div[button] "sort Name" (gridMain) | click | PASS | dom changed; 1 xas req |
| button[combobox] "Contains" (fName) | click | PASS | dom changed [Contains ⏎ Starts with ⏎ Ends with ⏎ Greater than ⏎ Greater than or ] |
| div[button] "sort Email" (gridMain) | click | PASS | dom changed; 1 xas req |
| button[combobox] "Contains" (fEmail) | click | PASS | dom changed [/Contains ⏎ Starts with ⏎ Ends with ⏎ Greater than ⏎ Greater than or] |
| div[button] "sort Phone" (gridMain) | click | PASS | dom changed; 1 xas req |
| button[combobox] "Contains" (fPhone) | click | PASS | dom changed [//Contains ⏎ Starts with ⏎ Ends with ⏎ Greater than ⏎ Greater than o] |
| div[button] "sort City" (gridMain) | click | PASS | dom changed; 1 xas req |
| button[combobox] "Contains" (fCity) | click | PASS | dom changed [///Contains ⏎ Starts with ⏎ Ends with ⏎ Greater than ⏎ Greater than ] |
| div[button] "sort Country" (gridMain) | click | PASS | dom changed; 1 xas req |
| div[button] "sort Is customer" (gridMain) | click | PASS | dom changed; 1 xas req |
| div[combobox] "filter" (fIsCustomer) | click | PASS | dom changed [////Yes ⏎ No/] |
| div[button] "sort Is vendor" (gridMain) | click | PASS | dom changed; 1 xas req |
| div[combobox] "filter" (fIsVendor) | click | PASS | dom changed [/////Yes ⏎ No] |
| div[button] "sort Salesperson" (gridMain) | click | PASS | dom changed; 1 xas req |
| button "Column selector" (gridMain) | click | PASS | dom changed |
| div[gridcell] "Ada Admin" (gridMain) | click | PASS | dom changed [//////]; 9 xas req; title Ada Admin |
| button "Go to first page" (gridMain) | click | N/A (by design) | disabled; pager status: 1 to 20 of 35 |
| button "Go to previous page" (gridMain) | click | N/A (by design) | disabled; pager status: 1 to 20 of 35 |
| button "Go to next page" (gridMain) | click | PASS | dom changed; 1 xas req |
| button "Go to last page" (gridMain) | click | PASS | dom changed; 1 xas req |

### Partners.Partner_NewEdit (fresh record via New)

| element | action | verdict | observation |
|---|---|---|---|
| button "Save" (btnSave0) | click | PASS | dom changed [Name is required.///////]; 1 xas req |
| button "Archive" (btnArchive1) | click | PASS | dom changed [/////]; 2 xas req; title Contacts |
| input[combobox] "" (cmbPartnerParentCompany) | click | PASS | dom changed [Ada Admin ⏎ Azure Interior ⏎ Azure Interior, Accounts ⏎ Bea Billin] |
| input[combobox] "" (cmbPartnerTags) | click | PASS | dom changed |
| input[combobox] "" (cmbPartnerCountry) | click | PASS | dom changed [//Belgium ⏎ France ⏎ Germany ⏎ Netherlands ⏎ United Kingdom ⏎ United S] |
| input[combobox] "" (cmbPartnerSalesperson) | click | PASS | dom changed [///Ada Admin ⏎ Bea Billing ⏎ Ingrid Warehouse ⏎ Ivan Ledger ⏎ Marc D] |
| input[combobox] "" (cmbPartnerCustomerPaymentTerm) | click | PASS | dom changed [////15 Days ⏎ 30 Days ⏎ Immediate Payment//] |
| input[combobox] "" (cmbPartnerPricelist) | click | PASS | dom changed [/////Public Pricelist/] |
| input[combobox] "" (cmbPartnerVendorPaymentTerm) | click | PASS | dom changed [//////15 Days ⏎ 30 Days ⏎ Immediate Payment] |
| div[button] "sort Address type" (gridContactsaddresses) | click | PASS | dom changed; 1 xas req |
| div[button] "sort Name" (gridContactsaddresses) | click | PASS | dom changed; 1 xas req |
| div[button] "sort Email" (gridContactsaddresses) | click | PASS | dom changed; 1 xas req |
| div[button] "sort Phone" (gridContactsaddresses) | click | PASS | dom changed; 1 xas req |
| div[button] "sort City" (gridContactsaddresses) | click | PASS | dom changed; 1 xas req |
| button "Column selector" (gridContactsaddresses) | click | PASS | dom changed |
| button "Go to first page" (gridContactsaddresses) | click | N/A (by design) | disabled; pager status: 0 to 0 of 0 |
| button "Go to previous page" (gridContactsaddresses) | click | N/A (by design) | disabled; pager status: 0 to 0 of 0 |
| button "Go to next page" (gridContactsaddresses) | click | N/A (by design) | disabled; pager status: 0 to 0 of 0 |
| button "Go to last page" (gridContactsaddresses) | click | N/A (by design) | disabled; pager status: 0 to 0 of 0 |
| a[button] "+ Add" (btnAddChild) | click | PASS | dom changed [////////]; 2 xas req; title New [dialog] |

### Partners.PartnerChild_NewEdit (fresh parent via New, then "+ Add")

| element | action | verdict | observation |
|---|---|---|---|
| button "close" | click | PASS | dom changed [//////]; 3 xas req; title New |
| input[combobox] "" (pcmbAddressType) | click | PASS | dom changed [///////Contact ⏎ Invoice address ⏎ Delivery address ⏎ Other addres] |
| button "Clear selection" (pcmbAddressType) | click | PASS | dom changed |
| input[combobox] "" (pcmbPartnerCountry) | click | PASS | dom changed [////////Belgium ⏎ France ⏎ Germany ⏎ Netherlands ⏎ United Kingdom ⏎ Un] |
| button "Save" (pbtnSave0) | click | PASS | dom changed [////////Name is required./]; 1 xas req |
| button "Cancel" (pbtnCancel) | click | PASS | dom changed [//////]; 3 xas req; title New |

### Partners.UserProfile_Edit (NO entry point)

| element | action | verdict | observation |
|---|---|---|---|
| button "Save" (pbtnSave0) | click | UNREACHED | page has no route to it: no nav item, no show-page reference anywhere in the model (SHOW REFERENCES TO Partners.UserProfile_Edit = none), no URL; granted to Partners.Admin only. Cannot be landed on by real navigation. |
| button "Cancel" (pbtnCancel) | click | UNREACHED | same: orphan page |
| combobox pcmbUserProfilePartner | click | UNREACHED | same: orphan page |
| combobox pcmbUserProfileAccount | click | UNREACHED | same: orphan page |

### Shell: side navigation tree (this user)

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

