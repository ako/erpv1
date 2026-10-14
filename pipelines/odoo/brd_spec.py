"""Target design for erpv1: the Odoo-inspired, Mendix-native domain and the eight BRDs (F001–F008).

This file is the single source of identifiers (the "facts" every BRD shares). brd_generator.py reads
it, resolves every `odoo` field reference against the knowledge base (type, required, selection
values) and fails on any reference that does not exist — so each attribute is traceable to Odoo or
is explicitly marked new. Decisions that simplify Odoo are listed per BRD in `simplifications` and
the contestable ones are raised as `openQuestions`.

Conventions (Mendix-native, recorded as deviations from brd-generation.md's template):
  * No hand-made audit attributes (CreatedOn/CreatedBy/...): every persistent entity enables the
    Mendix system members createdDate, changedDate, owner, changedBy.
  * `Active` only where Odoo archives records (`active` field).
  * Monetary amounts are Decimal; quantities Decimal; one company currency (see F001 open question).
  * Document numbers come from a Core.Sequence entity (Odoo ir.sequence / sequence.mixin prefixes).
"""

MODULES = ['Core', 'Partners', 'Products', 'Sales', 'Purchasing', 'Inventory', 'Invoicing']

# ── Enumerations: (MendixValue, odooValue|None, caption) ─────────────────────────────────────
ENUMS = {
    'Partners.ENUM_AddressType': dict(odoo='res.partner.type', values=[
        ('Contact', 'contact', 'Contact'), ('Invoice', 'invoice', 'Invoice address'),
        ('Delivery', 'delivery', 'Delivery address'), ('Other', 'other', 'Other address')]),
    'Products.ENUM_UoMType': dict(odoo='uom.uom.uom_type', values=[
        ('Reference', 'reference', 'Reference unit for this category'), ('Bigger', 'bigger', 'Bigger than the reference unit'),
        ('Smaller', 'smaller', 'Smaller than the reference unit')]),
    'Products.ENUM_ProductType': dict(odoo='product.template.type', values=[
        ('Goods', 'consu', 'Goods'), ('Service', 'service', 'Service')],
        note="Odoo 'combo' dropped (combo products out of scope)"),
    'Products.ENUM_InvoicePolicy': dict(odoo='product.template.invoice_policy', values=[
        ('OrderedQuantities', 'order', 'Ordered quantities'), ('DeliveredQuantities', 'delivery', 'Delivered quantities')]),
    'Products.ENUM_BillPolicy': dict(odoo='product.template.purchase_method', values=[
        ('OrderedQuantities', 'purchase', 'On ordered quantities'), ('ReceivedQuantities', 'receive', 'On received quantities')]),
    'Products.ENUM_PriceRuleScope': dict(odoo='product.pricelist.item.applied_on', values=[
        ('AllProducts', '3_global', 'All products'), ('ProductCategory', '2_product_category', 'Product category'),
        ('Product', '1_product', 'Product')], note="'0_product_variant' dropped with variants"),
    'Products.ENUM_PriceComputation': dict(odoo='product.pricelist.item.compute_price', values=[
        ('FixedPrice', 'fixed', 'Fixed price'), ('Discount', 'percentage', 'Discount (%)')],
        note="'formula' (margins, rounding, surcharge) dropped"),
    'Core.ENUM_LineType': dict(odoo='sale.order.line.display_type', values=[
        ('Product', None, 'Product line'), ('Section', 'line_section', 'Section'), ('Note', 'line_note', 'Note')],
        note="Odoo uses display_type=False for product lines; made explicit. Shared by sales, purchase and invoice lines"),
    'Sales.ENUM_SalesOrderStatus': dict(odoo='sale.order.state', values=[
        ('Quotation', 'draft', 'Quotation'), ('QuotationSent', 'sent', 'Quotation sent'),
        ('SalesOrder', 'sale', 'Sales order'), ('Cancelled', 'cancel', 'Cancelled')]),
    'Core.ENUM_InvoiceStatus': dict(odoo='sale.order.invoice_status', values=[
        ('NothingToInvoice', 'no', 'Nothing to invoice'), ('ToInvoice', 'to invoice', 'To invoice'),
        ('FullyInvoiced', 'invoiced', 'Fully invoiced')],
        note="sale 'upselling' dropped; shared by sales and purchase orders (purchase.order.invoice_status has the same 3 values)"),
    'Sales.ENUM_DeliveryStatus': dict(odoo='sale.order.delivery_status', values=[
        ('NotDelivered', 'pending', 'Not delivered'), ('Started', 'started', 'Started'),
        ('PartiallyDelivered', 'partial', 'Partially delivered'), ('FullyDelivered', 'full', 'Fully delivered')]),
    'Purchasing.ENUM_PurchaseOrderStatus': dict(odoo='purchase.order.state', values=[
        ('RFQ', 'draft', 'Request for quotation'), ('RFQSent', 'sent', 'RFQ sent'), ('ToApprove', 'to approve', 'To approve'),
        ('PurchaseOrder', 'purchase', 'Purchase order'), ('Cancelled', 'cancel', 'Cancelled')],
        note="'done' (locked) replaced by the Locked boolean, as Odoo 18 itself does for sales orders"),
    'Purchasing.ENUM_ReceiptStatus': dict(odoo='purchase.order.receipt_status', values=[
        ('NotReceived', 'pending', 'Not received'), ('PartiallyReceived', 'partial', 'Partially received'),
        ('FullyReceived', 'full', 'Fully received')]),
    'Inventory.ENUM_LocationType': dict(odoo='stock.location.usage', values=[
        ('Vendor', 'supplier', 'Vendor location'), ('View', 'view', 'View'), ('Internal', 'internal', 'Internal location'),
        ('Customer', 'customer', 'Customer location'), ('InventoryLoss', 'inventory', 'Inventory loss / adjustment')],
        note="'production' (MRP) and 'transit' (inter-warehouse) dropped"),
    'Inventory.ENUM_OperationKind': dict(odoo='stock.picking.type.code', values=[
        ('Receipt', 'incoming', 'Receipt'), ('Delivery', 'outgoing', 'Delivery'), ('Internal', 'internal', 'Internal transfer')]),
    'Inventory.ENUM_TransferStatus': dict(odoo='stock.picking.state', values=[
        ('Draft', 'draft', 'Draft'), ('Waiting', 'confirmed', 'Waiting'), ('Ready', 'assigned', 'Ready'),
        ('Done', 'done', 'Done'), ('Cancelled', 'cancel', 'Cancelled')],
        note="'waiting' (waiting another operation) dropped: no chained multi-step routes. Also used for stock moves"),
    'Invoicing.ENUM_InvoiceType': dict(odoo='account.move.move_type', values=[
        ('CustomerInvoice', 'out_invoice', 'Customer invoice'), ('CustomerCreditNote', 'out_refund', 'Customer credit note'),
        ('VendorBill', 'in_invoice', 'Vendor bill'), ('VendorCreditNote', 'in_refund', 'Vendor credit note')],
        note="'entry' (journal entries) and receipts dropped: no general ledger in scope"),
    'Invoicing.ENUM_InvoiceStatus': dict(odoo='account.move.state', values=[
        ('Draft', 'draft', 'Draft'), ('Posted', 'posted', 'Posted'), ('Cancelled', 'cancel', 'Cancelled')]),
    'Invoicing.ENUM_PaymentStatus': dict(odoo='account.move.payment_state', values=[
        ('NotPaid', 'not_paid', 'Not paid'), ('PartiallyPaid', 'partial', 'Partially paid'), ('Paid', 'paid', 'Paid'),
        ('Reversed', 'reversed', 'Reversed')], note="'in_payment' (bank reconciliation pending), 'blocked', 'invoicing_legacy' dropped"),
    'Invoicing.ENUM_PaymentDirection': dict(odoo='account.payment.payment_type', values=[
        ('Inbound', 'inbound', 'Receive money'), ('Outbound', 'outbound', 'Send money')]),
    'Invoicing.ENUM_PartnerKind': dict(odoo='account.payment.partner_type', values=[
        ('Customer', 'customer', 'Customer'), ('Vendor', 'supplier', 'Vendor')]),
    'Invoicing.ENUM_PaymentState': dict(odoo='account.payment.state', values=[
        ('Draft', 'draft', 'Draft'), ('Paid', 'paid', 'Paid'), ('Cancelled', 'canceled', 'Cancelled')],
        note="'in_process' and 'rejected' are bank-reconciliation states; dropped"),
    'Invoicing.ENUM_PaymentMethod': dict(odoo=None, values=[
        ('BankTransfer', None, 'Bank transfer'), ('Cash', None, 'Cash')],
        note="new: replaces account.journal (bank/cash journals) + account.payment.method.line"),
    'Invoicing.ENUM_TaxScope': dict(odoo='account.tax.type_tax_use', values=[
        ('Sales', 'sale', 'Sales'), ('Purchases', 'purchase', 'Purchases')], note="'none' (tax groups children) dropped"),
    'Invoicing.ENUM_TaxComputation': dict(odoo='account.tax.amount_type', values=[
        ('Percentage', 'percent', 'Percentage of price'), ('Fixed', 'fixed', 'Fixed amount per unit')],
        note="'group' and 'division' dropped"),
    'Invoicing.ENUM_PaymentTermValue': dict(odoo='account.payment.term.line.value', values=[
        ('Percent', 'percent', 'Percent'), ('Fixed', 'fixed', 'Fixed amount')]),
    'Invoicing.ENUM_PaymentTermDelay': dict(odoo='account.payment.term.line.delay_type', values=[
        ('DaysAfterInvoiceDate', 'days_after', 'Days after invoice date'),
        ('DaysAfterEndOfMonth', 'days_after_end_of_month', 'Days after end of month')],
        note="two rarer delay types dropped"),
}

