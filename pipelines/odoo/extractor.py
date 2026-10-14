#!/usr/bin/env python3
"""Odoo addon extractor -> toolkit knowledge base (Stage 1, Path A).

Reads an Odoo addon tree (sources/odoo/addons/<addon>/...) and writes the toolkit's
knowledge-base JSONs (entities, structures, staticEntities, logics, screens, roles, timers,
serviceApis, workflows, extEntities, cross-reference-map) plus Odoo-specific extras
(menus.json, sequences.json) and reports/*.md.

Mechanism: Python `ast` for models (so field kwargs, selections and decorators are read
structurally), ElementTree for XML, csv for ACLs. validator.py deliberately uses a
different mechanism (line-oriented regex) — extractor-quality-loop.md's
correlated-blind-spot rule.

Usage: extractor.py --source sources/odoo/addons --out analysis/odoo/knowledge-base
"""
import argparse, ast, csv, json, os, re, sys
import xml.etree.ElementTree as ET
from collections import defaultdict, OrderedDict

# ── Capability map (triage.md C1–C12) ────────────────────────────────────────────────────────
C1_BASE = re.compile(r'^res\.(partner|company|users|currency|country|bank)(\.|$)|^format\.(address|vat)')
C8_ACCOUNT = re.compile(r'^account\.(move|move\.line|tax|tax\.|payment|payment\.|journal$|move\.reversal|invoice\.report|cash\.rounding|incoterms|move\.send)')
ADDON_CAP = {'uom': 'C2', 'product': 'C3', 'sales_team': 'C4', 'sale': 'C4', 'sale_management': 'C4',
             'purchase': 'C5', 'stock': 'C6', 'sale_stock': 'C7', 'purchase_stock': 'C7',
             'analytic': 'C10', 'stock_account': 'C11'}
CAP_NAMES = {'C1': 'Contacts, companies & users', 'C2': 'Units of measure', 'C3': 'Product catalogue & pricing',
             'C4': 'Sales', 'C5': 'Purchasing', 'C6': 'Inventory & warehouse', 'C7': 'Order fulfilment bridges',
             'C8': 'Invoices, bills & payments', 'C9': 'General ledger core', 'C10': 'Analytic accounting',
             'C11': 'Stock valuation', 'C12': 'Platform / framework'}
IN_SCOPE = {'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8'}


def capability(model, addon):
    if addon == 'base':
        return 'C1' if C1_BASE.search(model) else 'C12'
    if addon == 'account':
        return 'C8' if C8_ACCOUNT.search(model) else 'C9'
    return ADDON_CAP.get(addon, 'C12')


# ── Odoo field type -> Mendix type ───────────────────────────────────────────────────────────
def mendix_type(f, enum_name):
    t = f['odooType']
    if t == 'Char':
        return 'String(%s)' % f['size'] if f.get('size') else 'String(200)'
    if t in ('Text', 'Html'):
        return 'String(unlimited)'
    if t == 'Integer':
        return 'Integer'
    if t in ('Float', 'Monetary'):
        return 'Decimal'
    if t == 'Boolean':
        return 'Boolean'
    if t in ('Date', 'Datetime'):
        return 'DateTime'
    if t == 'Selection':
        return 'Enumeration(%s)' % enum_name
    if t in ('Binary', 'Image'):
        return 'Binary'
    if t in ('Json', 'Properties', 'PropertiesDefinition', 'Reference', 'Many2oneReference'):
        return 'String(unlimited)'
    if t == 'Many2one':
        return 'Reference'
    if t in ('One2many', 'Many2many'):
        return 'ReferenceSet'
    if t == 'Id':
        return 'Long'
    return 'String(unlimited)'


RELATIONAL = ('Many2one', 'One2many', 'Many2many')


def enum_name_for(model, field):
    return (model.replace('.', '_') + '_' + field)


# ── Python model parsing ─────────────────────────────────────────────────────────────────────
def lit(node):
    """Best-effort literal value of an AST node; translation calls _('x') -> 'x'."""
    if node is None:
        return None
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in ('_', '_lt') and node.args:
        return lit(node.args[0])
    if isinstance(node, (ast.List, ast.Tuple)):
        return [lit(e) for e in node.elts]
    if isinstance(node, ast.Dict):
        return {lit(k): lit(v) for k, v in zip(node.keys, node.values)}
    return None


def src(node):
    try:
        return ast.unparse(node)
    except Exception:
        return None


def selection_values(node, consts):
    """-> (values|None, source). values = [{'name','label'}]"""
    if node is None:
        return None, 'none'
    if isinstance(node, ast.Name):
        if node.id in consts:
            return selection_values(consts[node.id], consts)
        return None, 'unresolved-constant:' + node.id
    if isinstance(node, (ast.List, ast.Tuple)):
        vals = []
        for e in node.elts:
            v = lit(e)
            if isinstance(v, (list, tuple)) and len(v) >= 1:
                vals.append({'name': v[0], 'label': v[1] if len(v) > 1 else v[0]})
            else:
                return None, 'non-literal-list'
        return vals, 'static'
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return None, 'method:' + node.value
    if isinstance(node, ast.Lambda):
        return None, 'lambda'
    if isinstance(node, ast.Call):
        return None, 'call:' + (src(node.func) or '?')
    if isinstance(node, ast.Attribute):
        return None, 'attr:' + (src(node) or '?')
    return None, 'other'


def deco_info(fn):
    out = []
    for d in fn.decorator_list:
        if isinstance(d, ast.Call):
            out.append({'name': src(d.func), 'args': [lit(a) if lit(a) is not None else src(a) for a in d.args]})
        else:
            out.append({'name': src(d), 'args': []})
    return out


STATE_RE = re.compile(r"""['"]state['"]\s*:\s*['"](\w+)['"]|\.state\s*=\s*['"](\w+)['"]""")
RAISE_RE = re.compile(r"""raise\s+(UserError|ValidationError|AccessError|RedirectWarning)\(\s*_\(\s*(['"])(.+?)\2""", re.S)


