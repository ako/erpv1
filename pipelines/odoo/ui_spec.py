"""Screen-level UI spec for the wireframes (design-artifacts.md Step 2–3, interaction-model.md).

One entry per screen in the inventory. Field names are Mendix member names from brd_spec.py
(attributes or associations, `Assoc/Attr` for one hop) — wf_render.py fails on any that does not
exist, so a wireframe can only bind what the domain model has. Sample rows show TWO objects per
list (interaction-model.md Step 4: walk with two objects).

kinds: list | form | popup | task | inbox | dashboard | report
"""

import re as _re


def route(screen):
    """Prototype route of a screen (design/wireframes/<Screen>.html data-route)."""
    return 'home' if screen == 'Home' else _re.sub(r'(?<!^)(?=[A-Z])', '-', screen).replace('_-', '-').replace('_', '-').lower()


NAV = [  # (group, label, screen) — side rail; a menu item opens a list, inbox, dashboard, singleton or report only
    ('Sales', 'Quotations & orders', 'SalesOrder_Overview'),
    ('Sales', 'Quotation templates', 'QuotationTemplate_Overview'),
    ('Sales', 'Sales teams', 'SalesTeam_Overview'),
    ('Purchase', 'RFQs & orders', 'PurchaseOrder_Overview'),
    ('Purchase', 'Approvals', 'PurchaseApproval_Inbox'),
    ('Purchase', 'Vendor prices', 'VendorPrice_Overview'),
    ('Inventory', 'Overview', 'Inventory_Dashboard'),
    ('Inventory', 'Transfers', 'Transfer_Overview'),
    ('Inventory', 'Stock', 'StockLevel_Overview'),
    ('Inventory', 'Reorder rules', 'ReorderRule_Overview'),
    ('Invoicing', 'Invoices & bills', 'Invoice_Overview'),
    ('Invoicing', 'Payments', 'Payment_Overview'),
    ('Contacts', 'Contacts', 'Partner_Overview'),
    ('Products', 'Products', 'Product_Overview'),
    ('Products', 'Pricelists', 'Pricelist_Overview'),
    ('Reporting', 'Sales analysis', 'SalesAnalysis_Report'),
    ('Reporting', 'Purchase analysis', 'PurchaseAnalysis_Report'),
    ('Reporting', 'Invoice analysis', 'InvoiceAnalysis_Report'),
    ('Configuration', 'Company', 'Company_Edit'),
    ('Configuration', 'Warehouse', 'Warehouse_Edit'),
    ('Configuration', 'Numbering', 'Sequence_Overview'),
    ('Configuration', 'Taxes', 'Tax_Overview'),
    ('Configuration', 'Payment terms', 'PaymentTerm_Overview'),
    ('Configuration', 'Units of measure', 'UoMCategory_Overview'),
    ('Configuration', 'Product categories', 'ProductCategory_Overview'),
]

ROLE_HOME = {
    'SalesUser': 'SalesOrder_Overview', 'SalesManager': 'SalesOrder_Overview', 'Purchaser': 'PurchaseOrder_Overview',
    'PurchaseManager': 'PurchaseApproval_Inbox', 'InventoryUser': 'Inventory_Dashboard', 'InventoryManager': 'Inventory_Dashboard',
    'Billing': 'Invoice_Overview', 'InvoicingManager': 'Invoice_Overview', 'Administrator': 'Company_Edit',
}

ALL = list(ROLE_HOME)
SALES = ['SalesUser', 'SalesManager']
PURCH = ['Purchaser', 'PurchaseManager']
INV = ['InventoryUser', 'InventoryManager']
BILL = ['Billing', 'InvoicingManager']

S = {}


def screen(name, kind, title, entity, roles, reached, param=None, **kw):
    S[name] = dict(name=name, kind=kind, title=title, entity=entity, roles=roles, reached=reached, param=param, **kw)


# ── F001 Contacts / company / users ─────────────────────────────────────────────────────────
screen('Partner_Overview', 'list', 'Contacts', 'Partners.Partner', SALES + PURCH + BILL + ['Administrator'], ['menu Contacts'],
       columns=['Name', 'Email', 'Phone', 'City', 'Partner_Country', 'IsCustomer', 'IsVendor', 'Partner_Salesperson'],
       filters=['IsCustomer', 'IsVendor', 'Partner_Tags'], open='Partner_NewEdit', new='Partner_NewEdit',
       rows=[['Azure Interior', 'azure.interior24@example.com', '+31 20 555 0101', 'Amsterdam', 'Netherlands', 'yes', '', 'Mitchell Admin'],
             ['Wood Corner', 'wood.corner26@example.com', '+31 10 555 0144', 'Rotterdam', 'Netherlands', 'yes', 'yes', 'Marc Demo']])
screen('Partner_NewEdit', 'form', 'Contact', 'Partners.Partner', SALES + PURCH + BILL + ['Administrator'],
       ['row of Partner_Overview', 'New on Partner_Overview', 'customer link on SalesOrder_NewEdit'], param='Partners.Partner',
       sections=[('Identity', ['Name', 'IsCompany', 'Partner_ParentCompany', 'JobPosition', 'Partner_Tags']),
                 ('Address', ['Street', 'Street2', 'Zip', 'City', 'Partner_Country']),
                 ('Contact', ['Email', 'Phone', 'Mobile', 'Website', 'VATNumber', 'Reference']),
                 ('Sales & purchase', ['IsCustomer', 'Partner_Salesperson', 'Partner_CustomerPaymentTerm', 'Partner_Pricelist',
                                       'IsVendor', 'Partner_VendorPaymentTerm'])],
       lines=dict(entity='Partners.Partner', via='Partner_ParentCompany', title='Contacts & addresses',
                  columns=['AddressType', 'Name', 'Email', 'Phone', 'City'], open='PartnerChild_NewEdit',
                  rows=[['Contact', 'Brandon Freeman', 'brandon.freeman55@example.com', '+31 20 555 0102', 'Amsterdam'],
                        ['Invoice address', 'Azure Interior, Accounts', 'ap@azure.example.com', '', 'Amsterdam']]),
       notes='Notes', buttons=[('Save', 'ACT_Partner_Save'), ('Archive', 'ACT_Partner_Save')],
       sample={'Name': 'Azure Interior', 'IsCompany': True, 'Email': 'azure.interior24@example.com', 'City': 'Amsterdam'})