# ── Entities ─────────────────────────────────────────────────────────────────────────────────
# attrs: (Name, odooField | None, overrides). overrides keys: type, length, mandatory, enum, calculated, note, default
# assocs: (Name, Target, 'Reference'|'ReferenceSet', odooField|None, note)
E = []


def entity(name, odoo, purpose, attrs, assocs=(), persistent=True, active=False, brd=None, generalization=None, note=None):
    E.append(dict(name=name, odoo=odoo, purpose=purpose, attrs=list(attrs), assocs=list(assocs), persistent=persistent,
                  active=active, brd=brd, generalization=generalization, note=note))


# F001 — Core + Partners (C1)
entity('Core.Company', 'res.company', 'The single company operating the app: identity, currency and document defaults.', [
    ('Name', 'name', {}), ('Email', 'email', {}), ('Phone', 'phone', {}), ('Street', 'street', {}), ('Street2', 'street2', {}),
    ('Zip', 'zip', {}), ('City', 'city', {}), ('VATNumber', 'vat', {}), ('Website', 'website', {}),
    ('QuotationValidityDays', 'quotation_validity_days', {'default': '30'}),
    ('POApprovalEnabled', 'po_double_validation', {'type': 'Boolean', 'note': 'Odoo selection one_step/two_step -> boolean'}),
    ('POApprovalThreshold', 'po_double_validation_amount', {}),
    ('PurchaseLeadDays', 'po_lead', {}),
    ('InvoiceTerms', 'invoice_terms', {}),
], [
    ('Company_Country', 'Core.Country', 'Reference', 'country_id', None),
    ('Company_Currency', 'Core.Currency', 'Reference', 'currency_id', None),
    ('Company_DefaultSalesTax', 'Invoicing.Tax', 'Reference', 'account_sale_tax_id', None),
    ('Company_DefaultPurchaseTax', 'Invoicing.Tax', 'Reference', 'account_purchase_tax_id', None),
], brd='F001', note='Singleton (multi-company out of scope). Odoo keeps the address on a linked res.partner; flattened here.')
entity('Core.Country', 'res.country', 'Countries for addresses.', [
    ('Name', 'name', {}), ('Code', 'code', {})], brd='F001')
entity('Core.Currency', 'res.currency', 'Currency of the company and its documents.', [
    ('Name', 'name', {'note': 'ISO code, e.g. EUR'}), ('Symbol', 'symbol', {}), ('Rounding', 'rounding', {}),
    ('DecimalPlaces', 'decimal_places', {}), ('SymbolPosition', 'position', {'type': 'String', 'length': 10, 'note': 'before/after'})],
    active=True, brd='F001')