def method_kind(name, decos, compute_names):
    dn = [d['name'] for d in decos]
    if any(n and n.endswith('constrains') for n in dn):
        return 'constraint'
    if any(n and n.endswith('onchange') for n in dn):
        return 'onchange'
    if name in compute_names or name.startswith('_compute_'):
        return 'compute'
    if name.startswith('_inverse_'):
        return 'inverse'
    if name.startswith(('action_', 'button_')):
        return 'action'
    if name in ('create', 'write', 'unlink', 'copy', 'copy_data', 'default_get', 'name_create',
                '_compute_display_name', 'name_search', '_name_search', 'read_group'):
        return 'override'
    if name.startswith('_cron') or 'cron' in name:
        return 'scheduled'
    return 'helper' if name.startswith('_') else 'public'


def parse_py(path, rel, addon, consts, errors):
    try:
        text = open(path, encoding='utf-8').read()
        tree = ast.parse(text)
    except Exception as e:
        errors.append({'file': rel, 'error': 'parse: %s' % e})
        return []
    lines = text.splitlines()
    out = []
    for cls in [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]:
        bases = [src(b) for b in cls.bases]
        kind = None
        for b in bases:
            if b and b.endswith('TransientModel'):
                kind = 'transient'
            elif b and b.endswith('AbstractModel'):
                kind = 'abstract'
            elif b and b.endswith('.Model') or b == 'Model':
                kind = kind or 'persistent'
        if kind is None:
            continue
        attrs = {}
        fields = []
        methods = []
        for st in cls.body:
            if isinstance(st, ast.AnnAssign) and isinstance(st.target, ast.Name) and st.value is not None:
                st = ast.Assign(targets=[st.target], value=st.value, lineno=st.lineno)  # `x: Model = fields.T(...)`
            if isinstance(st, ast.Assign) and len(st.targets) == 1 and isinstance(st.targets[0], ast.Name):
                tname = st.targets[0].id
                v = st.value
                if isinstance(v, ast.Call) and isinstance(v.func, ast.Attribute) and isinstance(v.func.value, ast.Name) \
                        and v.func.value.id == 'fields':
                    fields.append(parse_field(tname, v.func.attr, v, consts, st.lineno))
                elif tname.startswith('_'):
                    attrs[tname] = v
            elif isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef)):
                methods.append(st)
        name = lit(attrs.get('_name'))
        if '_name' in attrs and not isinstance(name, str):
            errors.append({'file': rel, 'error': 'non-literal _name in class %s: %s' % (cls.name, src(attrs['_name']))})
            continue
        inherit = lit(attrs.get('_inherit'))
        if isinstance(inherit, str):
            inherit = [inherit]
        inherit = [i for i in (inherit or []) if isinstance(i, str)]
        inherits = lit(attrs.get('_inherits')) or {}
        if not name:
            if not inherit:
                continue  # base python class, not a registered model
            name = inherit[0]
            mode = 'extension'
            mixins = inherit[1:]
        else:
            mode = 'extension' if name in inherit else 'definition'
            mixins = [i for i in inherit if i != name]
        compute_names = {f.get('compute') for f in fields if f.get('compute')}
        mitems = []
        for m in methods:
            decos = deco_info(m)
            body = '\n'.join(lines[m.lineno - 1:(m.end_lineno or m.lineno)])
            calls = sorted({c.func.attr for c in ast.walk(m) if isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute)})
            mitems.append({
                'name': m.name, 'kind': method_kind(m.name, decos, compute_names), 'decorators': decos,
                'doc': (ast.get_docstring(m) or '')[:500], 'line': m.lineno, 'endLine': m.end_lineno,
                'params': [a.arg for a in m.args.args[1:]],
                'calls': calls[:60],
                'writesState': sorted({a or b for a, b in STATE_RE.findall(body)}),
                'raises': [{'type': t, 'message': msg[:200]} for t, _q, msg in RAISE_RE.findall(body)][:10],
            })
        sqlc = attrs.get('_sql_constraints')
        out.append({
            'model': name, 'addon': addon, 'file': rel, 'line': cls.lineno, 'class': cls.name,
            'kind': kind, 'mode': mode, 'mixins': mixins,
            'delegates': {k: v for k, v in inherits.items()} if isinstance(inherits, dict) else {},
            'description': lit(attrs.get('_description')) or '',
            'order': lit(attrs.get('_order')), 'recName': lit(attrs.get('_rec_name')),
            'sqlConstraints': [c for c in (lit(sqlc) or []) if isinstance(c, (list, tuple))] if sqlc is not None else [],
            'fields': fields, 'methods': mitems,
        })
    return out


FIELD_KW = ('string', 'required', 'readonly', 'compute', 'store', 'related', 'index', 'ondelete', 'inverse_name',
            'comodel_name', 'size', 'tracking', 'copy', 'groups', 'company_dependent', 'currency_field', 'translate',
            'inverse', 'search', 'precompute', 'help', 'check_company', 'domain', 'relation', 'column1', 'column2')


def parse_field(name, ftype, call, consts, lineno):
    f = OrderedDict(name=name, odooType=ftype, line=lineno)
    kws = {k.arg: k.value for k in call.keywords if k.arg}
    pos = call.args
    if ftype in RELATIONAL:
        if pos:
            f['comodel'] = lit(pos[0])
        if ftype == 'One2many' and len(pos) > 1:
            f['inverse_name'] = lit(pos[1])
        if ftype == 'Many2one' and len(pos) > 1:
            f['string'] = lit(pos[1])
        if ftype == 'One2many' and len(pos) > 2:
            f['string'] = lit(pos[2])
        if ftype == 'Many2many':
            if len(pos) > 1: f['relation'] = lit(pos[1])
            if len(pos) > 4: f['string'] = lit(pos[4])
    elif ftype == 'Selection':
        selnode = pos[0] if pos else kws.get('selection')
        vals, how = selection_values(selnode, consts)
        f['selectionSource'] = how
        if vals is not None:
            f['selection'] = vals
        if len(pos) > 1:
            f['string'] = lit(pos[1])
        if 'selection_add' in kws:
            add, how2 = selection_values(kws['selection_add'], consts)
            f['selectionAdd'] = add or []
    else:
        if pos:
            f['string'] = lit(pos[0])
    for k in FIELD_KW:
        if k in kws:
            v = lit(kws[k])
            f[k] = v if v is not None else src(kws[k])
    if 'comodel_name' in f and not f.get('comodel'):
        f['comodel'] = f.pop('comodel_name')
    if 'default' in kws:
        f['default'] = src(kws['default'])
    if ftype in ('Float', 'Monetary') and 'digits' in kws:
        f['digits'] = src(kws['digits'])
    if isinstance(f.get('help'), str):
        f['help'] = f['help'][:300]
    return f