screen('PartnerChild_NewEdit', 'popup', 'Contact or address', 'Partners.Partner', SALES + PURCH + BILL,
       ['row / Add line in Contacts & addresses on Partner_NewEdit'], param='Partners.Partner',
       sections=[('Type', ['AddressType']), ('Contact', ['Name', 'JobPosition', 'Email', 'Phone']),
                 ('Address', ['Street', 'Zip', 'City', 'Partner_Country'])],
       buttons=[('Save', 'ACT_Partner_Save')], back='Partner_NewEdit')
screen('Company_Edit', 'form', 'Company', 'Core.Company', ['Administrator'], ['menu Configuration › Company', 'home of Administrator'],
       param=None, singleton='DS_Company_Get (the one company)',
       sections=[('Identity', ['Name', 'VATNumber', 'Company_Currency', 'Website']),
                 ('Address', ['Street', 'Street2', 'Zip', 'City', 'Company_Country', 'Email', 'Phone']),
                 ('Sales', ['QuotationValidityDays', 'Company_DefaultSalesTax']),
                 ('Purchase', ['POApprovalEnabled', 'POApprovalThreshold', 'PurchaseLeadDays', 'Company_DefaultPurchaseTax']),
                 ('Invoicing', ['InvoiceTerms'])],
       links=[('Users: Administration › Accounts, a row opens the user profile', 'UserProfile_Edit')],
       buttons=[('Save', 'save')])
screen('UserProfile_Edit', 'popup', 'User profile', 'Partners.UserProfile', ['Administrator'], ['row of Account_Overview (Administration)', 'Users link on Company_Edit (prototype stand-in for Account_Overview)'],
       param='Partners.UserProfile', sections=[('Profile', ['DisplayName', 'UserProfile_Partner', 'UserProfile_Account'])],
       buttons=[('Save', 'save')], back='Company_Edit')
screen('Sequence_Overview', 'list', 'Document numbering', 'Core.Sequence', ['Administrator'], ['menu Configuration › Numbering'],
       columns=['Code', 'Prefix', 'Padding', 'NextNumber'], editable=True,
       rows=[['sale.order', 'S', '5', '43'], ['purchase.order', 'P', '5', '18']])

# ── F002 / F003 Products ────────────────────────────────────────────────────────────────────
screen('UoMCategory_Overview', 'list', 'Units of measure', 'Products.UoMCategory', ['InventoryManager', 'SalesManager', 'Administrator'],
       ['menu Configuration › Units of measure'], columns=['Name'], open='UoMCategory_NewEdit', new='UoMCategory_NewEdit',
       rows=[['Unit'], ['Weight']])
screen('UoMCategory_NewEdit', 'form', 'Unit category', 'Products.UoMCategory', ['InventoryManager', 'SalesManager', 'Administrator'],
       ['row of UoMCategory_Overview'], param='Products.UoMCategory', sections=[('Category', ['Name'])],
       lines=dict(entity='Products.UoM', via='UoM_Category', title='Units', editable=True,
                  columns=['Name', 'UoMType', 'Factor', 'Rounding', 'Active'],
                  rows=[['Units', 'Reference unit', '1.00', '0.01', 'yes'], ['Dozens', 'Bigger', '0.0833', '0.01', 'yes']]),
       buttons=[('Save', 'VAL_UoMCategory')])
screen('Product_Overview', 'list', 'Products', 'Products.Product', SALES + PURCH + INV, ['menu Products'],
       columns=['InternalReference', 'Name', 'ProductType', 'Product_Category', 'SalesPrice', 'Cost', 'Product_UoM'],
       filters=['ProductType', 'CanBeSold', 'CanBePurchased', 'Product_Category'], open='Product_NewEdit', new='Product_NewEdit',
       rows=[['FURN_7800', 'Desk Combination', 'Goods', 'All / Saleable / Office', '450.00', '290.00', 'Units'],
             ['FURN_8888', 'Office Lamp', 'Goods', 'All / Saleable / Office', '40.00', '22.50', 'Units']])
screen('Product_NewEdit', 'form', 'Product', 'Products.Product', ['SalesManager', 'PurchaseManager', 'InventoryManager'],
       ['row of Product_Overview', 'New on Product_Overview'], param='Products.Product',
       sections=[('General', ['Name', 'InternalReference', 'Barcode', 'ProductType', 'TrackInventory', 'Product_Category', 'Product_Tags']),
                 ('Sales', ['CanBeSold', 'SalesPrice', 'Product_CustomerTaxes', 'InvoicePolicy', 'SalesDescription', 'CustomerLeadDays']),
                 ('Purchase', ['CanBePurchased', 'Cost', 'Product_VendorTaxes', 'BillPolicy', 'Product_PurchaseUoM', 'PurchaseDescription']),
                 ('Inventory', ['Product_UoM', 'Weight', 'Volume'])],
       links=[('Vendor prices', 'VendorPrice_Overview')], image=True, notes='InternalNotes',
       buttons=[('Save', 'ACT_Product_Save'), ('Archive', 'ACT_Product_Save')])
