#!/usr/bin/env python3
"""mdl_pages.py — generate page scripts (list / form / popup) from ui_spec.py, the spec the wireframes
were drawn from (design/wireframes/<Page>.html). Also generates mdlsource/0-scaffold/010-navigation.mdl.

Usage:
  python3 -I pipelines/odoo/mdl_pages.py <Page> [<Page> ...]   # write the page script(s) the plan names
  python3 -I pipelines/odoo/mdl_pages.py --nav                   # regenerate navigation from the model's pages

Rules applied (ui-preflight-pages.md, design-spacing.md, learned-mdl-preflight.md, docs/design-reaches-app.md):
  - every full page: page-head (crumb + one H1 + right-aligned actions), sections spaced -large;
  - classes: only ledger recipe classes, Atlas classes and Core's promoted ones (page-head, crumb);
  - association columns unquoted (STOP 26); dynamictext params bare attributes only (STOP 12);
  - grants co-located: `grant view` ends every page script (module roles derived from the screen's roles);
  - every document carries a folder (module-brief "Document folder plan").
kinds report / inbox / task / dashboard are hand-written scripts; this generator refuses them.
"""
import os, re, subprocess, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
import ui_spec as U            # noqa: E402
import mdl_domain as D         # noqa: E402
from arch_blueprint import MODULE_ROLES  # noqa: E402
from wf_render import caption as WF_CAPTION, READONLY_PAT  # noqa: E402  (labels/read-only exactly as the wireframes)

ENTS, ENUMS = D.load()
SYS_ATTR = {'CreatedDate': 'DateTime', 'ChangedDate': 'DateTime'}
# links whose wireframe target is a prototype stand-in: the real page they open in the app
LINK_TARGET = {'UserProfile_Edit': 'Administration.Account_Overview'}
# hand-written logic a generated save runs just before its commit
# ratios stored with 8 decimals must display them all (Dozens = 0.08333333; ui-review 2026-10-15 P2-4)
DECIMAL_PRECISION = {'Factor': 8}
# On change of a field: the ACT_ that applies its dependent defaults (BRD onchange rules). Keyed by (entity, field).
ONCHANGE = {('Invoicing.InvoiceLine', 'InvoiceLine_Product'): 'Invoicing.ACT_InvoiceLine_ChangeProduct',
            **{('Invoicing.InvoiceLine', f): 'Invoicing.ACT_InvoiceLine_Recompute'
               for f in ('Quantity', 'UnitPrice', 'DiscountPercent', 'InvoiceLine_Taxes')},
            ('Sales.SalesOrder', 'SalesOrder_Customer'): 'Sales.ACT_SalesOrder_ChangeCustomer',
            ('Sales.SalesOrder', 'SalesOrder_QuotationTemplate'): 'Sales.ACT_SalesOrder_ApplyTemplate',
            ('Sales.SalesOrderLine', 'SalesOrderLine_Product'): 'Sales.ACT_SalesOrderLine_ChangeProduct',
            **{('Sales.SalesOrderLine', f): 'Sales.ACT_SalesOrderLine_Recompute'
               for f in ('Quantity', 'UnitPrice', 'DiscountPercent', 'SalesOrderLine_Taxes')},
            ('Purchasing.PurchaseOrder', 'PurchaseOrder_Vendor'): 'Purchasing.ACT_PurchaseOrder_ChangeVendor',
            ('Purchasing.PurchaseOrderLine', 'PurchaseOrderLine_Product'): 'Purchasing.ACT_PurchaseOrderLine_ChangeProduct',
            **{('Purchasing.PurchaseOrderLine', f): 'Purchasing.ACT_PurchaseOrderLine_Recompute'
               for f in ('Quantity', 'UnitPrice', 'DiscountPercent', 'PurchaseOrderLine_Taxes')}}
# The New button of a list whose new record needs defaults (number, dates, salesperson): a microflow, not create object.
NEW_ACTION = {'SalesOrder_Overview': 'Sales.ACT_SalesOrder_New', 'PurchaseOrder_Overview': 'Purchasing.ACT_PurchaseOrder_New',
              'Transfer_Overview': 'Inventory.ACT_Transfer_New'}
# Buttons whose microflow belongs to a later phase: left off the page until that phase builds it (build plan).
DEFERRED_BUTTONS = {'ACT_SalesOrder_CreateInvoice': 'Invoicing phase, build-plan row 52',
                    'ACT_PurchaseOrder_CreateBill': 'Invoicing phase, build-plan row 64'}
# Picker data-source constraints (coherence 2026-10-15 C1-02): archived records and the wrong kind never offered.
ACTIVE = '[Active = true()]'
PICKER_WHERE = {('Sales.SalesOrder', 'SalesOrder_Customer'): ACTIVE + '[IsCustomer = true()]',
                ('Sales.SalesOrder', 'SalesOrder_InvoiceAddress'): ACTIVE, ('Sales.SalesOrder', 'SalesOrder_DeliveryAddress'): ACTIVE,
                ('Sales.SalesOrderLine', 'SalesOrderLine_Product'): ACTIVE + '[CanBeSold = true()]',
                ('Sales.QuotationTemplateLine', 'QuotationTemplateLine_Product'): ACTIVE + '[CanBeSold = true()]',
                ('Products.PriceRule', 'PriceRule_Product'): ACTIVE,
                ('Purchasing.PurchaseOrder', 'PurchaseOrder_Vendor'): ACTIVE + '[IsVendor = true()]',
                ('Purchasing.PurchaseOrderLine', 'PurchaseOrderLine_Product'): ACTIVE + '[CanBePurchased = true()]',
                ('Purchasing.VendorPrice', 'VendorPrice_Vendor'): ACTIVE + '[IsVendor = true()]',
                ('Purchasing.VendorPrice', 'VendorPrice_Product'): ACTIVE + '[CanBePurchased = true()]'}
# Document lines removed through a guarded microflow (refuses delivered/received/invoiced lines, recomputes totals) — C1-04/05.
LINE_DELETE = {'Invoicing.InvoiceLine': 'Invoicing.ACT_InvoiceLine_Delete', 'Sales.SalesOrderLine': 'Sales.ACT_SalesOrderLine_Delete', 'Purchasing.PurchaseOrderLine': 'Purchasing.ACT_PurchaseOrderLine_Delete'}
# List-page tabs (wireframe lg-tabs, user 2026-10-16): caption -> XPath on the list's entity ('' = all).
TAB_WHERE = {
    'SalesOrder_Overview': [('All', ''), ('Quotations', "[Status = 'Quotation' or Status = 'QuotationSent']"),
                            ('Sales orders', "[Status = 'SalesOrder']"), ('To invoice', "[InvoiceStatus = 'ToInvoice']")],
    'PurchaseOrder_Overview': [('All', ''), ('RFQs', "[Status = 'RFQ' or Status = 'RFQSent']"), ('To approve', "[Status = 'ToApprove']"),
                               ('Purchase orders', "[Status = 'PurchaseOrder']")],
    'Transfer_Overview': [('All', '')] + [(cap, "[Inventory.Transfer_OperationType/Inventory.OperationType/Kind = '%s']" % k)
                                          for cap, k in (('Receipts', 'Receipt'), ('Deliveries', 'Delivery'), ('Internal', 'Internal'))],
    'Invoice_Overview': [('All', ''), ('Customer invoices', "[InvoiceType = 'CustomerInvoice']"), ('Vendor bills', "[InvoiceType = 'VendorBill']"),
                         ('Credit notes', "[InvoiceType = 'CustomerCreditNote' or InvoiceType = 'VendorCreditNote']")],
}
# A button over a list's selected rows (multi-select grid, control bar): (page, caption) -> microflow taking the list.
LIST_SELECTION_BUTTON = {('Invoice_Overview', 'Register payment'): 'Invoicing.ACT_Invoice_RegisterPayment'}
# A button on each row of an editable list: entity -> (caption, microflow taking the row). The row goes to the microflow with
# its unsaved edits, so it cannot race the row's save-on-leave (Apply counts after typing a count applied nothing, J-INV-04).
ROW_ACTION = {'Inventory.StockLevel': ('Apply', 'Inventory.ACT_StockLevel_ApplyCount'),
              'Inventory.ReorderRule': ('Order once', 'Inventory.ACT_ReorderRule_OrderOnce')}