def module_consts(paths):
    """Module-level list/tuple constants across all files (selection lists are often shared)."""
    consts = {}
    for p in paths:
        try:
            tree = ast.parse(open(p, encoding='utf-8').read())
        except Exception:
            continue
        for st in tree.body:
            if isinstance(st, ast.Assign) and len(st.targets) == 1 and isinstance(st.targets[0], ast.Name) \
                    and isinstance(st.value, (ast.List, ast.Tuple)):
                consts.setdefault(st.targets[0].id, st.value)
    return consts


# ── XML parsing ──────────────────────────────────────────────────────────────────────────────
def xml_records(path, rel, addon, errors):
    try:
        root = ET.parse(path).getroot()
    except Exception as e:
        errors.append({'file': rel, 'error': 'xml: %s' % e})
        return [], []
    recs, menus = [], []

    def walk_menus(el, parent):
        for m in el.findall('menuitem'):
            mid = m.get('id')
            menus.append({'id': qual(mid, addon), 'name': m.get('name'), 'parent': qual(m.get('parent'), addon) if m.get('parent') else parent,
                          'action': qual(m.get('action'), addon) if m.get('action') else None, 'sequence': m.get('sequence'),
                          'groups': m.get('groups'), 'addon': addon, 'file': rel})
            walk_menus(m, qual(mid, addon))

    for container in [root] + root.findall('data'):
        walk_menus(container, None)
        for r in container.findall('record'):
            fd = {}
            for fe in r.findall('field'):
                fname = fe.get('name')
                if fe.get('ref'):
                    fd[fname] = {'ref': qual(fe.get('ref'), addon)}
                elif fe.get('eval') is not None:
                    fd[fname] = {'eval': fe.get('eval')}
                elif fe.get('type') == 'xml' or len(fe):
                    fd[fname] = {'xml': fe}
                else:
                    fd[fname] = (fe.text or '').strip()
            recs.append({'id': qual(r.get('id'), addon), 'model': r.get('model'), 'fields': fd, 'addon': addon, 'file': rel})
        for t in container.findall('template'):
            recs.append({'id': qual(t.get('id'), addon), 'model': 'qweb.template', 'fields': {'inherit_id': t.get('inherit_id')},
                         'addon': addon, 'file': rel})
    return recs, menus


def qual(xid, addon):
    if not xid:
        return xid
    return xid if '.' in xid else addon + '.' + xid


REF_RE = re.compile(r"ref\(['\"]([\w.]+)['\"]\)")


def view_info(rec, model_ids):
    f = rec['fields']
    arch = f.get('arch', {}).get('xml') if isinstance(f.get('arch'), dict) else None
    root = arch[0] if arch is not None and len(arch) else None
    vtype = root.tag if root is not None else None
    if vtype == 'tree':
        vtype = 'list'
    inherit = f.get('inherit_id', {}).get('ref') if isinstance(f.get('inherit_id'), dict) else None
    model = f.get('model') if isinstance(f.get('model'), str) else None
    flds, buttons, pages = [], [], []
    if root is not None:
        for el in root.iter():
            if el.tag == 'field' and el.get('name') and el.get('position') is None:
                if el.get('name') not in flds:
                    flds.append(el.get('name'))
            elif el.tag == 'button':
                buttons.append({'name': el.get('name'), 'type': el.get('type'), 'string': el.get('string'),
                                'invisible': el.get('invisible'), 'groups': el.get('groups')})
            elif el.tag == 'page' and el.get('string'):
                pages.append(el.get('string'))
    statusbar = None
    if root is not None:
        for el in root.iter('field'):
            if el.get('widget') == 'statusbar':
                statusbar = {'field': el.get('name'), 'visible': el.get('statusbar_visible')}
    return {'type': 'screen', 'linkId': 'odoo:screen:' + rec['id'], 'uniqueId': rec['id'], 'name': rec['id'],
            'label': f.get('name') if isinstance(f.get('name'), str) else rec['id'], 'module': rec['addon'],
            'model': model, 'viewType': vtype, 'inheritsView': inherit, 'mode': 'extension' if inherit else 'primary',
            'fields': flds, 'buttons': buttons, 'pages': pages, 'statusbar': statusbar,
            '_source': rec['file'], 'sourceRef': rec['file'], '_gaps': [], '_links': []}


