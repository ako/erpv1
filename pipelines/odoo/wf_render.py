#!/usr/bin/env python3
"""Render the Stage 3 design artifacts from ui_spec.py + the generated BRDs.

  design/wireframes/<Screen>.html   one per screen: wf-contract, ledger shell drawn as the screen's role,
                                    #/route navigation, data-bind on every control, table.bind
  design/wireframes/Home.html       prototype role picker (data-chrome)
  design/target-ui.md               UX pattern inventory + ## Screen Inventory
  design/interaction-model.md       role homes, inboxes, per-page contract, two-object two-role walk
  design/brand.md                   ledger basis, tokens, Atlas/theme mapping, decisions
  design/design-system.html         showcase of ds.css (light + dark)

Fails (exit 1) when a screen binds a member the domain model does not have, when a BRD page has no
screen, or when a navigation target does not exist.
Usage: wf_render.py [--kb analysis/odoo/knowledge-base] [--out design]
"""
import argparse, glob, html, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import brd_spec as SP      # noqa: E402
import brd_content as C    # noqa: E402
import ui_spec as U        # noqa: E402

E = html.escape
errors = []


route = U.route


# ── domain lookups ──────────────────────────────────────────────────────────────────────────
def load(kb):
    ents = {}
    for f in glob.glob(os.path.join(kb, 'brd', 'F*.brd.json')):
        for de in json.load(open(f))['domainEntities']:
            if de.get('extensionOf'):
                continue
            ents[de['name']] = de
    return ents


SAMPLE_TARGET = {
    'Partners.Partner': 'Azure Interior', 'Core.Country': 'Netherlands', 'Core.Currency': 'EUR', 'Core.Tax': 'VAT 21%',
    'Core.PaymentTerm': '30 days', 'Products.Pricelist': 'Public pricelist', 'Products.ProductCategory': 'All / Saleable / Office',
    'Products.Product': '[FURN_7800] Desk Combination', 'Products.UoM': 'Units', 'Products.UoMCategory': 'Unit', 'Products.ProductTag': 'Office',
    'Partners.PartnerTag': 'VIP', 'Administration.Account': 'Mitchell Admin', 'Sales.SalesTeam': 'Sales', 'Sales.QuotationTemplate': 'Office starter pack',
    'Sales.SalesOrder': 'S00042', 'Purchasing.PurchaseOrder': 'P00017', 'Inventory.Location': 'WH/Stock', 'Inventory.OperationType': 'Delivery orders',
    'Inventory.Transfer': 'WH/OUT/00030', 'Inventory.Warehouse': 'WH', 'Invoicing.Invoice': 'INV/2026/00020', 'Partners.BankAccount': 'NL91 ABNA 0417 1643 00',
    'Partners.UserProfile': 'Mitchell Admin', 'Inventory.ReorderRule': 'OP/00003',
}
ASSOC_SAMPLE = {'SalesOrder_DeliveryAddress': 'Azure Interior, Warehouse', 'SalesOrder_InvoiceAddress': 'Azure Interior, Accounts',
                'Transfer_SourceLocation': 'WH/Stock', 'Transfer_DestinationLocation': 'Partners/Customers', 'Transfer_SalesOrder': 'S00042',
                'Transfer_PurchaseOrder': '', 'Transfer_Backorder': '', 'Invoice_ReversalOf': '', 'Invoice_PurchaseOrder': '',
                'Partner_ParentCompany': '', 'PurchaseOrder_Vendor': 'Wood Corner', 'Transfer_Partner': 'Azure Interior',
                'Partner_Salesperson': 'Mitchell Admin', 'UserProfile_Partner': 'Mitchell Admin', 'ProductCategory_Parent': 'All / Saleable',
                'Warehouse_Address': 'YourCompany', 'Payment_Partner': 'Wood Corner', 'Invoice_SalesOrders': 'S00042'}


def member(ents, entity, name):
    e = ents.get(entity)
    if not e:
        errors.append('unknown entity %s' % entity)
        return None
    for at in e['attributes']:
        if at['name'] == name:
            return dict(at, kind='attr')
    for asc in e['associations']:
        if asc['name'] == name:
            return dict(asc, kind='assoc')
    errors.append('%s has no member %s' % (entity, name))
    return None


def caption(name):
    s = re.sub(r'^[A-Za-z]+_', '', name) if '_' in name else name
    s = s.replace('PurchaseUoM', 'PurchaseUnit').replace('UoMType', 'UnitType').replace('UoM', 'Unit')
    s = re.sub(r'(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])', ' ', s)
    return s[:1].upper() + s[1:].lower().replace('vat', 'VAT').replace('bic', 'BIC').replace('po ', 'PO ')


def enum_vals(enum):
    return [v[2] for v in SP.ENUMS[enum]['values']]