screen('ProductCategory_Overview', 'list', 'Product categories', 'Products.ProductCategory', ['SalesManager', 'InventoryManager', 'Administrator'],
       ['menu Configuration › Product categories'], columns=['FullName'], open='ProductCategory_NewEdit', new='ProductCategory_NewEdit',
       rows=[['All / Saleable'], ['All / Saleable / Office']])
screen('ProductCategory_NewEdit', 'popup', 'Product category', 'Products.ProductCategory', ['SalesManager', 'InventoryManager', 'Administrator'],
       ['row / New on ProductCategory_Overview'], param='Products.ProductCategory',
       sections=[('Category', ['Name', 'ProductCategory_Parent'])], buttons=[('Save', 'save')], back='ProductCategory_Overview')
screen('Pricelist_Overview', 'list', 'Pricelists', 'Products.Pricelist', ['SalesManager'], ['menu Products › Pricelists'],
       columns=['Name', 'Pricelist_Currency', 'Active'], open='Pricelist_NewEdit', new='Pricelist_NewEdit',
       rows=[['Public pricelist', 'EUR', 'yes'], ['Wholesale', 'EUR', 'yes']])
screen('Pricelist_NewEdit', 'form', 'Pricelist', 'Products.Pricelist', ['SalesManager'], ['row of Pricelist_Overview'], param='Products.Pricelist',
       sections=[('Pricelist', ['Name', 'Pricelist_Currency', 'Sequence'])],
       lines=dict(entity='Products.PriceRule', via='PriceRule_Pricelist', title='Price rules', editable=True,
                  columns=['AppliesTo', 'PriceRule_Category', 'PriceRule_Product', 'MinQuantity', 'Computation', 'FixedPrice',
                           'DiscountPercent', 'ValidFrom', 'ValidTo'],
                  rows=[['Product category', 'All / Saleable / Office', '', '10', 'Discount', '', '10.00', '', ''],
                        ['Product', '', 'Office Lamp', '1', 'Fixed price', '35.00', '', '2026-01-01', '2026-12-31']]),
       buttons=[('Save', 'save')])

# ── F004 Sales ──────────────────────────────────────────────────────────────────────────────
SO_LINES = dict(entity='Sales.SalesOrderLine', via='SalesOrderLine_SalesOrder', title='Order lines', editable=True,
                # Description and Invoiced left out of the line editor: ten columns clipped every cell at 1280 (ui-review 2026-10-15
                # Sales P2); the description defaults from the product, invoiced quantities show as the order's invoice status
                columns=['SalesOrderLine_Product', 'Quantity', 'QuantityDelivered', 'SalesOrderLine_UoM',
                         'UnitPrice', 'SalesOrderLine_Taxes', 'DiscountPercent', 'Subtotal'],
                rows=[['[FURN_7800] Desk Combination', '2.00', '0.00', 'Units', '450.00', 'VAT 21%', '', '900.00'],
                      ['(section)', '', '', '', '', '', '', ''],
                      ['[FURN_8888] Office Lamp', '4.00', '0.00', 'Units', '40.00', 'VAT 21%', '10.00', '144.00']],
                onchange='ACT_SalesOrderLine_ChangeProduct', recompute='SUB_SalesOrder_RecomputeTotals')
screen('SalesOrder_Overview', 'list', 'Quotations & sales orders', 'Sales.SalesOrder', ['SalesManager', 'SalesUser', 'Billing'],
       ['menu Sales › Quotations & orders', 'home of SalesUser / SalesManager'],
       tabs=['All (11)', 'Quotations (4)', 'Sales orders (7)', 'To invoice (2)'],
       columns=['Number', 'OrderDate', 'SalesOrder_Customer', 'SalesOrder_Salesperson', 'AmountTotal', 'Status', 'InvoiceStatus', 'DeliveryStatus'],
       filters=['Status', 'InvoiceStatus', 'SalesOrder_Salesperson'], open='SalesOrder_NewEdit', new='SalesOrder_NewEdit',
       rows=[['S00042', '2026-10-12', 'Azure Interior', 'Mitchell Admin', '1 263.24', 'Sales order', 'To invoice', 'Not delivered'],
             ['S00043', '2026-10-14', 'Wood Corner', 'Marc Demo', '544.50', 'Quotation', 'Nothing to invoice', '']],
       xpath="SalesUser: [SalesOrder_Salesperson = '[%CurrentUser%]'] (Odoo rule 'Personal Orders')")