entity('Core.Sequence', 'ir.sequence', 'Document numbering per document type (S00001, P00001, WH/IN/00001, INV/2026/00001, ...).', [
    ('Code', None, {'type': 'String', 'length': 50, 'mandatory': True, 'note': 'ir.sequence.code, e.g. sale.order'}),
    ('Prefix', None, {'type': 'String', 'length': 30, 'note': 'ir.sequence.prefix; %(year)s supported'}),
    ('Padding', None, {'type': 'Integer', 'default': '5'}),
    ('NextNumber', None, {'type': 'Integer', 'default': '1'})], brd='F001',
    note='ir.sequence is a framework model (C12); kept as a tiny Mendix entity because every document needs a readable number.')
entity('Core.LineAmounts', None, 'Result of a line amount computation (subtotal, tax, total) passed between microflows.', [
    ('Subtotal', None, {'type': 'Decimal'}), ('TaxAmount', None, {'type': 'Decimal'}), ('Total', None, {'type': 'Decimal'})],
    persistent=False, brd='F008', note='new: helper for SUB_Tax_ComputeLine')
entity('Core.UserProfile', 'res.users', 'Business data of an app user (Mendix account): display name and linked partner. Team membership lives on Sales.SalesTeam.', [
    ('DisplayName', None, {'type': 'String', 'length': 200, 'note': 'shown on documents; Odoo takes it from the linked partner'}),
], [
    ('UserProfile_Account', 'Administration.Account', 'Reference', None, 'Mendix account (System.User) — replaces res.users login/groups'),
    ('UserProfile_Partner', 'Partners.Partner', 'Reference', 'partner_id', 'res.users _inherits res.partner -> association, not generalization'),
], brd='F001', note='Odoo res.users delegates to res.partner (_inherits). Mendix: Administration.Account for login/roles + this profile.')
entity('Partners.Partner', 'res.partner', 'Any customer, vendor or contact person — companies and their contacts/addresses.', [
    ('Name', 'name', {}), ('IsCompany', 'is_company', {}), ('AddressType', 'type', {'enum': 'Partners.ENUM_AddressType'}),
    ('Email', 'email', {}), ('Phone', 'phone', {}), ('Mobile', 'mobile', {}), ('JobPosition', 'function', {}),
    ('Street', 'street', {}), ('Street2', 'street2', {}), ('Zip', 'zip', {}), ('City', 'city', {}),
    ('VATNumber', 'vat', {}), ('Website', 'website', {}), ('Reference', 'ref', {}), ('Notes', 'comment', {}),
    ('IsCustomer', 'customer_rank', {'type': 'Boolean', 'note': 'Odoo integer rank (>0 = customer) -> explicit flag'}),
    ('IsVendor', 'supplier_rank', {'type': 'Boolean', 'note': 'Odoo integer rank (>0 = vendor) -> explicit flag'}),
], [
    ('Partner_ParentCompany', 'Partners.Partner', 'Reference', 'parent_id', 'contacts and addresses belong to a company'),
    ('Partner_Country', 'Core.Country', 'Reference', 'country_id', None),
    ('Partner_Tags', 'Partners.PartnerTag', 'ReferenceSet', 'category_id', None),
    ('Partner_Salesperson', 'Administration.Account', 'Reference', 'user_id', None),
    ('Partner_CustomerPaymentTerm', 'Invoicing.PaymentTerm', 'Reference', 'property_payment_term_id', 'company-dependent in Odoo; single company here'),
    ('Partner_VendorPaymentTerm', 'Invoicing.PaymentTerm', 'Reference', 'property_supplier_payment_term_id', None),
    ('Partner_Pricelist', 'Products.Pricelist', 'Reference', 'property_product_pricelist', None),
], active=True, brd='F001')
entity('Partners.PartnerTag', 'res.partner.category', 'Free tags to classify partners.', [
    ('Name', 'name', {}), ('Color', 'color', {})], active=True, brd='F001')
entity('Partners.BankAccount', 'res.partner.bank', 'Bank account of a partner (shown on vendor bills / customer payments).', [
    ('AccountNumber', 'acc_number', {}), ('HolderName', 'acc_holder_name', {}),
    ('BankName', 'bank_name', {'type': 'String', 'length': 200, 'note': 'flattened from res.bank'}),
    ('BIC', 'bank_bic', {'type': 'String', 'length': 20, 'note': 'flattened from res.bank'})], [
    ('BankAccount_Partner', 'Partners.Partner', 'Reference', 'partner_id', None)], active=True, brd='F001')

# F002 — Units of measure (C2)
entity('Products.UoMCategory', 'uom.category', 'Groups units that convert into each other (Unit, Weight, Volume, Time...).', [
    ('Name', 'name', {})], brd='F002')
entity('Products.UoM', 'uom.uom', 'A unit of measure and its conversion factor to the category reference unit.', [
    ('Name', 'name', {}), ('UoMType', 'uom_type', {'enum': 'Products.ENUM_UoMType'}),
    ('Factor', 'factor', {'note': 'reference units per this unit, Odoo semantics'}), ('Rounding', 'rounding', {})], [
    ('UoM_Category', 'Products.UoMCategory', 'Reference', 'category_id', None)], active=True, brd='F002')

# F003 — Products & pricing (C3)
entity('Products.ProductCategory', 'product.category', 'Hierarchical product grouping (used by price rules and reporting).', [
    ('Name', 'name', {}), ('FullName', 'complete_name', {'note': 'stored path "All / Saleable"'})], [
    ('ProductCategory_Parent', 'Products.ProductCategory', 'Reference', 'parent_id', None)], brd='F003')
entity('Products.Product', 'product.template', 'A sellable and/or purchasable product or service (variants merged in).', [
    ('Name', 'name', {}), ('InternalReference', 'default_code', {}), ('Barcode', 'barcode', {'type': 'String', 'length': 50}),
    ('ProductType', 'type', {'enum': 'Products.ENUM_ProductType'}), ('TrackInventory', 'is_storable', {}),
    ('SalesPrice', 'list_price', {}), ('Cost', 'standard_price', {'type': 'Decimal', 'note': 'company-dependent on product.product in Odoo'}),
    ('CanBeSold', 'sale_ok', {}), ('CanBePurchased', 'purchase_ok', {}),
    ('InvoicePolicy', 'invoice_policy', {'enum': 'Products.ENUM_InvoicePolicy'}),
    ('BillPolicy', 'purchase_method', {'enum': 'Products.ENUM_BillPolicy'}),
    ('SalesDescription', 'description_sale', {}), ('PurchaseDescription', 'description_purchase', {}),
    ('InternalNotes', 'description', {'type': 'String', 'length': 'unlimited'}),
    ('Weight', 'weight', {}), ('Volume', 'volume', {}), ('CustomerLeadDays', 'sale_delay', {}),
], [
    ('Product_Category', 'Products.ProductCategory', 'Reference', 'categ_id', None),
    ('Product_UoM', 'Products.UoM', 'Reference', 'uom_id', 'sales and stock unit'),
    ('Product_PurchaseUoM', 'Products.UoM', 'Reference', 'uom_po_id', None),
    ('Product_CustomerTaxes', 'Invoicing.Tax', 'ReferenceSet', 'taxes_id', None),
    ('Product_VendorTaxes', 'Invoicing.Tax', 'ReferenceSet', 'supplier_taxes_id', None),
    ('Product_Tags', 'Products.ProductTag', 'ReferenceSet', 'product_tag_ids', None),
], active=True, brd='F003',
    note='product.template and product.product merged: variants out of scope. Image via a ProductImage specialization of System.Image.')