# ── Main ─────────────────────────────────────────────────────────────────────────────────────
def addon_order(manifests):
    order, seen = [], set()

    def visit(a, stack=()):
        if a in seen or a not in manifests:
            return
        for d in manifests[a].get('depends', []):
            if d not in stack:
                visit(d, stack + (a,))
        seen.add(a)
        order.append(a)
    if 'base' in manifests:
        visit('base')
    for a in sorted(manifests):
        visit(a)
    return order


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', required=True)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    srcroot, out = a.source.rstrip('/'), a.out
    proj_rel = lambda p: os.path.relpath(p, os.path.join(srcroot, '..', '..', '..'))
    errors = []
    manifests = {}
    for addon in sorted(os.listdir(srcroot)):
        mp = os.path.join(srcroot, addon, '__manifest__.py')
        if os.path.exists(mp):
            text = open(mp, encoding='utf-8').read()
            manifests[addon] = ast.literal_eval(text[text.index('{'):])
    order = addon_order(manifests)
    pyfiles = defaultdict(list)
    xmlfiles = defaultdict(list)
    csvfiles = defaultdict(list)
    other_files = defaultdict(list)   # files read by the secondary readers below
    for addon in order:
        for dp, dn, fn in os.walk(os.path.join(srcroot, addon)):
            dn.sort()
            for f in sorted(fn):
                p = os.path.join(dp, f)
                sub = os.path.relpath(p, os.path.join(srcroot, addon)).split(os.sep)[0]
                if f.endswith('.py') and sub not in ('controllers', 'migrations', 'tests', 'demo') and f not in ('__init__.py', '__manifest__.py'):
                    pyfiles[addon].append(p)
                elif f.endswith('.xml') and sub in ('views', 'wizard', 'report', 'security', 'data', 'demo'):
                    xmlfiles[addon].append(p)
                elif f == 'ir.model.access.csv':
                    csvfiles[addon].append(p)
                else:
                    other_files[addon].append(p)
    consts = module_consts([p for ps in pyfiles.values() for p in ps])

    # 1. models
    classes = []
    for addon in order:
        for p in pyfiles[addon]:
            classes += parse_py(p, proj_rel(p), addon, consts, errors)
    models = OrderedDict()
    for c in classes:
        m = models.get(c['model'])
        if m is None or c['mode'] == 'definition' and m['origin'] is None:
            if m is None:
                m = models[c['model']] = {'model': c['model'], 'origin': None, 'kind': None, 'description': '', 'order': None,
                                         'recName': None, 'mixins': [], 'delegates': {}, 'fields': OrderedDict(),
                                         'methods': [], 'extendedBy': [], 'sqlConstraints': [], 'files': []}
        if c['mode'] == 'definition' and m['origin'] is None:
            m['origin'] = c['addon']
            m['kind'] = c['kind']
        elif c['addon'] not in m['extendedBy'] and c['addon'] != m['origin']:
            m['extendedBy'].append(c['addon'])
        m['description'] = m['description'] or c['description']
        m['order'] = c['order'] or m['order']
        m['recName'] = c['recName'] or m['recName']
        m['mixins'] += [x for x in c['mixins'] if x not in m['mixins']]
        m['delegates'].update(c['delegates'])
        m['sqlConstraints'] += c['sqlConstraints']
        m['files'].append(c['file'])
        for f in c['fields']:
            prev = m['fields'].get(f['name'])
            f2 = dict(f)
            f2['definedIn'] = c['addon']
            f2['file'] = c['file']
            if prev:
                merged = dict(prev)
                for k, v in f2.items():
                    if k in ('definedIn', 'file'):
                        continue
                    if k == 'selectionAdd':
                        merged['selection'] = (merged.get('selection') or []) + [x for x in v if x['name'] not in {s['name'] for s in (merged.get('selection') or [])}]
                        merged.setdefault('selectionAddedBy', []).append(c['addon'])
                        continue
                    merged[k] = v
                merged.setdefault('redefinedIn', []).append(c['addon'])
                m['fields'][f['name']] = merged
            else:
                if 'selectionAdd' in f2 and 'selection' not in f2:
                    f2['selection'] = f2['selectionAdd']
                m['fields'][f['name']] = f2
        for me in c['methods']:
            me = dict(me, addon=c['addon'], file=c['file'])
            m['methods'].append(me)
    # kind for models only extended (origin outside the imported addons)
    external = sorted(n for n, m in models.items() if m['origin'] is None)
    for n in external:
        models[n]['kind'] = 'external'

    # mixin field inheritance (prototype _inherit copies fields)
    def inherited_fields(name, seen=()):
        m = models.get(name)
        if not m or name in seen:
            return OrderedDict()
        acc = OrderedDict()
        for mx in m['mixins']:
            for k, v in inherited_fields(mx, seen + (name,)).items():
                acc.setdefault(k, v)
            mm = models.get(mx)
            if mm:
                for k, v in mm['fields'].items():
                    acc.setdefault(k, dict(v, inheritedFrom=mx))
        return acc

    # related / comodel-less relational fields: walk the related path to find the target model
    def find_field(model, fname, seen=()):
        m = models.get(model)
        if not m or model in seen:
            return None
        if fname in m['fields']:
            return m['fields'][fname]
        for mx in m['mixins']:
            f = find_field(mx, fname, seen + (model,))
            if f:
                return f
        for parent in m['delegates']:
            f = find_field(parent, fname, seen + (model,))
            if f:
                return f
        return None

    def related_target(model, path, depth=0):
        cur = model
        f = None
        for seg in path.split('.'):
            f = find_field(cur, seg)
            if not f or depth > 8:
                return None
            if f['odooType'] in RELATIONAL:
                cur = f.get('comodel') or (related_target(cur, f['related'], depth + 1) if isinstance(f.get('related'), str) else None)
                if not cur:
                    return None
            else:
                cur = None
        return cur if f and f['odooType'] in RELATIONAL else None

    for name, m in models.items():
        for fname, f in m['fields'].items():
            if f['odooType'] in RELATIONAL and not f.get('comodel') and isinstance(f.get('related'), str):
                t = related_target(name, f['related'])
                if t:
                    f['comodel'] = t
                    f['comodelFromRelated'] = True

    # 2. XML: views, actions, menus, groups, rules, crons, sequences, server actions
    recs, menus = [], []
    for addon in order:
        for p in xmlfiles[addon]:
            r, mn = xml_records(p, proj_rel(p), addon, errors)
            recs += r
            menus += mn
    model_xmlid = {}
    for n in models:
        model_xmlid['model_' + n.replace('.', '_')] = n
    def model_of_ref(ref):
        if not ref:
            return None
        return model_xmlid.get(ref.split('.')[-1], ref)

    screens = [view_info(r, model_xmlid) for r in recs if r['model'] == 'ir.ui.view']
    actions = {}
    for r in recs:
        if r['model'] == 'ir.actions.act_window':
            f = r['fields']
            actions[r['id']] = {'id': r['id'], 'name': f.get('name') if isinstance(f.get('name'), str) else None,
                                'resModel': f.get('res_model') if isinstance(f.get('res_model'), str) else None,
                                'viewMode': f.get('view_mode') if isinstance(f.get('view_mode'), str) else None,
                                'domain': (f.get('domain') or {}).get('eval') if isinstance(f.get('domain'), dict) else f.get('domain'),
                                'context': (f.get('context') or {}).get('eval') if isinstance(f.get('context'), dict) else f.get('context'),
                                'addon': r['addon'], 'file': r['file']}
    for mn in menus:
        act = actions.get(mn['action']) if mn['action'] else None
        mn['resModel'] = act['resModel'] if act else None
    groups, rules, timers, sequences, server_actions = {}, [], [], [], []
    for r in recs:
        f = r['fields']
        def fv(k):
            v = f.get(k)
            return v if isinstance(v, str) else (v.get('ref') or v.get('eval')) if isinstance(v, dict) and 'xml' not in v else None
        if r['model'] == 'res.groups':
            groups[r['id']] = {'id': r['id'], 'name': fv('name'), 'category': fv('category_id'),
                               'implies': [qual(x, r['addon']) for x in REF_RE.findall(fv('implied_ids') or '')],
                               'comment': fv('comment'), 'addon': r['addon'], 'file': r['file'], 'acl': [], 'rules': []}
        elif r['model'] == 'ir.rule':
            rules.append({'id': r['id'], 'name': fv('name'), 'model': model_of_ref(fv('model_id')), 'domain': fv('domain_force'),
                          'groups': [qual(x, r['addon']) for x in REF_RE.findall(fv('groups') or '')],
                          'perms': {k: fv(k) for k in ('perm_read', 'perm_write', 'perm_create', 'perm_unlink') if fv(k) is not None},
                          'addon': r['addon'], 'file': r['file']})
        elif r['model'] == 'ir.cron':
            timers.append({'type': 'timer', 'linkId': 'odoo:timer:' + r['id'], 'uniqueId': r['id'], 'name': fv('name') or r['id'],
                           'module': r['addon'], 'model': model_of_ref(fv('model_id')), 'code': fv('code'),
                           'interval': '%s %s' % (fv('interval_number') or '1', fv('interval_type') or ''),
                           'active': fv('active'), '_source': r['file'], 'sourceRef': r['file'], '_gaps': [], '_links': []})
        elif r['model'] == 'ir.sequence':
            sequences.append({'id': r['id'], 'name': fv('name'), 'code': fv('code'), 'prefix': fv('prefix'),
                              'padding': fv('padding'), 'addon': r['addon'], 'file': r['file']})
        elif r['model'] == 'ir.actions.server':
            server_actions.append({'id': r['id'], 'name': fv('name'), 'model': model_of_ref(fv('model_id')),
                                   'state': fv('state'), 'code': fv('code'), 'addon': r['addon'], 'file': r['file']})
    # ACL csv
    acl_rows = []
    for addon in order:
        for p in csvfiles[addon]:
            with open(p, encoding='utf-8') as fh:
                for row in csv.DictReader(fh):
                    gid = row.get('group_id:id') or ''
                    acl_rows.append({'id': qual(row.get('id'), addon), 'model': model_of_ref(row.get('model_id:id')),
                                     'group': qual(gid, addon) if gid else None,
                                     'read': row.get('perm_read') == '1', 'write': row.get('perm_write') == '1',
                                     'create': row.get('perm_create') == '1', 'unlink': row.get('perm_unlink') == '1',
                                     'addon': addon, 'file': proj_rel(p)})
    for row in acl_rows:
        g = groups.get(row['group']) if row['group'] else None
        if g is None:
            key = row['group'] or '(all users)'
            g = groups.setdefault(key, {'id': key, 'name': None, 'category': None, 'implies': [], 'comment': None,
                                        'addon': None, 'file': None, 'acl': [], 'rules': [], 'definedOutsideImport': bool(row['group'])})
        g['acl'].append({k: row[k] for k in ('model', 'read', 'write', 'create', 'unlink', 'id')})
    for ru in rules:
        for gid in ru['groups'] or ['(all users)']:
            g = groups.setdefault(gid, {'id': gid, 'name': None, 'category': None, 'implies': [], 'comment': None, 'addon': None,
                                        'file': None, 'acl': [], 'rules': [], 'definedOutsideImport': gid != '(all users)'})
            g['rules'].append({'model': ru['model'], 'name': ru['name'], 'domain': ru['domain'], 'perms': ru['perms']})

    # 3. Emit KB items
    entities, structures, statics, logics, workflows, ext = [], [], [], [], [], []
    xref = {}
    screens_by_model = defaultdict(list)
    for s in screens:
        if s['model']:
            screens_by_model[s['model']].append(s['uniqueId'])
    menus_by_model = defaultdict(list)
    for mn in menus:
        if mn['resModel']:
            menus_by_model[mn['resModel']].append(mn['name'])
    acl_by_model = defaultdict(list)
    for row in acl_rows:
        acl_by_model[row['model']].append(row['group'] or '(all users)')
    for name, m in models.items():
        addon = m['origin'] or (m['extendedBy'][0] if m['extendedBy'] else None)
        cap = capability(name, m['origin'] or addon)
        if m['kind'] == 'external':
            ext.append({'type': 'ext-entity', 'linkId': 'odoo:ext:' + name, 'uniqueId': name, 'name': name, 'label': name,
                        'module': addon, 'reason': 'defined in an addon that was not imported (Stage 0: declared not implemented)',
                        'extendedBy': m['extendedBy'], 'fields': list(m['fields']), '_source': m['files'][0], 'sourceRef': m['files'][0],
                        '_gaps': [], '_links': []})
            continue
        inh = inherited_fields(name)
        allf = OrderedDict()
        for k, v in m['fields'].items():
            allf[k] = v
        for k, v in inh.items():
            allf.setdefault(k, v)
        attributes, assocs = [], []
        for fn_, f in allf.items():
            en = enum_name_for(name, fn_) if f['odooType'] == 'Selection' else None
            stored = not ((f.get('compute') or f.get('related')) and f.get('store') is not True)
            if f['odooType'] in RELATIONAL:
                assocs.append({'name': fn_, 'odooType': f['odooType'], 'target': f.get('comodel'), 'inverseName': f.get('inverse_name'),
                               'required': f.get('required') is True, 'ondelete': f.get('ondelete'), 'stored': stored,
                               'compute': f.get('compute'), 'related': f.get('related'), 'label': f.get('string'),
                               'definedIn': f.get('definedIn'), 'inheritedFrom': f.get('inheritedFrom'),
                               'mendixKind': {'Many2one': 'Reference', 'Many2many': 'ReferenceSet', 'One2many': 'inverse of Reference'}[f['odooType']]})
                if f['odooType'] == 'Many2one':
                    attributes.append({'name': fn_, 'type': '%s Identifier' % f.get('comodel'), 'odooType': 'Many2one',
                                       'mendixType': 'Reference', 'isMandatory': f.get('required') is True, 'isAutoNumber': False,
                                       'isForeignKey': True, 'referencedEntity': f.get('comodel'), 'deleteRule': f.get('ondelete') or '',
                                       'length': '', 'label': f.get('string'), 'stored': stored, 'definedIn': f.get('definedIn'),
                                       'inheritedFrom': f.get('inheritedFrom')})
                continue
            att = {'name': fn_, 'type': f['odooType'], 'odooType': f['odooType'], 'mendixType': mendix_type(f, en),
                   'isMandatory': f.get('required') is True, 'isAutoNumber': False, 'isForeignKey': False, 'referencedEntity': '',
                   'deleteRule': '', 'length': f.get('size') or '', 'label': f.get('string'), 'stored': stored,
                   'compute': f.get('compute'), 'related': f.get('related'), 'default': f.get('default'),
                   'help': f.get('help'), 'definedIn': f.get('definedIn'), 'inheritedFrom': f.get('inheritedFrom'),
                   'redefinedIn': f.get('redefinedIn')}
            if en:
                att['enumeration'] = en
                st = {'type': 'staticEntity', 'linkId': 'odoo:enum:' + en, 'uniqueId': en, 'name': en, 'label': f.get('string') or fn_,
                      'module': f.get('definedIn'), 'model': name, 'field': fn_, 'selectionSource': f.get('selectionSource'),
                      'records': f.get('selection') or [], 'selectionAddedBy': f.get('selectionAddedBy', []),
                      'capability': cap, 'inScope': cap in IN_SCOPE,
                      '_source': f.get('file'), 'sourceRef': f.get('file'), '_gaps': [], '_links': []}
                if not f.get('selection') and f.get('selectionSource', '').startswith(('method', 'lambda', 'call', 'attr', 'unresolved')):
                    st['_gaps'].append('dynamic selection (%s) — values computed at runtime; BRD-only' % f.get('selectionSource'))
                if not f.get('inheritedFrom'):
                    statics.append(st)
            attributes.append(att)
        item = {'type': 'entity' if m['kind'] == 'persistent' else 'structure',
                'linkId': 'odoo:%s:%s' % ('entity' if m['kind'] == 'persistent' else 'structure', name),
                'uniqueId': name, 'name': name, 'label': m['description'] or name, 'description': m['description'],
                'module': m['origin'], 'odooKind': m['kind'], 'capability': cap, 'capabilityName': CAP_NAMES[cap],
                'inScope': cap in IN_SCOPE, 'isStatic': False, 'isPublic': True, 'isMultitenant': 'company_id' in allf,
                'isPersistent': m['kind'] == 'persistent', 'deleteRule': '', 'order': m['order'], 'recName': m['recName'],
                'mixins': m['mixins'], 'delegates': m['delegates'], 'extendedBy': m['extendedBy'],
                'attributes': attributes, 'associations': assocs, 'indexes': [],
                'sqlConstraints': [{'name': c[0], 'definition': c[1] if len(c) > 1 else None, 'message': c[2] if len(c) > 2 else None}
                                   for c in m['sqlConstraints']],
                'ownFieldCount': len(m['fields']), 'inheritedFieldCount': len(allf) - len(m['fields']),
                '_source': m['files'][0], 'sourceRef': m['files'][0], 'files': m['files'], '_gaps': [], '_links': []}
        for asc in assocs:
            if asc['target'] and asc['target'] not in models:
                item['_gaps'].append('association %s -> %s: target model not in imported source' % (asc['name'], asc['target']))
        for mx in m['mixins']:
            if mx not in models or models[mx]['kind'] == 'external':
                item['_gaps'].append('mixin %s not in imported source (its fields are absent)' % mx)
        (entities if m['kind'] == 'persistent' else structures).append(item)
        for me in m['methods']:
            logics.append({'type': 'logic', 'logicKind': 'action', 'odooMethodKind': me['kind'],
                           'linkId': 'odoo:logic:%s.%s:%s' % (name, me['name'], me['addon']),
                           'uniqueId': '%s.%s@%s' % (name, me['name'], me['addon']), 'name': me['name'], 'label': me['name'],
                           'description': me['doc'], 'module': me['addon'], 'model': name, 'capability': cap, 'inScope': cap in IN_SCOPE,
                           'isPublic': not me['name'].startswith('_'), 'decorators': me['decorators'],
                           'inputParameters': [{'name': p, 'type': 'unknown', 'isMandatory': True} for p in me['params']],
                           'outputParameters': [], 'calls': [{'name': c} for c in me['calls']], 'aggregates': [],
                           'throwsExceptions': me['raises'], 'writesState': me['writesState'],
                           '_source': me['file'], 'sourceRef': '%s:%s-%s' % (me['file'], me['line'], me['endLine']),
                           '_gaps': [], '_links': []})
        # state machine
        for sf in ('state',):
            if sf in m['fields'] and m['fields'][sf]['odooType'] == 'Selection':
                trans = [{'method': me['name'], 'addon': me['addon'], 'to': s} for me in m['methods'] for s in me['writesState']]
                workflows.append({'type': 'workflow', 'linkId': 'odoo:workflow:%s.%s' % (name, sf), 'uniqueId': '%s.%s' % (name, sf),
                                  'name': '%s lifecycle' % name, 'label': '%s %s' % (name, sf), 'module': m['origin'], 'model': name,
                                  'field': sf, 'capability': cap, 'inScope': cap in IN_SCOPE,
                                  'states': m['fields'][sf].get('selection') or [], 'transitions': trans,
                                  '_source': m['files'][0], 'sourceRef': m['files'][0],
                                  '_gaps': ['transitions inferred from state writes in method bodies; guards/side effects are BRD-only'],
                                  '_links': []})
        xref[name] = {'capability': cap, 'inScope': cap in IN_SCOPE, 'origin': m['origin'], 'extendedBy': m['extendedBy'],
                      'screens': screens_by_model.get(name, []), 'menus': menus_by_model.get(name, []),
                      'aclGroups': sorted(set(acl_by_model.get(name, []))), 'logicCount': len(m['methods'])}
    for s in screens:
        mm = s['model']
        cap = capability(mm, models[mm]['origin'] or s['module']) if mm in models else 'C12'
        s['capability'] = cap
        s['inScope'] = cap in IN_SCOPE
        if mm and mm not in models:
            s['_gaps'].append('view model %s not in imported source' % mm)
    roles = []
    for gid, g in groups.items():
        roles.append({'type': 'role', 'linkId': 'odoo:role:' + gid, 'uniqueId': gid, 'name': g['name'] or gid, 'label': g['name'] or gid,
                      'module': g['addon'], 'category': g['category'], 'implies': g['implies'], 'description': g['comment'] or '',
                      'acl': g['acl'], 'recordRules': g['rules'], 'definedOutsideImport': g.get('definedOutsideImport', False),
                      '_source': g['file'], 'sourceRef': g['file'], '_gaps': [], '_links': []})
    apis = []
    for addon in order:
        cdir = os.path.join(srcroot, addon, 'controllers')
        if not os.path.isdir(cdir):
            continue
        for f in sorted(os.listdir(cdir)):
            if not f.endswith('.py') or f == '__init__.py':
                continue
            p = os.path.join(cdir, f)
            try:
                tree = ast.parse(open(p, encoding='utf-8').read())
            except Exception as e:
                errors.append({'file': proj_rel(p), 'error': str(e)})
                continue
            for fn in [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]:
                for d in fn.decorator_list:
                    if isinstance(d, ast.Call) and src(d.func) in ('http.route', 'route'):
                        if not d.args and not any(k.arg == 'route' for k in d.keywords):
                            routes = [None]  # override of an inherited route: path comes from the parent controller
                        else:
                            routes = lit(d.args[0]) if d.args else lit(next((k.value for k in d.keywords if k.arg == 'route'), None))
                            routes = routes if isinstance(routes, list) else [routes]
                        kw = {k.arg: lit(k.value) for k in d.keywords}
                        for rt in routes:
                            apis.append({'type': 'serviceApi', 'linkId': 'odoo:api:%s:%s' % (addon, rt), 'uniqueId': '%s %s' % (addon, rt or fn.name),
                                         'name': fn.name, 'label': rt or '(inherited route) ' + fn.name, 'module': addon, 'path': rt,
                                         'overridesInheritedRoute': rt is None, 'methods': kw.get('methods'),
                                         'auth': kw.get('auth'), 'routeType': kw.get('type'), 'capability': 'C12', 'inScope': False,
                                         'note': 'portal/download endpoints — out of scope (portal declared not implemented)',
                                         '_source': proj_rel(p), 'sourceRef': '%s:%s' % (proj_rel(p), fn.lineno), '_gaps': [], '_links': []})

    # 3b. Secondary readers: manifests, __init__ imports, demo/data seed records, csv templates,
    #     report actions, migrations — so every file the extractor reads is named with its yield.
    file_yield = OrderedDict()
    def y(path, what):
        file_yield.setdefault(proj_rel(path), []).append(what)
    addons_out = []
    for addon in order:
        m = manifests[addon]
        mp = os.path.join(srcroot, addon, '__manifest__.py')
        addons_out.append({'addon': addon, 'name': m.get('name'), 'summary': m.get('summary'), 'category': m.get('category'),
                           'depends': m.get('depends', []), 'missingDepends': [d for d in m.get('depends', []) if d not in manifests],
                           'data': m.get('data', []), 'demo': m.get('demo', []), 'license': m.get('license'),
                           'manifest': proj_rel(mp)})
        y(mp, 'manifest: %s, depends %s' % (m.get('name'), ', '.join(m.get('depends', [])) or '-'))
    for addon in order:
        for p in pyfiles[addon]:
            n_cls = sum(1 for c in classes if c['file'] == proj_rel(p))
            if n_cls:
                y(p, '%d model class(es): %s' % (n_cls, ', '.join(sorted({c['model'] for c in classes if c['file'] == proj_rel(p)}))[:300]))
            else:
                try:
                    t = ast.parse(open(p, encoding='utf-8').read())
                    defs = [n.name for n in t.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))]
                except Exception:
                    defs = []
                y(p, 'no registered model; module-level helpers: %s' % (', '.join(defs[:15]) or '(none)'))
    seed = []
    for r in recs:
        f = r['fields']
        if r['model'] in ('ir.ui.view', 'ir.actions.act_window', 'res.groups', 'ir.rule', 'ir.cron', 'ir.sequence', 'ir.actions.server', 'qweb.template'):
            continue
        sub = r['file'].split('/')[4] if len(r['file'].split('/')) > 4 else ''
        seed.append({'id': r['id'], 'model': r['model'], 'kind': 'demo' if sub == 'demo' else 'data', 'addon': r['addon'], 'file': r['file'],
                     'values': {k: (v if isinstance(v, str) or v is None else (v.get('ref') or v.get('eval'))) for k, v in f.items()
                                if not (isinstance(v, dict) and 'xml' in v)}})
    reports_out = [{'id': x['id'], 'name': x['values'].get('name'), 'model': x['values'].get('model'), 'reportName': x['values'].get('report_name'),
                    'reportType': x['values'].get('report_type'), 'file': x['file']} for x in seed if x['model'] == 'ir.actions.report']
    by_file = defaultdict(lambda: defaultdict(int))
    for x in seed:
        by_file[x['file']][x['model']] += 1
    for r in recs:
        if r['model'] in ('ir.ui.view', 'ir.actions.act_window', 'res.groups', 'ir.rule', 'ir.cron', 'ir.sequence', 'ir.actions.server', 'qweb.template'):
            by_file[r['file']][r['model']] += 1
    for mn in menus:
        by_file[mn['file']]['menuitem'] += 1
    for addon in order:
        for p in xmlfiles[addon]:
            c = by_file.get(proj_rel(p))
            y(p, 'records: ' + (', '.join('%s x%d' % (k, v) for k, v in sorted(c.items())) if c else '(none)'))
        for p in csvfiles[addon]:
            y(p, 'ACL rows: %d' % sum(1 for row in acl_rows if row['file'] == proj_rel(p)))
    csv_templates = []
    for addon in order:
        for p in other_files[addon]:
            rel = proj_rel(p)
            fn = os.path.basename(p)
            if fn == '__init__.py':
                t = open(p, encoding='utf-8').read()
                imps = re.findall(r'^from \. import (.+)$|^from \.(\w+) import', t, re.M)
                names = sorted({x.strip() for a_, b_ in imps for x in (a_ or b_).split(',') if x.strip()})
                y(p, 'imports: ' + (', '.join(names) or '(none)'))
            elif fn.endswith('.csv'):
                with open(p, encoding='utf-8') as fh:
                    rows = list(csv.reader(fh))
                model = fn.split('-')[0]
                csv_templates.append({'file': rel, 'model': model, 'columns': rows[0] if rows else [], 'rows': max(len(rows) - 1, 0)})
                y(p, 'template csv: %s, %d rows, columns %s' % (model, max(len(rows) - 1, 0), ', '.join((rows[0] if rows else [])[:8])))
            elif '/migrations/' in rel and fn.endswith('.py'):
                t = open(p, encoding='utf-8').read()
                y(p, 'migration script (data upgrade, not ported): defines %s' % ', '.join(re.findall(r'^def (\w+)', t, re.M)))
            elif '/demo/' in rel and fn.endswith('.py'):
                t = open(p, encoding='utf-8').read()
                y(p, 'demo data generator: %s' % ', '.join(re.findall(r'^\s+def (\w+)', t, re.M)[:10]))
    for a_ in apis:
        y(os.path.join(srcroot, '..', '..', '..', a_['_source']), 'http route %s' % (a_['path'] or '(inherited) ' + a_['name']))

    # 4. Write
    ext_dir = os.path.join(out, 'extracted')
    rep_dir = os.path.join(out, 'reports')
    os.makedirs(ext_dir, exist_ok=True)
    os.makedirs(rep_dir, exist_ok=True)

    def w(name, data, d=out):
        with open(os.path.join(d, name), 'w', encoding='utf-8') as fh:
            json.dump(data, fh, indent=1, ensure_ascii=False, default=str)
    raw_items = entities + structures + statics + logics + screens + roles + timers + apis + workflows + ext
    w('odoo-odoo.json', {'source': 'odoo', 'items': raw_items, 'errors': errors,
                         'meta': {'addons': order, 'pyFiles': sum(len(v) for v in pyfiles.values()),
                                  'xmlFiles': sum(len(v) for v in xmlfiles.values()), 'csvFiles': sum(len(v) for v in csvfiles.values())}}, ext_dir)
    w('entities.json', entities)
    w('structures.json', structures)
    w('staticEntities.json', statics)
    w('logics.json', logics)
    w('screens.json', screens)
    w('webBlocks.json', [])
    w('webFlows.json', [])
    w('workflows.json', workflows)
    w('dataScreenActions.json', [])
    w('serviceApis.json', apis)
    w('extEntities.json', ext)
    w('exceptions.json', [])
    w('timers.json', timers)
    w('roles.json', roles)
    w('menus.json', menus)
    w('actions.json', list(actions.values()))
    w('sequences.json', sequences)
    w('serverActions.json', server_actions)
    w('recordRules.json', rules)
    w('acl.json', acl_rows)
    w('cross-reference-map.json', xref)
    w('addons.json', addons_out)
    w('seedData.json', seed)
    w('reports.json', reports_out)
    w('csvTemplates.json', csv_templates)
    w('source-files.json', [{'file': k, 'yield': v} for k, v in file_yield.items()], ext_dir)

    # reports
    def cnt(items, pred=lambda i: True):
        return sum(1 for i in items if pred(i))
    insc = lambda i: i.get('inScope')
    lines = ['# Odoo extraction summary', '', 'Source: `%s` (addons in dependency order: %s)' % (srcroot, ', '.join(order)), '',
             '| Type | File | Items | In scope (C1–C8) |', '|---|---|---|---|']
    for lbl, fname, items in (('Entities (persistent models)', 'entities.json', entities),
                              ('Structures (transient + abstract models)', 'structures.json', structures),
                              ('Static entities (selection enumerations)', 'staticEntities.json', statics),
                              ('Logic (model methods)', 'logics.json', logics), ('Screens (views)', 'screens.json', screens),
                              ('Workflows (state machines)', 'workflows.json', workflows), ('Roles (groups)', 'roles.json', roles),
                              ('Timers (ir.cron)', 'timers.json', timers), ('Service APIs (http routes)', 'serviceApis.json', apis),
                              ('External entities (not imported)', 'extEntities.json', ext)):
        lines.append('| %s | `%s` | %d | %s |' % (lbl, fname, len(items), cnt(items, insc) if items and 'inScope' in items[0] else '—'))
    lines += ['', 'Extras: %d menus, %d window actions, %d sequences, %d server actions, %d record rules, %d ACL rows.' %
              (len(menus), len(actions), len(sequences), len(server_actions), len(rules), len(acl_rows)),
              '', 'Parse errors: %d' % len(errors)] + ['- `%s`: %s' % (e['file'], e['error']) for e in errors]
    lines += ['', '## Per capability', '', '| Capability | Entities | Structures | Enumerations | Logic | Screens |', '|---|---|---|---|---|---|']
    for c in CAP_NAMES:
        f = lambda i: i.get('capability') == c
        lines.append('| %s %s%s | %d | %d | %d | %d | %d |' % (c, CAP_NAMES[c], '' if c in IN_SCOPE else ' (deferred)', cnt(entities, f),
                                                         cnt(structures, f), cnt(statics, f), cnt(logics, f), cnt(screens, f)))
    summary = '\n'.join(lines) + '\n'
    open(os.path.join(rep_dir, 'summary.md'), 'w').write(summary)
    open(os.path.join(out, 'summary.md'), 'w').write(summary)
    gl = ['# Gaps report', '', 'Unresolved references point at addons declared not implemented at Stage 0.', '']
    gap_targets = defaultdict(list)
    for e in entities + structures:
        for g in e['_gaps']:
            gap_targets[e['name']].append(g)
    for k in sorted(gap_targets):
        gl.append('- **%s**: %s' % (k, '; '.join(gap_targets[k])))
    gl += ['', '## Models only extended here (origin addon not imported)', ''] + ['- `%s` (extended by %s)' % (e['name'], ', '.join(e['extendedBy'])) for e in ext]
    dyn = [s for s in statics if s['_gaps']]
    gl += ['', '## Dynamic selections (%d) — values are BRD-only' % len(dyn), ''] + ['- `%s` (%s)' % (s['name'], s['selectionSource']) for s in dyn]
    open(os.path.join(rep_dir, 'gaps-report.md'), 'w').write('\n'.join(gl) + '\n')
    cl = ['# Coverage report', '', '| Addon | Python files | XML files | Models defined | Models extended |', '|---|---|---|---|---|']
    for addon in order:
        cl.append('| %s | %d | %d | %d | %d |' % (addon, len(pyfiles[addon]), len(xmlfiles[addon]),
                                                  sum(1 for m in models.values() if m['origin'] == addon),
                                                  sum(1 for m in models.values() if addon in m['extendedBy'])))
    open(os.path.join(rep_dir, 'coverage-report.md'), 'w').write('\n'.join(cl) + '\n')
    print(summary)
    return 0


if __name__ == '__main__':
    sys.exit(main())