screen('SalesOrder_NewEdit', 'form', 'Sales order', 'Sales.SalesOrder', SALES,
       ['row of SalesOrder_Overview', 'New on SalesOrder_Overview', 'Source order link on Transfer_NewEdit', 'order link on Invoice_NewEdit'],
       param='Sales.SalesOrder', statusbar=('Status', ['Quotation', 'Quotation sent', 'Sales order'], 'Sales order'),
       buttons=[('Create invoice', 'ACT_SalesOrder_CreateInvoice', ['Sales order']),
                ('Send (mark as sent)', 'ACT_SalesOrder_MarkSent', ['Quotation']),
                ('Confirm', 'ACT_SalesOrder_Confirm', ['Quotation', 'Quotation sent']),
                ('Cancel order', 'ACT_SalesOrder_Cancel', ['Quotation', 'Quotation sent', 'Sales order']),
                ('Set to quotation', 'ACT_SalesOrder_SetToQuotation', ['Cancelled']),
                ('Lock', 'ACT_SalesOrder_ToggleLock', ['Sales order']),
                ('Save', 'ACT_SalesOrder_Save')],
       smart=[('Delivery', 'Transfer_NewEdit', '1'), ('Invoices', 'Invoice_NewEdit', '0')],
       header='Number',
       sections=[('Customer', ['SalesOrder_Customer', 'SalesOrder_InvoiceAddress', 'SalesOrder_DeliveryAddress', 'SalesOrder_QuotationTemplate']),
                 ('Terms', ['ExpirationDate', 'SalesOrder_Pricelist', 'SalesOrder_PaymentTerm', 'OrderDate']),
                 ('Other info', ['SalesOrder_Salesperson', 'SalesOrder_SalesTeam', 'CustomerReference', 'DeliveryDate', 'Source',
                                 'InvoiceStatus', 'DeliveryStatus', 'Locked'])],
       lines=SO_LINES, totals=['AmountUntaxed', 'AmountTax', 'AmountTotal'], notes='TermsAndConditions',
       popups=['CreateInvoice_Popup'], sample={'Number': 'S00042', 'ExpirationDate': '2026-11-11', 'OrderDate': '2026-10-12', 'DeliveryDate': '2026-10-20'})
screen('QuotationTemplate_Overview', 'list', 'Quotation templates', 'Sales.QuotationTemplate', ['SalesManager'],
       ['menu Sales › Quotation templates'], columns=['Name', 'ValidityDays', 'Active'], open='QuotationTemplate_NewEdit',
       new='QuotationTemplate_NewEdit', rows=[['Office starter pack', '30', 'yes'], ['Lighting refresh', '15', 'yes']])
screen('QuotationTemplate_NewEdit', 'form', 'Quotation template', 'Sales.QuotationTemplate', ['SalesManager'],
       ['row of QuotationTemplate_Overview'], param='Sales.QuotationTemplate',
       sections=[('Template', ['Name', 'ValidityDays'])],
       lines=dict(entity='Sales.QuotationTemplateLine', via='QuotationTemplateLine_Template', title='Lines', editable=True,
                  columns=['LineType', 'QuotationTemplateLine_Product', 'Description', 'Quantity', 'QuotationTemplateLine_UoM'],
                  rows=[['Product line', 'Desk Combination', 'Desk combination', '1.00', 'Units'],
                        ['Product line', 'Office Lamp', 'Office lamp', '2.00', 'Units']]),
       notes='TermsAndConditions', buttons=[('Save', 'save')])
screen('SalesTeam_Overview', 'list', 'Sales teams', 'Sales.SalesTeam', ['SalesManager'], ['menu Sales › Sales teams'],
       columns=['Name', 'SalesTeam_Leader', 'InvoicingTarget'], open='SalesTeam_NewEdit', new='SalesTeam_NewEdit',
       rows=[['Sales', 'Mitchell Admin', '50 000.00'], ['Website', 'Marc Demo', '20 000.00']])
screen('SalesTeam_NewEdit', 'form', 'Sales team', 'Sales.SalesTeam', ['SalesManager'], ['row of SalesTeam_Overview'], param='Sales.SalesTeam',
       sections=[('Team', ['Name', 'SalesTeam_Leader', 'InvoicingTarget', 'SalesTeam_Members'])], buttons=[('Save', 'save')])
screen('SalesAnalysis_Report', 'report', 'Sales analysis', 'Sales.SalesAnalysis', ['SalesManager'], ['menu Reporting › Sales analysis'],
       kpis=[('Revenue (confirmed)', '84 210.00'), ('Orders', '37'), ('Average order', '2 275.95')],
       charts=['Revenue per month', 'Revenue per salesperson'], columns=['Month', 'Customer', 'Product', 'Salesperson', 'Quantity', 'Untaxed'],
       rows=[['2026-09', 'Azure Interior', 'Desk Combination', 'Mitchell Admin', '6', '2 700.00'],
             ['2026-10', 'Wood Corner', 'Office Lamp', 'Marc Demo', '12', '432.00']])

# ── F005 Purchasing ─────────────────────────────────────────────────────────────────────────
PO_LINES = dict(entity='Purchasing.PurchaseOrderLine', via='PurchaseOrderLine_PurchaseOrder', title='Products', editable=True,
                # Description and Billed left out of the line editor, as for sales lines (ui-review 2026-10-15 Sales P2)
                columns=['PurchaseOrderLine_Product', 'Quantity', 'QuantityReceived', 'PurchaseOrderLine_UoM',
                         'UnitPrice', 'PurchaseOrderLine_Taxes', 'Subtotal'],
                rows=[['[FURN_8888] Office Lamp', '50.00', '0.00', 'Units', '22.50', 'VAT 21% (purchase)', '1 125.00'],
                      ['[FURN_7800] Desk Combination', '10.00', '0.00', 'Units', '290.00', 'VAT 21% (purchase)', '2 900.00']],
                onchange='ACT_PurchaseOrderLine_ChangeProduct', recompute='SUB_PurchaseOrder_RecomputeTotals')