entity('Products.ProductImage', None, 'Product picture.', [], [
    ('ProductImage_Product', 'Products.Product', 'Reference', None, 'Odoo image.mixin image_1920')], brd='F003',
    generalization='System.Image', note='new: Mendix-native file storage for image.mixin')
entity('Products.ProductTag', 'product.tag', 'Free tags on products.', [('Name', 'name', {}), ('Color', 'color', {})], brd='F003')
entity('Products.VendorPrice', 'product.supplierinfo', "A vendor's price and lead time for a product (drives RFQ prices).", [
    ('MinQuantity', 'min_qty', {}), ('Price', 'price', {}), ('Discount', 'discount', {}), ('LeadTimeDays', 'delay', {}),
    ('VendorProductCode', 'product_code', {}), ('VendorProductName', 'product_name', {}),
    ('ValidFrom', 'date_start', {}), ('ValidTo', 'date_end', {}), ('Sequence', 'sequence', {})], [
    ('VendorPrice_Vendor', 'Partners.Partner', 'Reference', 'partner_id', None),
    ('VendorPrice_Product', 'Products.Product', 'Reference', 'product_tmpl_id', None)], brd='F003')
entity('Products.Pricelist', 'product.pricelist', 'A named set of price rules assigned to customers.', [
    ('Name', 'name', {}), ('Sequence', 'sequence', {})], [
    ('Pricelist_Currency', 'Core.Currency', 'Reference', 'currency_id', None)], active=True, brd='F003')
entity('Products.PriceRule', 'product.pricelist.item', 'One pricelist rule: fixed price or % discount, for all/category/product, from a minimum quantity.', [
    ('AppliesTo', 'applied_on', {'enum': 'Products.ENUM_PriceRuleScope'}), ('Computation', 'compute_price', {'enum': 'Products.ENUM_PriceComputation'}),
    ('FixedPrice', 'fixed_price', {}), ('DiscountPercent', 'percent_price', {}), ('MinQuantity', 'min_quantity', {}),
    ('ValidFrom', 'date_start', {}), ('ValidTo', 'date_end', {})], [
    ('PriceRule_Pricelist', 'Products.Pricelist', 'Reference', 'pricelist_id', None),
    ('PriceRule_Product', 'Products.Product', 'Reference', 'product_tmpl_id', None),
    ('PriceRule_Category', 'Products.ProductCategory', 'Reference', 'categ_id', None)], brd='F003')

# F004 — Sales (C4)
entity('Sales.SalesTeam', 'crm.team', 'Sales team with a leader and members (reporting, default on orders).', [
    ('Name', 'name', {}), ('InvoicingTarget', 'invoiced_target', {})], [
    ('SalesTeam_Leader', 'Administration.Account', 'Reference', 'user_id', None),
    ('SalesTeam_Members', 'Administration.Account', 'ReferenceSet', 'member_ids', 'crm.team.member flattened to a reference set')],
    active=True, brd='F004')
entity('Sales.SalesOrder', 'sale.order', 'A quotation that becomes a confirmed sales order.', [
    ('Number', 'name', {'note': 'Core.Sequence code sale.order, prefix S'}), ('Status', 'state', {'enum': 'Sales.ENUM_SalesOrderStatus'}),
    ('Locked', 'locked', {}), ('OrderDate', 'date_order', {}), ('ExpirationDate', 'validity_date', {}),
    ('DeliveryDate', 'commitment_date', {}), ('CustomerReference', 'client_order_ref', {}), ('Source', 'origin', {}),
    ('TermsAndConditions', 'note', {}),
    ('AmountUntaxed', 'amount_untaxed', {'note': 'stored, recomputed by SUB_SalesOrder_RecomputeTotals'}),
    ('AmountTax', 'amount_tax', {}), ('AmountTotal', 'amount_total', {}),
    ('InvoiceStatus', 'invoice_status', {'enum': 'Core.ENUM_InvoiceStatus'}),
    ('DeliveryStatus', 'delivery_status', {'enum': 'Sales.ENUM_DeliveryStatus'}),
], [
    ('SalesOrder_Customer', 'Partners.Partner', 'Reference', 'partner_id', None),
    ('SalesOrder_InvoiceAddress', 'Partners.Partner', 'Reference', 'partner_invoice_id', None),
    ('SalesOrder_DeliveryAddress', 'Partners.Partner', 'Reference', 'partner_shipping_id', None),
    ('SalesOrder_Salesperson', 'Administration.Account', 'Reference', 'user_id', None),
    ('SalesOrder_SalesTeam', 'Sales.SalesTeam', 'Reference', 'team_id', None),
    ('SalesOrder_Pricelist', 'Products.Pricelist', 'Reference', 'pricelist_id', None),
    ('SalesOrder_PaymentTerm', 'Invoicing.PaymentTerm', 'Reference', 'payment_term_id', None),
    ('SalesOrder_Currency', 'Core.Currency', 'Reference', 'currency_id', None),
    ('SalesOrder_QuotationTemplate', 'Sales.QuotationTemplate', 'Reference', 'sale_order_template_id', None),
], brd='F004')
entity('Sales.SalesOrderLine', 'sale.order.line', 'A product, section or note line of a sales order.', [
    ('Sequence', 'sequence', {}), ('LineType', 'display_type', {'enum': 'Core.ENUM_LineType'}), ('Description', 'name', {}),
    ('Quantity', 'product_uom_qty', {}), ('UnitPrice', 'price_unit', {}), ('DiscountPercent', 'discount', {}),
    ('Subtotal', 'price_subtotal', {}), ('TaxAmount', 'price_tax', {}), ('Total', 'price_total', {}),
    ('QuantityDelivered', 'qty_delivered', {}), ('QuantityInvoiced', 'qty_invoiced', {}),
    ('QuantityToInvoice', 'qty_to_invoice', {}), ('LeadTimeDays', 'customer_lead', {})], [
    ('SalesOrderLine_SalesOrder', 'Sales.SalesOrder', 'Reference', 'order_id', 'delete lines with the order'),
    ('SalesOrderLine_Product', 'Products.Product', 'Reference', 'product_id', None),
    ('SalesOrderLine_UoM', 'Products.UoM', 'Reference', 'product_uom', None),
    ('SalesOrderLine_Taxes', 'Invoicing.Tax', 'ReferenceSet', 'tax_id', None)], brd='F004')