READONLY_PAT = re.compile(r'^(Amount(Untaxed|Tax|Total|Due)$|Subtotal|TaxAmount|Total$|Quantity(Delivered|Invoiced|Received|Billed|To)|Number$|Status$|InvoiceStatus|DeliveryStatus|'
                          r'ReceiptStatus|BillingStatus|PaymentStatus|ConfirmationDate|DateDone|FullName|ReservedQuantity|Locked$|AmountDue)')


def widget_for(m):
    if m is None:
        return 'Text box', 'String'
    if m['kind'] == 'assoc':
        return ('Combo box (reference set, tags)' if m['type'] == 'ReferenceSet' else 'Combo box (reference)'), m['target']
    t = m.get('type')
    if t == 'Enumeration':
        return 'Drop-down (enumeration)', m.get('enumeration')
    if t == 'Boolean':
        return 'Check box', 'Boolean'
    if t == 'DateTime':
        return 'Date picker', 'DateTime'
    if t in ('Decimal', 'Integer', 'Long'):
        return 'Text box (numeric)', t
    if t == 'String' and m.get('length') == 'unlimited':
        return 'Text area', 'String(unlimited)'
    return 'Text box', 'String' + ('(%s)' % m['length'] if m.get('length') else '')


def sample_value(m, name, sample):
    if name in sample:
        v = sample[name]
        return 'yes' if v is True else str(v)
    if m is None:
        return ''
    if m['kind'] == 'assoc':
        return ASSOC_SAMPLE.get(name, SAMPLE_TARGET.get(m['target'], ''))
    t = m.get('type')
    if t == 'Enumeration':
        return enum_vals(m['enumeration'])[0]
    if t == 'Boolean':
        return ''
    if t == 'DateTime':
        return '2026-10-14'
    if t == 'Decimal':
        return '0.00'
    if t == 'Integer':
        return '0'
    return ''


TONE = [(r'^(Sales order|Posted|Done|Paid|Fully|Purchase order|Ready|yes)', 'is-ok'), (r'^(To approve|Partially|Waiting|To invoice|Started)', 'is-warn'),
        (r'^(Cancelled|Not paid|Reversed|Late)', 'is-risk'), (r'^(Quotation sent|RFQ sent|Receive money|Send money)', 'is-info')]


def pill(v):
    for pat, cls in TONE:
        if re.match(pat, v):
            return '<span class="lg-pill %s">%s</span>' % (cls, E(v))
    return '<span class="lg-pill">%s</span>' % E(v)


class Binds:
    def __init__(self):
        self.rows = []

    def add(self, first, widget, source, required='', readonly='', cond='', rid=None):
        rid = rid or 'b%d' % (len(self.rows) + 1)
        self.rows.append((rid, first, widget, source, required, readonly, cond))
        return rid

    def table(self, title):
        out = ['<table class="bind"><caption>Bindings — %s</caption><thead><tr><th>Source field / element</th><th>Mendix widget</th>'
               '<th>Datasource</th><th>Required</th><th>Read-only</th><th>Conditional</th></tr></thead><tbody>' % E(title)]
        for rid, first, w, s, r, ro, c in self.rows:
            out.append('<tr id="%s" data-row="%s"><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' %
                       (rid, rid, E(first), E(w), E(s), E(r), E(ro), E(c)))
        out.append('</tbody></table>')
        return '\n'.join(out)


def field_html(ents, entity, name, sample, binds, readonly_page=False, cond=''):
    m = member(ents, entity, name)
    w, ds = widget_for(m)
    req = 'yes' if m and m.get('mandatory') else ''
    ro = readonly_page or bool(READONLY_PAT.match(name))
    src = '%s.%s' % (entity, name) + (' ← %s' % m['sourceOdoo'] if m and m.get('sourceOdoo') else ' (new)')
    rid = binds.add(src, w if not ro else 'Text (read-only)', ds, req, 'renders as text' if ro else '', cond)
    label = caption(name)
    val = sample_value(m, name, sample)
    fid = 'f-%s' % rid
    if ro:
        if m and m.get('type') == 'Boolean':
            val = 'Yes' if val == 'yes' else 'No'
        ctl = (pill(val) if (m and m.get('type') == 'Enumeration' and val) else E(val) or '—')
        ctl = '<div class="lg-readonly" id="%s" data-bind="%s">%s</div>' % (fid, rid, ctl)
    elif m and m['kind'] == 'assoc' and m['type'] == 'ReferenceSet':
        ctl = '<div class="lg-tags" id="%s" data-bind="%s">%s</div>' % (fid, rid, ''.join(pill(x) for x in [val] if x))
    elif w.startswith('Drop-down'):
        opts = ''.join('<option%s>%s</option>' % (' selected' if o == val else '', E(o)) for o in enum_vals(m['enumeration']))
        ctl = '<select class="lg-select" id="%s" data-bind="%s">%s</select>' % (fid, rid, opts)
    elif w.startswith('Combo'):
        ctl = '<select class="lg-select" id="%s" data-bind="%s"><option>%s</option></select>' % (fid, rid, E(val))
    elif w == 'Check box':
        ctl = '<input type="checkbox" class="lg-check" id="%s" data-bind="%s"%s>' % (fid, rid, ' checked' if val == 'yes' else '')
    elif w == 'Text area':
        ctl = '<textarea class="lg-textarea" id="%s" data-bind="%s">%s</textarea>' % (fid, rid, E(val))
    else:
        num = ' is-num' if 'numeric' in w else ''
        ctl = '<input class="lg-input%s" id="%s" data-bind="%s" value="%s">' % (num, fid, rid, E(val))
    return '<div class="lg-field"><label for="%s"%s>%s</label>%s</div>' % (fid, ' class="is-required"' if req and not ro else '', E(label), ctl)