screen('PurchaseOrder_Overview', 'list', 'Requests for quotation & purchase orders', 'Purchasing.PurchaseOrder', PURCH + ['Billing'],
       ['menu Purchase › RFQs & orders', 'home of Purchaser'], tabs=['All (9)', 'RFQs (3)', 'To approve (1)', 'Purchase orders (5)'],
       columns=['Number', 'OrderDeadline', 'PurchaseOrder_Vendor', 'PurchaseOrder_Buyer', 'AmountTotal', 'Status', 'ReceiptStatus', 'BillingStatus'],
       filters=['Status', 'ReceiptStatus', 'BillingStatus'], open='PurchaseOrder_NewEdit', new='PurchaseOrder_NewEdit',
       rows=[['P00018', '2026-10-10', 'Wood Corner', 'Marc Demo', '4 871.25', 'To approve', 'Not received', 'Nothing to invoice'],
             ['P00017', '2026-10-03', 'Deco Addict', 'Marc Demo', '871.20', 'Purchase order', 'Partially received', 'To invoice']])
screen('PurchaseOrder_NewEdit', 'form', 'Purchase order', 'Purchasing.PurchaseOrder', PURCH,
       ['row of PurchaseOrder_Overview', 'New on PurchaseOrder_Overview', 'Source order link on Transfer_NewEdit', 'order link on Invoice_NewEdit',
        'Open order on PurchaseApproval_Task'],
       param='Purchasing.PurchaseOrder', statusbar=('Status', ['RFQ', 'RFQ sent', 'To approve', 'Purchase order'], 'To approve'),
       buttons=[('Send (mark as sent)', 'ACT_PurchaseOrder_MarkSent', ['RFQ']),
                ('Confirm order', 'ACT_PurchaseOrder_Confirm', ['RFQ', 'RFQ sent']),
                ('Create bill', 'ACT_PurchaseOrder_CreateBill', ['Purchase order']),
                ('Cancel order', 'ACT_PurchaseOrder_Cancel', ['RFQ', 'RFQ sent', 'To approve', 'Purchase order']),
                ('Set to RFQ', 'ACT_PurchaseOrder_SetToDraft', ['Cancelled']),
                ('Lock', 'ACT_PurchaseOrder_ToggleLock', ['Purchase order']),
                ('Save', 'ACT_PurchaseOrder_Save')],
       smart=[('Receipt', 'Transfer_NewEdit', '1'), ('Bills', 'Invoice_NewEdit', '0')], header='Number',
       sections=[('Vendor', ['PurchaseOrder_Vendor', 'VendorReference', 'PurchaseOrder_Currency']),
                 ('Dates', ['OrderDeadline', 'ExpectedArrival', 'ConfirmationDate']),
                 ('Other info', ['PurchaseOrder_Buyer', 'PurchaseOrder_PaymentTerm', 'Source', 'ReceiptStatus', 'BillingStatus', 'Locked'])],
       lines=PO_LINES, totals=['AmountUntaxed', 'AmountTax', 'AmountTotal'], notes='Notes')
screen('PurchaseApproval_Inbox', 'inbox', 'Purchase approvals', 'Purchasing.PurchaseOrder', ['PurchaseManager'],
       ['menu Purchase › Approvals', 'home of PurchaseManager'],
       columns=['Number', 'PurchaseOrder_Vendor', 'PurchaseOrder_Buyer', 'AmountTotal', 'OrderDeadline'], open='PurchaseApproval_Task',
       rows=[['P00018', 'Wood Corner', 'Marc Demo', '4 871.25', '2026-10-10'], ['P00016', 'Gemini Furniture', 'Marc Demo', '12 400.00', '2026-10-09']],
       source='Workflow Commons task inbox (Buy), filtered to WF_PurchaseOrderApproval user tasks assigned to the current user')
screen('PurchaseApproval_Task', 'task', 'Approve purchase order', 'Purchasing.PurchaseOrder', ['PurchaseManager'],
       ['row of PurchaseApproval_Inbox'], param='System.WorkflowUserTask',
       source='page parameters $WorkflowUserTask (System.WorkflowUserTask) + $WorkflowContext (Purchasing.PurchaseOrder) — workflow-structure-rules.md §11 (CE7412)',
       sections=[('Order', ['Number', 'PurchaseOrder_Vendor', 'PurchaseOrder_Buyer', 'AmountTotal', 'OrderDeadline', 'ExpectedArrival'])],
       lines=dict(PO_LINES, editable=False), reason=True,
       buttons=[('Approve', 'SUB_PurchaseOrder_Approve'), ('Reject', 'ACT_PurchaseOrder_Reject')],
       links=[('Open order', 'PurchaseOrder_NewEdit')])
screen('VendorPrice_Overview', 'list', 'Vendor prices', 'Purchasing.VendorPrice', PURCH, ['menu Purchase › Vendor prices', 'Vendor prices link on Product_NewEdit'],
       columns=['VendorPrice_Vendor', 'VendorPrice_Product', 'VendorProductCode', 'MinQuantity', 'Price', 'Discount', 'LeadTimeDays', 'ValidFrom', 'ValidTo'],
       filters=['VendorPrice_Vendor', 'VendorPrice_Product'], editable=True, add=True,
       rows=[['Wood Corner', 'Desk Combination', 'WC-DESK-01', '1', '290.00', '', '5', '', ''],
             ['Wood Corner', 'Office Lamp', 'WC-LAMP-07', '20', '22.50', '5.00', '5', '2026-01-01', '']])
screen('PurchaseAnalysis_Report', 'report', 'Purchase analysis', 'Purchasing.PurchaseAnalysis', ['PurchaseManager'], ['menu Reporting › Purchase analysis'],
       kpis=[('Purchased (confirmed)', '41 380.00'), ('Orders', '18'), ('Received on time', '83 %')],
       charts=['Purchases per month', 'Purchases per vendor'], columns=['Month', 'Vendor', 'Product', 'Ordered', 'Received', 'Billed', 'Untaxed'],
       rows=[['2026-09', 'Wood Corner', 'Office Lamp', '50', '50', '50', '1 125.00'], ['2026-10', 'Deco Addict', 'Desk Combination', '4', '2', '0', '1 160.00']])