# Inputs on an editable list that do NOT save on leave: the row action is their only writer. A counted quantity that saved on
# leave landed after Apply had cleared it, so the count came back and a second Apply would add the stock twice (J-INV-04).
NO_ROW_SAVE = {('Inventory.StockLevel', 'CountedQuantity')}
# Inputs editable only while empty (a new row): the fields that identify the row. An automated sweep's "Clear selection" on
# a saved stock row's product/location saved at once and orphaned the stock (verify-module monkey, 2026-10-16).
EDITABLE_WHEN_EMPTY = {('Inventory.StockLevel', 'StockLevel_Product'), ('Inventory.StockLevel', 'StockLevel_Location'),
                       ('Inventory.ReorderRule', 'ReorderRule_Product'), ('Inventory.ReorderRule', 'ReorderRule_Location'),
                       ('Purchasing.VendorPrice', 'VendorPrice_Vendor'), ('Purchasing.VendorPrice', 'VendorPrice_Product')}
# Inputs shown only in some states (C1-04: a template replaces every line, so only on a quotation).
VISIBLE_WHEN = {('Sales.SalesOrder', 'SalesOrder_QuotationTemplate'):
                "$currentObject/Status = Sales.ENUM_SalesOrderStatus.Quotation or $currentObject/Status = Sales.ENUM_SalesOrderStatus.QuotationSent"}
# Fields shown but never typed into: computed or system-maintained (stock is changed only by moves and counts).
READONLY_FIELDS = {('Inventory.StockLevel', 'Quantity'), ('Inventory.StockLevel', 'ReservedQuantity'),
                   ('Inventory.StockMove', 'Status'), ('Inventory.Transfer', 'DateDone'),
                   # a popup's documents are the ones it was opened for; the amount proposed is theirs (F008-UC006/UC007)
                   ('Invoicing.RegisterPaymentRequest', 'RegisterPaymentRequest_Invoices'), ('Invoicing.CreditNoteRequest', 'CreditNoteRequest_Invoice')}
# Page-level buttons on list pages: (page, caption) -> microflow without parameters.
LIST_BUTTON = {('ReorderRule_Overview', 'Run scheduler'): 'Inventory.ACT_ReorderRules_RunNow'}
# Smart buttons (Odoo stat buttons) under the status pill: (page, caption) -> microflow taking the form's object.
SMART_ACTION = {('SalesOrder_NewEdit', 'Delivery'): ('Inventory.ACT_SalesOrder_OpenDelivery',
                                                     "$currentObject/Status = Sales.ENUM_SalesOrderStatus.SalesOrder"),
                ('PurchaseOrder_NewEdit', 'Receipt'): ('Inventory.ACT_PurchaseOrder_OpenReceipt',
                                                       "$currentObject/Status = Purchasing.ENUM_PurchaseOrderStatus.PurchaseOrder")}
# Related links that open the object behind an association: (page, caption) -> (microflow taking the form's object, visible).
LINK_ACTION = {('Transfer_NewEdit', 'Open sales order'): ('Inventory.ACT_Transfer_OpenSalesOrder', '$currentObject/Inventory.Transfer_SalesOrder != empty'),
               ('Transfer_NewEdit', 'Open purchase order'): ('Inventory.ACT_Transfer_OpenPurchaseOrder', '$currentObject/Inventory.Transfer_PurchaseOrder != empty')}
# Odoo checks (BRD odooConstraints/odooChecks, disposition "val: <entity's VAL_>") added to the generated VAL_<E>, after the
# required fields (hand-written VALs — VAL_UoMCategory 401, VAL_Product 405 — carry their Odoo checks themselves).
# Each block is MDL; $E is the form's object. Lines are checked over the association, as the form holds them.
VAL_EXTRA = {
    'Core.PaymentTerm': ['''  retrieve $TermLines from $E/Core.PaymentTermLine_PaymentTerm;
  $BadPercent = find $TermLines where $currentObject/Value = Core.ENUM_PaymentTermValue.Percent and ($currentObject/ValueAmount < 0 or $currentObject/ValueAmount > 100);
  if $BadPercent != empty then
    validation feedback $BadPercent/ValueAmount message 'Percentages on the payment term lines must be between 0 and 100.';
    set $IsValid = false;
  end if;'''],
    'Products.ProductCategory': ['''  retrieve $NewParent from $E/Products.ProductCategory_Parent;
  if $NewParent != empty and ($NewParent = $E or ($E/FullName != empty and startsWith($NewParent/FullName, $E/FullName + ' / '))) then
    validation feedback $E/Products.ProductCategory_Parent message 'You cannot create recursive categories.';
    set $IsValid = false;
  end if;'''],
    'Products.Pricelist': ['''  retrieve $Rules from $E/Products.PriceRule_Pricelist;
  $BadDates = find $Rules where $currentObject/ValidFrom != empty and $currentObject/ValidTo != empty and $currentObject/ValidTo < $currentObject/ValidFrom;
  if $BadDates != empty then
    validation feedback $BadDates/ValidTo message 'The end date of a price rule cannot be before its start date.';
    set $IsValid = false;
  end if;
  $NoCategory = find $Rules where $currentObject/AppliesTo = Products.ENUM_PriceRuleScope.ProductCategory and $currentObject/Products.PriceRule_Category = empty;
  if $NoCategory != empty then
    validation feedback $NoCategory/Products.PriceRule_Category message 'Choose the category this rule applies to.';
    set $IsValid = false;
  end if;
  $NoProduct = find $Rules where $currentObject/AppliesTo = Products.ENUM_PriceRuleScope.Product and $currentObject/Products.PriceRule_Product = empty;
  if $NoProduct != empty then
    validation feedback $NoProduct/Products.PriceRule_Product message 'Choose the product this rule applies to.';
    set $IsValid = false;
  end if;'''],
    'Sales.QuotationTemplate': ['''  retrieve $TemplateLines from $E/Sales.QuotationTemplateLine_Template;
  $NoProduct = find $TemplateLines where $currentObject/Sales.QuotationTemplateLine_Product = empty;
  if $NoProduct != empty then
    validation feedback $NoProduct/Sales.QuotationTemplateLine_Product message 'Every template line needs a product.';
    set $IsValid = false;
  end if;'''],
}
# Row checks on editable list pages (rows save on change): (condition on $E, member, message). A row with such checks saves
# through ACT_<E>_SaveRow -> VAL_<E>_Row instead of "save changes", so a bad value is flagged on the row and not stored
# (user 2026-10-16; inline lists bypassed every VAL_).
ROW_VAL = {
    'Core.Sequence': [("$E/Code = empty or trim($E/Code) = ''", 'Code', 'Code is required.')],
    'Purchasing.VendorPrice': [("$E/Price != empty and $E/Price < 0", 'Price', 'The price cannot be negative.'),
                               ("$E/MinQuantity != empty and $E/MinQuantity < 0", 'MinQuantity', 'The minimum quantity cannot be negative.')],
    'Inventory.ReorderRule': [("$E/MinQuantity != empty and $E/MaxQuantity != empty and $E/MinQuantity > $E/MaxQuantity", 'MinQuantity',
                               'The minimum quantity must be less than or equal to the maximum quantity.'),
                              ("$E/MinQuantity != empty and $E/MinQuantity < 0", 'MinQuantity', 'The minimum quantity cannot be negative.'),
                              ("$E/MaxQuantity != empty and $E/MaxQuantity < 0", 'MaxQuantity', 'The maximum quantity cannot be negative.')],
}


def row_save_microflows(s, folder):
    """VAL_<E>_Row / SUB_<E>_SaveRow / ACT_<E>_SaveRow for an editable list whose rows carry checks (ROW_VAL)."""
    e = s['entity']
    if e not in ROW_VAL:
        return []
    mod, short = module_of(e), e.split('.')[1]
    mf = folder.replace('/Pages', '/Microflows')
    checks = '\n'.join('''  if %s then
    validation feedback $%s/%s message '%s';
    set $IsValid = false;
  end if;''' % (c.replace('$E', '$' + short), short, m, esc(msg)) for c, m, msg in ROW_VAL[e])
    return ['''/** Checks on one %(short)s row of %(page)s (the row saves on change). */
create or modify microflow %(mod)s.VAL_%(short)s_Row ($%(short)s: %(e)s)
returns Boolean as $IsValid
folder '%(f)s'
begin
  declare $IsValid Boolean = true;
%(checks)s
  return $IsValid;
end;

/** Persist one checked %(short)s row. */
create or modify microflow %(mod)s.SUB_%(short)s_SaveRow ($%(short)s: %(e)s)
folder '%(f)s'
begin
  commit $%(short)s with events refresh;
end;

/** On change of a %(short)s row on %(page)s: save it when its checks pass, else flag the field and keep it unsaved. */
create or modify microflow %(mod)s.ACT_%(short)s_SaveRow ($%(short)s: %(e)s)
folder '%(f)s'
begin
  $IsValid = call microflow %(mod)s.VAL_%(short)s_Row(%(short)s = $%(short)s);
  if $IsValid then
    call microflow %(mod)s.SUB_%(short)s_SaveRow(%(short)s = $%(short)s);
  end if;
end;
''' % dict(short=short, mod=mod, e=e, page=s['name'], f=mf, checks=checks)]