def grid_html(ents, entity, cols, rows, binds, open_route=None, editable=False, title='', section_rows=True, add_bind=None):
    heads, nums = [], []
    for c in cols:
        m = member(ents, entity, c)
        w, ds = widget_for(m)
        isnum = m is not None and m['kind'] == 'attr' and m.get('type') in ('Decimal', 'Integer')
        nums.append(isnum)
        ro = (not editable) or bool(READONLY_PAT.match(c))
        binds.add('column %s.%s' % (entity, c) + (' ← %s' % m['sourceOdoo'] if m and m.get('sourceOdoo') else ''),
                  ('Data grid 2 column — ' + ('inline ' + w if not ro else 'text')), ds, '', 'yes' if ro else '', '')
        heads.append('<th%s>%s</th>' % (' class="is-num"' if isnum else '', E(caption(c))))
    body = []
    for r in rows:
        if r and r[0] == '(section)':
            body.append('<tr class="is-section"><td colspan="%d">%s</td></tr>' % (len(cols), E(r[1])))
            continue
        tds = []
        for i, v in enumerate(r):
            m = member(ents, entity, cols[i]) if i < len(cols) else None
            cell = E(v)
            if m and m['kind'] == 'attr' and m.get('type') == 'Enumeration' and v and cols[i] in ('Status', 'InvoiceStatus', 'DeliveryStatus', 'ReceiptStatus',
                                                                                                  'BillingStatus', 'PaymentStatus', 'Direction'):
                cell = pill(v)
            if i == 0 and open_route:
                cell = '<a class="lg-rowlink" href="#/%s">%s</a>' % (open_route, E(v))
            tds.append('<td%s>%s</td>' % (' class="is-num"' if nums[i] else '', cell))
        body.append('<tr>%s</tr>' % ''.join(tds))
    out = '<div class="lg-gridwrap"><table class="lg-table"><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (''.join(heads), ''.join(body))
    if add_bind:
        out += '<button class="lg-btn is-link lg-addline" data-bind="%s">+ Add a line</button>' % add_bind
    return out


def shell(role, active, title, inner, nav_screens):
    rail = ['<nav class="lg-rail" aria-label="Main menu"><div class="lg-appname">erpv1</div>']
    group = None
    for g, label, scr in U.NAV:
        if scr not in nav_screens or role not in U.S[scr]['roles']:
            continue
        if g != group:
            rail.append('<div class="lg-navgroup">%s</div>' % E(g))
            group = g
        rail.append('<a href="#/%s"%s>%s</a>' % (route(scr), ' class="is-active"' if scr == active else '', E(label)))
    rail.append('</nav>')
    top = ('<div class="lg-topbar"><span>%s</span><span>Signed in as <b>%s</b> · <a href="#/home">switch role (prototype)</a></span></div>'
           % (E(title), E(role)))
    return '<div class="lg-shell">%s<div class="lg-main">%s<main class="lg-content">%s</main></div></div>' % (''.join(rail), top, inner)


def button(label, target, binds, primary=False, entity=''):
    cls = 'lg-btn' + (' is-primary' if primary else '') + (' is-danger' if label in ('Cancel', 'Reject') else '')
    if target == 'save':
        rid = binds.add('Save — commit object and close page', 'Action button (Save changes)', entity, '', '', '')
        return '<button class="%s" data-bind="%s">%s</button>' % (cls, rid, E(label))
    if target in U.S or target == 'Home':
        return '<a class="%s" href="#/%s">%s</a>' % (cls, route(target), E(label))
    rid = binds.add('%s — microflow %s' % (label, target), 'Action button (call microflow)', target, '', '', '')
    return '<button class="%s" data-bind="%s">%s</button>' % (cls, rid, E(label))