# ── F006 / F007 Inventory ───────────────────────────────────────────────────────────────────
screen('Inventory_Dashboard', 'dashboard', 'Inventory overview', 'Inventory.OperationType', INV,
       ['menu Inventory › Overview', 'home of InventoryUser / InventoryManager'],
       tiles=[('Receipts', 'WH/IN', [('Ready', '3'), ('Waiting', '1'), ('Late', '0')]),
              ('Delivery orders', 'WH/OUT', [('Ready', '2'), ('Waiting', '4'), ('Late', '1')]),
              ('Internal transfers', 'WH/INT', [('Ready', '0'), ('Waiting', '0'), ('Late', '0')])],
       open='Transfer_Overview')
screen('Transfer_Overview', 'list', 'Transfers', 'Inventory.Transfer', INV, ['menu Inventory › Transfers', 'tile of Inventory_Dashboard'],
       tabs=['All', 'Receipts', 'Deliveries', 'Internal'],
       sort='ScheduledDate', columns=['Number', 'Transfer_Partner', 'ScheduledDate', 'SourceDocument', 'Transfer_OperationType', 'Status'],
       filters=['Status', 'Transfer_OperationType'], open='Transfer_NewEdit', new='Transfer_NewEdit',
       rows=[['WH/OUT/00031', 'Azure Interior', '2026-10-15', 'S00042', 'Delivery orders', 'Waiting'],
             ['WH/IN/00012', 'Wood Corner', '2026-10-17', 'P00017', 'Receipts', 'Ready']])
screen('Transfer_NewEdit', 'form', 'Transfer', 'Inventory.Transfer', INV + ['SalesUser', 'SalesManager', 'Purchaser', 'PurchaseManager'],
       ['row of Transfer_Overview', 'Delivery / Receipt smart button on SalesOrder_NewEdit / PurchaseOrder_NewEdit'],
       param='Inventory.Transfer', statusbar=('Status', ['Draft', 'Waiting', 'Ready', 'Done'], 'Ready'),
       buttons=[('Validate', 'ACT_Transfer_Validate', ['Waiting', 'Ready']), ('Mark as to do', 'ACT_Transfer_Confirm', ['Draft']),
                ('Check availability', 'ACT_Transfer_CheckAvailability', ['Waiting']),
                ('Cancel transfer', 'ACT_Transfer_Cancel', ['Draft', 'Waiting', 'Ready']), ('Save', 'save')],
       header='Number',
       sections=[('Transfer', ['Transfer_Partner', 'Transfer_OperationType', 'Transfer_SourceLocation', 'Transfer_DestinationLocation']),
                 ('Dates', ['ScheduledDate', 'Deadline', 'DateDone']),
                 # order pickers left out: sales and purchase users open this page from their order (Inventory.Reader) and hold no
                 # read access to the other side's orders (CE2729); the source document and the Open order links cover it
                 ('Origin', ['SourceDocument', 'Transfer_Backorder', 'Transfer_Responsible'])],
       # 'Open sales order' / 'Open purchase order' links wait for the read-only order views (PROJECT.md C1-01, Invoicing phase):
       # opening the order forms from here made each side's users reach the other side's orders (CE2729)
       lines=dict(entity='Inventory.StockMove', via='StockMove_Transfer', title='Operations', editable=True,
                  columns=['StockMove_Product', 'DemandQuantity', 'Quantity', 'StockMove_UoM', 'Picked', 'Status'],
                  rows=[['[FURN_7800] Desk Combination', '2.00', '2.00', 'Units', 'yes', 'Ready'],
                        ['[FURN_8888] Office Lamp', '4.00', '3.00', 'Units', 'yes', 'Ready']]),
       notes='Notes', popup='ValidateTransfer_Popup')
screen('ValidateTransfer_Popup', 'popup', 'Create backorder?', 'Inventory.ValidateTransferRequest', INV,
       ['Validate on Transfer_NewEdit when a move has quantity < demand'], param='Inventory.ValidateTransferRequest',
       message='You have processed less than the initial demand. Create a backorder for the remaining products, or cancel them?',
       buttons=[('Create backorder', 'SUB_Transfer_Done'), ('No backorder', 'SUB_Transfer_Done')], back='Transfer_NewEdit')
screen('StockLevel_Overview', 'list', 'Stock', 'Inventory.StockLevel', INV, ['menu Inventory › Stock'],
       columns=['StockLevel_Product', 'StockLevel_Location', 'Quantity', 'ReservedQuantity', 'CountedQuantity', 'ScheduledCountDate'],
       filters=['StockLevel_Product', 'StockLevel_Location'], editable=True,
       rows=[['[FURN_7800] Desk Combination', 'WH/Stock', '14.00', '2.00', '13.00', '2026-12-31'],
             ['[FURN_8888] Office Lamp', 'WH/Stock', '61.00', '4.00', '', '']])
screen('ReorderRule_Overview', 'list', 'Reorder rules', 'Inventory.ReorderRule', ['InventoryManager', 'Purchaser'], ['menu Inventory › Reorder rules'],
       columns=['ReorderRule_Product', 'ReorderRule_Location', 'ReorderRule_Vendor', 'MinQuantity', 'MaxQuantity', 'QuantityMultiple', 'Automatic'],
       editable=True, add=True, buttons=[('Order once', 'SUB_ReorderRule_Replenish'), ('Run scheduler', 'SCE_ReorderRules_Run')],
       rows=[['[FURN_8888] Office Lamp', 'WH/Stock', 'Wood Corner', '20.00', '100.00', '10.00', 'yes'],
             ['[FURN_7800] Desk Combination', 'WH/Stock', 'Wood Corner', '5.00', '15.00', '1.00', '']])