entity('Sales.QuotationTemplate', 'sale.order.template', 'Reusable quotation: default lines, validity and terms.', [
    ('Name', 'name', {}), ('ValidityDays', 'number_of_days', {}), ('TermsAndConditions', 'note', {})], active=True, brd='F004')
entity('Sales.QuotationTemplateLine', 'sale.order.template.line', 'A default line of a quotation template.', [
    ('Sequence', 'sequence', {}), ('LineType', 'display_type', {'enum': 'Core.ENUM_LineType'}), ('Description', 'name', {}),
    ('Quantity', 'product_uom_qty', {})], [
    ('QuotationTemplateLine_Template', 'Sales.QuotationTemplate', 'Reference', 'sale_order_template_id', None),
    ('QuotationTemplateLine_Product', 'Products.Product', 'Reference', 'product_id', None),
    ('QuotationTemplateLine_UoM', 'Products.UoM', 'Reference', 'product_uom_id', None)], brd='F004')
entity('Sales.CreateInvoiceRequest', 'sale.advance.payment.inv', 'Wizard data: create the invoice(s) for selected sales orders.', [
    ('ConsolidatePerCustomer', None, {'type': 'Boolean', 'note': 'new: Odoo groups by partner/currency automatically'})], [
    ('CreateInvoiceRequest_SalesOrders', 'Sales.SalesOrder', 'ReferenceSet', 'sale_order_ids', None)],
    persistent=False, brd='F008', note='Regular invoices only; down payments (advance_payment_method=percentage/fixed) dropped.')

# F005 — Purchasing (C5)
entity('Purchasing.PurchaseOrder', 'purchase.order', 'A request for quotation that becomes a (possibly approved) purchase order.', [
    ('Number', 'name', {'note': 'Core.Sequence code purchase.order, prefix P'}),
    ('Status', 'state', {'enum': 'Purchasing.ENUM_PurchaseOrderStatus'}), ('Locked', None, {'type': 'Boolean', 'note': "replaces Odoo state 'done'"}),
    ('OrderDeadline', 'date_order', {}), ('ConfirmationDate', 'date_approve', {}), ('ExpectedArrival', 'date_planned', {}),
    ('VendorReference', 'partner_ref', {}), ('Source', 'origin', {}), ('Notes', 'notes', {}),
    ('AmountUntaxed', 'amount_untaxed', {}), ('AmountTax', 'amount_tax', {}), ('AmountTotal', 'amount_total', {}),
    ('BillingStatus', 'invoice_status', {'enum': 'Core.ENUM_InvoiceStatus'}),
    ('ReceiptStatus', 'receipt_status', {'enum': 'Purchasing.ENUM_ReceiptStatus'})], [
    ('PurchaseOrder_Vendor', 'Partners.Partner', 'Reference', 'partner_id', None),
    ('PurchaseOrder_Buyer', 'Administration.Account', 'Reference', 'user_id', None),
    ('PurchaseOrder_PaymentTerm', 'Invoicing.PaymentTerm', 'Reference', 'payment_term_id', None),
    ('PurchaseOrder_Currency', 'Core.Currency', 'Reference', 'currency_id', None),
    ('PurchaseOrder_DeliverTo', 'Inventory.OperationType', 'Reference', 'picking_type_id', 'receipt operation of the warehouse'),
    ('PurchaseOrder_ReorderRule', 'Inventory.ReorderRule', 'Reference', None, 'new: which replenishment rule created this RFQ')],
    brd='F005')
entity('Purchasing.PurchaseOrderLine', 'purchase.order.line', 'A product, section or note line of a purchase order.', [
    ('Sequence', 'sequence', {}), ('LineType', 'display_type', {'enum': 'Core.ENUM_LineType'}), ('Description', 'name', {}),
    ('Quantity', 'product_qty', {}), ('UnitPrice', 'price_unit', {}), ('DiscountPercent', 'discount', {}),
    ('ExpectedArrival', 'date_planned', {}), ('Subtotal', 'price_subtotal', {}), ('TaxAmount', 'price_tax', {}), ('Total', 'price_total', {}),
    ('QuantityReceived', 'qty_received', {}), ('QuantityBilled', 'qty_invoiced', {}), ('QuantityToBill', 'qty_to_invoice', {})], [
    ('PurchaseOrderLine_PurchaseOrder', 'Purchasing.PurchaseOrder', 'Reference', 'order_id', 'delete lines with the order'),
    ('PurchaseOrderLine_Product', 'Products.Product', 'Reference', 'product_id', None),
    ('PurchaseOrderLine_UoM', 'Products.UoM', 'Reference', 'product_uom', None),
    ('PurchaseOrderLine_Taxes', 'Invoicing.Tax', 'ReferenceSet', 'taxes_id', None)], brd='F005')

# F006 — Inventory (C6)
entity('Inventory.Warehouse', 'stock.warehouse', 'The (single) warehouse: its stock location and operation types.', [
    ('Name', 'name', {}), ('ShortName', 'code', {})], [
    ('Warehouse_StockLocation', 'Inventory.Location', 'Reference', 'lot_stock_id', None),
    ('Warehouse_Address', 'Partners.Partner', 'Reference', 'partner_id', None)], active=True, brd='F006',
    note='reception_steps / delivery_steps fixed to one step; no routes/rules.')