def render(scr, ents, nav_screens):
    s = U.S[scr]
    binds = Binds()
    role = s['roles'][0]
    entity = s['entity']
    sample = s.get('sample', {})
    title = s['title']
    param = s.get('param')
    if param:
        param_line = param
    elif s.get('singleton'):
        param_line = 'none — singleton'
    elif s['kind'] in ('list', 'report', 'inbox', 'dashboard'):
        param_line = 'none — list page' if s['kind'] in ('list', 'inbox') else 'none — %s' % ('report' if s['kind'] == 'report' else 'home')
    else:
        param_line = 'none'
    source = s.get('source') or ('page parameter' if param else s.get('singleton') or 'database %s' % entity)
    contract = ('<div class="wf-contract"><p>Page parameter: %s</p><p>Reached from: %s</p><p>Drawn as role: %s</p><p>Data view source: %s</p>%s</div>'
                % (E(param_line), E('; '.join(s['reached'])), E(role), E(source),
                   '<p>Row-level access: %s</p>' % E(s['xpath']) if s.get('xpath') else ''))
    parts = []
    k = s['kind']
    if k in ('list', 'inbox'):
        acts = []
        if s.get('new'):
            acts.append('<a class="lg-btn is-primary" href="#/%s">New</a>' % route(s['new']))
        for lbl, tgt in s.get('buttons', []):
            acts.append(button(lbl, tgt, binds, entity=entity))
        parts.append('<div class="lg-pagehead"><h1>%s</h1><div class="lg-actions">%s</div></div>' % (E(title), ''.join(acts)))
        if s.get('tabs'):
            parts.append('<div class="lg-tabs">%s</div>' % ''.join('<a href="#/%s"%s>%s</a>' % (route(scr), ' class="is-active"' if i == 0 else '', E(t))
                                                                   for i, t in enumerate(s['tabs'])))
            binds.add('tabs: %s' % ', '.join(s['tabs']), 'Tab container, one Data grid 2 per tab (XPath on status/type)', entity, '', '', '')
        if s.get('filters'):
            fl = ['<input class="lg-input" placeholder="Search…" aria-label="Search">']
            for f in s['filters']:
                m = member(ents, entity, f)
                fl.append('<select class="lg-select" aria-label="%s"><option>%s: all</option></select>' % (E(caption(f)), E(caption(f))))
            binds.add('filters: %s' % ', '.join(s['filters']), 'Data grid 2 header filters (text, enumeration, association)', entity, '', '', '')
            parts.append('<div class="lg-filters">%s</div>' % ''.join(fl))
        parts.append(grid_html(ents, entity, s['columns'], s['rows'], binds, route(s['open']) if s.get('open') else None, s.get('editable', False)))
        parts.append('<div class="lg-pager">1–%d of %d</div>' % (len(s['rows']), len(s['rows'])))
        if k == 'inbox':
            parts.insert(0, '<div class="lg-note">Workflow Commons task inbox (marketplace) — rows are user tasks of WF_PurchaseOrderApproval assigned to you.</div>')
    elif k in ('form', 'task'):
        if s.get('statusbar') or s.get('buttons'):
            acts = []
            cur = s['statusbar'][2] if s.get('statusbar') else None
            shown = [b for b in s.get('buttons', []) if len(b) < 3 or cur in b[2]]
            for b in s.get('buttons', []):
                if len(b) == 3 and cur not in b[2]:
                    binds.add('%s — microflow %s (hidden in this state)' % (b[0], b[1]), 'Action button (call microflow)', b[1], '', '',
                              'visible when %s in: %s' % (s['statusbar'][0], ', '.join(b[2])), rid='h%d' % (len(binds.rows) + 1))
            for i, b in enumerate(shown):
                acts.append(button(b[0], b[1], binds, primary=(i == 0), entity=entity))
                if len(b) == 3:
                    binds.rows[-1] = binds.rows[-1][:6] + ('visible when %s in: %s' % (s['statusbar'][0], ', '.join(b[2])),)
            sb = ''
            if s.get('statusbar'):
                fld, steps, cur = s['statusbar']
                binds.add('%s.%s (status bar)' % (entity, fld), 'Text (read-only) — status steps via enumeration', s['statusbar'][0], '', 'yes',
                          'buttons shown per status (see BRD use cases)')
                sb = '<div class="lg-statusbar" aria-label="Status">%s</div>' % ''.join(
                    '<span%s>%s</span>' % (' class="is-current"' if st == cur else '', E(st)) for st in steps)
            parts.append('<div class="lg-toolbar"><div class="lg-actions">%s</div>%s</div>' % (''.join(acts), sb))
        head_val = sample.get(s.get('header', ''), SAMPLE_TARGET.get(entity, ''))
        head = '<div class="lg-pagehead"><div><div class="lg-eyebrow">%s</div><h1 class="lg-docno">%s</h1></div>%s</div>' % (
            E(title), E(head_val or title), pill(sample_value(member(ents, entity, s['badge']), s['badge'], sample)) if s.get('badge') else '')
        if s.get('header'):
            m = member(ents, entity, s['header'])
            binds.add('%s.%s (title)' % (entity, s['header']) + (' ← %s' % m['sourceOdoo'] if m and m.get('sourceOdoo') else ''),
                      'Text (read-only)', 'String', '', 'yes', 'empty while draft (number assigned on save/post)')
        parts.append(head)
        if s.get('smart'):
            parts.append('<div class="lg-smart">%s</div>' % ''.join('<a href="#/%s"><b>%s</b>%s</a>' % (route(t), E(n), E(l)) for l, t, n in s['smart']))
            binds.add('smart buttons: %s' % ', '.join(l for l, t, n in s['smart']), 'Action buttons with count (microflow GET_ count + show page)',
                      entity, '', '', 'hidden when count = 0')
        sheet = []
        if s.get('image'):
            rid = binds.add('Products.ProductImage (System.Image)', 'Image uploader', 'ProductImage_Product', '', '', '')
            sheet.append('<div class="lg-image" data-bind="%s">image</div>' % rid)
        secs = s.get('sections', [])
        pairs = [secs[i:i + 2] for i in range(0, len(secs), 2)]
        for pair in pairs:
            sheet.append('<div class="lg-grid2">')
            for title2, fields in pair:
                sheet.append('<section class="lg-section"><h2>%s</h2>%s</section>' % (
                    E(title2), ''.join(field_html(ents, entity, f, sample, binds, readonly_page=s.get('readonly', False) or k == 'task') for f in fields)))
            sheet.append('</div>')
        if s.get('links'):
            sheet.append('<p>%s</p>' % ' · '.join('<a href="#/%s">%s</a>' % (route(t), E(l)) for l, t in s['links']))
        ln = s.get('lines')
        if ln:
            add = None
            if s.get('lines_locked'):
                binds.add('Add a line (%s)' % ln['entity'], 'Action button (create object, inline edit)', ln['entity'], '', '', 'only while Status = Draft (hidden here: posted)', rid='h-add')
            elif ln.get('editable', True) and k != 'task' and not s.get('readonly'):
                add = binds.add('Add a line (%s)' % ln['entity'], 'Action button (create object, inline edit)', ln['entity'], '', '',
                                'hidden when document locked / not draft')
            if ln.get('onchange'):
                binds.add('on change product → microflow %s' % ln['onchange'], 'Grid cell OnChange', ln['onchange'], '', '', '')
            if ln.get('recompute'):
                binds.add('after line change → microflow %s' % ln['recompute'], 'Grid cell OnChange', ln['recompute'], '', '', '')
            sheet.append('<section class="lg-section"><h2>%s</h2>%s</section>' % (
                E(ln['title']), grid_html(ents, ln['entity'], ln['columns'], ln['rows'], binds, route(ln['open']) if ln.get('open') else None,
                                          ln.get('editable', True) and k != 'task', add_bind=add)))
            binds.add('lines datasource: %s over %s' % (ln['entity'], ln['via']), 'Data grid 2', 'association %s' % ln['via'], '', '', '')
        if s.get('totals'):
            tot = []
            for i, t in enumerate(s['totals']):
                m = member(ents, entity, t)
                binds.add('%s.%s' % (entity, t) + (' ← %s' % m['sourceOdoo'] if m and m.get('sourceOdoo') else ''), 'Text (read-only, currency)',
                          'Decimal', '', 'yes', 'recomputed by microflow on line change')
                tot.append('<div%s><span>%s</span><span>%s</span></div>' % (' class="is-grand"' if t == 'AmountTotal' else '', E(caption(t)),
                                                                            {'AmountUntaxed': '1 044.00', 'AmountTax': '219.24', 'AmountTotal': '1 263.24',
                                                                             'AmountDue': '1 263.24'}.get(t, '0.00')))
            sheet.append('<div class="lg-totals">%s</div>' % ''.join(tot))
        if s.get('notes'):
            sheet.append(field_html(ents, entity, s['notes'], sample, binds))
        if s.get('reason'):
            rid = binds.add('Reject reason (workflow task outcome comment)', 'Text area (required for Reject)', 'WF_PurchaseOrderApproval', 'for Reject', '', '')
            sheet.append('<div class="lg-field"><label for="reason">Reason (required to reject)</label><textarea class="lg-textarea" id="reason" data-bind="%s"></textarea></div>' % rid)
        parts.append('<div class="lg-sheet">%s</div>' % ''.join(sheet))
        for pop in s.get('popups', []) + ([s['popup']] if s.get('popup') else []):
            parts.append('<p class="wf-notes">Opens popup <a href="#/%s">%s</a></p>' % (route(pop), E(pop)))
    elif k == 'popup':
        body = []
        if s.get('message'):
            body.append('<div class="lg-note">%s</div>' % E(s['message']))
        for title2, fields in s.get('sections', []):
            body.append('<section class="lg-section"><h2>%s</h2>%s</section>' % (E(title2), ''.join(field_html(ents, entity, f, sample, binds) for f in fields)))
        btns = ''.join(button(l, t, binds, primary=(i == 0), entity=entity) for i, (l, t) in enumerate(s.get('buttons', [])))
        btns += '<a class="lg-btn" href="#/%s">%s</a>' % (route(s.get('back', 'Home')), 'Discard')
        dialog = '<div class="lg-backdrop"><div class="lg-dialog" role="dialog" aria-label="%s"><header><h1>%s</h1></header><div class="lg-dialog-body">%s</div><footer>%s</footer></div></div>' % (
            E(title), E(title), ''.join(body), btns)
        return contract, dialog, binds
    elif k == 'report':
        parts.append('<div class="lg-pagehead"><h1>%s</h1></div>' % E(title))
        parts.append('<div class="lg-kpis">%s</div>' % ''.join('<div class="lg-kpi"><div class="lg-kpi-label">%s</div><div class="lg-kpi-value">%s</div></div>'
                                                            % (E(l), E(v)) for l, v in s['kpis']))
        binds.add('KPIs: %s' % ', '.join(l for l, v in s['kpis']), 'Text (aggregates over view entity)', entity, '', 'yes', '')
        parts.append('<div class="lg-charts">%s</div>' % ''.join(
            '<div class="lg-chart"><h3>%s</h3><div class="lg-chart-bars">%s</div></div>' % (E(c), ''.join('<i style="height:%d%%"></i>' % h for h in (40, 62, 55, 80, 71, 90)))
            for c in s['charts']))
        binds.add('charts: %s' % ', '.join(s['charts']), 'Charts (marketplace) — series colours from dataviz palette', entity, '', 'yes', '')
        cols = s['columns']
        parts.append('<div class="lg-gridwrap"><table class="lg-table"><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (
            ''.join('<th>%s</th>' % E(c) for c in cols), ''.join('<tr>%s</tr>' % ''.join('<td>%s</td>' % E(v) for v in r) for r in s['rows'])))
        binds.add('grid over view entity %s: %s' % (entity, ', '.join(cols)), 'Data grid 2 with filters + export', 'OQL view entity %s' % entity, '', 'yes', '')
    elif k == 'dashboard':
        parts.append('<div class="lg-pagehead"><h1>%s</h1></div>' % E(title))
        tiles = []
        for name, code, counts in s['tiles']:
            tiles.append('<div class="lg-tile"><div class="lg-eyebrow">%s</div><h2>%s</h2><div class="lg-counts">%s</div></div>' % (
                E(code), E(name), ''.join('<a href="#/%s"><b>%s</b>%s</a>' % (route(s['open']), E(n), E(l)) for l, n in counts)))
        binds.add('tile per Inventory.OperationType: counts of Transfers by Status (Ready / Waiting / Late)', 'List view of operation types + count microflows',
                  'database Inventory.OperationType', '', 'yes', '')
        parts.append('<div class="lg-tiles">%s</div>' % ''.join(tiles))
    return contract, shell(role, scr if scr in nav_screens else None, title, ''.join(parts), nav_screens), binds