screen('Warehouse_Edit', 'form', 'Warehouse', 'Inventory.Warehouse', ['InventoryManager', 'Administrator'], ['menu Configuration › Warehouse'],
       singleton='DS_Warehouse_Get (the one warehouse)',
       sections=[('Warehouse', ['Name', 'ShortName', 'Warehouse_Address', 'Warehouse_StockLocation'])],
       lines=dict(entity='Inventory.OperationType', via='OperationType_Warehouse', title='Operation types', editable=True,
                  columns=['Name', 'Kind', 'SequenceCode', 'OperationType_DefaultSource', 'OperationType_DefaultDestination', 'CreateBackorder'],
                  rows=[['Receipts', 'Receipt', 'IN', 'Vendors', 'WH/Stock', 'yes'], ['Delivery orders', 'Delivery', 'OUT', 'WH/Stock', 'Customers', 'yes']]),
       buttons=[('Save', 'save')])

# ── F008 Invoicing ──────────────────────────────────────────────────────────────────────────
screen('Invoice_Overview', 'list', 'Invoices & bills', 'Invoicing.Invoice', BILL + ['SalesManager', 'PurchaseManager'],
       ['menu Invoicing › Invoices & bills', 'home of Billing / InvoicingManager'],
       tabs=['All', 'Customer invoices', 'Vendor bills', 'Credit notes'],
       columns=['Number', 'Invoice_Partner', 'InvoiceDate', 'DueDate', 'AmountTotal', 'AmountDue', 'Status', 'PaymentStatus'],
       filters=['InvoiceType', 'Status', 'PaymentStatus', 'Invoice_Partner'], open='Invoice_NewEdit', new='Invoice_NewEdit',
       buttons=[('Register payment', 'ACT_Invoice_RegisterPayment')],
       rows=[['INV/2026/00021', 'Azure Interior', '2026-10-12', '2026-11-11', '1 263.24', '1 263.24', 'Posted', 'Not paid'],
             ['INV/2026/00020', 'Wood Corner', '2026-10-01', '2026-10-31', '544.50', '244.50', 'Posted', 'Partially paid']])
screen('Invoice_NewEdit', 'form', 'Invoice', 'Invoicing.Invoice', BILL + SALES + PURCH,
       ['row of Invoice_Overview', 'New on Invoice_Overview', 'Invoices / Bills smart button on SalesOrder_NewEdit / PurchaseOrder_NewEdit',
        'invoice link on Payment_View'],
       param='Invoicing.Invoice', statusbar=('Status', ['Draft', 'Posted'], 'Posted'),
       buttons=[('Register payment', 'ACT_Invoice_RegisterPayment', ['Posted']), ('Confirm', 'ACT_Invoice_Post', ['Draft']),
                ('Credit note', 'ACT_Invoice_CreateCreditNote', ['Posted']), ('Reset to draft', 'ACT_Invoice_ResetToDraft', ['Posted']),
                ('Cancel', 'ACT_Invoice_Cancel', ['Draft'])],
       header='Number', badge='PaymentStatus',
       sections=[('Partner', ['InvoiceType', 'Invoice_Partner', 'Invoice_DeliveryAddress', 'Reference', 'PaymentReference', 'Invoice_BankAccount']),
                 ('Dates & terms', ['InvoiceDate', 'DueDate', 'Invoice_PaymentTerm', 'Invoice_Currency']),
                 # no Sales orders / Purchase order pickers: sales and purchase users open this form (2026-10-16) and may not
                 # read each other's orders (CE2729); the source document shows the order numbers
                 ('Other info', ['Invoice_Salesperson', 'SourceDocument', 'Invoice_ReversalOf'])],
       links=[('Open sales order', 'SalesOrder_NewEdit'), ('Open purchase order', 'PurchaseOrder_NewEdit')],
       lines=dict(entity='Invoicing.InvoiceLine', via='InvoiceLine_Invoice', title='Invoice lines', editable=True,
                  columns=['InvoiceLine_Product', 'Description', 'Quantity', 'InvoiceLine_UoM', 'UnitPrice', 'InvoiceLine_Taxes', 'DiscountPercent', 'Subtotal'],
                  rows=[['[FURN_7800] Desk Combination', 'S00042 – Desk combination', '2.00', 'Units', '450.00', 'VAT 21%', '', '900.00'],
                        ['[FURN_8888] Office Lamp', 'S00042 – Office lamp', '4.00', 'Units', '40.00', 'VAT 21%', '10.00', '144.00']],
                  recompute='SUB_Invoice_RecomputeTotals'),
       totals=['AmountUntaxed', 'AmountTax', 'AmountTotal', 'AmountDue'], notes='Notes', lines_locked=True,
       popups=['RegisterPayment_Popup', 'CreditNote_Popup'],
       sample={'Number': 'INV/2026/00021', 'InvoiceDate': '2026-10-12', 'DueDate': '2026-11-11', 'SourceDocument': 'S00042', 'PaymentReference': 'INV/2026/00021'})
