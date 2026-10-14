#!/usr/bin/env python3
"""Stage 3 architecture artifacts (architecture-blueprint.md Steps 1–4, 7), generated from the confirmed design.

  architecture/modules/<Module>/definition.md   Step 1
  architecture/blueprint.md                     Steps 2, 3, 3b, 3d + security + NFRs (Mermaid, the source of truth)
  architecture/fit-gap.md                       Step 4
  architecture/blueprint.html                   Step 7 render (diagrams pre-rendered to inline SVG with mermaid-cli)

Usage: arch_blueprint.py [--kb analysis/odoo/knowledge-base] [--out architecture] [--no-svg]
"""
import argparse, glob, html, json, os, re, subprocess, sys, tempfile
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import brd_spec as S      # noqa: E402
import brd_content as C   # noqa: E402
import ui_spec as U       # noqa: E402
from arch_render import RATIONALE  # noqa: E402

LAYER = {'Core': 'Common', 'Products': 'Common (master data)', 'Partners': 'Common (master data)', 'Sales': 'Domain + Logic',
         'Purchasing': 'Domain + Logic', 'Inventory': 'Domain + Logic (downstream)', 'Invoicing': 'Domain + Logic (downstream)'}
MODULE_ROLES = {  # module role -> user roles (Q-F001-2)
    'Core': {'Admin': ['Administrator'], 'Config': ['InvoicingManager'], 'Reader': ['SalesUser', 'SalesManager', 'Purchaser', 'PurchaseManager',
                                                                                    'InventoryUser', 'InventoryManager', 'Billing']},
    'Products': {'Manager': ['SalesManager', 'PurchaseManager', 'InventoryManager', 'Administrator'],
                 'Reader': ['SalesUser', 'Purchaser', 'InventoryUser', 'Billing', 'InvoicingManager']},
    'Partners': {'Editor': ['SalesUser', 'SalesManager', 'Purchaser', 'PurchaseManager', 'Billing', 'InvoicingManager'], 'Admin': ['Administrator'],
                 'Reader': ['InventoryUser', 'InventoryManager']},
    'Sales': {'User': ['SalesUser'], 'Manager': ['SalesManager'], 'Reader': ['Billing', 'InvoicingManager', 'InventoryUser', 'InventoryManager']},
    'Purchasing': {'User': ['Purchaser'], 'Manager': ['PurchaseManager'], 'Reader': ['Billing', 'InvoicingManager', 'InventoryUser', 'InventoryManager']},
    'Inventory': {'User': ['InventoryUser'], 'Manager': ['InventoryManager', 'Administrator'], 'Reader': ['SalesUser', 'SalesManager', 'Purchaser', 'PurchaseManager']},
    'Invoicing': {'Billing': ['Billing'], 'Manager': ['InvoicingManager'], 'Creator': ['SalesUser', 'SalesManager', 'Purchaser', 'PurchaseManager']},
}
FITGAP = [
    ('Odoo res.users / res.groups / login', 'Administration module accounts + 9 user roles mapped to module roles', 'Buy', 'Administration (marketplace)'),
    ('Odoo web client shell, menus, list/form views', 'Atlas Core layouts + side-rail navigation; pages per ui_spec', 'Native', '—'),
    ('Look & feel', 'mxcli theme "ledger" (`mxcli theme apply ledger`)', 'Config', '—'),
    ('List views with filters / group-by / search panel', 'Data Grid 2 with header filters, tabs per status', 'Buy', 'Data Widgets (marketplace)'),
    ('Editable one2many lines with sections/notes', 'Data Grid 2 inline editing + LineType enumeration + OnChange microflows', 'Build', '—'),
    ('Pivot / graph analyses (sale.report, purchase.report, account.invoice.report, report.stock.quantity)',
     '4 OQL view entities + report pages with Charts and Data Grid 2', 'Build + Buy', 'Charts (marketplace)'),
    ('Purchase double validation (state "to approve")', 'Mendix workflow WF_PurchaseOrderApproval + user-task inbox', 'Native + Buy', 'Workflow Commons (marketplace)'),
    ('ir.sequence numbering', 'Core.Sequence + SUB_Sequence_NextNumber', 'Build', '—'),
    ('ir.cron (reorder scheduler)', 'Scheduled event calling SCE_ReorderRules_Run (daily)', 'Native', '—'),
    ('Seed data (UoM, currencies, countries, chart of taxes, sequences)', 'After-startup microflow ASU_Core_SeedData from KB seedData.json', 'Build', '—'),
    ('ir.rule record rules (own documents)', 'XPath entity access constraints per module role', 'Native', '—'),
    ('Computed stored fields (amounts, statuses)', 'Stored attributes recomputed by SUB_* microflows on change', 'Build (changed behaviour)', 'recomputation is explicit, not ORM-triggered'),
    ('Tax computation (account.tax compute_all)', 'SUB_Tax_ComputeLine: percentage/fixed, included/excluded, per-line rounding', 'Build (simplified)', 'Q-F008-1, simplifications in F008'),
    ('Procurement / stock rules / routes', 'Explicit bridge microflows SUB_SalesOrder_CreateDelivery / SUB_PurchaseOrder_CreateReceipt', 'Build (changed behaviour)', 'single warehouse, one step (Q-F006-1)'),
    ('Reconciliation of journal items', 'Invoicing.PaymentAllocation', 'Build (changed behaviour)', 'no ledger (Q-F008-1)'),
    ('Product images (image.mixin)', 'Products.ProductImage specialization of System.Image + image uploader', 'Native', '—'),
    ('Wizards (create invoice, register payment, backorder, credit note)', 'Popup pages over non-persistent entities', 'Native', '—'),
    ('Email / chatter / activities (mail)', '—', 'Gap — declared not implemented', 'Stage 0 decision'),
    ('Customer portal, online payment, EDI, barcodes', '—', 'Gap — declared not implemented', 'Stage 0 decision'),
    ('Quote / invoice PDF (QWeb)', 'On-screen documents only', 'Gap — deferred', 'Q-F004-1, Q-F008-3'),
    ('Light/dark switch', 'Follows OS (theme --variant auto); optional `mxcli theme switcher install`', 'Config', '—'),
]
JOURNEYS = [
    ('J-01', 'Quote → order → delivery → invoice → payment', ['SalesUser', 'InventoryUser', 'Billing'], ['Sales', 'Inventory', 'Invoicing', 'Partners', 'Products', 'Core'],
     """sequenceDiagram
  participant SU as SalesUser
  participant IU as InventoryUser
  participant BI as Billing
  SU->>SU: create quotation S00043 (pricelist price, taxes)
  SU->>SU: mark as sent, confirm
  SU->>IU: delivery WH/OUT created (SUB_SalesOrder_CreateDelivery)
  IU->>IU: check availability, validate (backorder?)
  IU-->>SU: delivered quantities + delivery status updated
  SU->>BI: create invoice (to invoice)
  BI->>BI: post INV/2026/000nn
  BI->>BI: register payment (partial or full)"""),
    ('J-02', 'RFQ → approval → receipt → vendor bill', ['Purchaser', 'PurchaseManager', 'InventoryUser', 'Billing'], ['Purchasing', 'Inventory', 'Invoicing'],
     """sequenceDiagram
  participant PU as Purchaser
  participant PM as PurchaseManager
  participant IU as InventoryUser
  participant BI as Billing
  PU->>PU: create RFQ P00018 (vendor prices)
  PU->>PM: confirm above threshold → approval task
  PM-->>PU: reject with reason (back to RFQ)
  PM->>IU: approve → receipt WH/IN created
  IU->>IU: validate receipt
  IU-->>PU: received quantities + receipt status
  PU->>BI: create bill from PO
  BI->>BI: post bill, register outgoing payment"""),
    ('J-03', 'Stock below minimum → automatic RFQ', ['InventoryManager', 'Purchaser'], ['Inventory', 'Purchasing'],
     """sequenceDiagram
  participant SCH as Scheduler
  participant IM as InventoryManager
  participant PU as Purchaser
  IM->>IM: maintain reorder rule (min/max, vendor)
  SCH->>SCH: SCE_ReorderRules_Run (daily)
  SCH->>PU: RFQ created/extended for the vendor (source = rule)
  PU->>PU: continue as J-02"""),
    ('J-04', 'Credit note for a posted invoice', ['Billing', 'InvoicingManager'], ['Invoicing'],
     """sequenceDiagram
  participant BI as Billing
  participant IM as InvoicingManager
  BI->>BI: credit note (reason, date) from posted invoice
  BI->>BI: post credit note → allocated to original
  IM->>IM: follow receivables in invoice analysis"""),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--kb', default='analysis/odoo/knowledge-base')
    ap.add_argument('--out', default='architecture')
    ap.add_argument('--no-svg', action='store_true')
    a = ap.parse_args()
    graph = json.load(open(os.path.join(a.kb, 'brd', 'module-graph.json')))
    brds = [json.load(open(f)) for f in sorted(glob.glob(os.path.join(a.kb, 'brd', 'F*.brd.json')))]
    ents = {}
    mfs = {m: [] for m in S.MODULES}
    for b in brds:
        for de in b['domainEntities']:
            if not de.get('extensionOf'):
                ents[de['name']] = de
        for m in b['microflows'] + b.get('workflows', []):
            if m.get('module') in mfs and m['name'] not in [x['name'] for x in mfs[m['module']]]:
                mfs[m['module']].append(m)
    pages = {m: [] for m in S.MODULES}
    for scr, s in U.S.items():
        pages[s['entity'].split('.')[0]].append(scr)

    # Step 1: module definitions
    for mod in S.MODULES:
        d = os.path.join(a.out, 'modules', mod)
        os.makedirs(d, exist_ok=True)
        L = ['# Module: %s' % mod, '**Layer:** %s' % LAYER[mod], '**Responsibility:** %s' % RATIONALE[mod]['mission'], '',
             '_Generated by `pipelines/odoo/arch_blueprint.py` from the confirmed BRDs; edit brd_spec.py / brd_content.py / ui_spec.py._', '',
             '## Entities', '', '| Entity | Persistent? | Key attributes | Notes |', '|---|---|---|---|']
        for n, e in ents.items():
            if e['module'] != mod:
                continue
            key = ', '.join(x['name'] for x in e['attributes'][:6])
            L.append('| %s | %s | %s | %s |' % (n.split('.')[1], 'yes' if e['persistent'] else 'no (non-persistent)', key,
                                                (e.get('note') or e['purpose']).replace('|', '/')))
        for v in S.VIEWS:
            if v['name'].startswith(mod + '.'):
                L.append('| %s | view entity (OQL) | — | %s (replaces %s) |' % (v['name'].split('.')[1], v['purpose'], v['odoo']))
        L += ['', '## Key microflows', '', '| Microflow | Kind | Purpose |', '|---|---|---|']
        for m in mfs[mod]:
            L.append('| %s | %s | %s |' % (m['name'], m['name'].split('_')[0], m.get('purpose', '').replace('|', '/')))
        L += ['', '## Pages / snippets', '', '| Page | Type | Source screen |', '|---|---|---|']
        for p in pages[mod]:
            s = U.S[p]
            L.append('| %s | %s | design/wireframes/%s.html |' % (p, {'list': 'Overview', 'form': 'NewEdit', 'popup': 'Popup', 'task': 'Workflow task',
                                                                     'inbox': 'Inbox', 'report': 'Report', 'dashboard': 'Dashboard'}[s['kind']], p))
        L += ['', '## Security', '', '| Module role | User roles |', '|---|---|']
        for mr, urs in MODULE_ROLES[mod].items():
            L.append('| %s.%s | %s |' % (mod, mr, ', '.join(urs)))
        if mod == 'Sales':
            L.append('\nEntity access: SalesUser reads/writes `Sales.SalesOrder` only where `SalesOrder_Salesperson = [%CurrentUser%]` (Odoo rule "Personal Orders").')
        L += ['', '## Dependencies', '',
              '- **Imports (associations to):** %s' % ('; '.join('%s (%s)' % (k.split(' -> ')[1], ', '.join(v)) for k, v in graph['associationEdges'].items()
                                                          if k.startswith(mod + ' ->')) or '—'),
              '- **Calls into:** %s' % ('; '.join('%s: %s' % (k.split(' -> ')[1], ', '.join(v)) for k, v in graph['callEdges'].items()
                                                   if k.startswith(mod + ' ->')) or '—'),
              '- **Used by:** %s' % (', '.join(sorted({k.split(' -> ')[0] for k in graph['associationEdges'] if k.endswith('-> ' + mod)})) or '—'),
              '- **Cross-module associations:** owned by this module (it is always the lower-layer side that is referenced; the owner is the referencing module).']
        open(os.path.join(d, 'definition.md'), 'w').write('\n'.join(L) + '\n')

    # blueprint.md
    layer_d = """flowchart TD
  subgraph UI[UI layer — Atlas Core, ledger theme, side rail]
    U1[Pages per module: overviews, hubs, popups, task inbox, reports]
  end
  subgraph DL[Domain + Logic]
    SAL[Sales]
    PUR[Purchasing]
    INV[Inventory]
    INVC[Invoicing]
  end
  subgraph MD[Common — master data]
    PAR[Partners]
    PRO[Products]
  end
  subgraph CM[Common — shared kernel]
    CORE[Core]
  end
  subgraph MP[Platform / marketplace]
    ADM[Administration]
    WFC[Workflow Commons]
    DW[Data Widgets + Charts]
  end
  U1 --> SAL & PUR & INV & INVC
  INV --> SAL & PUR
  INVC --> SAL & PUR
  SAL & PUR --> PAR & PRO
  PAR --> PRO
  PAR & PRO --> CORE
  SAL & PUR & INV & INVC --> CORE
  PAR -.-> ADM
  PUR -.-> WFC
  U1 -.-> DW"""
    wiring = ['flowchart LR']
    for k, v in graph['associationEdges'].items():
        src, dst = k.split(' -> ')
        wiring.append('  %s -. "%d assoc" .-> %s' % (src, len(v), dst))
    for k, v in graph['callEdges'].items():
        src, dst = k.split(' -> ')
        if S.MODULES.index(dst) > S.MODULES.index(src):
            wiring.append('  %s -->|"calls %s"| %s' % (src, v[0].split(' -> ')[1], dst))
    wf = """stateDiagram-v2
  [*] --> RFQ
  RFQ --> RFQSent: ACT_PurchaseOrder_MarkSent
  RFQ --> ToApprove: Confirm, total >= threshold, not manager
  RFQSent --> ToApprove: Confirm, total >= threshold, not manager
  RFQ --> PurchaseOrder: Confirm (approval not needed)
  RFQSent --> PurchaseOrder: Confirm (approval not needed)
  ToApprove --> PurchaseOrder: WF task Approve (PurchaseManager)
  ToApprove --> RFQ: WF task Reject + reason
  RFQ --> Cancelled
  RFQSent --> Cancelled
  ToApprove --> Cancelled
  PurchaseOrder --> Cancelled: no done receipt, no posted bill
  Cancelled --> RFQ: Set to RFQ"""
    so = """stateDiagram-v2
  [*] --> Quotation
  Quotation --> QuotationSent: mark as sent
  Quotation --> SalesOrder: Confirm (delivery created)
  QuotationSent --> SalesOrder: Confirm (delivery created)
  Quotation --> Cancelled
  QuotationSent --> Cancelled
  SalesOrder --> Cancelled: no posted invoice
  Cancelled --> Quotation: Set to quotation"""
    inv = """stateDiagram-v2
  [*] --> Draft
  Draft --> Posted: Confirm (number, due date)
  Draft --> Cancelled
  Posted --> Draft: Reset (no allocations)
  state Posted {
    NotPaid --> PartiallyPaid: payment / credit note allocated
    PartiallyPaid --> Paid
    NotPaid --> Paid
    NotPaid --> Reversed: full credit note
  }"""
    tr = """stateDiagram-v2
  [*] --> Draft
  Draft --> Waiting: Mark as to do
  Waiting --> Ready: Check availability (reserved)
  Ready --> Done: Validate (quantities)
  Ready --> Done: Validate short → backorder Waiting/Ready
  Draft --> Cancelled
  Waiting --> Cancelled
  Ready --> Cancelled"""
    B = ['# Blueprint — erpv1', '', '_Source of truth for the Stage 3 architecture. Generated by `pipelines/odoo/arch_blueprint.py` from the confirmed BRDs '
         '(`analysis/odoo/knowledge-base/brd/`), `module-graph.json` and `ui_spec.py`; `blueprint.html` renders this file._', '',
         '**One Mendix 11.15 app, 7 modules, ledger theme, side-rail navigation.** Module rationale: `architecture/module-design.html`. ERD: `architecture/erd.md`.', '',
         '## Tiers (layer view)', '', '```mermaid', layer_d, '```', '',
         'Arrows point down the tiers only. Associations are acyclic (checked by `brd_generator.py`); the only upward calls are the sanctioned bridges '
         'Sales/Purchasing → Inventory/Invoicing (user actions on an order).', '',
         '## Module wiring (build-order view)', '', '```mermaid', '\n'.join(wiring), '```', '',
         'Dotted = cross-module associations (owned by the referencing module, created in that module\'s domain-model script). Solid = sanctioned upward microflow calls.',
         '**Build order:** Core → Products → Partners → Sales → Purchasing → Inventory → Invoicing (the bridges in Inventory/Invoicing are built with those modules; '
         'Sales/Purchasing call them through stubs until then).', '',
         '## Modules', '', '| Module | Layer | Persistent entities | Microflows | Pages | Definition |', '|---|---|---|---|---|---|']
    for mod in S.MODULES:
        B.append('| %s | %s | %d | %d | %d | [definition](modules/%s/definition.md) |' % (
            mod, LAYER[mod], sum(1 for e in ents.values() if e['module'] == mod and e['persistent']), len(mfs[mod]), len(pages[mod]), mod))
    B += ['', '## Workflow and lifecycles (Step 3b)', '', '### WF_PurchaseOrderApproval (Mendix workflow) and purchase order status', '',
          '```mermaid', wf, '```', '', 'User task "Approve purchase order": assigned to PurchaseManager (module role Purchasing.Manager), outcomes Approve / Reject '
          '(reason required), inbox `PurchaseApproval_Inbox` (Workflow Commons), task page `PurchaseApproval_Task`. No timers, no parallel paths; one pool.', '',
          '### Sales order status', '', '```mermaid', so, '```', '', '### Transfer status', '', '```mermaid', tr, '```', '',
          '### Invoice status and payment status', '', '```mermaid', inv, '```', '',
          '## Cross-persona journeys (Step 3d)', '', '| Journey id | Name | Personas involved | Modules touched |', '|---|---|---|---|']
    for jid, name, pers, mods, d in JOURNEYS:
        B.append('| %s | %s | %s | %s |' % (jid, name, ', '.join(pers), ', '.join('`%s`' % m for m in mods)))
    for jid, name, pers, mods, d in JOURNEYS:
        B += ['', '### %s — %s' % (jid, name), '', '```mermaid', d, '```']
    B += ['', '## Security model (Step 6a)', '', 'Project security: production level; no anonymous/guest access; demo users one per user role.', '',
          '| User role | ' + ' | '.join(S.MODULES) + ' |', '|---|' + '---|' * len(S.MODULES)]
    for ur in U.ROLE_HOME:
        row = []
        for mod in S.MODULES:
            row.append(', '.join(mr for mr, urs in MODULE_ROLES[mod].items() if ur in urs) or '—')
        B.append('| %s | %s |' % (ur, ' | '.join(row)))
    B += ['', 'Row-level: SalesUser sees own sales orders only (XPath on SalesOrder_Salesperson). Approval task only for PurchaseManager. '
          'Configuration pages (Company, Warehouse, Numbering, Taxes, Payment terms, UoM, categories) need the Admin/Manager/Config module roles.', '',
          '## Volumes and NFRs (Step 6b)', '', 'Demo data: tens to hundreds of rows per entity; ≤ 5 concurrent users; no SLA (CONFIRMED 2026-10-14). Consequences: '
          'Data Grid 2 with paging (20 rows), no batching in microflows, indexes only on `Number`, date and `Status` attributes of SalesOrder, '
          'PurchaseOrder, Transfer, Invoice, Payment.', '', '## Integrations (Step 6c)', '',
          'None live. Email, portal, payment providers, EDI and barcodes are declared not implemented (Stage 0); no stubs needed because no '
          'flow calls them — the corresponding buttons are absent (e.g. "Send" only marks as sent).', '',
          '## Fit-gap', '', 'See [fit-gap.md](fit-gap.md).', '', '## Dependencies and open issues', '',
          'Register rows OI-1…OI-5 in `PROJECT.md` (single decision register).']
    open(os.path.join(a.out, 'blueprint.md'), 'w').write('\n'.join(B) + '\n')

    # fit-gap.md
    F = ['# Fit-gap — erpv1', '', '_Generated by `pipelines/odoo/arch_blueprint.py`. Verdicts: Native · Config · Buy · Build · Workaround · Gap._', '',
         '| Source capability (Odoo) | Mendix approach | Verdict | Open issue / note |', '|---|---|---|---|']
    for r in FITGAP:
        F.append('| %s | %s | **%s** | %s |' % r)
    F += ['', '**Buy (confirmed 2026-10-14):** Administration, Atlas Core, Data Widgets, Charts, Workflow Commons — installed at build-plan Step 0, '
          'before any domain-model script. No other marketplace content.', '',
          '**BPMN screen:** no BPMN / swimlane source; the only workflow (purchase approval) is one pool, one user task, one exclusive decision — all '
          'native and scriptable.']
    open(os.path.join(a.out, 'fit-gap.md'), 'w').write('\n'.join(F) + '\n')

    # blueprint.html (Step 7)
    md = open(os.path.join(a.out, 'blueprint.md')).read()
    svgs = {}
    blocks = re.findall(r'```mermaid\n(.*?)```', md, re.S)
    if not a.no_svg:
        tmp = tempfile.mkdtemp()
        pp = os.path.join(tmp, 'pp.json')
        chrome = sorted(glob.glob('/opt/pw-browsers/chromium-*/chrome-linux*/chrome'))
        json.dump({'executablePath': chrome[-1] if chrome else None, 'args': ['--no-sandbox']}, open(pp, 'w'))
        for i, blk in enumerate(blocks):
            src, out = os.path.join(tmp, 'd%d.mmd' % i), os.path.join(tmp, 'd%d.svg' % i)
            open(src, 'w').write(blk)
            r = subprocess.run(['npx', '-y', '@mermaid-js/mermaid-cli@11.4.2', '-p', pp, '-i', src, '-o', out, '-b', 'transparent', '-t', 'neutral'],
                               capture_output=True, text=True, env=dict(os.environ, PUPPETEER_SKIP_DOWNLOAD='1'))
            if r.returncode != 0 or not os.path.exists(out):
                print('mermaid render failed for diagram %d:\n%s' % (i, r.stderr[-800:]))
                return 1
            svgs[i] = re.sub(r'^<\?xml[^>]*>', '', open(out).read())
    def md_to_html(text):
        out, i = [], 0
        lines = text.split('\n')
        n_block = 0
        while i < len(lines):
            ln = lines[i]
            if ln.startswith('```mermaid'):
                j = i + 1
                while not lines[j].startswith('```'):
                    j += 1
                out.append('<figure class="diagram">%s</figure>' % (svgs.get(n_block) or '<pre class="mermaid">%s</pre>' % html.escape('\n'.join(lines[i + 1:j]))))
                n_block += 1
                i = j + 1
                continue
            if ln.startswith('|'):
                rows = []
                while i < len(lines) and lines[i].startswith('|'):
                    rows.append(lines[i]); i += 1
                cells = [[c.strip() for c in r.strip('|').split('|')] for r in rows if not re.match(r'^\|[-| ]+\|$', r)]
                t = '<table><thead><tr>%s</tr></thead><tbody>%s</tbody></table>' % (
                    ''.join('<th>%s</th>' % inline(c) for c in cells[0]), ''.join('<tr>%s</tr>' % ''.join('<td>%s</td>' % inline(c) for c in r) for r in cells[1:]))
                out.append(t)
                continue
            m = re.match(r'^(#{1,3}) (.*)', ln)
            if m:
                out.append('<h%d>%s</h%d>' % (len(m.group(1)), inline(m.group(2)), len(m.group(1))))
            elif ln.strip():
                out.append('<p>%s</p>' % inline(ln))
            i += 1
        return '\n'.join(out)
    def inline(t):
        t = html.escape(t)
        t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
        t = re.sub(r'(?<!\w)_(.+?)_(?!\w)', r'<i>\1</i>', t)
        t = re.sub(r'`(.+?)`', r'<code>\1</code>', t)
        t = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', t)
        return t
    body = md_to_html(md) + '<h2>Fit-gap</h2>' + md_to_html(open(os.path.join(a.out, 'fit-gap.md')).read().split('\n', 2)[2])
    css = open(os.path.join(os.path.dirname(a.out) or '.', 'design', 'ds.css')).read() if os.path.exists('design/ds.css') else ''
    css = css.replace('url("fonts/', 'url("../design/fonts/')
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Blueprint — erpv1</title><style>{css}
.bp {{ max-width: 1100px; margin: 0 auto; padding: 24px 16px 64px; }}
.bp h1 {{ font-size: 30px; margin: 8px 0 12px; }} .bp h2 {{ font-size: 22px; margin: 32px 0 10px; padding-bottom: 6px; border-bottom: 1px solid var(--mxt-line); }}
.bp h3 {{ font-size: 17px; margin: 20px 0 8px; }} .bp p {{ margin: 6px 0; }}
.bp table {{ border-collapse: collapse; width: 100%; margin: 8px 0 16px; background: var(--mxt-surface); font-size: 13px; }}
.bp th, .bp td {{ border-bottom: 1px solid var(--mxt-line); padding: 5px 8px; text-align: left; vertical-align: top; }}
.bp th {{ font-size: 12px; text-transform: uppercase; letter-spacing: .04em; color: var(--mxt-ink-muted); border-bottom-color: var(--mxt-ink-faint); }}
.bp code {{ font-size: 12px; background: var(--mxt-surface-alt); padding: 0 3px; }}
.diagram {{ background: var(--mxt-surface); border: 1px solid var(--mxt-line); padding: 12px; margin: 8px 0 16px; overflow-x: auto; }}
.diagram svg {{ max-width: 100%; height: auto; }}
.banner {{ background: var(--mxt-tint-warn); color: var(--mxt-tone-warn); padding: 8px 12px; font-size: 13px; }}
</style></head><body class="lg-body"><div class="banner">Generated from blueprint.md and fit-gap.md on {date.today()} — do not edit; regenerate with
<code>python3 -I pipelines/odoo/arch_blueprint.py</code>.</div><main class="bp">{body}</main></body></html>'''
    open(os.path.join(a.out, 'blueprint.html'), 'w').write(page)
    print('wrote %d module definitions, blueprint.md (%d diagrams), fit-gap.md (%d rows), blueprint.html' % (len(S.MODULES), len(blocks), len(FITGAP)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