entity('Inventory.Location', 'stock.location', 'A physical or virtual place stock moves from/to (WH/Stock, Vendors, Customers, Inventory adjustment).', [
    ('Name', 'name', {}), ('FullName', 'complete_name', {}), ('LocationType', 'usage', {'enum': 'Inventory.ENUM_LocationType'}),
    ('Barcode', 'barcode', {})], [
    ('Location_Parent', 'Inventory.Location', 'Reference', 'location_id', None),
    ('Location_Warehouse', 'Inventory.Warehouse', 'Reference', 'warehouse_id', None)], active=True, brd='F006')
entity('Inventory.OperationType', 'stock.picking.type', 'Receipts, Delivery orders, Internal transfers: numbering and default locations.', [
    ('Name', 'name', {}), ('Kind', 'code', {'enum': 'Inventory.ENUM_OperationKind'}), ('SequenceCode', 'sequence_code', {}),
    ('CreateBackorder', 'create_backorder', {'type': 'Boolean', 'note': "Odoo ask/always/never -> 'always ask' dropped: true=create"})], [
    ('OperationType_Warehouse', 'Inventory.Warehouse', 'Reference', 'warehouse_id', None),
    ('OperationType_DefaultSource', 'Inventory.Location', 'Reference', 'default_location_src_id', None),
    ('OperationType_DefaultDestination', 'Inventory.Location', 'Reference', 'default_location_dest_id', None)], active=True, brd='F006')
entity('Inventory.Transfer', 'stock.picking', 'A receipt, delivery or internal transfer grouping stock moves.', [
    ('Number', 'name', {'note': 'WH/IN/00001, WH/OUT/00001, WH/INT/00001'}), ('Status', 'state', {'enum': 'Inventory.ENUM_TransferStatus'}),
    ('ScheduledDate', 'scheduled_date', {}), ('DateDone', 'date_done', {}), ('Deadline', 'date_deadline', {}),
    ('SourceDocument', 'origin', {}), ('Notes', 'note', {})], [
    ('Transfer_OperationType', 'Inventory.OperationType', 'Reference', 'picking_type_id', None),
    ('Transfer_Partner', 'Partners.Partner', 'Reference', 'partner_id', None),
    ('Transfer_SourceLocation', 'Inventory.Location', 'Reference', 'location_id', None),
    ('Transfer_DestinationLocation', 'Inventory.Location', 'Reference', 'location_dest_id', None),
    ('Transfer_Backorder', 'Inventory.Transfer', 'Reference', 'backorder_id', 'the transfer this one is the backorder of'),
    ('Transfer_SalesOrder', 'Sales.SalesOrder', 'Reference', 'sale_id', 'sale_stock'),
    ('Transfer_PurchaseOrder', 'Purchasing.PurchaseOrder', 'Reference', 'purchase_id', 'purchase_stock (computed in Odoo via moves; stored here)'),
    ('Transfer_Responsible', 'Administration.Account', 'Reference', 'user_id', None)], brd='F006')
entity('Inventory.StockMove', 'stock.move', 'Movement of one product quantity between two locations (stock.move.line merged in).', [
    ('Description', 'name', {}), ('Status', 'state', {'enum': 'Inventory.ENUM_TransferStatus'}),
    ('Date', 'date', {}), ('DemandQuantity', 'product_uom_qty', {}), ('Quantity', 'quantity', {'note': 'quantity actually moved'}),
    ('Picked', 'picked', {}), ('SourceDocument', 'origin', {}), ('IsInventoryAdjustment', 'is_inventory', {})], [
    ('StockMove_Transfer', 'Inventory.Transfer', 'Reference', 'picking_id', None),
    ('StockMove_Product', 'Products.Product', 'Reference', 'product_id', None),
    ('StockMove_UoM', 'Products.UoM', 'Reference', 'product_uom', None),
    ('StockMove_SourceLocation', 'Inventory.Location', 'Reference', 'location_id', None),
    ('StockMove_DestinationLocation', 'Inventory.Location', 'Reference', 'location_dest_id', None),
    ('StockMove_SalesOrderLine', 'Sales.SalesOrderLine', 'Reference', 'sale_line_id', None),
    ('StockMove_PurchaseOrderLine', 'Purchasing.PurchaseOrderLine', 'Reference', 'purchase_line_id', None)], brd='F006')
entity('Inventory.StockLevel', 'stock.quant', 'Quantity of a product in an internal location (on hand, reserved, counted).', [
    ('Quantity', 'quantity', {}), ('ReservedQuantity', 'reserved_quantity', {}), ('CountedQuantity', 'inventory_quantity', {}),
    ('CountSet', 'inventory_quantity_set', {}), ('ScheduledCountDate', 'inventory_date', {}), ('IncomingDate', 'in_date', {})], [
    ('StockLevel_Product', 'Products.Product', 'Reference', 'product_id', None),
    ('StockLevel_Location', 'Inventory.Location', 'Reference', 'location_id', None)], brd='F006',
    note='No lots, packages or owners: one row per product × location.')
entity('Inventory.ReorderRule', 'stock.warehouse.orderpoint', 'Min/max replenishment rule: below minimum, create an RFQ up to maximum.', [
    ('Name', 'name', {}), ('MinQuantity', 'product_min_qty', {}), ('MaxQuantity', 'product_max_qty', {}),
    ('QuantityMultiple', 'qty_multiple', {}), ('Automatic', 'trigger', {'type': 'Boolean', 'note': "Odoo trigger auto/manual -> boolean"})], [
    ('ReorderRule_Product', 'Products.Product', 'Reference', 'product_id', None),
    ('ReorderRule_Location', 'Inventory.Location', 'Reference', 'location_id', None),
    ('ReorderRule_Vendor', 'Partners.Partner', 'Reference', 'vendor_id', None)], active=True, brd='F006')
entity('Inventory.ValidateTransferRequest', 'stock.backorder.confirmation', 'Wizard data: validate a transfer with less than the demand — create a backorder or not.', [
    ('CreateBackorder', None, {'type': 'Boolean', 'default': 'true', 'note': 'Odoo: two buttons process / process_cancel_backorder'})], [
    ('ValidateTransferRequest_Transfer', 'Inventory.Transfer', 'Reference', 'pick_ids', None)], persistent=False, brd='F006')