screen('CreateInvoice_Popup', 'popup', 'Create invoice', 'Sales.CreateInvoiceRequest', SALES + BILL,
       ['Create invoice on SalesOrder_NewEdit / selection on SalesOrder_Overview'], param='Sales.CreateInvoiceRequest',
       sections=[('Options', ['ConsolidatePerCustomer', 'CreateInvoiceRequest_SalesOrders'])],
       message='Regular invoice for the quantities to invoice of the selected orders (down payments are not in scope).',
       buttons=[('Create invoice', 'SUB_SalesOrders_CreateInvoices')], back='SalesOrder_NewEdit')
screen('RegisterPayment_Popup', 'popup', 'Register payment', 'Invoicing.RegisterPaymentRequest', BILL,
       ['Register payment on Invoice_NewEdit / selection on Invoice_Overview'], param='Invoicing.RegisterPaymentRequest',
       sections=[('Payment', ['Amount', 'PaymentDate', 'Method', 'Memo', 'RegisterPaymentRequest_Invoices'])], sample={'Amount': '244.50', 'Memo': 'INV/2026/00020'},
       buttons=[('Create payment', 'SUB_Payment_Create')], back='Invoice_NewEdit')
screen('CreditNote_Popup', 'popup', 'Credit note', 'Invoicing.CreditNoteRequest', BILL, ['Credit note on Invoice_NewEdit'],
       param='Invoicing.CreditNoteRequest', sections=[('Reversal', ['Reason', 'ReversalDate', 'CreditNoteRequest_Invoice'])],
       buttons=[('Reverse', 'ACT_Invoice_CreateCreditNote')], back='Invoice_NewEdit')
screen('Payment_Overview', 'list', 'Payments', 'Invoicing.Payment', BILL, ['menu Invoicing › Payments'],
       columns=['Number', 'PaymentDate', 'Payment_Partner', 'Direction', 'Method', 'Amount', 'Status'], filters=['Direction', 'Status'],
       open='Payment_View', rows=[['PAY/2026/00009', '2026-10-13', 'Wood Corner', 'Receive money', 'Bank transfer', '300.00', 'Paid'],
                                  ['PAY/2026/00008', '2026-10-08', 'Deco Addict', 'Send money', 'Bank transfer', '871.20', 'Paid']])
screen('Payment_View', 'form', 'Payment', 'Invoicing.Payment', BILL, ['row of Payment_Overview', 'payment row on Invoice_NewEdit'],
       param='Invoicing.Payment', readonly=True, header='Number',
       sections=[('Payment', ['Direction', 'PartnerKind', 'Payment_Partner', 'Amount', 'Payment_Currency', 'PaymentDate', 'Method', 'Memo', 'Status'])],
       lines=dict(entity='Invoicing.PaymentAllocation', via='PaymentAllocation_Payment', title='Allocated to', editable=False,
                  columns=['PaymentAllocation_Invoice', 'Amount'], rows=[['INV/2026/00020', '300.00'], ['INV/2026/00017', '0.00']],
                  open='Invoice_NewEdit', open_via='PaymentAllocation_Invoice', add=False))
screen('Tax_Overview', 'list', 'Taxes', 'Core.Tax', ['InvoicingManager', 'Administrator'], ['menu Configuration › Taxes'],
       columns=['Name', 'Scope', 'Computation', 'Amount', 'IncludedInPrice', 'Active'], open='Tax_NewEdit', new='Tax_NewEdit',
       rows=[['VAT 21%', 'Sales', 'Percentage', '21.00', '', 'yes'], ['VAT 21% (purchase)', 'Purchases', 'Percentage', '21.00', '', 'yes']])
screen('Tax_NewEdit', 'popup', 'Tax', 'Core.Tax', ['InvoicingManager', 'Administrator'], ['row / New on Tax_Overview'], param='Core.Tax',
       sections=[('Tax', ['Name', 'Scope', 'Computation', 'Amount', 'IncludedInPrice', 'LabelOnInvoice', 'Sequence'])],
       buttons=[('Save', 'save')], back='Tax_Overview')
screen('PaymentTerm_Overview', 'list', 'Payment terms', 'Core.PaymentTerm', ['InvoicingManager', 'Administrator'], ['menu Configuration › Payment terms'],
       columns=['Name', 'Note'], open='PaymentTerm_NewEdit', new='PaymentTerm_NewEdit',
       rows=[['30 days', 'Payment within 30 days'], ['30% now, balance in 60 days', '']])
screen('PaymentTerm_NewEdit', 'form', 'Payment term', 'Core.PaymentTerm', ['InvoicingManager', 'Administrator'], ['row of PaymentTerm_Overview'],
       param='Core.PaymentTerm', sections=[('Term', ['Name', 'Note'])],
       lines=dict(entity='Core.PaymentTermLine', via='PaymentTermLine_PaymentTerm', title='Instalments', editable=True,
                  columns=['Value', 'ValueAmount', 'Days', 'DelayType'],
                  rows=[['Percent', '30.00', '0', 'Days after invoice date'], ['Percent', '70.00', '60', 'Days after invoice date']]),
       buttons=[('Save', 'save')])
screen('InvoiceAnalysis_Report', 'report', 'Invoice analysis', 'Invoicing.InvoiceAnalysis', ['InvoicingManager'], ['menu Reporting › Invoice analysis'],
       kpis=[('Invoiced (posted)', '78 940.00'), ('Open receivables', '12 380.50'), ('Overdue', '2 104.00')],
       charts=['Invoiced per month', 'Receivables by partner'], columns=['Month', 'Partner', 'Type', 'Untaxed', 'Total', 'Residual'],
       rows=[['2026-09', 'Azure Interior', 'Customer invoice', '2 700.00', '3 267.00', '0.00'],
             ['2026-10', 'Wood Corner', 'Customer invoice', '450.00', '544.50', '244.50']])