def page_doc(title, rt, body, extra_attr=''):
    return ('<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">\n'
            '<title>%s — wireframe</title><link rel="stylesheet" href="../ds.css"></head>\n<body class="lg-body" data-route="%s"%s>\n%s\n</body></html>\n'
            % (E(title), rt, extra_attr, body))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--kb', default='analysis/odoo/knowledge-base')
    ap.add_argument('--out', default='design')
    a = ap.parse_args()
    ents = load(a.kb)
    nav_screens = {scr for g, l, scr in U.NAV}
    for g, l, scr in U.NAV:
        if scr not in U.S:
            errors.append('nav item %s -> unknown screen %s' % (l, scr))
    # every BRD page has a screen (except marketplace pages)
    brd_pages = {p['name']: f for f, b in C.BRDS.items() for p in b['pages'] if p['pattern'] != 'extension'}
    for p in brd_pages:
        if p not in U.S:
            errors.append('BRD page %s has no screen in ui_spec' % p)
    for scr, s in U.S.items():
        if scr not in brd_pages:
            errors.append('screen %s is not a BRD page' % scr)
        for key in ('open', 'new', 'back', 'popup'):
            if s.get(key) and s[key] not in U.S and s[key] != 'Home':
                errors.append('%s.%s -> unknown screen %s' % (scr, key, s[key]))
    wdir = os.path.join(a.out, 'wireframes')
    os.makedirs(wdir, exist_ok=True)
    for f in glob.glob(os.path.join(wdir, '*.html')):
        os.remove(f)
    summary = []
    for scr in U.S:
        contract, body, binds = render(scr, ents, nav_screens)
        doc = page_doc(U.S[scr]['title'], route(scr), contract + '\n' + body + '\n' + binds.table(scr))
        open(os.path.join(wdir, scr + '.html'), 'w').write(doc)
        summary.append((scr, len(binds.rows)))
    # Home: prototype role picker
    roles = list(U.ROLE_HOME)
    items = ''.join('<a class="lg-tile" href="#/%s"><div class="lg-eyebrow">%s</div><h2>%s</h2><p>Lands on %s</p></a>' % (
        route(U.ROLE_HOME[r]), E(r), E({'SalesUser': 'Sales user', 'SalesManager': 'Sales manager', 'Purchaser': 'Purchaser',
                                       'PurchaseManager': 'Purchase manager', 'InventoryUser': 'Warehouse user', 'InventoryManager': 'Inventory manager',
                                       'Billing': 'Billing clerk', 'InvoicingManager': 'Invoicing manager', 'Administrator': 'Administrator'}[r]),
        E(U.S[U.ROLE_HOME[r]]['title'])) for r in roles)
    home = ('<div class="wf-contract"><p>Page parameter: none — home</p><p>Reached from: prototype start; "switch role" link on every screen</p>'
            '<p>Drawn as role: (prototype only)</p><p>Data view source: none</p></div>'
            '<main class="lg-content"><div class="lg-pagehead"><h1>erpv1 prototype — choose a role</h1></div>'
            '<p>Odoo-inspired ERP POC on Mendix 11.15, ledger theme. Each role opens on its home page (design/interaction-model.md).</p>'
            '<div class="lg-tiles">%s</div></main>' % items)
    open(os.path.join(wdir, 'Home.html'), 'w').write(page_doc('Choose a role', 'home', home, ' data-chrome="prototype role picker — not an app page"'))

    # target-ui.md
    tu = ['# Target UI — erpv1', '', 'Generated by `pipelines/odoo/wf_render.py` from `ui_spec.py`; edit the spec, not this file.', '',
          '## UX patterns (Odoo web client → Mendix / Atlas under the ledger theme)', '',
          '| Odoo pattern | Mendix implication | Constraint |', '|---|---|---|',
          '| List view with search panel, filters, group-by | Data Grid 2 with header filters; tabs for status sets | one main grid per page (interaction-model rule 4) |',
          '| Form view with header buttons + statusbar | Action buttons in a toolbar row; read-only status steps from the enumeration | buttons visible per status (BRD use cases) |',
          '| Smart buttons (Delivery 1, Invoices 2) | Action buttons with a count, microflow opens the related object | hidden when count is 0 |',
          '| Editable one2many lines (order lines, sections/notes) | Data Grid 2 inline editing over the association; LineType drives section/note rows | totals recomputed by microflow |',
          '| Many2one / many2many widgets | Combo box (reference / reference set) | many2many tags → combo box with tags |',
          '| Wizards (create invoice, register payment, backorder, credit note) | Popup pages over non-persistent entities | Discard closes without commit |',
          '| Kanban dashboards (inventory overview) | Tile list over OperationType with counts | — |',
          '| Pivot / graph analyses | Report page: KPIs + Charts + Data Grid 2 over an OQL view entity | no pivot engine (Q-F004-3) |',
          '| Activity / approval (to approve) | Workflow Commons task inbox + user-task page | WF_PurchaseOrderApproval |',
          '| Chatter, email composer, portal | not implemented (Stage 0) | — |', '',
          '## Screen Inventory', '', '| Screen | Basis | Notes |', '|---|---|---|']
    for scr, s in U.S.items():
        tu.append('| %s | DESIGN FROM BRD | %s; Odoo views %s |' % (scr, s['kind'], ', '.join(
            next((p['odooRefs'] for b in C.BRDS.values() for p in b['pages'] if p['name'] == scr), [])) or '—'))
    tu.append('| Account_Overview | Buy | reuses the Administration module page (marketplace); no wireframe |')
    tu.append('| Home | GENERATIVE | prototype role picker (data-chrome), not built in the app |')
    open(os.path.join(a.out, 'target-ui.md'), 'w').write('\n'.join(tu) + '\n')

    # interaction-model.md
    im = ['# Interaction model — erpv1', '', 'Generated by `pipelines/odoo/wf_render.py` (skills/interaction-model.md). Edit `ui_spec.py`.', '',
          '## 1. Role homes', '', '| Role | Home page | Comes to do |', '|---|---|---|']
    todo = {'SalesUser': 'Quote and follow own orders', 'SalesManager': 'Follow all orders, lock, templates, teams', 'Purchaser': 'Create RFQs and follow POs',
            'PurchaseManager': 'Approve purchase orders waiting for them', 'InventoryUser': 'Process ready receipts and deliveries',
            'InventoryManager': 'Configure warehouse, counts, reorder rules', 'Billing': 'Invoice, post, register payments',
            'InvoicingManager': 'Taxes, payment terms, receivables', 'Administrator': 'Company, users, numbering'}
    for r, h in U.ROLE_HOME.items():
        im.append('| %s | `%s` | %s |' % (r, h, todo[r]))
    im += ['', 'Homes differ per role area (sales, purchase, approval inbox, inventory, invoicing, admin) — no shared home.', '',
           '## 2. Inboxes and object hubs', '', '| User task / approval | Role | Inbox | Grouping | Row opens |', '|---|---|---|---|---|',
           '| WF_PurchaseOrderApproval "Approve purchase order" | PurchaseManager | `PurchaseApproval_Inbox` (Workflow Commons) | oldest deadline first | `PurchaseApproval_Task` with its Purchasing.PurchaseOrder |',
           '', 'Object hubs (followed over time; process steps are buttons on the hub, never menu items): `SalesOrder_NewEdit`, `PurchaseOrder_NewEdit`, '
           '`Transfer_NewEdit`, `Invoice_NewEdit` (status bar + actions + smart buttons to the related documents).', '',
           '## 3. Per-page contract', '', '| Page | How reached | Page parameter / context object | Data view source | Nav entry | Role(s) |',
           '|---|---|---|---|---|---|']
    nav_label = {scr: '%s › %s' % (g, l) for g, l, scr in U.NAV}
    for scr, s in U.S.items():
        if s.get('param'):
            p = s['param']
        elif s.get('singleton'):
            p = 'none — singleton'
        elif s['kind'] in ('list', 'inbox'):
            p = 'none — list page'
        else:
            p = 'none — %s' % ('report' if s['kind'] == 'report' else 'home')
        src = s.get('source') or ('page parameter' if s.get('param') else s.get('singleton') or 'grid: database %s' % s['entity'])
        if s.get('param') and scr in nav_label:
            errors.append('%s takes a parameter but is in the menu (interaction-model rule 2)' % scr)
        im.append('| `%s` | %s | %s | %s | %s | %s |' % (scr, '; '.join(s['reached']), p, src, nav_label.get(scr, '—'), ', '.join(s['roles'])))
    im += ['', '## 4. Walk with two objects and two roles (paper walk over the wireframes, 2026-10-14)', '',
           'Seeded objects in the wireframes: S00042 / S00043, P00018 / P00017 (P00016 also waiting), WH/OUT/00031 / WH/IN/00012, INV/2026/00021 / INV/2026/00020.', '',
           '- **SalesUser (Marc Demo)** → home `SalesOrder_Overview` → row **S00043** (second object) → `SalesOrder_NewEdit(S00043)` → Confirm. The page parameter is the clicked order; the grid is limited to own orders by XPath.',
           '- **PurchaseManager** → home `PurchaseApproval_Inbox` → row **P00016** (second waiting task) → `PurchaseApproval_Task(P00016)` → Approve → `SUB_PurchaseOrder_Approve` for that order. "Open order" passes P00016 to `PurchaseOrder_NewEdit`.',
           '- **InventoryUser** → home `Inventory_Dashboard` → Delivery orders · Waiting → `Transfer_Overview` → row **WH/IN/00012** → `Transfer_NewEdit(WH/IN/00012)` → Validate → `ValidateTransfer_Popup` for that transfer.',
           '- **Billing** → home `Invoice_Overview` → row **INV/2026/00020** (partially paid) → `Invoice_NewEdit(INV/2026/00020)` → Register payment → `RegisterPayment_Popup` with that invoice.',
           '', 'No route passes through "the first record" or a menu stage: every object page is reached from a row, a smart button or a popup caller that holds the object.', '',
           '## Done when', '', '- Role homes: %d of %d roles.' % (len(U.ROLE_HOME), len(U.ROLE_HOME)),
           '- Inboxes: 1 of 1 user task (WF_PurchaseOrderApproval).', '- Per-page table: %d of %d screens (+ Account_Overview reused from Administration, Home prototype chrome).' % (len(U.S), len(U.S)),
           '- Walk: 4 roles, second object each (above).']
    open(os.path.join(a.out, 'interaction-model.md'), 'w').write('\n'.join(im) + '\n')

    for scr, n in summary:
        pass
    print('wireframes: %d (+ Home), bindings: %d rows' % (len(summary), sum(n for _, n in summary)))
    if errors:
        print('ERRORS (%d):' % len(errors))
        for e in sorted(set(errors)):
            print('  - ' + e)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