# Buttons whose microflow differs from the spec's BRD name: (page, caption) -> qualified microflow, called with the page's object.
# Popup confirmations call an ACT that checks, creates and closes (a SUB on a button has no grant, so users would not see it).
BUTTON_MF = {('CreditNote_Popup', 'Reverse'): 'Invoicing.ACT_Invoice_CreateCreditNote',
             ('RegisterPayment_Popup', 'Create payment'): 'Invoicing.ACT_RegisterPaymentRequest_Create',
             ('CreateInvoice_Popup', 'Create invoice'): 'Invoicing.ACT_CreateInvoiceRequest_Create',
             ('Invoice_NewEdit', 'Register payment'): 'Invoicing.ACT_Invoice_OpenRegisterPayment',
             ('Invoice_NewEdit', 'Credit note'): 'Invoicing.ACT_Invoice_OpenCreditNote'}
# Buttons left out of a generated page and inserted later by an ALTER script, to break a page <-> popup creation cycle
# (the form opens a popup whose confirmation opens the form): (page, caption) -> the script that inserts them.
# The plan's script gets the page without them; the named script re-creates the whole page with them (create or modify, so
# both re-run unchanged; an ALTER insert would refuse its second run as a duplicate widget).
DEFERRED_PAGE_BUTTONS = {('Invoice_NewEdit', 'Register payment'): 'mdlsource/9-invoicing/909-invoicing-page-invoice-new-edit-complete.mdl',
                         ('Invoice_NewEdit', 'Credit note'): 'mdlsource/9-invoicing/909-invoicing-page-invoice-new-edit-complete.mdl'}
COMPLETE_PASS = False   # True while writing that second script
# Visibility of a form button beyond its states: (page, caption) -> condition on $currentObject.
BUTTON_VISIBLE = {('Invoice_NewEdit', 'Register payment'): '$currentObject/Status = Invoicing.ENUM_InvoiceStatus.Posted and $currentObject/AmountDue > 0',
                  ('Invoice_NewEdit', 'Credit note'): '$currentObject/Status = Invoicing.ENUM_InvoiceStatus.Posted and '
                  '($currentObject/InvoiceType = Invoicing.ENUM_InvoiceType.CustomerInvoice or $currentObject/InvoiceType = Invoicing.ENUM_InvoiceType.VendorBill)'}
# Forms editable only in some states: page -> condition on the page parameter (Odoo locks posted documents).
FORM_EDITABLE_WHEN = {'Invoice_NewEdit': '$Invoice/Status = Invoicing.ENUM_InvoiceStatus.Draft'}
# Related links not rendered yet (their target page does not exist yet): (page, caption).
LINK_DEFERRED = {('Invoice_NewEdit', 'Open sales order'), ('Invoice_NewEdit', 'Open purchase order')}
SAVE_HOOK = {'Products.ProductCategory': 'Products.SUB_ProductCategory_ComputeFullName'}
LINK_CAPTION = {'Administration.Account_Overview': 'User accounts (Administration)'}


def existing_page(scr):
    """Qualified name of a ui_spec list page if it already exists in the model (links to later modules appear once built)."""
    if scr not in U.S or U.S[scr]['kind'] != 'list':
        return None
    q = '%s.%s' % (module_of(U.S[scr]['entity']), scr)
    out = subprocess.run(['./mxcli', '-p', 'app/erpv1.mpr', '-c', 'LIST PAGES'], cwd=ROOT, capture_output=True, text=True).stdout
    return q if ('| %s ' % q) in out else None
CAPTION_PREF = ['Name', 'Number', 'DisplayName', 'Code', 'FullName']
EXTERNAL_CAPTION = {'Administration.Account': 'FullName', 'System.User': 'Name', 'System.Image': 'Name'}


def module_of(q):
    return q.split('.')[0]


def humanize(n):
    n = re.sub(r'^[A-Z][A-Za-z]*_', '', n) if '_' in n else n
    s = re.sub(r'(?<=[a-z0-9])(?=[A-Z])', ' ', n)
    s = re.sub(r'\bUo M\b', 'UoM', s)
    return s[:1].upper() + s[1:].lower() if s else s


def ent(qname):
    e = ENTS.get(qname)
    if not e:
        raise SystemExit('unknown entity %s' % qname)
    return e


def attr(e, name):
    return next((a for a in e['attributes'] if a['name'] == name), None)


def assoc(e, name):
    """Association by short name, owned by e (or any entity: forms can show associations owned by e only)."""
    a = next((x for x in e['associations'] if x['name'] == name), None)
    return a


def caption_attr(target):
    if target in EXTERNAL_CAPTION:
        return EXTERNAL_CAPTION[target]
    t = ENTS.get(target)
    if not t:
        return 'Name'
    for c in CAPTION_PREF:
        if attr(t, c):
            return c
    return t['attributes'][0]['name']


def label_of(e, name):
    # wf_render.caption title-cases first and acronym-fixes only the tail ("Vat number", "Po approval");
    # repair the head here so the app reads VAT / PO (wireframe text-match is case-insensitive on labels).
    return re.sub(r'^(Vat|Po|Bic)\b', lambda m: m.group(1).upper(), WF_CAPTION(name))


def esc(s):
    return (s or '').replace("'", "''")


WID_PREFIX = ''   # 'p' while generating a popup: its widgets never share a name with the page underneath (DOM selectors)


def _wid(prefix, name):
    return WID_PREFIX + prefix + re.sub(r'[^A-Za-z0-9]', '', name.split('/')[-1])


def wid(prefix, name):
    return _wid(prefix, name)


def is_readonly(a, name=''):
    # exactly the wireframes' rule (wf_render.READONLY_PAT). Odoo's computed-not-stored flag is NOT used: e.g.
    # res.company.street is related to its partner in Odoo but a plain stored, editable attribute here.
    return bool(READONLY_PAT.match(name))


def enum_value_for_caption(enum_name, caption):
    for v in ENUMS[enum_name]['values']:
        if v['caption'].lower() == caption.lower() or v['name'].lower() == caption.replace(' ', '').lower():
            return v['name']
    raise SystemExit('no value with caption %r in %s' % (caption, enum_name))