# F008 — Invoicing (C8)
entity('Invoicing.Invoice', 'account.move', 'Customer invoice / credit note or vendor bill / credit note (no journal entries).', [
    ('Number', 'name', {'note': 'INV/2026/00001, RINV/..., BILL/..., RBILL/... via Core.Sequence; empty while draft'}),
    ('InvoiceType', 'move_type', {'enum': 'Invoicing.ENUM_InvoiceType'}), ('Status', 'state', {'enum': 'Invoicing.ENUM_InvoiceStatus'}),
    ('PaymentStatus', 'payment_state', {'enum': 'Invoicing.ENUM_PaymentStatus'}),
    ('InvoiceDate', 'invoice_date', {}), ('DueDate', 'invoice_date_due', {}), ('Reference', 'ref', {'note': 'vendor bill reference'}),
    ('PaymentReference', 'payment_reference', {}), ('SourceDocument', 'invoice_origin', {}), ('Notes', 'narration', {}),
    ('AmountUntaxed', 'amount_untaxed', {}), ('AmountTax', 'amount_tax', {}), ('AmountTotal', 'amount_total', {}),
    ('AmountDue', 'amount_residual', {})], [
    ('Invoice_Partner', 'Partners.Partner', 'Reference', 'partner_id', None),
    ('Invoice_DeliveryAddress', 'Partners.Partner', 'Reference', 'partner_shipping_id', None),
    ('Invoice_Salesperson', 'Administration.Account', 'Reference', 'invoice_user_id', None),
    ('Invoice_PaymentTerm', 'Invoicing.PaymentTerm', 'Reference', 'invoice_payment_term_id', None),
    ('Invoice_Currency', 'Core.Currency', 'Reference', 'currency_id', None),
    ('Invoice_ReversalOf', 'Invoicing.Invoice', 'Reference', 'reversed_entry_id', 'credit note -> original invoice'),
    ('Invoice_BankAccount', 'Partners.BankAccount', 'Reference', 'partner_bank_id', 'where the money goes'),
    ('Invoice_SalesOrders', 'Sales.SalesOrder', 'ReferenceSet', None, 'new: Odoo links through invoice lines (sale_line_ids); kept at header for navigation'),
    ('Invoice_PurchaseOrder', 'Purchasing.PurchaseOrder', 'Reference', 'purchase_id', None)], brd='F008')
entity('Invoicing.InvoiceLine', 'account.move.line', 'A product, section or note line of an invoice (no tax/receivable/payable journal items).', [
    ('Sequence', 'sequence', {}), ('LineType', 'display_type', {'enum': 'Core.ENUM_LineType',
                                                              'note': "Odoo 'product'/'line_section'/'line_note'; tax/payment_term/rounding lines dropped"}),
    ('Description', 'name', {}), ('Quantity', 'quantity', {}), ('UnitPrice', 'price_unit', {}), ('DiscountPercent', 'discount', {}),
    ('Subtotal', 'price_subtotal', {}), ('Total', 'price_total', {})], [
    ('InvoiceLine_Invoice', 'Invoicing.Invoice', 'Reference', 'move_id', 'delete lines with the invoice'),
    ('InvoiceLine_Product', 'Products.Product', 'Reference', 'product_id', None),
    ('InvoiceLine_UoM', 'Products.UoM', 'Reference', 'product_uom_id', None),
    ('InvoiceLine_Taxes', 'Invoicing.Tax', 'ReferenceSet', 'tax_ids', None),
    ('InvoiceLine_SalesOrderLines', 'Sales.SalesOrderLine', 'ReferenceSet', 'sale_line_ids', None),
    ('InvoiceLine_PurchaseOrderLine', 'Purchasing.PurchaseOrderLine', 'Reference', 'purchase_line_id', None)], brd='F008')
entity('Invoicing.Tax', 'account.tax', 'A sales or purchase tax: percentage or fixed amount, price-included or not.', [
    ('Name', 'name', {}), ('Scope', 'type_tax_use', {'enum': 'Invoicing.ENUM_TaxScope'}),
    ('Computation', 'amount_type', {'enum': 'Invoicing.ENUM_TaxComputation'}), ('Amount', 'amount', {}),
    ('IncludedInPrice', 'price_include_override', {'type': 'Boolean', 'note': "Odoo tax_included/tax_excluded/company default -> boolean"}),
    ('LabelOnInvoice', 'invoice_label', {}), ('Sequence', 'sequence', {})], active=True, brd='F008',
    note='No tax groups, repartition lines, fiscal positions or cash basis.')
entity('Invoicing.PaymentTerm', 'account.payment.term', 'When an invoice must be paid: one or more instalments.', [
    ('Name', 'name', {}), ('Note', 'note', {}), ('Sequence', 'sequence', {})], active=True, brd='F008',
    note='Early-payment discounts dropped.')
entity('Invoicing.PaymentTermLine', 'account.payment.term.line', 'One instalment: percent or fixed amount, due N days after a reference date.', [
    ('Value', 'value', {'enum': 'Invoicing.ENUM_PaymentTermValue'}), ('ValueAmount', 'value_amount', {}),
    ('Days', 'nb_days', {}), ('DelayType', 'delay_type', {'enum': 'Invoicing.ENUM_PaymentTermDelay'})], [
    ('PaymentTermLine_PaymentTerm', 'Invoicing.PaymentTerm', 'Reference', 'payment_id', None)], brd='F008')
entity('Invoicing.Payment', 'account.payment', 'Money received from a customer or paid to a vendor, allocated to invoices.', [
    ('Number', 'name', {'note': 'PAY/2026/00001'}), ('Direction', 'payment_type', {'enum': 'Invoicing.ENUM_PaymentDirection'}),
    ('PartnerKind', 'partner_type', {'enum': 'Invoicing.ENUM_PartnerKind'}), ('Amount', 'amount', {}), ('PaymentDate', 'date', {}),
    ('Memo', 'memo', {}), ('Status', 'state', {'enum': 'Invoicing.ENUM_PaymentState'}),
    ('Method', None, {'enum': 'Invoicing.ENUM_PaymentMethod', 'note': 'replaces journal_id + payment_method_line_id'})], [
    ('Payment_Partner', 'Partners.Partner', 'Reference', 'partner_id', None),
    ('Payment_Currency', 'Core.Currency', 'Reference', 'currency_id', None),
    ('Payment_BankAccount', 'Partners.BankAccount', 'Reference', 'partner_bank_id', None),
    ('Payment_Invoices', 'Invoicing.Invoice', 'ReferenceSet', 'invoice_ids', 'replaces reconciliation (account.partial.reconcile)')], brd='F008')
