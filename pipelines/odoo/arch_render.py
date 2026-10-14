#!/usr/bin/env python3
"""Render Stage 3 architecture artifacts from the BRD design (single source: brd_spec.py / brd_content.py).

  architecture/module-design.html   modularize-domain.md Step 4 sign-off artifact
  architecture/erd.md               opt-in artifact `erd` (Mermaid erDiagram of the target domain)

Usage: arch_render.py [--kb analysis/odoo/knowledge-base] [--out architecture]
"""
import argparse, html, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import brd_spec as S      # noqa: E402
import brd_content as C   # noqa: E402

RATIONALE = {
    'Core': dict(
        mission='Shared kernel: the company, its currency and countries, taxes, payment terms and document numbering.',
        processes='Company setup; tax and payment-term configuration; numbering for every document type.',
        roles='Administrator, InvoicingManager (taxes, terms); read by everyone.',
        criterion='Bounded context "company configuration" used by every other module; sits at the bottom so nothing below it can create a cycle.',
        rejected='Keeping Tax and PaymentTerm in Invoicing (as Odoo does in `account`): Partners, Products and Company reference them, which made '
                 'master data depend on Invoicing and closed a cycle. Moved here.'),
    'Products': dict(
        mission='What we sell and buy: products, categories, units of measure and customer pricelists.',
        processes='Product catalogue maintenance; price determination for sales lines (F003 UC003); unit conversion (F002).',
        roles='SalesManager, InventoryManager, PurchaseManager maintain; everyone reads.',
        criterion='Bounded context (catalogue & pricing, Odoo `product` + `uom`).',
        rejected='Vendor prices (Odoo `product.supplierinfo`) kept here: they point to vendors, which made Products depend on Partners while '
                 'partners point to pricelists. Moved to Purchasing, where they are used. Separate UoM module: 2 entities, no criterion met.'),
    'Partners': dict(
        mission='One address book: customers, vendors, contact persons and addresses, bank accounts, and the business profile of app users.',
        processes='Contact maintenance; address resolution for orders and invoices; user onboarding (profile + partner).',
        roles='SalesUser, Purchaser, Billing maintain; SalesManager archives; Administrator manages users.',
        criterion='Bounded context (Odoo `res.partner`), referenced by every transactional module.',
        rejected='Merging into Core: partners are business data with their own UI and access rules, Core is configuration. '
                 'UserProfile in Core: it links to Partner, which would make Core depend on Partners.'),
    'Sales': dict(
        mission='Quotations to sales orders, quotation templates, sales teams and sales analysis.',
        processes='Quote → order (F004); triggers delivery (F007) and invoicing (F008).',
        roles='SalesUser (own orders), SalesManager (all orders, lock, templates, teams, analysis).',
        criterion='Bounded context and security segregation (sales roles, own-documents rule).',
        rejected='One "Orders" module with sales and purchasing: different roles, approval rules and record rules; nothing shared but master data.'),
    'Purchasing': dict(
        mission='RFQs to purchase orders with manager approval, vendor prices and purchase analysis.',
        processes='RFQ → PO (F005) incl. the approval workflow; triggers receipt (F007) and bills (F008); receives RFQs from reorder rules.',
        roles='Purchaser, PurchaseManager (approval inbox, analysis).',
        criterion='Bounded context and security segregation (purchase roles, approval).',
        rejected='Purchase order pointing to the warehouse operation type and the reorder rule (Odoo `picking_type_id`, `orderpoint_id`): '
                 'made Purchasing depend on Inventory while Inventory points to orders. Dropped / reversed (single warehouse).'),
    'Inventory': dict(
        mission='Warehouse, locations, transfers and stock moves, stock levels, counts and reorder rules — plus the order-fulfilment bridge.',
        processes='Receipts, deliveries, internal transfers, backorders (F006); delivery/receipt from orders (F007); replenishment.',
        roles='InventoryUser (operations), InventoryManager (configuration, counts, rules).',
        criterion='Bounded context (Odoo `stock`); owns the links to sales/purchase orders exactly like Odoo `sale_stock`/`purchase_stock`.',
        rejected='A separate "Fulfilment" module for the bridges: 0 own entities, only associations and 4 microflows — over-split signal.'),
    'Invoicing': dict(
        mission='Customer invoices, vendor bills, credit notes and payments with allocations; invoice analysis.',
        processes='Invoice/bill from orders, posting, credit notes, payment registration (F008).',
        roles='Billing, InvoicingManager; SalesUser/Purchaser trigger invoice/bill creation from their orders.',
        criterion='Bounded context (Odoo `account`, invoices only) and security segregation (billing roles).',
        rejected='Full accounting with ledger, journals and reconciliation: out of scope (Q-F008-1).'),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--kb', default='analysis/odoo/knowledge-base')
    ap.add_argument('--out', default='architecture')
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    graph = json.load(open(os.path.join(a.kb, 'brd', 'module-graph.json')))
    ents = {e['name']: e for e in S.E}
    by_mod = {m: [e for e in S.E if e['name'].split('.')[0] == m] for m in S.MODULES}
    views = {m: [v for v in S.VIEWS if v['name'].split('.')[0] == m] for m in S.MODULES}
    enums = {m: [n for n in S.ENUMS if n.split('.')[0] == m] for m in S.MODULES}
    mfs = {m: [] for m in S.MODULES}
    import glob
    for f in sorted(glob.glob(os.path.join(a.kb, 'brd', 'F*.brd.json'))):
        b = json.load(open(f))
        for x in b['microflows'] + b.get('workflows', []):
            mod = x.get('module')
            if mod in mfs and x['name'] not in mfs[mod]:
                mfs[mod].append(x['name'])
    pages = {m: sorted({p['name'] for b in C.BRDS.values() for p in b['pages'] if p['pattern'] != 'extension'
                        and p['dataContext'].split('.')[0] == m}) for m in S.MODULES}
    deps = {m: sorted({k.split(' -> ')[1] for k in graph['associationEdges'] if k.startswith(m + ' ->')}) for m in S.MODULES}
    used_by = {m: sorted({k.split(' -> ')[0] for k in graph['associationEdges'] if k.endswith('-> ' + m)}) for m in S.MODULES}

    E = html.escape
    cards = []
    for i, m in enumerate(S.MODULES):
        r = RATIONALE[m]
        internal = [asc[0] for e in by_mod[m] for asc in e['assocs'] if asc[1].split('.')[0] == m]
        cross = ['%s → %s' % (asc[0], asc[1]) for e in by_mod[m] for asc in e['assocs'] if asc[1].split('.')[0] not in (m,)]
        ent_list = ''.join('<li><code>%s</code>%s — %s</li>' % (E(e['name'].split('.')[1]), '' if e['persistent'] else ' <span class="tag">non-persistent</span>',
                                                              E(e['purpose'])) for e in by_mod[m])
        ent_list += ''.join('<li><code>%s</code> <span class="tag">view entity</span> — %s</li>' % (E(v['name'].split('.')[1]), E(v['purpose'])) for v in views[m])
        cards.append(f'''
<section class="card" id="{m}">
  <div class="head"><span class="layer">layer {i + 1}</span><h2>{m}</h2></div>
  <p class="mission">{E(r['mission'])}</p>
  <dl>
    <dt>Business processes</dt><dd>{E(r['processes'])}</dd>
    <dt>Users / roles</dt><dd>{E(r['roles'])}</dd>
    <dt>Boundary earned by</dt><dd>{E(r['criterion'])}</dd>
    <dt>Rejected alternative</dt><dd>{E(r['rejected'])}</dd>
    <dt>Depends on (associations)</dt><dd>{', '.join(deps[m]) or '—'}</dd>
    <dt>Used by</dt><dd>{', '.join(used_by[m]) or '—'}</dd>
  </dl>
  <h3>Owned data — {sum(1 for e in by_mod[m] if e['persistent'])} persistent entities, {len(enums[m])} enumerations</h3>
  <ul class="ents">{ent_list}</ul>
  <p class="small"><b>Associations inside the module ({len(internal)}):</b> {E(', '.join(internal)) or '—'}</p>
  <p class="small"><b>Cross-module associations ({len(cross)}), all pointing down the layer stack:</b> {E(', '.join(cross)) or '—'}</p>
  <p class="small"><b>Logic:</b> {len(mfs[m])} microflows/workflows · <b>Pages:</b> {len(pages[m])} ({E(', '.join(pages[m]))})</p>
</section>''')
    up = ''.join('<li>%s: %s</li>' % (E(k), E('; '.join(v))) for k, v in graph['callEdges'].items()
                 if S.MODULES.index(k.split(' -> ')[1]) > S.MODULES.index(k.split(' -> ')[0]))
    stack = ' → '.join(reversed(S.MODULES))
    doc = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Module Design — erpv1</title>
<style>
:root {{ --bg:#f8fafc; --surface:#fff; --ink:#1e293b; --ink-soft:#64748b; --ink-faint:#94a3b8; --line:#e2e8f0; --accent:#0f4c81;
  --pass-bg:#dcfce7; --pass-ink:#166534; --warn-bg:#fef3c7; --warn-ink:#92400e; --radius:10px;
  --font:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; --mono:ui-monospace,'SF Mono',Menlo,monospace; }}
@media (prefers-color-scheme: dark) {{ :root {{ --bg:#0f172a; --surface:#1e293b; --ink:#e2e8f0; --ink-soft:#94a3b8; --ink-faint:#64748b;
  --line:#334155; --accent:#7cb3e8; --pass-bg:#14532d; --pass-ink:#bbf7d0; --warn-bg:#78350f; --warn-ink:#fde68a; }} }}
*,*::before,*::after {{ box-sizing:border-box; margin:0; padding:0; }}
body {{ background:var(--bg); color:var(--ink); font:15px/1.55 var(--font); padding:32px 16px; }}
main {{ max-width:980px; margin:0 auto; }}
h1 {{ font-size:26px; margin-bottom:6px; }} h2 {{ font-size:20px; }} h3 {{ font-size:14px; margin:14px 0 6px; color:var(--ink-soft); }}
.lede {{ color:var(--ink-soft); margin-bottom:22px; }}
.card {{ background:var(--surface); border:1px solid var(--line); border-radius:var(--radius); padding:20px 22px; margin:16px 0; }}
.head {{ display:flex; align-items:baseline; gap:10px; }}
.layer {{ font:12px var(--mono); color:var(--accent); border:1px solid var(--line); border-radius:6px; padding:1px 6px; }}
.mission {{ margin:8px 0 12px; font-weight:500; }}
dl {{ display:grid; grid-template-columns:200px 1fr; gap:6px 14px; font-size:14px; }}
dt {{ color:var(--ink-soft); }} code {{ font-family:var(--mono); font-size:13px; }}
.ents {{ list-style:none; font-size:14px; }} .ents li {{ padding:3px 0; border-bottom:1px solid var(--line); }}
.small {{ font-size:13px; color:var(--ink-soft); margin-top:8px; }}
.tag {{ font-size:11px; background:var(--warn-bg); color:var(--warn-ink); border-radius:4px; padding:0 5px; }}
.stack {{ font:14px var(--mono); background:var(--surface); border:1px solid var(--line); border-radius:var(--radius); padding:14px 18px; }}
.ok {{ background:var(--pass-bg); color:var(--pass-ink); border-radius:var(--radius); padding:12px 16px; margin:12px 0; }}
.q {{ background:var(--surface); border:2px solid var(--accent); border-radius:var(--radius); padding:18px 22px; margin-top:26px; }}
.q li {{ margin:6px 0 6px 18px; }}
@media (max-width:640px) {{ dl {{ grid-template-columns:1fr; }} }}
</style></head><body><main>
<h1>Module design — erpv1</h1>
<p class="lede">Odoo 18.0 → Mendix 11.15 POC · Stage 3 sign-off artifact (modularize-domain.md) · generated by
<code>pipelines/odoo/arch_render.py</code> from the confirmed BRDs F001–F008 · one Mendix app (Stage 0).</p>

<h3>Proposal: 7 modules in a strict layer stack (associations only point downwards)</h3>
<div class="stack">{stack}</div>
<div class="ok">Association graph is acyclic (checked by <code>brd_generator.py</code>, mutation-tested). {sum(len(v) for v in graph['associationEdges'].values())}
cross-module associations, every one pointing to a lower layer. No module exceeds 15 persistent entities (largest: {max(S.MODULES, key=lambda m: sum(1 for e in by_mod[m] if e['persistent']))},
{max(sum(1 for e in by_mod[m] if e['persistent']) for m in S.MODULES)}).</div>
<p class="small"><b>Sanctioned upward calls</b> (user actions on an order trigger the downstream bridge microflow, as Odoo's
sale_stock / purchase_stock / sale→account do): <ul class="small">{up}</ul></p>
<p class="small"><b>Platform modules used:</b> System, Administration (accounts, roles), Atlas Core (UI), Data Widgets (grids/filters),
Workflow Commons (approval inbox), Charts (analysis pages) — buy/build per item is the fit-gap step that follows this sign-off.</p>
{''.join(cards)}
<div class="q"><h2>Does this match how your teams and processes are actually organised?</h2>
<p class="small">modularize-domain.md Step 1 — the inputs a BRD cannot contain:</p>
<ol>
<li><b>Team ownership</b> — will different people/teams own sales, purchasing, inventory, invoicing? (POC default: one owner → boundaries by bounded context only)</li>
<li><b>Reuse intent</b> — any module you want to lift into another app later (e.g. Partners, Products)?</li>
<li><b>Release cadence</b> — must anything ship independently? (POC default: no)</li>
<li><b>Security / regulatory segregation</b> — any data that must be isolated beyond the 9 roles (e.g. invoicing only for finance)?</li>
</ol></div>
</main></body></html>'''
    open(os.path.join(a.out, 'module-design.html'), 'w').write(doc)

    # ERD (Mermaid)
    def mid(n):
        return n.replace('.', '_')
    lines = ['# Target domain ERD — erpv1', '', 'Opt-in artifact `erd` (PROJECT.md). Generated by `pipelines/odoo/arch_render.py` from',
             '`brd_spec.py`; do not hand-edit. One diagram per module (owned entities + the entities they reference),',
             'then the cross-module overview. `}o--||` = many-to-one Reference; `}o--o{` = ReferenceSet.', '']
    resolved = {}
    import glob
    for f in glob.glob(os.path.join(a.kb, 'brd', 'F*.brd.json')):
        for de in json.load(open(f))['domainEntities']:
            if not de.get('extensionOf'):
                resolved[de['name']] = {at['name']: at for at in de['attributes']}

    def block(ents_in, title):
        out = ['## ' + title, '', '```mermaid', 'erDiagram']
        shown = set()
        for e in ents_in:
            shown.add(e['name'])
            out.append('  %s {' % mid(e['name']))
            for n, of, ov in e['attrs']:
                at = resolved.get(e['name'], {}).get(n, {})
                t = at.get('type') or 'String'
                if t == 'Enumeration':
                    t = at.get('enumeration', 'Enum').split('.')[-1]
                out.append('    %s %s%s' % (t, n, ' "src: %s"' % at['sourceOdoo'] if at.get('sourceOdoo') else ''))
            out.append('  }')
        for e in ents_in:
            for n, tgt, typ, of, note in e['assocs']:
                rel = '}o--o{' if typ == 'ReferenceSet' else '}o--||'
                out.append('  %s %s %s : "%s"' % (mid(e['name']), rel, mid(tgt), n.split('_', 1)[1]))
        out += ['```', '']
        return out
    for m in S.MODULES:
        lines += block(by_mod[m], '%s (%d entities)' % (m, len(by_mod[m])))
    lines += ['## Cross-module overview (module → module, association count)', '', '```mermaid', 'flowchart BT']
    for k, v in graph['associationEdges'].items():
        src, dst = k.split(' -> ')
        lines.append('  %s -->|%d| %s' % (src, len(v), dst))
    lines += ['```', '']
    open(os.path.join(a.out, 'erd.md'), 'w').write('\n'.join(lines))
    print('wrote %s/module-design.html and %s/erd.md' % (a.out, a.out))


if __name__ == '__main__':
    main()