# ── widgets ──────────────────────────────────────────────────────────────────────────────────
def input_widget(e, f, ind, readonly=False, prefix='in', row_save=False):
    """One input for field f (attribute or owned association) of entity e. Line-editor inputs (prefix 'ln')
    get their own widget names so they never clash with the header fields (CE0495)."""
    wid = (lambda k, n: _wid('ln' + k, n)) if prefix == 'ln' else _wid
    a = attr(e, f)
    lab = esc(label_of(e, f))
    ro = ', Editable: Never' if (readonly or is_readonly(a, f) or (e['name'], f) in READONLY_FIELDS) else ''
    oc = ONCHANGE.get((e['name'], f))
    if oc and not ro:
        ro = ', OnChange: call microflow %s(%s = $currentObject)' % (oc, e['name'].split('.')[1])
    elif row_save and not ro and e['name'] in ROW_VAL:
        ro = ', OnChange: call microflow %s.ACT_%s_SaveRow(%s = $currentObject)' % (module_of(e['name']), e['name'].split('.')[1], e['name'].split('.')[1])
    elif row_save and not ro:
        ro = ', OnChange: save changes'   # a row of an editable list page commits itself (C1-07: edits were lost)
    if (e['name'], f) in EDITABLE_WHEN_EMPTY and 'Editable: Never' not in ro:
        ro += ', Editable: $currentObject/%s.%s = empty' % (e['name'].split('.')[0], f)
    vis = VISIBLE_WHEN.get((e['name'], f))
    if vis:
        ro += ', Visible: ' + vis
    if a or f in SYS_ATTR:
        t = a['type'] if a else SYS_ATTR[f]
        if t == 'Boolean':
            return '%scheckbox %s (Label: \'%s\', Attribute: %s%s)' % (ind, wid('cb', f), lab, D.q(f), ro)
        if t == 'Enumeration':
            return '%scombobox %s (Label: \'%s\', Attribute: %s%s)' % (ind, wid('cmb', f), lab, D.q(f), ro)
        if t == 'DateTime':
            return '%sdatepicker %s (Label: \'%s\', Attribute: %s%s)' % (ind, wid('dp', f), lab, D.q(f), ro)
        if t == 'String' and (a.get('length') in (None, 'unlimited') or (isinstance(a.get('length'), int) and a['length'] > 2000)):
            return '%stextarea %s (Label: \'%s\', Attribute: %s%s)' % (ind, wid('ta', f), lab, D.q(f), ro)
        if t == 'Decimal':
            prec = DECIMAL_PRECISION.get(f, 2)
            return '%stextbox %s (Label: \'%s\', Attribute: %s, DecimalPrecision: %d, GroupDigits: true%s)' % (ind, wid('txt', f), lab, D.q(f), prec, ro)
        return '%stextbox %s (Label: \'%s\', Attribute: %s%s)' % (ind, wid('txt', f), lab, D.q(f), ro)
    s = assoc(e, f)
    if s:
        tgt = s['target']
        cap = caption_attr(tgt)
        where = PICKER_WHERE.get((e['name'], f))
        where = ' where ' + where if where else ''
        return ('%scombobox %s (Label: \'%s\', Attribute: %s, DataSource: database %s%s sort by %s asc, CaptionAttribute: %s%s)'
                % (ind, wid('cmb', f), lab, f, D.qn(tgt), where, D.q(cap), D.q(cap), ro))
    raise SystemExit('field %s is neither attribute nor owned association of %s' % (f, e['name']))


def column(e, f, filters=False):
    a = attr(e, f)
    if a or f in SYS_ATTR:
        t = a['type'] if a else SYS_ATTR[f]
        align = ', Alignment: right' if t in ('Decimal', 'Integer', 'Long') else ''
        cls = ", DynamicCellClass: 'num-right'" if t in ('Decimal', 'Integer', 'Long') else ''
        # no autoFit: it starved the text and association columns to ~15px (ui-review 2026-10-15 Sales P1)
        fit = ''
        # wrap rather than truncate: statuses like "Purchase order" were cut to "Purchase or…" (ui-review 2026-10-15 Purchasing P2)
        # an address never wraps: it broke mid-word over three lines and tripled the row height (ui-review 2026-10-16 Partners P2)
        wrap = 'false' if f in ('Email', 'Website') else 'true'
        head = "column (Attribute: %s, Caption: '%s'%s%s%s, WrapText: %s)" % (D.q(f), esc(label_of(e, f)), align, cls, fit, wrap)
        if filters:
            flt = {'String': 'textfilter', 'Decimal': 'numberfilter', 'Integer': 'numberfilter', 'Long': 'numberfilter',
                   'DateTime': 'datefilter', 'Enumeration': 'dropdownfilter', 'Boolean': 'dropdownfilter'}[t]
            return head + ' { %s %s }' % (flt, wid('f', f))
        return head
    s = assoc(e, f)
    if s and s['type'] == 'Reference':
        cap = caption_attr(s['target'])
        head = "column (Attribute: %s/%s, Caption: '%s', WrapText: true)" % (f, cap, esc(label_of(e, f)))
        return head
    raise SystemExit('column %s not usable on %s' % (f, e['name']))


# ── page access ──────────────────────────────────────────────────────────────────────────────
def module_roles_for(page_module, user_roles):
    roles = []
    for r, users in MODULE_ROLES[page_module].items():
        if set(users) & set(user_roles):
            roles.append('%s.%s' % (page_module, r))
    return roles


def folder_of(module, page):
    brief = os.path.join(ROOT, 'architecture/modules/%s/module-brief.md' % module)
    for line in open(brief):
        m = re.match(r'^\| %s \| `([^`]+)` \|' % re.escape(page), line)
        if m:
            return m.group(1)
    raise SystemExit('no folder row for %s in %s brief' % (page, module))


# ── page bodies ──────────────────────────────────────────────────────────────────────────────
def page_head(crumb, title_line, actions, ind='  '):
    L = ['%scontainer ctnPageHead (Class: \'page-head spacing-outer-bottom-large\') {' % ind,
         '%s  container ctnPageHeadTitle (Class: \'page-head-title\') {' % ind]
    if crumb:
        L.append('%s    dynamictext txtCrumb (Content: \'%s\', RenderMode: Text, Class: \'crumb\')' % (ind, esc(crumb)))
    L.append('%s    %s' % (ind, title_line))
    L.append('%s  }' % ind)
    if actions:
        L.append('%s  container ctnPageHeadActions (Class: \'page-head-actions\') {' % ind)
        L += ['%s    %s' % (ind, a) for a in actions]
        L.append('%s  }' % ind)
    L.append('%s}' % ind)
    return L


def show_page_action(target_page, param_name, value='$currentObject'):
    tm = page_module(target_page)
    return 'show page %s.%s(%s = %s)' % (tm, target_page, param_name, value)


def page_module(p):
    return U.S[p]['entity'].split('.')[0] if U.S[p].get('param') or U.S[p]['kind'] in ('list', 'form', 'popup') else None


def param_name(qtype):
    return qtype.split('.')[-1]


def gen_list(s):
    e = ent(s['entity'])
    mod = module_of(s['entity'])
    actions = []
    if s.get('new'):
        tgt = s['new']
        if s['name'] in NEW_ACTION:
            actions.append("actionbutton btnNew (Caption: 'New', Action: call microflow %s, ButtonStyle: Primary)" % NEW_ACTION[s['name']])
        else:
            actions.append("actionbutton btnNew (Caption: 'New', Action: create object %s then show page %s.%s, ButtonStyle: Primary)"
                           % (D.qn(s['entity']), page_module(tgt), tgt))
    for i, b in enumerate(s.get('buttons', [])):
        mf = LIST_BUTTON.get((s['name'], b[0]))
        if mf:
            actions.append("actionbutton %s (Caption: '%s', Action: call microflow %s, ButtonStyle: %s)"
                           % (wid('btn', b[0] + str(i)), esc(b[0]), mf, 'Default' if actions else 'Primary'))
    L = page_head(None, "dynamictext txtTitle (Content: '%s', RenderMode: H1)" % esc(s['title']), actions)
    filt = set(s.get('filters', []))
    if s.get('editable'):
        first = s['columns'][0]
        sort = D.q(first) if attr(e, first) else first + '/' + caption_attr(assoc(e, first)['target'])
        add = '%s.ACT_%s_Add' % (mod, s['entity'].split('.')[1]) if s.get('add') else None
        L += editable_listview(e, s['columns'], 'database %s sort by %s asc' % (D.qn(s['entity']), sort), '  ', add, delete=bool(s.get('add')), row_save=True)
        return L
    sort = s.get('sort', s['columns'][0])
    # documents (numbered) list newest first, as Odoo does; the newest also stays on page 1 (J-INV-01 control, 2026-10-16)
    direction = 'desc' if sort == 'Number' or (attr(e, sort) or {}).get('type') == 'DateTime' else 'asc'
    src = 'database %s sort by %s %s' % (D.qn(s['entity']), D.q(sort) if attr(e, sort) else sort + '/' + caption_attr(assoc(e, sort)['target']), direction)
    open_ = ''
    if s.get('open'):
        open_ = ', OnClick: %s' % show_page_action(s['open'], param_name(U.S[s['open']]['param']))
    sel = [(cap, mf) for (pg, cap), mf in LIST_SELECTION_BUTTON.items() if pg == s['name']]
    def grid(name, where, sfx, ind):
        g = ["%sdatagrid %s (DataSource: %s, PagingPosition: bottom, Class: 'density-compact'%s%s) {"
             % (ind, name, src.replace(' sort by ', ' where %s sort by ' % where, 1) if where else src, open_,
                ', Selection: Multi' if sel else '')]
        if sel:   # the control bar is not row-scoped: it passes the grid's selection
            g.append(ind + '  controlbar {')
            for cap, mf in sel:
                g.append(ind + "    actionbutton %s (Caption: '%s', Action: call microflow %s(%sList = $%s))"
                         % (wid('btnSel', cap + sfx), esc(cap), mf, s['entity'].split('.')[1], name))
            g.append(ind + '  }')
        for c in s['columns']:   # every attribute column filterable (P2-3); filter names unique per page (CE0495)
            g.append(ind + '  ' + re.sub(r'(filter f\w+)', r'\g<1>' + sfx, column(e, c, filters=not assoc(e, c))))
        g.append(ind + '}')
        return g
    tabs = TAB_WHERE.get(s['name'])
    if not tabs:
        return L + grid('gridMain', '', '', '  ')
    # the wireframe's tabs (user 2026-10-16 "yes"): one grid per tab; the first keeps gridMain for journeys and shot lists
    L.append('  tabcontainer tabsList {')
    for i, (cap, where) in enumerate(tabs):
        key = re.sub(r'\W', '', cap.title())
        L.append("    tabpage tp%s (Caption: '%s') {" % (key, esc(cap)))
        L += grid('gridMain' if i == 0 else 'grid' + key, where, '' if i == 0 else key, '      ')
        L.append('    }')
    L.append('  }')
    return L


