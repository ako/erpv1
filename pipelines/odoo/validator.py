#!/usr/bin/env python3
"""Validator for the Odoo extractor (extractor-quality-loop.md).

Derives ground truth from the source with a DIFFERENT mechanism than extractor.py:
line-oriented regex and paren counting over raw text — no `ast`, no ElementTree, no csv module.
Then compares against the knowledge base and writes extraction-quality.json.

Odoo-shaped dimensions (declared here, per the skill's "replace the dimensions, keep the contract"):
  entityFields   every `x = fields.T(` declared in a model class is captured on that model
  typeAccuracy   captured field has the same Odoo type (and hence Mendix type) as the source
  associations   every relational field is captured with the right target model
  enumerations   every static Selection (incl. selection_add) has exactly the source's values
  views          every ir.ui.view record is a screen
  menus          every <menuitem> is captured
  security       ACL csv rows + ir.rule records + res.groups records captured
  endpoints      every @http.route path captured
  timers         every ir.cron record captured
The toolkit's `testCoverage` dimension is not scored: tests/ were excluded at import (SOURCE.md).

Usage: validator.py --source sources/odoo/addons --kb analysis/odoo/knowledge-base --out <dir>
Exit 0 when overall >= 95, else 1.
"""
import argparse, glob, json, os, re, sys
from collections import defaultdict
from datetime import datetime, timezone

THRESHOLD = 95.0
CLASS_RE = re.compile(r'^class\s+\w+\s*\(([^)]*)\)\s*:', re.M)
NAME_RE = re.compile(r'^    _name\s*=\s*[\'"]([\w.]+)[\'"]', re.M)
INH_RE = re.compile(r'^    _inherit\s*=\s*(?:\[\s*)?[\'"]([\w.]+)[\'"]', re.M)
FIELD_RE = re.compile(r'^    (\w+)(?:\s*:\s*[\w.\[\]]+)?\s*=\s*fields\.(\w+)\(', re.M)  # incl. `x: Model = fields.T(`
VAL_RE = re.compile(r'\(\s*[\'"]([\w.\-/ ]+)[\'"]\s*,')
CONST_RE = r'^{name}\s*=\s*[\[\(]'


def call_text(text, start):
    """Text of a call starting at the '(' at/after start, by paren counting (strings ignored crudely)."""
    i = text.index('(', start)
    depth, j, q = 0, i, None
    while j < len(text):
        ch = text[j]
        if q:
            if ch == '\\':
                j += 2
                continue
            if ch == q:
                q = None
        elif ch in '\'"':
            q = ch
        elif ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
            if depth == 0:
                return text[i + 1:j]
        j += 1
    return text[i + 1:]


def bracket_text(text, i):
    """Text of a [...] or (...) literal starting at index i."""
    open_ch = text[i]
    close = {'[': ']', '(': ')'}[open_ch]
    depth, j, q = 0, i, None
    while j < len(text):
        ch = text[j]
        if q:
            if ch == q:
                q = None
        elif ch in '\'"':
            q = ch
        elif ch == open_ch:
            depth += 1
        elif ch == close:
            depth -= 1
            if depth == 0:
                return text[i:j + 1]
        j += 1
    return text[i:]


def top_level_list_values(lst):
    """Values of the first element of each top-level tuple in a list literal text."""
    vals, depth, q, k = [], 0, None, 0
    while k < len(lst):
        ch = lst[k]
        if q:
            if ch == q:
                q = None
        elif ch in '\'"':
            q = ch
        elif ch in '[(':
            depth += 1
            if ch == '(' and depth == 2:
                m = re.match(r'\(\s*[\'"]([^\'"]+)[\'"]', lst[k:])
                if m:
                    vals.append(m.group(1))
        elif ch in '])':
            depth -= 1
        k += 1
    return vals


def model_python_files(src):
    out = []
    for p in sorted(glob.glob(os.path.join(src, '*', '**', '*.py'), recursive=True)):
        parts = os.path.relpath(p, src).split(os.sep)
        if parts[1] in ('controllers', 'migrations', 'tests', 'demo') or parts[-1] in ('__init__.py', '__manifest__.py'):
            continue
        out.append(p)
    return out