entity('Invoicing.PaymentAllocation', None, 'Amount of a payment applied to one invoice (makes partial payments explicit).', [
    ('Amount', None, {'type': 'Decimal', 'mandatory': True})], [
    ('PaymentAllocation_Payment', 'Invoicing.Payment', 'Reference', None, None),
    ('PaymentAllocation_Invoice', 'Invoicing.Invoice', 'Reference', None, None)], brd='F008',
    note='new: Mendix-native replacement of account.partial.reconcile / matching numbers.')
entity('Invoicing.RegisterPaymentRequest', 'account.payment.register', 'Wizard data: register a payment for one or more posted invoices.', [
    ('Amount', 'amount', {}), ('PaymentDate', 'payment_date', {}), ('Memo', 'communication', {}),
    ('Method', None, {'enum': 'Invoicing.ENUM_PaymentMethod'})], [
    ('RegisterPaymentRequest_Invoices', 'Invoicing.Invoice', 'ReferenceSet', 'line_ids', 'Odoo selects journal items; here invoices')],
    persistent=False, brd='F008')
entity('Invoicing.CreditNoteRequest', 'account.move.reversal', 'Wizard data: reverse a posted invoice into a credit note.', [
    ('Reason', 'reason', {}), ('ReversalDate', 'date', {})], [
    ('CreditNoteRequest_Invoice', 'Invoicing.Invoice', 'Reference', 'move_ids', None)], persistent=False, brd='F008')

# View entities (OQL) — Mendix-native replacement of Odoo's SQL-view report models
VIEWS = [
    dict(name='Sales.SalesAnalysis', odoo='sale.report', brd='F004',
         purpose='Order lines joined to order, customer, product, salesperson: amounts and quantities for pivots/charts.'),
    dict(name='Purchasing.PurchaseAnalysis', odoo='purchase.report', brd='F005',
         purpose='Purchase lines with ordered/received/billed quantities and amounts per vendor/product.'),
    dict(name='Inventory.StockOnHand', odoo='report.stock.quantity', brd='F006',
         purpose='Per product: on hand, reserved, incoming and outgoing quantities (forecast).'),
    dict(name='Invoicing.InvoiceAnalysis', odoo='account.invoice.report', brd='F008',
         purpose='Posted invoice lines with untaxed/total amounts and residual per partner/product/period.'),
]

# ── In-scope Odoo models (C1–C8) NOT mapped to an entity, with the reason ─────────────────────
DROPPED = {
    'res.bank': 'flattened into Partners.BankAccount (BankName, BIC)',
    'res.country.group': 'only used for pricelist/fiscal-position country filters — both dropped',
    'res.country.state': 'states not needed for the POC address (Street/Zip/City/Country)',
    'res.currency.rate': 'single currency (F001 open question Q-F001-1)',
    'res.partner.title': 'salutations (Mr/Ms) — cosmetic',
    'res.partner.industry': 'not used by any in-scope flow',
    'res.users.log': 'login log — Mendix platform (System.Session / audit)',
    'res.users.apikeys': 'API keys — Mendix platform security',
    'res.users.deletion': 'GDPR self-deletion requests — framework',
    'res.users.settings': 'per-user UI preferences — framework',
    'product.product': 'merged into Products.Product (no variants)',
    'product.attribute': 'variants/configurator out of scope (Q-F003-1)',
    'product.attribute.value': 'variants out of scope (Q-F003-1)',
    'product.attribute.custom.value': 'variants out of scope (Q-F003-1)',
    'product.template.attribute.line': 'variants out of scope (Q-F003-1)',
    'product.template.attribute.value': 'variants out of scope (Q-F003-1)',
    'product.template.attribute.exclusion': 'variants out of scope (Q-F003-1)',
    'product.combo': 'combo products out of scope',
    'product.combo.item': 'combo products out of scope',
    'product.document': 'product attachments — ir.attachment based; not needed for the demo',
    'product.packaging': 'packagings out of scope (no packages)',
    'crm.tag': 'CRM tags on orders — not used without the CRM app',
    'crm.team.member': 'flattened into SalesTeam_Members reference set',
    'sale.order.option': 'optional products on quotes — dropped (portal upsell feature)',
    'sale.order.template.option': 'optional products on templates — dropped with sale.order.option',
    'purchase.bill.union': 'bills-and-POs union list for bill matching — replaced by "create bill from PO"',
    'purchase.bill.line.match': 'bill line matching UI — replaced by "create bill from PO"',
    'product.removal': 'removal strategies (FIFO/LIFO picking order) — no lots/locations hierarchy',
    'stock.putaway.rule': 'putaway rules — single stock location',
    'stock.route': 'routes — fixed one-step receipt and delivery',
    'stock.rule': 'stock rules — replaced by explicit microflows (confirm order -> transfer)',
    'procurement.group': 'procurement grouping — transfers link directly to the sales/purchase order',
    'stock.lot': 'lots/serial numbers out of scope (Q-F006-1)',
    'stock.lot.report': 'lots out of scope',
    'stock.move.line': 'merged into Inventory.StockMove (no lots/packages, one line per move)',
    'stock.package_level': 'packages out of scope',
    'stock.package.type': 'packages out of scope',
    'stock.quant.package': 'packages out of scope',
    'stock.scrap': 'scrapping — not in the demo flows (Q-F006-2)',
    'stock.scrap.reason.tag': 'scrapping dropped',
    'stock.storage.category': 'storage capacity rules — single location',
    'stock.storage.category.capacity': 'storage capacity rules — single location',
    'vendor.delay.report': 'vendor on-time statistics — could be a view entity later; not in POC',
    'account.cash.rounding': 'cash rounding — not needed',
    'account.incoterms': 'incoterms — not needed for the demo',
    'account.journal': 'no ledger: sales/purchase journals become invoice types, bank/cash journals become ENUM_PaymentMethod',
    'account.payment.method': 'replaced by ENUM_PaymentMethod',
    'account.payment.method.line': 'replaced by ENUM_PaymentMethod',
    'account.tax.group': 'tax groups (subtotal grouping) — dropped; taxes summed per tax',
    'account.tax.repartition.line': 'tax repartition to accounts — no ledger',
}
# In-scope transient/abstract models (structures) not mapped:
DROPPED_STRUCTURES_REASON = ('wizard or mixin not needed in the Mendix design: its job is done by a page + microflow, '
                             'or it belongs to a dropped feature (variants, lots, packages, portal, EDI, mail)')