LINE_READONLY = {'Code'}   # business keys other code depends on (Core.Sequence.Code = the numbering contract)


def editable_listview(e, cols, source, ind, add_mf, delete=True, row_save=False):
    """Inline-editable rows: a caption row (desktop/tablet), then one row of inputs per object. Inputs keep their
    labels; Core main.scss shows them only on phones, where the caption row is hidden (ui-review 2026-10-14 P2-1)."""
    def weight(c):
        a = attr(e, c)
        if c == cols[0] and assoc(e, c) and (e['name'].endswith('Line') or e['name'] == 'Inventory.StockMove'):
            return 4   # the line's product: its name must read (ui-review 2026-10-15 Sales/Purchasing P2)
        if assoc(e, c) or (a and a['type'] == 'String'):
            return 2   # pickers and text need room for a caption next to their buttons
        return 1.2     # numbers, dates, check boxes
    row_act = ROW_ACTION.get(e['name'])
    avail = 12 - (1 if delete else 0) - (1 if row_act else 0)
    ws = [weight(c) for c in cols]
    # largest remainder: leftover columns go to the inputs that lost most to rounding, not to the first ones
    # (ui-review 2026-10-16: Quantity got 2 columns while Unit and Taxes showed only their buttons)
    raw = [avail * w / sum(ws) for w in ws]
    widths = [max(1, int(r)) for r in raw]
    for i in sorted(range(len(cols)), key=lambda k: raw[k] - widths[k], reverse=True):
        if sum(widths) >= avail:
            break
        widths[i] += 1
    while sum(widths) > avail:
        widths[widths.index(max(widths))] -= 1
    L = ['%slayoutgrid gridLinesHead (Class: \'th lines-head hide-phone\') {' % ind, '%s  row {' % ind]
    for c, w in zip(cols, widths):
        L.append("%s    column (DesktopWidth: %d) { dynamictext %s (Content: '%s', RenderMode: Text) }" % (ind, w, wid('hd', c), esc(label_of(e, c))))
    L += ['%s  }' % ind, '%s}' % ind]
    L.append('%slistview lvLines (DataSource: %s, Editable: true, Class: \'lines-list\') {' % (ind, source))
    L += ['%s  layoutgrid gridLine {' % ind, '%s    row {' % ind]
    for c, w in zip(cols, widths):
        wd = input_widget(e, c, '', prefix='ln', readonly=c in LINE_READONLY, row_save=row_save and (e['name'], c) not in NO_ROW_SAVE)
        L.append('%s      column (DesktopWidth: %d, TabletWidth: %d, PhoneWidth: 12) { %s }' % (ind, w, w, wd))
    if row_act:
        L.append("%s      column (DesktopWidth: 1, TabletWidth: 1, PhoneWidth: 12) { linkbutton btnRowAction (Caption: '%s', Action: call microflow %s(%s = $currentObject)) }"
                 % (ind, esc(row_act[0]), row_act[1], e['name'].split('.')[1]))
    if delete:
        act = ('call microflow %s(%s = $currentObject)' % (LINE_DELETE[e['name']], e['name'].split('.')[1])) if e['name'] in LINE_DELETE else 'delete'
        L.append("%s      column (DesktopWidth: 1, TabletWidth: 1, PhoneWidth: 12) { linkbutton btnLineDelete (Caption: 'Remove', Action: %s) }" % (ind, act))
    L += ['%s    }' % ind, '%s  }' % ind, '%s}' % ind]
    if add_mf:
        L.append("%slinkbutton btnAddLine (Caption: '+ Add a line', Action: call microflow %s)" % (ind, add_mf))
    return L


def sections_block(e, sections, ind, readonly_all=False, popup_title=None):
    L = ['%slayoutgrid gridSections (Class: \'spacing-outer-bottom-large\') {' % ind, '%s  row {' % ind]
    width = 6 if len(sections) > 1 else 12
    for title, fields in sections:
        L.append('%s    column (DesktopWidth: %d, TabletWidth: %d, PhoneWidth: 12) {' % (ind, width, width))
        if not (popup_title and len(sections) == 1):
            L.append("%s      dynamictext %s (Content: '%s', RenderMode: H2)" % (ind, wid('h', title), esc(title)))
        for f in fields:
            L.append(input_widget(e, f, ind + '      ', readonly=readonly_all))
        L.append('%s    }' % ind)
    L += ['%s  }' % ind, '%s}' % ind]
    return L


def buttons(s, e, pname, popup=False):
    out = []
    shown = []   # the states of the buttons emitted so far
    for i, b in enumerate(s.get('buttons', [])):
        cap, act = b[0], b[1]
        states = b[2] if len(b) > 2 else None
        if act in DEFERRED_BUTTONS or ((s['name'], cap) in DEFERRED_PAGE_BUTTONS and not COMPLETE_PASS):
            continue
        if cap == 'Archive':
            act = 'ACT_%s_Archive' % e['name'].split('.')[1]
        if act == 'save' or act.startswith('VAL_'):
            short = e['name'].split('.')[1]
            a = 'call microflow %s.ACT_%s_Save(%s = $currentObject)' % (module_of(e['name']), short, short)
        elif (s['name'], cap) in BUTTON_MF:
            a = 'call microflow %s(%s = $currentObject)' % (BUTTON_MF[(s['name'], cap)], e['name'].split('.')[1])
        else:
            mod = D_MF_MODULE(act, e['name'])
            params = MF_PARAMS(act, e['name'])
            args = ', '.join('%s = $currentObject' % p for p in params[:1])  # buttons sit inside dvMain
            a = 'call microflow %s.%s%s' % (mod, act, '(%s)' % args if args else '')
        vis = ''
        if states and s.get('statusbar'):
            stat_attr = s['statusbar'][0]
            en = attr(e, stat_attr)['enumeration']
            conds = ' or '.join('$currentObject/%s = %s.%s' % (stat_attr, en, enum_value_for_caption(en, st)) for st in states)
            vis = ', Visible: %s' % conds
        if (s['name'], cap) in BUTTON_VISIBLE:
            vis = ', Visible: %s' % BUTTON_VISIBLE[(s['name'], cap)]
        has_save = any(x[0] == 'Save' for x in s.get('buttons', []))
        # the first button of each state is primary (a posted invoice's Register payment, a draft's Confirm)
        overlap = any(st is None or states is None or set(st) & set(states) for st in shown)
        style = 'Primary' if (cap == 'Save' if has_save else not overlap) else 'Default'
        shown.append(states)
        out.append("actionbutton %s (Caption: '%s', Action: %s, ButtonStyle: %s%s)" % (wid('btn', cap + str(i)), esc(cap), a, style, vis))
    if popup:
        out.append("actionbutton %sbtnCancel (Caption: 'Cancel', Action: cancel changes close page)" % WID_PREFIX)
    return out


_MF = None


def _load_mfs():
    global _MF
    if _MF is None:
        import glob, json
        _MF = {}
        for f in glob.glob(os.path.join(ROOT, 'analysis/odoo/knowledge-base/brd/F*.brd.json')):
            for m in json.load(open(f))['microflows']:
                _MF[m['name']] = m
    return _MF


def D_MF_MODULE(name, entity=None):
    m = _load_mfs().get(name)
    return m['module'] if m else module_of(entity)


def MF_PARAMS(name, entity=None):
    m = _load_mfs().get(name)
    return [p['name'] for p in m.get('params', [])] if m else [entity.split('.')[1]]


