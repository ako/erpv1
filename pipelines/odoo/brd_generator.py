#!/usr/bin/env python3
"""Compose F001–F008 BRDs from brd_spec.py + brd_content.py, resolving every Odoo reference
against the knowledge base. Fails (exit 1) on any unresolved reference or unaccounted in-scope model.

Usage: brd_generator.py [--kb analysis/odoo/knowledge-base]
Writes <kb>/brd/F00N-<topic>.brd.json, <kb>/brd/index.json, <kb>/brd/traceability.json.
"""
import argparse, json, os, re, sys
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import brd_spec as S          # noqa: E402
import brd_content as C       # noqa: E402

SLUG = {'F001': 'contacts-company-users', 'F002': 'units-of-measure', 'F003': 'product-catalogue-pricing',
        'F004': 'sales', 'F005': 'purchasing', 'F006': 'inventory', 'F007': 'order-fulfilment', 'F008': 'invoicing-payments'}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--kb', default='analysis/odoo/knowledge-base')
    a = ap.parse_args()
    L = lambda n: json.load(open(os.path.join(a.kb, n), encoding='utf-8'))
    models = {e['name']: e for e in L('entities.json') + L('structures.json')}
    enums_kb = {s['model'] + '.' + s['field']: s for s in L('staticEntities.json')}
    logic_ids = {l['model'] + '.' + l['name'] for l in L('logics.json')}
    screen_ids = {s['uniqueId'] for s in L('screens.json')}
    action_ids = {x['id'] for x in L('actions.json')}
    role_ids = {r['uniqueId'] for r in L('roles.json')}
    errors, trace = [], []

    def field(model, fname):
        m = models.get(model)
        if not m:
            return None, None
        for at in m['attributes']:
            if at['name'] == fname:
                return 'attr', at
        for asc in m['associations']:
            if asc['name'] == fname:
                return 'assoc', asc
        return None, None

    def ref_ok(r):
        return r in logic_ids or r in screen_ids or r in action_ids or r in role_ids

    # enumerations
    enum_out = {}
    for name, en in S.ENUMS.items():
        kbv = None
        if en['odoo']:
            k = enums_kb.get(en['odoo'].rsplit('.', 1)[0].replace('.', '_') if False else None)
            model, fld = en['odoo'].rsplit('.', 1)
            s = enums_kb.get(model + '.' + fld) or next((x for x in enums_kb.values() if x['model'] == model and x['field'] == fld), None)
            if not s:
                errors.append('enum %s: odoo selection %s not in KB' % (name, en['odoo']))
            else:
                kbv = {r['name'] for r in s['records']}
        vals = []
        for mv, ov, cap in en['values']:
            if ov is not None and kbv is not None and ov not in kbv:
                errors.append('enum %s: value %s not in odoo %s %s' % (name, ov, en['odoo'], sorted(kbv)))
            vals.append({'name': mv, 'caption': cap, 'odooValue': ov})
        dropped = sorted(kbv - {v[1] for v in en['values']}) if kbv else []
        enum_out[name] = {'name': name, 'module': name.split('.')[0], 'sourceOdoo': en['odoo'], 'values': vals,
                          'droppedOdooValues': dropped, 'note': en.get('note')}

    def mtype(kbatt, ov):
        if ov.get('enum'):
            return 'Enumeration', None, ov['enum']
        if ov.get('type'):
            return ov['type'], ov.get('length'), None
        t = kbatt['mendixType']
        m = re.match(r'String\((\w+)\)', t)
        if m:
            return 'String', (m.group(1) if m.group(1) == 'unlimited' else int(m.group(1))), None
        if t.startswith('Enumeration'):
            errors.append('selection field %s needs an enum mapping' % kbatt['name'])
            return 'String', 50, None
        return t, None, None

    # entities
    ent_out = {}
    mapped_models = set()
    for e in S.E:
        if e['odoo']:
            if e['odoo'] not in models and e['odoo'] != 'ir.sequence':
                errors.append('entity %s: odoo model %s not in KB' % (e['name'], e['odoo']))
            mapped_models.add(e['odoo'])
        attrs = []
        for n, of, ov in e['attrs']:
            item = {'name': n}
            if of and e['odoo'] in models:
                kind, f = field(e['odoo'], of)
                if not f:
                    errors.append('%s.%s: odoo field %s.%s not found' % (e['name'], n, e['odoo'], of))
                    continue
                if kind == 'assoc' and not ov.get('type') and not ov.get('enum'):
                    errors.append('%s.%s: %s is relational; map it as an association' % (e['name'], n, of))
                t, length, enum = mtype(f, ov) if kind == 'attr' else (ov.get('type'), ov.get('length'), ov.get('enum'))
                item.update(type=t, sourceOdoo='%s.%s' % (e['odoo'], of), odooType=f.get('odooType'),
                            mandatory=ov.get('mandatory', f.get('isMandatory', False)))
                if f.get('label'):
                    item['label'] = f['label']
                if kind == 'attr' and not f.get('stored', True):
                    item['odooComputedNotStored'] = True
                if kind == 'attr' and (f.get('compute') or f.get('related')):
                    item['odooComputedBy'] = f.get('compute') or ('related: ' + str(f.get('related')))
                if f.get('default') and 'default' not in ov:
                    item['odooDefault'] = f['default']
            else:
                t, length, enum = (ov.get('type') or ('Enumeration' if ov.get('enum') else None)), ov.get('length'), ov.get('enum')
                if not t:
                    errors.append('%s.%s: new attribute without type' % (e['name'], n))
                item.update(type=t, sourceOdoo=('%s (framework, not extracted field-level)' % e['odoo']) if e['odoo'] else None,
                            mandatory=ov.get('mandatory', False), new=e['odoo'] is None or not of)
            if t == 'Enumeration':
                item['enumeration'] = enum
                if enum not in S.ENUMS:
                    errors.append('%s.%s: unknown enumeration %s' % (e['name'], n, enum))
            if length is not None:
                item['length'] = length
            for k in ('default', 'note'):
                if ov.get(k):
                    item[k] = ov[k]
            attrs.append(item)
            trace.append({'entity': e['name'], 'attribute': n, 'odoo': item.get('sourceOdoo'), 'new': item.get('new', False)})
        if e['active']:
            attrs.append({'name': 'Active', 'type': 'Boolean', 'default': 'true', 'mandatory': False,
                          'sourceOdoo': '%s.active' % e['odoo'] if e['odoo'] else None})
        assocs = []
        for n, tgt, typ, of, note in e['assocs']:
            item = {'name': n, 'owner': e['name'], 'target': tgt, 'type': typ}
            if of and e['odoo'] in models:
                kind, f = field(e['odoo'], of)
                if not f:
                    errors.append('%s: odoo field %s.%s not found' % (n, e['odoo'], of))
                else:
                    item['sourceOdoo'] = '%s.%s' % (e['odoo'], of)
                    item['odooTarget'] = f.get('target') or f.get('referencedEntity')
                    item['mandatory'] = f.get('required', f.get('isMandatory', False))
            else:
                item['new'] = True
            if note:
                item['note'] = note
            assocs.append(item)
            trace.append({'entity': e['name'], 'association': n, 'odoo': item.get('sourceOdoo'), 'new': item.get('new', False)})
        for asc in assocs:
            if asc['target'].split('.')[0] not in S.MODULES + ['Administration', 'System'] or (
                    asc['target'].split('.')[0] in S.MODULES and asc['target'] not in [x['name'] for x in S.E] + [v['name'] for v in S.VIEWS]):
                errors.append('%s -> unknown target %s' % (asc['name'], asc['target']))
        ent_out[e['name']] = {'name': e['name'], 'module': e['name'].split('.')[0], 'persistent': e['persistent'], 'purpose': e['purpose'],
                              'sourceOdoo': e['odoo'], 'generalization': e['generalization'],
                              'systemMembers': ['createdDate', 'changedDate', 'owner', 'changedBy'] if e['persistent'] else [],
                              'attributes': attrs, 'associations': assocs, 'note': e['note'], 'brd': e['brd']}
    for v in S.VIEWS:
        mapped_models.add(v['odoo'])

    # accounting for every in-scope Odoo model
    kb_ent = [x for x in L('entities.json') if x['inScope']]
    kb_str = [x for x in L('structures.json') if x['inScope']]
    unaccounted = [x['name'] for x in kb_ent if x['name'] not in mapped_models and x['name'] not in S.DROPPED]
    for u in unaccounted:
        errors.append('in-scope odoo model %s neither mapped nor dropped' % u)
    for d in S.DROPPED:
        if d not in {x['name'] for x in kb_ent}:
            errors.append('DROPPED lists %s which is not an in-scope persistent model' % d)

    # BRDs
    cap_of = {x['name']: x['capability'] for x in kb_ent + kb_str}
    outdir = os.path.join(a.kb, 'brd')
    os.makedirs(outdir, exist_ok=True)
    index = []
    for fid, b in C.BRDS.items():
        for uc in b['useCases']:
            for r in uc['odooRefs']:
                if not ref_ok(r):
                    errors.append('%s %s: unresolved odooRef %s' % (fid, uc['id'], r))
        for m in b['microflows'] + b.get('workflows', []):
            for r in m['odooRefs']:
                if not ref_ok(r):
                    errors.append('%s %s: unresolved odooRef %s' % (fid, m['name'], r))
        for p in b['pages']:
            for r in p['odooRefs']:
                if not ref_ok(r):
                    errors.append('%s %s: unresolved odooRef %s' % (fid, p['name'], r))
        for actor in b['actors']:
            for g in C.ROLES[actor]:
                if g not in role_ids:
                    errors.append('role %s: odoo group %s not in KB' % (actor, g))
        ents = [v for v in ent_out.values() if v['brd'] == fid]
        for en, at_names, as_names in b.get('entityExtensions', []):
            base = ent_out.get(en)
            if not base:
                errors.append('%s extension of unknown entity %s' % (fid, en))
                continue
            ats = [x for x in base['attributes'] if x['name'] in at_names]
            ass = [x for x in base['associations'] if x['name'] in as_names]
            if len(ats) != len(at_names) or len(ass) != len(as_names):
                errors.append('%s extension of %s names unknown members' % (fid, en))
            ents.append({'name': en, 'module': base['module'], 'extensionOf': en, 'definedInBrd': base['brd'], 'persistent': base['persistent'],
                         'purpose': 'Members this capability adds to %s (Odoo _inherit in the bridge addon); the entity itself is specified in %s'
                                    % (en, base['brd']), 'sourceOdoo': base['sourceOdoo'], 'attributes': ats, 'associations': ass})
        used_enums = sorted({at['enumeration'] for v in ents if not v.get('extensionOf') for at in v['attributes'] if at.get('enumeration')})
        cap = b['capability']
        dropped = [{'odooModel': k, 'reason': r} for k, r in S.DROPPED.items() if cap_of.get(k) == cap]
        dropped_struct = [{'odooModel': x['name'], 'reason': S.DROPPED_STRUCTURES_REASON} for x in kb_str
                          if x['capability'] == cap and x['name'] not in mapped_models]
        odoo_models = sorted(x['name'] for x in kb_ent if x['capability'] == cap)
        # confidence = extractor gaps on the mapped Odoo models, excluding gaps that point at addons declared not implemented (Stage 0)
        NI = ('mail.', 'portal.', 'utm.', 'payment.', 'digest.', 'onboarding.', 'base_setup', 'barcodes', 'account_payment')
        gaps = [g for v in ents if v.get('sourceOdoo') in models and not v.get('extensionOf')
                for g in models[v['sourceOdoo']]['_gaps'] if not any(n in g for n in NI)]
        ni_gaps = sum(1 for v in ents if v.get('sourceOdoo') in models and not v.get('extensionOf')
                      for g in models[v['sourceOdoo']]['_gaps'] if any(n in g for n in NI))
        conf_level = 'high' if not gaps else 'medium' if len(gaps) <= 3 else 'low'
        conf_basis = '%d extractor gap(s) on mapped models outside the declared-not-implemented addons%s; %d gap(s) point at not-implemented addons (mail/portal/utm/...)' % (
            len(gaps), (': ' + '; '.join(gaps[:5])) if gaps else '', ni_gaps)
        brd = {
            'id': fid, 'title': b['title'], 'modules': b['modules'], 'actors': b['actors'], 'capability': cap,
            'summary': b['summary'], 'provenance': 'code-extracted', 'generatedAt': str(date.today()),
            'design': 'Odoo-inspired, Mendix-native (intake Q3): Odoo is the functional reference; simplifications listed and signed off at the Stage 2 gate',
            'actorRoleMapping': {r: C.ROLES[r] for r in b['actors']},
            'useCases': b['useCases'],
            'domainEntities': ents,
            'enumerations': [enum_out[n] for n in used_enums],
            'viewEntities': [v for v in S.VIEWS if v['brd'] == fid],
            'microflows': b['microflows'], 'workflows': b.get('workflows', []), 'pages': b['pages'],
            'timers': [{'name': m['name'], 'interval': 'daily', 'purpose': m['purpose']} for m in b['microflows'] if m['pattern'] == 'scheduled'],
            'integrations': b['integrations'], 'simplifications': b['simplifications'],
            'odooModelsInCapability': odoo_models, 'droppedOdooModels': dropped + dropped_struct,
            'openQuestions': b['openQuestions'],
            'sourceKB': ['analysis/odoo/knowledge-base/entities.json', 'analysis/odoo/knowledge-base/structures.json',
                         'analysis/odoo/knowledge-base/staticEntities.json', 'analysis/odoo/knowledge-base/logics.json',
                         'analysis/odoo/knowledge-base/screens.json', 'analysis/odoo/knowledge-base/workflows.json',
                         'analysis/odoo/knowledge-base/roles.json', 'analysis/odoo/non-code-sources.md'],
            'confidence': conf_level, 'confidenceBasis': conf_basis,
            'summaryCounts': {'useCases': len(b['useCases']), 'entities': len(ents), 'enumerations': len(used_enums),
                              'microflows': len(b['microflows']), 'pages': len(b['pages']), 'openQuestions': len(b['openQuestions'])},
        }
        fn = '%s-%s.brd.json' % (fid, SLUG[fid])
        json.dump(brd, open(os.path.join(outdir, fn), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
        index.append({'id': fid, 'title': b['title'], 'file': fn, 'status': 'draft', 'capability': cap})
    json.dump({'generated': str(date.today()), 'brds': index}, open(os.path.join(outdir, 'index.json'), 'w'), indent=1)
    json.dump(trace, open(os.path.join(outdir, 'traceability.json'), 'w'), indent=1)
    # cross-BRD integrity (brd-validation.md check 4): calls, page actions, use-case screens, data contexts
    mf_names = {m['name'] for b in C.BRDS.values() for m in b['microflows'] + b.get('workflows', [])}
    page_names = {p['name'] for b in C.BRDS.values() for p in b['pages']}
    platform_pages = {'Account_Overview'}   # Administration module (marketplace)
    known_ctx = set(ent_out) | {v['name'] for v in S.VIEWS}
    for fid, b in C.BRDS.items():
        for m in b['microflows']:
            for c in m['calls']:
                if c not in mf_names:
                    errors.append('%s %s calls undefined microflow %s' % (fid, m['name'], c))
            for prm in m['params']:
                t = prm['type'].replace('List of ', '')
                if '.' in t and t.split('.')[0] in S.MODULES and t not in known_ctx and t not in S.ENUMS:
                    errors.append('%s %s param type %s unknown' % (fid, m['name'], t))
        for p in b['pages']:
            if p['pattern'] == 'extension' and p['name'] not in {q['name'] for bb in C.BRDS.values() for q in bb['pages'] if q['pattern'] != 'extension'}:
                errors.append('%s page extension %s extends no defined page' % (fid, p['name']))
            if p['dataContext'] not in known_ctx:
                errors.append('%s page %s: data context %s unknown' % (fid, p['name'], p['dataContext']))
            for act in p['actions']:
                if re.match(r'^(ACT|SUB|VAL|WF|SCE)_', act) and act not in mf_names:
                    errors.append('%s page %s: action %s undefined' % (fid, p['name'], act))
        for u in b['useCases']:
            for sc in u['screens']:
                if sc not in page_names and sc not in platform_pages:
                    errors.append('%s %s: screen %s is not a defined page' % (fid, u['id'], sc))
    unowned = [n for n, v in ent_out.items() if v['brd'] not in C.BRDS]
    for u in unowned:
        errors.append('entity %s has no BRD' % u)
    new_cnt = sum(1 for t in trace if t['new'])
    print('BRDs: %d  entities: %d  enumerations: %d  attributes+associations: %d (%d new, %d traced to Odoo)' %
          (len(index), len(ent_out), len(enum_out), len(trace), new_cnt, len(trace) - new_cnt))
    print('in-scope persistent models: %d mapped/view, %d dropped, %d unaccounted' %
          (len([x for x in kb_ent if x['name'] in mapped_models]), len([x for x in kb_ent if x['name'] in S.DROPPED]), len(unaccounted)))
    if errors:
        print('ERRORS (%d):' % len(errors))
        for e in errors:
            print('  - ' + e)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