def ground_truth(src):
    files = model_python_files(src)
    alltext = {p: open(p, encoding='utf-8').read() for p in files}
    consts = {}
    fields = defaultdict(dict)      # model -> field -> {type, target, selection(set)|None, dynamic}
    for p, text in alltext.items():
        starts = [m.start() for m in CLASS_RE.finditer(text)] + [len(text)]
        for a, b in zip(starts, starts[1:]):
            block = text[a:b]
            head = CLASS_RE.match(block).group(1)
            if not re.search(r'models\.(Model|TransientModel|AbstractModel)\b|\bModel\b', head):
                continue
            nm = NAME_RE.search(block)
            ih = INH_RE.search(block)
            model = nm.group(1) if nm else (ih.group(1) if ih else None)
            if not model:
                continue
            for fm in FIELD_RE.finditer(block):
                fname, ftype = fm.group(1), fm.group(2)
                body = re.sub(r'(?m)^(\s*)#[^\n]*$|\s#\s[^\n\'"]*$', r'\1', call_text(block, fm.end() - 1))
                rec = fields[model].setdefault(fname, {'type': ftype, 'target': None, 'selection': None, 'dynamic': False,
                                                       'file': os.path.relpath(p, src)})
                rec['type'] = ftype
                if ftype in ('Many2one', 'One2many', 'Many2many'):
                    t = re.match(r'\s*[\'"]([\w.]+)[\'"]', body) or re.search(r'comodel_name\s*=\s*[\'"]([\w.]+)[\'"]', body)
                    if t:
                        rec['target'] = t.group(1)
                if ftype == 'Selection':
                    for kw in ('', 'selection=', 'selection_add='):
                        if kw == '':
                            m = re.match(r'\s*(\[|[A-Z_][A-Z0-9_]*\b|[\'"]|lambda|\w)', body)
                        else:
                            m = re.search(r'\b' + kw + r'\s*(\[|[A-Z_][A-Z0-9_]*\b|[\'"]|lambda|\w)', body)
                        if not m:
                            continue
                        tok = m.group(1)
                        if tok == '[':
                            vals = top_level_list_values(bracket_text(body, m.end() - 1))
                        elif re.fullmatch(r'[A-Z_][A-Z0-9_]*', tok):
                            vals = None
                            for pp, tt in alltext.items():
                                cm = re.search(CONST_RE.format(name=tok), tt, re.M)
                                if cm:
                                    vals = top_level_list_values(bracket_text(tt, cm.end() - 1))
                                    break
                            if vals is None:
                                rec['dynamic'] = True
                                continue
                        else:
                            if kw != 'selection_add=':
                                rec['dynamic'] = True
                            continue
                        rec['selection'] = (rec['selection'] or set()) | set(vals)
                        if kw == '':
                            break
    # resolve related= paths for relational fields without a literal comodel (text-level walk)
    meta = defaultdict(lambda: {'parents': []})
    for p, text in alltext.items():
        starts = [m.start() for m in CLASS_RE.finditer(text)] + [len(text)]
        for a, b in zip(starts, starts[1:]):
            block = text[a:b]
            nm = NAME_RE.search(block)
            ih = re.search(r'^    _inherit\s*=\s*(\[[^\]]*\]|[\'"][\w.]+[\'"])', block, re.M)
            parents = re.findall(r'[\'"]([\w.]+)[\'"]', ih.group(1)) if ih else []
            model = nm.group(1) if nm else (parents[0] if parents else None)
            if not model:
                continue
            dl = re.search(r'^    _inherits\s*=\s*\{([^}]*)\}', block, re.M)
            if dl:
                parents += re.findall(r'[\'"]([\w.]+)[\'"]\s*:', dl.group(1))
            meta[model]['parents'] += [x for x in parents if x != model]
            for fm in FIELD_RE.finditer(block):
                body = call_text(block, fm.end() - 1)
                r = re.search(r'related\s*=\s*[\'"]([\w.]+)[\'"]', body)
                if r and fm.group(1) in fields[model]:
                    fields[model][fm.group(1)]['related'] = r.group(1)

    def lookup(model, fname, seen=()):
        if model in seen:
            return None
        if fname in fields.get(model, {}):
            return fields[model][fname]
        for par in meta[model]['parents']:
            r = lookup(par, fname, seen + (model,))
            if r:
                return r
        return None

    def walk(model, path, depth=0):
        cur, rec = model, None
        for seg in path.split('.'):
            rec = lookup(cur, seg)
            if not rec or depth > 8:
                return None
            if rec['type'] in ('Many2one', 'One2many', 'Many2many'):
                cur = rec['target'] or (walk(cur, rec['related'], depth + 1) if rec.get('related') else None)
                if not cur:
                    return None
        return cur if rec and rec['type'] in ('Many2one', 'One2many', 'Many2many') else None

    def breaks_outside(model, path):
        """True when the related path leaves the imported source (a segment defined nowhere we have)."""
        cur = model
        for seg in path.split('.'):
            rec = lookup(cur, seg)
            if not rec:
                return True
            if rec['type'] in ('Many2one', 'One2many', 'Many2many'):
                cur = rec['target'] or (walk(cur, rec['related']) if rec.get('related') else None)
                if not cur:
                    return rec.get('external', False) or not rec.get('related')
        return False

    for model, flds in fields.items():
        for fname, rec in flds.items():
            if rec['type'] in ('Many2one', 'One2many', 'Many2many') and not rec['target'] and rec.get('related'):
                rec['target'] = walk(model, rec['related'])
    for model, flds in fields.items():
        for fname, rec in flds.items():
            if rec['type'] in ('Many2one', 'One2many', 'Many2many') and not rec['target']:
                rec['external'] = (not rec.get('related')) or breaks_outside(model, rec['related'])
    # XML (regex, no parser)
    views, menus, groups, rules, crons = set(), 0, set(), 0, 0
    for p in sorted(glob.glob(os.path.join(src, '*', '**', '*.xml'), recursive=True)):
        parts = os.path.relpath(p, src).split(os.sep)
        if parts[1] not in ('views', 'wizard', 'report', 'security', 'data'):
            continue
        addon = parts[0]
        t = open(p, encoding='utf-8').read()
        t = re.sub(r'<!--.*?-->', '', t, flags=re.S)
        for m in re.finditer(r'<record\s+[^>]*>', t):
            tag = m.group(0)
            mid = re.search(r'\bid="([^"]+)"', tag)
            mod = re.search(r'\bmodel="([^"]+)"', tag)
            if not mid or not mod:
                continue
            xid = mid.group(1) if '.' in mid.group(1) else addon + '.' + mid.group(1)
            if mod.group(1) == 'ir.ui.view':
                views.add(xid)
            elif mod.group(1) == 'res.groups':
                groups.add(xid)
            elif mod.group(1) == 'ir.rule':
                rules += 1
            elif mod.group(1) == 'ir.cron':
                crons += 1
        menus += len(re.findall(r'<menuitem\b', t))
    acl = 0
    for p in glob.glob(os.path.join(src, '*', 'security', 'ir.model.access.csv')):
        acl += sum(1 for ln in open(p, encoding='utf-8').read().splitlines()[1:] if ln.strip())
    routes = 0
    for p in glob.glob(os.path.join(src, '*', 'controllers', '*.py')):
        t = open(p, encoding='utf-8').read()
        for m in re.finditer(r'@(?:http\.)?route\(', t):
            body = call_text(t, m.end() - 1).strip()
            if body.startswith('['):
                routes += len(re.findall(r'[\'"](/[^\'"]*)[\'"]', bracket_text(body, 0)))
            else:
                routes += 1
    return fields, {'views': views, 'menus': menus, 'groups': groups, 'rules': rules, 'crons': crons, 'acl': acl, 'routes': routes}