def gen_form(s, popup=False):
    e = ent(s['entity'])
    pname = param_name(s['param']) if s.get('param') else param_name(s['entity'])
    acts = buttons(s, e, pname, popup=popup)
    L = []
    if not popup:
        title_attr = s.get('header') or ('Name' if attr(e, 'Name') else None)
        # a new record has no name yet: the heading says 'New' until it does (blank H1, ui-review 2026-10-15 Sales)
        expr = "if $currentObject/%s = empty or trim($currentObject/%s) = '' then 'New' else $currentObject/%s" % ((title_attr,) * 3)
        title = ("dynamictext txtTitle (Content: '{1}', ContentParams: ({1} = %s), RenderMode: H1)" % expr) if title_attr \
            else "dynamictext txtTitle (Content: '%s', RenderMode: H1)" % esc(s['title'])
        L += page_head(s['title'], title, acts, ind='    ')
        if s.get('statusbar'):
            L.append("    dynamictext txtStatus (Content: '{1}', ContentParams: ({1} = %s), Class: 'pill pill-info spacing-outer-bottom-medium')" % D.q(s['statusbar'][0]))
        for i, (cap, _target, _n) in enumerate(s.get('smart', [])):
            sm = SMART_ACTION.get((s['name'], cap))
            if sm:
                L.append("    linkbutton %s (Caption: '%s', Action: call microflow %s(%s = $currentObject), Visible: %s)"
                         % (wid('lnkSmart', cap), esc(cap), sm[0], pname, sm[1]))
    L += sections_block(e, s.get('sections', []), '    ', readonly_all=s.get('readonly', False),
                        popup_title=s['title'] if popup else None)
    for ln in ([s['lines']] if isinstance(s.get('lines'), dict) else s.get('lines', []) or []):
        le = ent(ln['entity'])
        L.append("    dynamictext %s (Content: '%s', RenderMode: H2)" % (wid('h', ln['title']), esc(ln['title'])))
        lmod = module_of(ln['entity'])
        src = 'database from $currentObject/%s.%s/%s' % (lmod, ln['via'], D.qn(e['name']).replace(D.q(e['name'].split('.')[1]), e['name'].split('.')[1]))
        src = '$currentObject/%s.%s' % (lmod, ln['via'])
        add_mf = '%s.ACT_%s_Add' % (lmod, ln['entity'].split('.')[1]) if ln.get('editable') else None
        if add_mf:
            add_mf += '(%s = $currentObject)' % pname
        if ln.get('editable'):
            L += editable_listview(le, ln['columns'], src, '    ', add_mf)
        else:
            open_ = ''
            if ln.get('open_via'):   # the row opens the object across an association, not the row itself
                tp = U.S[ln['open']]
                open_ = ', OnClick: call microflow %s.ACT_%s_Open%s(%s = $currentObject)' % (
                    lmod, ln['entity'].split('.')[1], tp['param'].split('.')[1], param_name(ln['entity']))
            elif ln.get('open'):
                tp = U.S[ln['open']]
                open_ = ', OnClick: show page %s.%s(%s = $currentObject)' % (module_of(tp['entity']), ln['open'], param_name(tp['param']))
            # a database query, not $currentObject/<assoc>: the association may be a self-reference (Partner_ParentCompany),
            # which a grid cannot walk backwards (CE8812), and a query re-runs after the popup saves a child
            dsrc = "database %s where [%s.%s = '[%%CurrentObject%%]']" % (D.qn(ln['entity']), lmod, ln['via'])
            L.append("    datagrid %s (DataSource: %s, Class: 'density-compact'%s) {" % (wid('grid', ln['title']), dsrc, open_))
            L += ['      ' + column(le, c) for c in ln['columns']] + ['    }']
            if ln.get('open') and ln.get('add', True):
                L.append("    linkbutton btnAddChild (Caption: '+ Add', Action: call microflow %s.ACT_%s_AddTo%s(%s = $currentObject))"
                         % (lmod, ln['entity'].split('.')[1], pname, pname))
    if s.get('totals'):
        L.append("    container ctnTotals (Class: 'spacing-outer-bottom-large') {")
        for t in s['totals']:
            L.append(input_widget(e, t, '      ', readonly=True))
        L.append('    }')
    if s.get('notes'):
        L.append(input_widget(e, s['notes'], '    '))
    links = [(t, LINK_TARGET.get(g) or existing_page(g)) for t, g in s.get('links', [])]
    if any((p or LINK_ACTION.get((s['name'], t))) and (s['name'], t) not in LINK_DEFERRED for t, p in links):
        L.append("    dynamictext hRelated (Content: 'Related', RenderMode: H2)")
    for i, (text, page) in enumerate(links):
        if (s['name'], text) in LINK_DEFERRED:
            continue
        la = LINK_ACTION.get((s['name'], text))
        if la:
            L.append("    linkbutton lnk%d (Caption: '%s', Action: call microflow %s(%s = $currentObject), Visible: %s)" % (i, esc(text), la[0], pname, la[1]))
        elif page:
            L.append("    linkbutton lnk%d (Caption: '%s', Action: show page %s)" % (i, esc(LINK_CAPTION.get(page, text.split(':')[0])), page))
    if popup:
        L.append('    footer {')
        L += ['      ' + a for a in acts]
        L.append('    }')
    cond = FORM_EDITABLE_WHEN.get(s['name'])
    if cond:   # every input, and the line add/remove links, only while the condition holds (posted documents are locked)
        out = []
        for ln in L:
            if re.match(r'\s*(column \([^)]*\) \{ )?(textbox|textarea|combobox|datepicker|checkbox|radiobuttons) ', ln) and 'Editable:' not in ln:
                tail = ') }' if ln.rstrip().endswith(') }') else ')'
                ln = ln.rstrip()[:-len(tail)] + ', Editable: %s%s' % (cond, tail)
            elif re.search(r'linkbutton (btnAddLine|btnLineDelete) ', ln) and 'Visible:' not in ln:
                tail = ') }' if ln.rstrip().endswith(') }') else ')'
                ln = ln.rstrip()[:-len(tail)] + ', Visible: %s%s' % (cond, tail)
            out.append(ln)
        L = out
    return L, pname