def score(found, expected):
    return round(100.0 * found / expected, 2) if expected else None


def count_score(kb, expected):
    """For count-only dimensions: any disagreement in either direction costs score."""
    if not expected:
        return None
    return round(100.0 * min(kb, expected) / max(kb, expected), 2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', required=True)
    ap.add_argument('--kb', required=True)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    gt, xml = ground_truth(a.source)
    L = lambda n: json.load(open(os.path.join(a.kb, n), encoding='utf-8'))
    kb_models = {}
    for e in L('entities.json') + L('structures.json'):
        own = {}
        for at in e['attributes']:
            if not at.get('inheritedFrom'):
                own[at['name']] = {'type': at['odooType'], 'target': at.get('referencedEntity') or None}
        for asc in e['associations']:
            if not asc.get('inheritedFrom'):
                own[asc['name']] = {'type': asc['odooType'], 'target': asc['target']}
        kb_models[e['name']] = own
    for x in L('extEntities.json'):
        kb_models[x['name']] = {f: None for f in x['fields']}
    enums = {(s['model'], s['field']): {r['name'] for r in s['records']} for s in L('staticEntities.json')}

    dims, gaps = {}, defaultdict(list)
    external_rel = []
    # entityFields / typeAccuracy / associations / enumerations
    exp_f = fnd_f = exp_t = ok_t = exp_a = ok_a = exp_e = ok_e = 0
    for model, flds in gt.items():
        for fname, g in flds.items():
            exp_f += 1
            k = kb_models.get(model, {})
            if fname not in k:
                gaps['entityFields'].append('%s.%s missing' % (model, fname))
                continue
            fnd_f += 1
            kb = k[fname]
            if kb is None:      # external model: field names only
                exp_t += 1; ok_t += 1
                continue
            exp_t += 1
            if kb['type'] == g['type']:
                ok_t += 1
            else:
                gaps['typeAccuracy'].append('%s.%s: kb %s, source %s' % (model, fname, kb['type'], g['type']))
            if g['type'] in ('Many2one', 'One2many', 'Many2many') and g.get('external'):
                if kb['target']:
                    gaps['associations'].append('%s.%s: source target leaves the import, kb claims %s' % (model, fname, kb['target']))
                    exp_a += 1
                else:
                    external_rel.append('%s.%s' % (model, fname))
            elif g['type'] in ('Many2one', 'One2many', 'Many2many'):
                exp_a += 1
                if g['target'] and kb['target'] == g['target']:
                    ok_a += 1
                else:
                    gaps['associations'].append('%s.%s -> %s (kb: %s)' % (model, fname, g['target'], kb['target']))
            if g['type'] == 'Selection' and g['selection'] is not None and not g['dynamic']:
                exp_e += 1
                kv = enums.get((model, fname))
                if kv == g['selection']:
                    ok_e += 1
                else:
                    gaps['enumerations'].append('%s.%s: kb %s vs source %s' % (model, fname, sorted(kv) if kv is not None else None,
                                                                              sorted(g['selection'])))
    dims['entityFields'] = {'score': score(fnd_f, exp_f), 'found': fnd_f, 'expected': exp_f}
    dims['typeAccuracy'] = {'score': score(ok_t, exp_t), 'found': ok_t, 'expected': exp_t}
    dims['associations'] = {'score': score(ok_a, exp_a), 'found': ok_a, 'expected': exp_a}
    dims['enumerations'] = {'score': score(ok_e, exp_e), 'found': ok_e, 'expected': exp_e}
    # views
    kb_views = {s['uniqueId'] for s in L('screens.json')}
    vf = len(xml['views'] & kb_views)
    gaps['views'] = ['view %s missing' % v for v in sorted(xml['views'] - kb_views)]
    dims['views'] = {'score': score(vf, len(xml['views'])), 'found': vf, 'expected': len(xml['views'])}
    km = len(L('menus.json'))
    dims['menus'] = {'score': count_score(km, xml['menus']), 'found': km, 'expected': xml['menus']}
    if km != xml['menus']:
        gaps['menus'].append('kb %d menus vs source %d menuitem tags' % (km, xml['menus']))
    roles = L('roles.json')
    kb_groups = {r['uniqueId'] for r in roles if not r.get('definedOutsideImport') and r['uniqueId'] != '(all users)'}
    kb_acl = len(L('acl.json'))
    kb_rules = len(L('recordRules.json'))
    sec_exp = len(xml['groups']) + xml['acl'] + xml['rules']
    sec_fnd = len(xml['groups'] & kb_groups) - len(kb_groups - xml['groups']) + min(kb_acl, xml['acl']) - abs(kb_acl - xml['acl']) + min(kb_rules, xml['rules']) - abs(kb_rules - xml['rules'])
    for g in sorted(xml['groups'] - kb_groups):
        gaps['security'].append('group %s missing' % g)
    if kb_acl != xml['acl']:
        gaps['security'].append('ACL rows kb %d vs source %d' % (kb_acl, xml['acl']))
    if kb_rules != xml['rules']:
        gaps['security'].append('record rules kb %d vs source %d' % (kb_rules, xml['rules']))
    dims['security'] = {'score': score(sec_fnd, sec_exp), 'found': sec_fnd, 'expected': sec_exp}
    ka = len(L('serviceApis.json'))
    dims['endpoints'] = {'score': count_score(ka, xml['routes']), 'found': ka, 'expected': xml['routes']}
    if ka != xml['routes']:
        gaps['endpoints'].append('kb %d routes vs source %d' % (ka, xml['routes']))
    kt = len(L('timers.json'))
    dims['timers'] = {'score': count_score(kt, xml['crons']), 'found': kt, 'expected': xml['crons']}
    if kt != xml['crons']:
        gaps['timers'].append('kb %d crons vs source %d' % (kt, xml['crons']))
    zeros = [k for k, v in dims.items() if not v['expected']]
    for k, v in dims.items():
        v['gaps'] = gaps.get(k, [])[:50]
        v['gapCount'] = len(gaps.get(k, []))
        if v['score'] is None:
            v['score'] = 0.0
    scored = [v['score'] for k, v in dims.items()]
    overall = round(sum(scored) / len(scored), 2)
    q = {'project': 'erpv1', 'source': 'odoo', 'scoredAt': datetime.now(timezone.utc).isoformat(timespec='seconds'),
         'overallScore': overall, 'passed': overall >= THRESHOLD and not zeros, 'threshold': THRESHOLD,
         'methods': {'extractor': 'python ast + ElementTree + csv (pipelines/odoo/extractor.py)',
                     'validator': 'line regex + paren counting over raw text (pipelines/odoo/validator.py)'},
         'dimensions': dims, 'confirmedZeros': [],
         'externalRelations': {'count': len(external_rel), 'note': 'relational fields whose target is defined only in addons declared not implemented (utm, mail, base_setup, ...) — target unresolvable by both methods, not scored', 'fields': external_rel},
         'unscored': [{'dimension': 'testCoverage', 'reason': 'tests/ excluded at import (sources/odoo/SOURCE.md); nothing to classify'}],
         'brdOnly': ['Method behaviour: what action_* / _compute_* / constraint bodies do (logics.json lists them with source line ranges)',
                     'Dynamic selections (method/lambda) — values computed at runtime (reports/gaps-report.md)',
                     'Domain expressions on fields, actions and record rules — captured as text, meaning is BRD work',
                     'Onchange UX behaviour and view-level invisible/readonly conditions',
                     'Fields contributed by addons declared not implemented (mail, portal, utm, payment, ...)']}
    if zeros:
        q['unconfirmedZeros'] = zeros
    os.makedirs(a.out, exist_ok=True)
    json.dump(q, open(os.path.join(a.out, 'extraction-quality.json'), 'w'), indent=1)
    print('%-14s %7s %7s %7s' % ('dimension', 'score', 'found', 'expect'))
    for k, v in dims.items():
        print('%-14s %7.2f %7d %7d' % (k, v['score'], v['found'], v['expected']))
        for g in v['gaps'][:5]:
            print('    - ' + g)
    print('OVERALL %.2f  (threshold %.0f) -> %s' % (overall, THRESHOLD, 'PASS' if q['passed'] else 'FAIL'))
    return 0 if q['passed'] else 1


if __name__ == '__main__':
    sys.exit(main())