def save_microflows(s, folder):
    """VAL_/SUB_/ACT_<E>_Save for a form whose Save has no hand-written microflow in the BRDs.
    VAL_ flags every required (BRD mandatory) field shown on the page, collect-all
    (learned-microflow-patterns.md); SUB_ commits with refresh; ACT_ calls both and closes the page."""
    save_btn = next((b for b in s.get('buttons', []) if b[1] == 'save' or b[1].startswith('VAL_')), None)
    if not save_btn:
        return []
    own_val = save_btn[1] if save_btn[1].startswith('VAL_') else None
    e = ent(s['entity'])
    mod, short = module_of(e['name']), e['name'].split('.')[1]
    if 'ACT_%s_Save' % short in _load_mfs():
        return []
    shown = [f for _, fs in s.get('sections', []) for f in fs]
    checks = []
    for f in shown:
        a = attr(e, f)
        sa = assoc(e, f)
        if a and a.get('mandatory') and not is_readonly(a, f) and a.get('odooDefault') is None and a.get('default') is None:
            cond = "trim($%s/%s) = ''" % (short, f) if a['type'] == 'String' else '$%s/%s = empty' % (short, f)
            if a['type'] == 'String':
                cond = '$%s/%s = empty or %s' % (short, f, cond)
            checks.append((f, cond))
        elif sa and sa.get('mandatory') and sa['type'] == 'Reference':
            checks.append((f, '$%s/%s.%s = empty' % (short, mod, f)))
    body = '\n'.join('''  if %s then
    validation feedback $%s/%s message '%s is required.';
    set $IsValid = false;
  end if;''' % (c, short, f if attr(e, f) else '%s.%s' % (mod, f), esc(label_of(e, f))) for f, c in checks)
    mfolder = folder.replace('/Pages', '/Microflows')
    rules_doc = ''
    if e['name'] in VAL_EXTRA:
        # Odoo's checks in their own sub-microflow, so the VAL_ stays small (CONV009, 2026-10-16)
        rules_doc = '''/** Odoo's checks on a %(short)s and its lines (BRD odooConstraints / odooChecks, disposition val). */
create or modify microflow %(mod)s.VAL_%(short)s_Rules ($%(short)s: %(q)s)
returns Boolean as $IsValid
folder '%(f)s'
begin
  declare $IsValid Boolean = true;
%(blocks)s
  return $IsValid;
end;

''' % dict(short=short, mod=mod, q=e['name'], f=mfolder, blocks='\n'.join(b.replace('$E', '$' + short) for b in VAL_EXTRA[e['name']]))
        body += '''
  $RulesValid = call microflow %s.VAL_%s_Rules(%s = $%s);
  if not($RulesValid) then
    set $IsValid = false;
  end if;''' % (mod, short, short, short)
    hook = SAVE_HOOK.get(e['name'])
    hook_call = ('  call microflow %s(%s = $%s);\n' % (hook, short, short)) if hook else ''
    # Lines typed on the form travel with the Save call but are not committed by committing the header: commit them over
    # the association first (sweep 2026-10-16: a new Warehouse operation type lost its typed name on Save).
    lines = [ln for ln in ([s['lines']] if isinstance(s.get('lines'), dict) else (s.get('lines') or [])) if ln.get('editable')]
    hook_call += ''.join('  retrieve $Lines%d from $%s/%s.%s;\n  commit $Lines%d with events;\n'
                         % (i, short, module_of(ln['entity']), ln['via'], i) for i, ln in enumerate(lines))
    val_doc = '' if own_val else '''/** Validate a %(short)s before save: every required field on %(page)s, all flagged on one submit. */
create or modify microflow %(mod)s.VAL_%(short)s ($%(short)s: %(q)s)
returns Boolean as $IsValid
folder '%(f)s'
begin
  declare $IsValid Boolean = true;
%(body)s
  return $IsValid;
end;

''' % dict(short=short, mod=mod, q=e['name'], page=s['name'], f=mfolder, body=body)
    return [rules_doc + val_doc + '''/** Persist a validated %(short)s. */
create or modify microflow %(mod)s.SUB_%(short)s_Save ($%(short)s: %(q)s)
folder '%(f)s'
begin
%(hook)s  commit $%(short)s with events refresh;
end;

/** Save button on %(page)s: validate, persist, close. */
create or modify microflow %(mod)s.ACT_%(short)s_Save ($%(short)s: %(q)s)
folder '%(f)s'
begin
  $IsValid = call microflow %(mod)s.%(val)s(%(short)s = $%(short)s);
  if $IsValid then
    call microflow %(mod)s.SUB_%(short)s_Save(%(short)s = $%(short)s);
    close page;
  end if;
end;
''' % dict(short=short, mod=mod, q=e['name'], page=s['name'], f=mfolder, hook=hook_call, val=own_val or 'VAL_%s' % short)]
    return [rules_doc + '''/** Validate a %(short)s before save: every required field on %(page)s, all flagged on one submit. */
create or modify microflow %(mod)s.VAL_%(short)s ($%(short)s: %(q)s)
returns Boolean as $IsValid
folder '%(f)s'
begin
  declare $IsValid Boolean = true;
%(body)s
  return $IsValid;
end;

/** Persist a validated %(short)s. */
create or modify microflow %(mod)s.SUB_%(short)s_Save ($%(short)s: %(q)s)
folder '%(f)s'
begin
%(hook)s  commit $%(short)s with events refresh;
end;

/** Save button on %(page)s: validate, persist, close. */
create or modify microflow %(mod)s.ACT_%(short)s_Save ($%(short)s: %(q)s)
folder '%(f)s'
begin
  $IsValid = call microflow %(mod)s.VAL_%(short)s(%(short)s = $%(short)s);
  if $IsValid then
    call microflow %(mod)s.SUB_%(short)s_Save(%(short)s = $%(short)s);
    close page;
  end if;
end;
''' % dict(short=short, mod=mod, q=e['name'], page=s['name'], f=mfolder, body=body, hook=hook_call)]


def child_add_microflows(s):
    """'+ Add' under a read-only lines grid whose rows open a popup: a new child linked to the parent, opened in that popup
    (uncommitted: Save commits it, Cancel drops it)."""
    out = []
    lines = [s['lines']] if isinstance(s.get('lines'), dict) else (s.get('lines') or [])
    pq = s['param'] or s['entity']
    pname = param_name(pq)
    for ln in lines:
        if ln.get('editable') or not ln.get('open'):
            continue
        lmod, lshort = module_of(ln['entity']), ln['entity'].split('.')[1]
        tp = U.S[ln['open']]
        mf = folder_of(module_of(pq), s['name']).replace('/Pages', '/Microflows')
        if ln.get('open_via'):
            tq = tp['param']
            rn = param_name(ln['entity'])
            ts = tq.split('.')[1]
            out.append('''/** The %(ts)s this %(ls)s points at (empty when it points nowhere). */
create or modify microflow %(m)s.SUB_%(ls)s_Get%(ts)s ($%(rn)s: %(le)s)
returns %(tq)s as $Target
folder '%(f)s'
begin
  retrieve $Target from $%(rn)s/%(m)s.%(via)s;
  return $Target;
end;

/** A %(ls)s row on %(page)s opens its %(ts)s in %(open)s. */
create or modify microflow %(m)s.ACT_%(ls)s_Open%(ts)s ($%(rn)s: %(le)s)
folder '%(f)s'
begin
  $Target = call microflow %(m)s.SUB_%(ls)s_Get%(ts)s(%(rn)s = $%(rn)s);
  if $Target = empty then
    show message 'This row is not linked to a %(tl)s.' type Information;
    return;
  end if;
  show page %(tm)s.%(open)s(%(tp)s = $Target);
end;
''' % dict(ts=ts, ls=lshort, m=lmod, rn=rn, le=ln['entity'], tq=tq, f=mf, via=ln['open_via'], page=s['name'],
           open=ln['open'], tl=ts.lower(), tm=module_of(tp['entity']), tp=param_name(tq)))
        if not ln.get('add', True):
            continue
        out.append('''/** A new, uncommitted %s linked to this %s. */
create or modify microflow %s.SUB_%s_NewFor%s ($%s: %s)
returns %s as $Child
folder '%s'
begin
  $Child = create %s (%s.%s = $%s);
  return $Child;
end;

/** "+ Add" on %s: a new %s, opened in %s (Save commits it, Cancel drops it). */
create or modify microflow %s.ACT_%s_AddTo%s ($%s: %s)
folder '%s'
begin
  $Child = call microflow %s.SUB_%s_NewFor%s(%s = $%s);
  show page %s.%s(%s = $Child);
end;
''' % (lshort, pname, lmod, lshort, pname, pname, pq, ln['entity'], mf, D.qn(ln['entity']), lmod, ln['via'], pname,
       s['name'], lshort, ln['open'], lmod, lshort, pname, pname, pq, mf, lmod, lshort, pname, pname, pname,
       module_of(tp['entity']), ln['open'], param_name(tp['param'])))
    return out


def line_add_microflows(s):
    """ACT_<Line>_Add(<Parent>) for every editable lines block: create the line on the parent, commit, refresh."""
    out = []
    lines = [s['lines']] if isinstance(s.get('lines'), dict) else (s.get('lines') or [])
    pq = s['param'] or s['entity']
    pname = param_name(pq)
    for ln in lines:
        if not ln.get('editable'):
            continue
        lmod, lshort = module_of(ln['entity']), ln['entity'].split('.')[1]
        mf = folder_of(module_of(pq), s['name']).replace('/Pages', '/Microflows')
        out.append('''/** A new %s on the %s, committed so the line editor shows it at once. */
create or modify microflow %s.SUB_%s_Add ($%s: %s)
returns %s as $Line
folder '%s'
begin
  $Line = create %s (%s.%s = $%s);
  commit $Line refresh;
  return $Line;
end;

/** "+ Add a line" on %s. */
create or modify microflow %s.ACT_%s_Add ($%s: %s)
folder '%s'
begin
  $Line = call microflow %s.SUB_%s_Add(%s = $%s);
end;
''' % (lshort, pname, lmod, lshort, pname, pq, ln['entity'], mf, D.qn(ln['entity']), lmod, ln['via'], pname,
       s['name'], lmod, lshort, pname, pq, mf, lmod, lshort, pname, pname))
    return out


def gen_page(name):
    s = U.S[name]
    if s['kind'] not in ('list', 'form', 'popup'):
        raise SystemExit('%s is a %s — hand-written, not generated' % (name, s['kind']))
    global WID_PREFIX
    WID_PREFIX = 'p' if s['kind'] == 'popup' else ''
    mod = module_of(s['entity']) if s['kind'] == 'list' or s.get('param') else module_of(s['entity'])
    folder = folder_of(mod, name)
    roles = module_roles_for(mod, s['roles'])
    out = ['mdl 1;', '-- GENERATED by pipelines/odoo/mdl_pages.py from ui_spec.py["%s"] — wireframe design/wireframes/%s.html.' % (name, name),
           '-- Regenerate, do not hand-edit. Reached from: %s.' % '; '.join(s['reached']), '']
    if s['kind'] == 'list':
        if s.get('editable'):
            out += row_save_microflows(s, folder)
        if s.get('editable') and s.get('add'):
            short = s['entity'].split('.')[1]
            mf = folder.replace('/Pages', '/Microflows')
            out.append('''/** A new %s row, committed so the list shows it at once. */
create or modify microflow %s.SUB_%s_Add ()
returns %s as $Row
folder '%s'
begin
  $Row = create %s ();
  commit $Row refresh;
  return $Row;
end;

/** "+ Add a line" on %s. */
create or modify microflow %s.ACT_%s_Add ()
folder '%s'
begin
  $Row = call microflow %s.SUB_%s_Add();
end;
''' % (short, mod, short, s['entity'], mf, D.qn(s['entity']), name, mod, short, mf, mod, short))
        body = gen_list(s)
        params = ''
        layout = 'Core.App_Default'
        url = ",\n  Url: '%s'" % U.route(name)
    else:
        popup = s['kind'] == 'popup'
        out += save_microflows(s, folder)
        out += line_add_microflows(s)
        out += child_add_microflows(s)
        inner, pname = gen_form(s, popup=popup)
        if s.get('singleton'):
            short = s['entity'].split('.')[1]
            ds = 'microflow %s.DS_%s_Get' % (mod, short)
            params = ''
            out.append('''/** Data source of %s: %s. */
create or modify microflow %s.DS_%s_Get ()
returns %s as $%s
folder '%s'
begin
  retrieve $%s from %s first;
  return $%s;
end;
''' % (name, s['singleton'], mod, short, s['entity'], short, folder.replace('/Pages', '/Microflows'), short, s['entity'], short))
        else:
            ds = '$%s' % pname
            params = '  Params: ( $%s: %s ),\n' % (pname, s['param'])
        body = ['  layoutgrid gridPage {', '    row {', '      column (DesktopWidth: 12) {',
                '  dataview dvMain (DataSource: %s) {' % ds] + inner + ['  }', '      }', '    }', '  }']
        layout = 'Atlas_Core.PopupLayout' if popup else 'Core.App_Default'
        url = ",\n  Url: '%s'" % U.route(name) if s.get('singleton') else ''
    out.append('/** %s — %s. */' % (esc(s['title']), name))
    out.append("create or modify page %s.%s folder '%s'\n(\n%s  Title: '%s',\n  Layout: %s%s\n)\n{" % (
        mod, name, folder, params, esc(s['title']), layout, url))
    out += body
    out.append('};')
    out.append('')
    if roles:
        out.append('grant view on page %s.%s to %s;' % (mod, name, ', '.join(roles)))
    called = set(re.findall(r'(?:call microflow|microflow) ((?:%s)\.(?:ACT_\w+|DS_\w+_Get))' % '|'.join(D.MODULES), '\n'.join(out)))
    for mf in sorted(m for m in called if m.startswith(mod + '.')):
        # the New microflow opens the form: only roles that may open the form get it, so Mendix hides New from the rest (C1-01)
        r = module_roles_for(mod, U.S[s['new']]['roles']) if mf == NEW_ACTION.get(name) else roles
        # a Reader role views the page read-only: it gets navigation (…_Open…) and data sources only, so Mendix hides the
        # page's state-changing buttons from it (sales users open a delivery from their order, 2026-10-15)
        r = [x for x in r if not x.endswith('.Reader') or re.search(r'_Open|\.DS_', mf)]
        # a selection button's microflow keeps the grant of the script that defines it (Register payment: Billing and
        # Manager only, though sales and purchase managers see the invoice list; Mendix then hides the button from them)
        if mf in LIST_SELECTION_BUTTON.values():
            continue
        if not r:
            continue
        out.append('grant execute on microflow %s to %s;' % (mf, ', '.join(r)))
        if mf == NEW_ACTION.get(name) and r != roles:
            out.append('revoke execute on microflow %s from %s;' % (mf, ', '.join(x for x in roles if x not in r)))
    return '\n'.join(out) + '\n'


def script_path(name):
    plan = open(os.path.join(ROOT, 'architecture/build-plan.md')).read()
    m = re.search(r'`(mdlsource/[^`]*?-page-%s\.mdl)`' % re.escape(re.sub(r'(?<!^)(?=[A-Z])', '-', name).replace('_-', '-').replace('_', '-').lower()), plan)
    if not m:
        raise SystemExit('no plan row names a page script for %s' % name)
    return done_aware(os.path.join(ROOT, m.group(1)))


def done_aware(path):
    """iterative-build-loop.md: a verified script is renamed done-<name>; regenerate into that file."""
    d, b = os.path.split(path)
    done = os.path.join(d, 'done-' + b)
    return done if os.path.exists(done) else path


def gen_nav():
    out = subprocess.run(['./mxcli', '-p', 'app/erpv1.mpr', '-c', 'LIST PAGES'], cwd=ROOT, capture_output=True, text=True).stdout
    have = set(re.findall(r'\| ([A-Za-z]+\.[A-Za-z_]+) +\|', out))
    icons = {'Sales': 'shopping-cart', 'Purchase': 'shipment-box', 'Inventory': 'hierarchy-files', 'Invoicing': 'euro',
             'Contacts': 'contacts', 'Products': 'tag', 'Reporting': 'analytics-bars', 'Configuration': 'cog'}
    groups = defaultdict(list)
    for g, label, scr in U.NAV:
        q = next((p for p in have if p.endswith('.' + scr)), None)
        if q:
            groups[g].append((label, q))
    L = ['mdl 1;', '-- 010-navigation.mdl — GENERATED by pipelines/odoo/mdl_pages.py --nav from ui_spec.NAV and the pages',
         '-- that exist in the model. The ONE owner of the Responsive profile (STOP 21). Mendix hides an item whose',
         '-- page the user cannot open, so role filtering follows the page grants.', 'create or modify navigation Responsive',
         '  home page Core.Home_Web']
    for role, scr in U.ROLE_HOME.items():
        q = next((p for p in have if p.endswith('.' + scr)), None)
        if q:
            L.append('  home page %s for %s' % (q, role))
    L.append('{')
    L.append("  menu item 'Home' ( OnClick: show page Core.Home_Web, Icon: Atlas_Core.Atlas.home )")
    seen = []
    for g, _, _ in U.NAV:
        if g in seen or not groups.get(g):
            continue
        seen.append(g)
        L.append("  menu '%s' ( Icon: Atlas_Core.Atlas.%s ) {" % (g, D.q(icons[g]) if '-' in icons[g] else icons[g]))
        for label, q in groups[g]:
            L.append("    menu item '%s' ( OnClick: show page %s, Icon: Atlas_Core.Atlas.%s )" % (esc(label), q, D.q(icons[g]) if '-' in icons[g] else icons[g]))
        L.append('  }')
    L.append('};')
    p = done_aware(os.path.join(ROOT, 'mdlsource/0-scaffold/010-navigation.mdl'))
    open(p, 'w').write('\n'.join(L) + '\n')
    print('wrote', os.path.relpath(p, ROOT), '(%d groups)' % len(seen))


def main(argv):
    if argv == ['--nav']:
        return gen_nav()
    for name in argv:
        p = script_path(name)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, 'w').write(gen_page(name))
        print('wrote', os.path.relpath(p, ROOT))
        for later in sorted({v for (pg, _c), v in DEFERRED_PAGE_BUTTONS.items() if pg == name}):
            global COMPLETE_PASS
            COMPLETE_PASS = True
            try:
                body = gen_page(name)
            finally:
                COMPLETE_PASS = False
            caps = ', '.join(c for (pg, c), v in DEFERRED_PAGE_BUTTONS.items() if pg == name and v == later)
            note = ('-- The complete %s, with %s: those open popups whose confirmation opens this page, so the first pass (%s)\n'
                    '-- leaves them out and this script, run after the popups, re-creates the page with them.\n') % (
                    name, caps, os.path.relpath(p, os.path.join(ROOT, 'mdlsource')))
            head, rest = body.split('\n', 1)
            lp = done_aware(os.path.join(ROOT, later))
            open(lp, 'w').write(head + '\n' + note + rest)
            print('wrote', os.path.relpath(lp, ROOT))


if __name__ == '__main__':
    main(sys.argv[1:])
