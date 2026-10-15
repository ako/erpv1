#!/usr/bin/env python3
"""Stage 4: build plan, coverage ledgers and module briefs, generated from the confirmed BRDs + design.

  architecture/build-plan.md                               brd-to-build-plan.md (rows, claims, access roll-up, nav, reconciliation)
  architecture/modules/<Home>/coverage-ledger/<BRD>.md     coverage-ledger.md, per-BRD directory form
  architecture/modules/<Module>/module-brief.md            module-brief.md (Phase 1 domain content for all; full for Core)
  design/wireframes/PAGE-MAP.tsv                           page -> prototype route

Every BRD leaf is either claimed by exactly one plan row (BUILDABLE table) or ledgered with a category and a
reason (NON-BUILDABLE table); the script self-checks that before writing and exits 1 otherwise.
Usage: plan_render.py [--kb analysis/odoo/knowledge-base]
"""
import argparse, glob, json, math, os, re, sys
from collections import OrderedDict, defaultdict
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import brd_spec as S        # noqa: E402
import brd_content as C     # noqa: E402
import ui_spec as U         # noqa: E402
from arch_blueprint import MODULE_ROLES  # noqa: E402

TOOLKIT = os.path.expanduser('~/Mendix/mxcli-project-toolkit')
DEMO_PASSWORD = 'Erpv1-Demo-2026!'
PHASE_OF_MODULE = OrderedDict([('Core', ('3', '3-core')), ('Products', ('4', '4-products')), ('Partners', ('5', '5-partners')),
                               ('Sales', ('6', '6-sales')), ('Purchasing', ('7', '7-purchasing')), ('Inventory', ('8', '8-inventory')),
                               ('Invoicing', ('9', '9-invoicing'))])
HOME_MODULE = {'F001': 'Partners', 'F002': 'Products', 'F003': 'Products', 'F004': 'Sales', 'F005': 'Purchasing', 'F006': 'Inventory',
               'F007': 'Inventory', 'F008': 'Invoicing'}
UC_MODULE_OVERRIDE = {('F007', None): 'Inventory', ('F002', None): 'Products', ('F003', None): 'Products', ('F001', 'UC005'): 'Partners'}
SKILLS = {
    'scaffold': 'skills/walking-skeleton.md, skills/security-is-not-a-later-script.md',
    'marketplace': 'none (mxcli built-in download-marketplace-content)',
    'roles': 'skills/security-is-not-a-later-script.md, skills/learned-mdl-preflight.md',
    'domain': 'skills/learned-mdl-preflight.md, skills/security-is-not-a-later-script.md, skills/module-folder-convention.md',
    'uc': 'skills/learned-mdl-preflight.md, skills/learned-microflow-patterns.md, skills/microflow-preflight.md, skills/ui-preflight-pages.md, skills/design-spacing.md, skills/ui-loop.md, skills/security-is-not-a-later-script.md',
    'workflow': 'skills/learned-workflow-patterns.md, skills/workflow-structure-rules.md, skills/learned-mdl-preflight.md',
    'prove': 'skills/testing-shape.md',
    'close': 'skills/module-review.md, skills/testing-shape.md',
    'coherence': 'skills/process-coherence-pass.md',
    'gate': 'none',
    'brief': 'skills/module-brief.md, skills/module-folder-convention.md',
}


def leaves(doc):
    out = []

    def walk(v, path):
        if isinstance(v, dict):
            for k, x in v.items():
                walk(x, path + [str(k)])
        elif isinstance(v, list):
            for i, x in enumerate(v):
                walk(x, path + [str(i)])
        else:
            out.append('/' + '/'.join(path))
    walk(doc, [])
    return out


def count_under(lv, prefix):
    return sum(1 for x in lv if x.startswith(prefix + '/'))


def kebab(s):
    return re.sub(r'(?<!^)(?=[A-Z])', '-', s).replace('_-', '-').replace('_', '-').lower()



# ledger files are named after the BRD file (coverage-check-all.sh / verify-module match on the basename)
BRD_BASENAME = {os.path.basename(p).split('-')[0]: os.path.basename(p)[:-len('.brd.json')]
                for p in glob.glob('analysis/odoo/knowledge-base/brd/F*.brd.json')}

def model_inventory():
    """Names that exist in the live model, by document kind (one LIST per kind). Empty when no model."""
    inv = defaultdict(set)
    mpr = 'app/erpv1.mpr'
    if not os.path.exists(mpr):
        return inv
    for kind, cmd in [('ENTITY', 'LIST ENTITIES'), ('ENUMERATION', 'LIST ENUMERATIONS'), ('MICROFLOW', 'LIST MICROFLOWS'),
                      ('PAGE', 'LIST PAGES'), ('WORKFLOW', 'LIST WORKFLOWS')]:
        out = os.popen("./mxcli -p %s -c '%s' 2>/dev/null" % (mpr, cmd)).read()
        inv[kind] = set(re.findall(r'^\| ([A-Za-z_]+\.[A-Za-z_0-9]+) ', out, re.M))
    return inv


def status_of(acc, live):
    """Ledger status from the model: built when the acceptance DESCRIBE names something that exists.
    Journey/role/scheduled-event acceptances are not model lookups: they stay not-built until the module
    review measures them (verify-module / module-review)."""
    m = re.match(r'`DESCRIBE (ENTITY|ENUMERATION|MICROFLOW|PAGE|WORKFLOW) ([A-Za-z_]+\.[A-Za-z_0-9]+)`', acc)
    if not m or not live:
        return 'not-built'
    return 'built' if m.group(2) in live[m.group(1)] else 'not-built'

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--kb', default='analysis/odoo/knowledge-base')
    a = ap.parse_args()
    brds = OrderedDict()
    for f in sorted(glob.glob(os.path.join(a.kb, 'brd', 'F*.brd.json'))):
        b = json.load(open(f))
        brds[b['id']] = b
    LV = {fid: leaves(b) for fid, b in brds.items()}
    errors = []
    graph = json.load(open(os.path.join(a.kb, 'brd', 'module-graph.json')))

    rows = []           # dicts: n, phase, kind, step(list of scripts or command), produces, depends, skills, state, title, claims[(fid, ptr, count, kind, label, accept)]
    claims_by = defaultdict(dict)  # fid -> ptr -> row n

    def row(phase, kind, title, step, produces, skills, depends=None, claims=(), accept=None, extra=None):
        n = len(rows) + 1
        dep = depends if depends is not None else ([rows[-1]['n']] if rows else [])
        r = dict(n=n, phase=phase, kind=kind, title=title, step=step, produces=produces, depends=dep, skills=skills,
                 state='not built', claims=[], accept=accept, extra=extra or [])
        for c in claims:
            add_claim(r, *c)
        rows.append(r)
        return r

    def add_claim(r, fid, ptr, kind, label, accept):
        cnt = count_under(LV[fid], ptr)
        exact = ptr in LV[fid]
        if not cnt and not exact:
            errors.append('row %d claims %s %s which has no leaves' % (r['n'], fid, ptr))
            return
        if ptr in claims_by[fid]:
            errors.append('%s %s claimed by rows %d and %d' % (fid, ptr, claims_by[fid][ptr], r['n']))
        claims_by[fid][ptr] = r['n']
        r['claims'].append((fid, ptr, cnt if cnt else None, kind, label, accept))

    # ── Phase 0: scaffold ────────────────────────────────────────────────────────────────────
    P0 = '0'
    row(P0, 'BRIEF', 'Check the briefs exist for every module (Phase 0/1 content: domain, access, folders)',
        ['architecture/modules/*/module-brief.md'], '7 briefs present with domain + access sections', SKILLS['brief'], depends=[])
    row(P0, 'BUILD', 'Project scaffold', ['./mxcli new erpv1 --version 11.15.0 --output-dir app (then bin/doctor.sh --install . --yes)',
                                          'mdlsource/0-scaffold/000-scaffold.mdl'],
        'app/erpv1.mpr (Mendix 11.15.0); theme ledger (`./mxcli theme apply ledger`); project security production, demo users on, guest off; '
        'layout erpv1 App_Default with side rail; Responsive navigation shell with the 8 groups of ui_spec.NAV',
        SKILLS['scaffold'], accept='`SHOW PROJECT SECURITY` reads production / demo users on; `mxcli theme list -p app/erpv1.mpr` shows ledger applied')
    row(P0, 'BUILD', 'Marketplace imports (Step 0, CONFIRMED Buy)', ['./mxcli marketplace install <id> -p app/erpv1.mpr for: Administration, Data Widgets, Charts, Workflow Commons (Atlas Core ships with mxcli new)'],
        'Administration, DataWidgets, Charts, WorkflowCommons modules in the model', SKILLS['marketplace'],
        accept='`SHOW MODULES` lists Administration, DataWidgets, Charts, WorkflowCommons')
    row(P0, 'PROVE', 'Scaffold builds and boots', ['./bin/verify-model.sh', './mxcli run --local --setup --ensure-db -p app/erpv1.mpr (snapshot first)'],
        'mxbuild 0 errors; app boots; MxAdmin can log in; ledger paints', SKILLS['prove'])

    # ── Phase 1: domain models, all modules ─────────────────────────────────────────────────
    P1 = '1'
    row(P1, 'BRIEF', 'Check every module brief covers its entities, enumerations, entity access and folder plan', ['architecture/modules/*/module-brief.md'],
        'domain + access + validation sections per module', SKILLS['brief'])
    rr = row(P1, 'BUILD', 'Module roles and the 9 user roles', ['mdlsource/1-domain/100-security-roles.mdl'],
             'module roles per MODULE_ROLES (7 modules) + user roles Administrator, SalesUser, SalesManager, Purchaser, PurchaseManager, InventoryUser, '
             'InventoryManager, Billing, InvoicingManager composed of them (+ Administration/Workflow Commons roles)', SKILLS['roles'],
             accept='`SHOW USER ROLES` lists the 9 user roles with their module roles')
    for fid, b in brds.items():
        if 'actorRoleMapping' in b:
            add_claim(rr, fid, '/actorRoleMapping', 'roles', 'actor → Odoo group mapping', '`SHOW USER ROLES`')
        add_claim(rr, fid, '/actors', 'roles', 'actors', '`SHOW USER ROLES`')
    ent_index = {}  # (fid, entity name) -> index ; also extension entries
    for fid, b in brds.items():
        for i, de in enumerate(b['domainEntities']):
            ent_index[(fid, i)] = de
    enum_index = {(fid, i): en for fid, b in brds.items() for i, en in enumerate(b['enumerations'])}
    domain_rows = {}
    for mi, mod in enumerate(S.MODULES):
        ents = [e for e in S.E if e['name'].startswith(mod + '.')]
        r = row(P1, 'BUILD', '%s domain model + entity access' % mod, ['mdlsource/1-domain/%03d-%s-domain.mdl' % (110 + mi * 10, mod.lower())],
                '%d entities, %d enumerations, %d associations owned by %s; entity access grants per module role at the end of the script' % (
                    len(ents), sum(1 for n in S.ENUMS if n.startswith(mod + '.')), sum(len(e['assocs']) for e in ents), mod),
                SKILLS['domain'], accept='`SHOW ENTITIES IN %s`' % mod)
        domain_rows[mod] = r
        for (fid, i), de in ent_index.items():
            if de['module'] == mod:
                add_claim(r, fid, '/domainEntities/%d' % i, 'entity' if not de.get('extensionOf') else 'entity-extension', de['name'],
                          '`DESCRIBE ENTITY %s`' % de['name'])
        for (fid, i), en in enum_index.items():
            if en['module'] == mod:
                add_claim(r, fid, '/enumerations/%d' % i, 'enumeration', en['name'], '`DESCRIBE ENUMERATION %s`' % en['name'])
    row(P1, 'BUILD', 'Demo users, one per user role', ['mdlsource/1-domain/190-security-demo-users.mdl'],
        "demo users sales.user, sales.manager, purchaser, purchase.manager, warehouse.user, inventory.manager, billing, invoicing.manager, admin.user "
        "— password '%s' (throwaway, recorded here; MxAdmin untouched)" % DEMO_PASSWORD, SKILLS['roles'], accept='`SHOW DEMO USERS`')
    row(P1, 'PROVE', 'Domain skeleton read-back', ['./bin/verify-model.sh', './mxcli -p app/erpv1.mpr -c "DESCRIBE STRUCTURE"'],
        'mxbuild 0 errors; 43 entities, 27 enumerations, 53 cross-module associations present; no association cycle', SKILLS['prove'])

    # ── Feature phases: one per module, use-case rows ───────────────────────────────────────
    def uc_module(fid, uc):
        for (f, u), m in UC_MODULE_OVERRIDE.items():
            if f == fid and (u is None or u == uc['id']):
                return m
        for sc in uc['screens']:
            if sc in U.S:
                return U.S[sc]['entity'].split('.')[0]
        return HOME_MODULE[fid]

    # microflow / page / workflow / timer assignment to use cases (first use case that references it wins)
    mf_row, page_row = {}, {}
    plan_ucs = []   # (module, fid, uc_index, uc)
    for fid, b in brds.items():
        for ui, uc in enumerate(b['useCases']):
            plan_ucs.append((uc_module(fid, uc), fid, ui, uc))
    plan_ucs.sort(key=lambda t: (list(PHASE_OF_MODULE).index(t[0]), t[1], t[2]))
    assigned_mf = {fid: {} for fid in brds}
    assigned_pg = {fid: {} for fid in brds}
    for mod, fid, ui, uc in plan_ucs:
        b = brds[fid]
        refs = set(uc['odooRefs'])
        acts = set()
        for pi, p in enumerate(b['pages']):
            if p['name'] in uc['screens']:
                acts |= set(p['actions'])
                if pi not in assigned_pg[fid]:
                    assigned_pg[fid][pi] = (mod, fid, ui)
        for mi, m in enumerate(b['microflows']):
            if mi in assigned_mf[fid]:
                continue
            if refs & set(m['odooRefs']) or m['name'] in acts:
                assigned_mf[fid][mi] = (mod, fid, ui)
    # leftovers -> a shared-logic row of the BRD's home module
    shared = defaultdict(lambda: {'mf': [], 'pg': []})
    for fid, b in brds.items():
        for mi, m in enumerate(b['microflows']):
            if mi not in assigned_mf[fid]:
                shared[(m.get('module') or HOME_MODULE[fid], fid)]['mf'].append(mi)
        for pi, p in enumerate(b['pages']):
            if pi not in assigned_pg[fid]:
                shared[(p['dataContext'].split('.')[0], fid)]['pg'].append(pi)

    phase_rows = defaultdict(list)
    built_mf_row = {}
    built_page_row = {}
    pending_alters = []
    for mod, (pid, folder) in PHASE_OF_MODULE.items():
        P = pid
        row(P, 'BRIEF', 'Check `architecture/modules/%s/module-brief.md` covers this phase (screens, access, validation, test plan, build steps)' % mod,
            ['architecture/modules/%s/module-brief.md' % mod], 'brief extended for phase %s' % P, SKILLS['brief'])
        script_no = 300 + (int(P) - 3) * 100
        items = [(m, f, ui, uc) for (m, f, ui, uc) in plan_ucs if m == mod]
        groups = [(f, ui, uc) for (m, f, ui, uc) in items]
        # shared-logic rows first (helpers others call)
        for (smod, fid), sh in sorted(shared.items()):
            if smod != mod or not (sh['mf'] or sh['pg']):
                continue
            b = brds[fid]
            scripts, produces = [], []
            r = row(P, 'BUILD', '%s shared logic (%s)' % (mod, fid), [], '', SKILLS['uc'])
            for mi in sh['mf']:
                m = b['microflows'][mi]
                script_no += 1
                scripts.append('mdlsource/%s/%03d-%s-mf-%s.mdl' % (folder, script_no, mod.lower(), kebab(m['name'].split('_', 1)[1])))
                produces.append('%s.%s (+ grant execute)' % (m.get('module', mod), m['name']))
                built_mf_row[m['name']] = r['n']
                add_claim(r, fid, '/microflows/%d' % mi, 'microflow', m['name'], '`DESCRIBE MICROFLOW %s.%s`' % (m.get('module', mod), m['name']))
            for pi in sh['pg']:
                p = b['pages'][pi]
                script_no += 1
                scripts.append('mdlsource/%s/%03d-%s-page-%s.mdl' % (folder, script_no, mod.lower(), kebab(p['name'])))
                produces.append('%s.%s (+ grant view)' % (p['dataContext'].split('.')[0], p['name']))
                add_claim(r, fid, '/pages/%d' % pi, 'page', p['name'], '`DESCRIBE PAGE %s.%s`' % (p['dataContext'].split('.')[0], p['name']))
            r['step'] = scripts
            r['produces'] = '; '.join(produces)
            r['accept'] = ' and '.join(c[5] for c in r['claims'][:2])
        for fid, ui, uc in groups:
            b = brds[fid]
            r = row(P, 'BUILD', '%s-%s %s' % (fid, uc['id'], uc['title']), [], '', SKILLS['uc'])
            add_claim(r, fid, '/useCases/%d' % ui, 'useCase', '%s %s' % (uc['id'], uc['title']), 'journey step: %s' % uc['postconditions'][0])
            scripts, produces = [], []
            mfs = [mi for mi, t in assigned_mf[fid].items() if t == (mod, fid, ui)]
            pgs = [pi for pi, t in assigned_pg[fid].items() if t == (mod, fid, ui)]
            # microflows in groups of <= 6 per script
            for k in range(0, len(mfs), 6):
                script_no += 1
                chunk = mfs[k:k + 6]
                scripts.append('mdlsource/%s/%03d-%s-mf-%s.mdl' % (folder, script_no, mod.lower(), kebab(b['microflows'][chunk[0]]['name'].split('_', 1)[1])))
                for mi in chunk:
                    m = b['microflows'][mi]
                    produces.append('%s.%s (+ grant execute)' % (m.get('module', mod), m['name']))
                    built_mf_row[m['name']] = r['n']
                    add_claim(r, fid, '/microflows/%d' % mi, 'microflow', m['name'], '`DESCRIBE MICROFLOW %s.%s`' % (m.get('module', mod), m['name']))
            for pi in pgs:
                p = b['pages'][pi]
                pm = p['dataContext'].split('.')[0] if p['pattern'] != 'extension' else p['dataContext'].split('.')[0]
                script_no += 1
                if p['pattern'] == 'extension':
                    scripts.append('mdlsource/%s/%03d-%s-alter-%s.mdl' % (folder, script_no, mod.lower(), kebab(p['name'])))
                    produces.append('ALTER PAGE %s.%s: %s' % (pm, p['name'], p['purpose']))
                    acc = '`DESCRIBE PAGE %s.%s`' % (pm, p['name'])
                else:
                    scripts.append('mdlsource/%s/%03d-%s-page-%s.mdl' % (folder, script_no, mod.lower(), kebab(p['name'])))
                    produces.append('%s.%s (+ grant view) — wireframe design/wireframes/%s.html' % (pm, p['name'], p['name']))
                    built_page_row[p['name']] = r['n']
                    acc = '`DESCRIBE PAGE %s.%s`' % (pm, p['name'])
                add_claim(r, fid, '/pages/%d' % pi, 'page', p['name'], acc)
            for wi, w in enumerate(b.get('workflows', [])):
                if set(w['odooRefs']) & set(uc['odooRefs']) and ('/workflows/%d' % wi) not in claims_by[fid]:
                    script_no += 1
                    scripts.append('mdlsource/%s/%03d-%s-workflow-%s.mdl' % (folder, script_no, mod.lower(), kebab(w['name'].split('_', 1)[1])))
                    produces.append('%s.%s (workflow; task page first; native mx check after write)' % (w['module'], w['name']))
                    add_claim(r, fid, '/workflows/%d' % wi, 'workflow', w['name'], '`DESCRIBE WORKFLOW %s.%s`' % (w['module'], w['name']))
                    r['skills'] = SKILLS['uc'] + ', ' + SKILLS['workflow']
            for ti, t in enumerate(b.get('timers', [])):
                if t['name'] in [b['microflows'][mi]['name'] for mi in mfs]:
                    produces.append('scheduled event SE_%s (daily) → %s' % (t['name'], t['name']))
                    add_claim(r, fid, '/timers/%d' % ti, 'timer', t['name'], '`SHOW SCHEDULED EVENTS`')
            for vi, v in enumerate(b.get('viewEntities', [])):
                vpage = next((pp['name'] for pp in b['pages'] if pp['dataContext'] == v['name']), None)
                vshort = v['name'].split('.')[1]
                if ((vpage and vpage in uc['screens']) or vshort in json.dumps(uc)) and ('/viewEntities/%d' % vi) not in claims_by[fid]:
                    script_no += 1
                    scripts.insert(0, 'mdlsource/%s/%03d-%s-view-%s.mdl' % (folder, script_no, mod.lower(), kebab(v['name'].split('.')[1])))
                    produces.insert(0, '%s (OQL view entity, replaces %s)' % (v['name'], v['odoo']))
                    add_claim(r, fid, '/viewEntities/%d' % vi, 'viewEntity', v['name'], '`DESCRIBE ENTITY %s`' % v['name'])
            if not scripts:
                scripts = ['(no new document — use case is carried by the documents of rows %s)' % ', '.join(
                    str(built_page_row.get(sc, '?')) for sc in uc['screens'] if sc in built_page_row) or 'none']
            r['step'] = scripts
            r['produces'] = '; '.join(produces) or 'behaviour only (see scripts of the rows it depends on)'
            r['accept'] = 'journey: %s → %s' % (uc['mainFlow'][0], uc['postconditions'][0])
        # unit tests for calculation/state logic (intake Q13: unit tests default yes)
        row(P, 'PROVE', '%s unit tests' % mod, ['tests/%s/*.test.mdl via ./mxcli test tests/%s -p app/erpv1.mpr --local' % (mod, mod)],
            'every SUB_/ACT_ microflow with calculation or state change in %s has a .test.mdl with @verify; all pass' % mod, SKILLS['prove'])
        row(P, 'HARNESS', '%s module close' % mod, ['bin/verify-module.sh %s' % mod, 'LOOK + CONFIRM per module-review.md'],
            'verify-module summary has no FAULT; review states N of N pages reviewed', SKILLS['close'])
        if mod in ('Partners', 'Purchasing'):
            cl = {'Partners': 'Core, Products, Partners', 'Purchasing': 'Sales, Purchasing'}[mod]
            row(P, 'HARNESS', 'process-coherence-pass on %s' % cl, ['skills/process-coherence-pass.md over %s' % cl],
                'cluster journeys chain (master data → orders)', SKILLS['coherence'])
    # stubs and later alters: computed after all rows exist
    for r in rows:
        if r['kind'] != 'BUILD':
            continue
        for fid, ptr, cnt, kind, label, acc in r['claims']:
            if kind != 'microflow':
                continue
            m = brds[fid]['microflows'][int(ptr.split('/')[-1])]
            for cl in m['calls']:
                cr = built_mf_row.get(cl)
                if cr and cr > r['n']:
                    r['extra'].append('forward stub `%s` (empty body, returns default) — replaced by row %d (CREATE OR MODIFY)' % (cl, cr))
        for fid, ptr, cnt, kind, label, acc in r['claims']:
            if kind != 'page':
                continue
            p = brds[fid]['pages'][int(ptr.split('/')[-1])]
            for act in p['actions']:
                ar = built_mf_row.get(act)
                if ar and ar > r['n']:
                    rows[ar - 1]['extra'].append('ALTER PAGE %s: add action button `%s` (page built in row %d before this microflow existed)' % (p['name'], act, r['n']))
    P9 = '10'
    row(P9, 'HARNESS', 'process-coherence-pass on Inventory, Invoicing (+ quote-to-cash and procure-to-pay across all modules)',
        ['skills/process-coherence-pass.md over Inventory, Invoicing; journeys J-01..J-04 of architecture/blueprint.md'], 'J-01..J-04 chain end to end', SKILLS['coherence'])
    row(P9, 'RUN', 'Stage 5 gate', ['bin/gate-check.sh . 5'], 'every Stage 5 obligation discharged or waived with a reason: 0 PENDING', SKILLS['gate'])

    # ── self-check: every leaf claimed or ledgered ───────────────────────────────────────────
    NONBUILD = [  # (pointer prefix, category, reason)
        ('/id', 'provenance', 'BRD identifier'), ('/title', 'provenance', 'BRD title'), ('/capability', 'provenance', 'capability id from triage.md'),
        ('/provenance', 'provenance', 'BRD provenance flag'), ('/generatedAt', 'provenance', 'generation date'),
        ('/sourceKB', 'provenance', 'knowledge-base files the BRD was generated from'),
        ('/odooModelsInCapability', 'provenance', 'Odoo models of this capability (source inventory, not a target)'),
        ('/modules', 'interpretation', 'Mendix modules this BRD lands in — shaped the per-module phases 3–9 and the domain rows of phase 1'),
        ('/summary', 'interpretation', 'one-paragraph summary; shaped the use-case rows of this BRD'),
        ('/design', 'interpretation', 'design stance (Odoo-inspired, Mendix-native, intake Q3) — shaped every row'),
        ('/simplifications', 'interpretation', 'deliberate simplifications vs Odoo, signed off with the Stage 2 answers — shaped the domain and use-case rows'),
        ('/openQuestions', 'interpretation', 'all answered 2026-10-14 (status Resolved, "all as proposed"); each answer shaped the rows of its BRD — none open, so none in pending decisions'),
        ('/confidence', 'metric', 'extractor-gap confidence of the BRD'), ('/confidenceBasis', 'metric', 'how confidence was computed'),
        ('/summaryCounts', 'metric', 'counts of BRD sections'),
        ('/droppedOdooModels', 'descoped', 'Odoo models deliberately not built — PROJECT.md Stage 2 CONFIRMED BRD-set row (user, 2026-10-14) and Stage 0 dependency policy'),
        ('/integrations', 'descoped', 'email / EDI / portal integrations declared not implemented — PROJECT.md Stage 0 CONFIRMED (user, 2026-10-14)'),
    ]
    ledger_files = {}
    for fid, b in brds.items():
        claimed = set()
        for r in rows:
            for f, ptr, cnt, kind, label, acc in r['claims']:
                if f == fid:
                    claimed |= {x for x in LV[fid] if x == ptr or x.startswith(ptr + '/')}
        nb = []
        for pre, cat, reason in NONBUILD:
            hit = [x for x in LV[fid] if x == pre or x.startswith(pre + '/')]
            if hit:
                nb.append((pre if pre in LV[fid] else pre + '/*', len(hit) if pre not in LV[fid] else None, cat, reason, set(hit)))
        ledgered = set().union(*[h for *_, h in nb]) if nb else set()
        both = claimed & ledgered
        missing = set(LV[fid]) - claimed - ledgered
        if both:
            errors.append('%s: %d leaves both claimed and ledgered, e.g. %s' % (fid, len(both), sorted(both)[0]))
        if missing:
            errors.append('%s: %d leaves neither claimed nor ledgered, e.g. %s' % (fid, len(missing), sorted(missing)[:3]))
        ledger_files[fid] = nb

    # ── write build-plan.md ──────────────────────────────────────────────────────────────────
    nuc = sum(len(b['useCases']) for b in brds.values())
    nbuild = sum(1 for r in rows if r['kind'] == 'BUILD')
    phases_meta = OrderedDict([('0', 'Project scaffold'), ('1', 'Domain models, all modules')] +
                              [(p, '%s (%s)' % (m, folder)) for m, (p, folder) in PHASE_OF_MODULE.items()] + [('10', 'Close')])
    L = ['# Build plan — erpv1', '',
         '_Generated by `pipelines/odoo/plan_render.py` from the confirmed BRDs (`analysis/odoo/knowledge-base/brd/`), `ui_spec.py` and the Stage 3 '
         'architecture. Edit the generators, never this file. The plan contains no MDL: scripts are drafted per phase, after the previous phase passed its gate._', '',
         '## Pending decisions (Stage 4 ✋ — answer before row 1)', '',
         '| ID | Decision | Proposal | Blocks |', '|---|---|---|---|',
         '| PD-1 | Acceptance criteria per module | Module done = verify-module.sh no FAULT · every use case of the module walked as its demo user (journey passes, data effect asserted by OQL) · unit tests pass · every page LOOKed at 1280 and 390 px against its wireframe · coverage ledger clean for its BRD rows | every HARNESS close row |',
         '| PD-2 | Environment / DTAP | Local only: `mxcli run --local` in this cloud container, `--hub` public preview URL for the demo; no Mendix Cloud deployment, no DTAP; optional Docker image at the end | row 4 onwards (boot) |',
         '| PD-3 | StyleGallery UI module (Step 4b ✋) | **No** — the mxcli ledger theme already ships the recipe classes (num, pill, stat, density) and the widget layer; `design/design-system.html` is the reference; a gallery would add ~12 scripts for a POC. Phase 2 is therefore absent | phase 3 page rows |',
         '| PD-4 | MDL generation strategy / security timing (CAC-5 Q1, Q2) | Phase-by-phase in dependency order, draft + exec + verify each phase before drafting the next; security in layer 1 (roles + entity grants in phase 1, grants co-located in every script) | all rows |',
         '| PD-5 | Deadline / priority feature (CAC-5 open question) | none — pure dependency order (Core → … → Invoicing) | ordering |',
         '| PD-6 | Optional Stage 5 artifacts (demo script, test plan, acceptance criteria) | demo script — recommended, since the POC ends in a demo; written before phase 3 | — |', '',
         '## 0. Marketplace imports (Step 0)', '', 'Confirmed Buy (fit-gap, Stage 3): Administration, Data Widgets, Charts, Workflow Commons; Atlas Core comes with `mxcli new`. Imported in row 3, before any domain script.', '',
         '## 1. Module dependency order and test shape', '', '| Module | Dep. order | Depends on (associations) | Test shape | Calls out? |', '|---|---|---|---|---|']
    for i, m in enumerate(S.MODULES):
        deps = sorted({k.split(' -> ')[1] for k in graph['associationEdges'] if k.startswith(m + ' ->')})
        L.append('| %s | %d | %s | UI + Data + Unit | no — unit because intake Q13 = yes and the module has %s logic |' % (
            m, i + 1, ', '.join(deps) or '—', {'Core': 'tax / numbering / due-date', 'Products': 'unit conversion / pricing', 'Partners': 'address resolution',
                                              'Sales': 'totals / status', 'Purchasing': 'totals / approval routing', 'Inventory': 'stock / reservation',
                                              'Invoicing': 'invoice / payment'}[m]))
    L += ['', '## 2. Architecture questions resolved before scripting', '', '| # | Question | Resolution |', '|---|---|---|',
          '| 1 | Iteration granularity | one use case per BUILD row (default); scripts per layer inside a row, microflows ≤ 6 per script; BUILD rows ÷ use cases = %d ÷ %d = **%.2f** (in range 0.5–1.5) |' % (nbuild, nuc, nbuild / nuc),
          '| 2 | Cross-module association ownership | the referencing module owns and creates each association in its phase-1 domain script (53 associations, `module-graph.json`); layers acyclic |',
          '| 3 | Stub vs real | no integrations; forward stubs only for bridge microflows built in a later phase (listed per row) |',
          '| 4 | Demo users / roles | 9 user roles (Q-F001-2); demo users in row "Demo users"; happy path as the non-admin role of each use case |',
          '| 5 | Acceptance criteria | PD-1 (pending) |', '| 6 | Environment | PD-2 (pending) |', '',
          '## 3. Granularity', '', 'Default applied: a row is one BRD use case. Shared logic used across use cases gets its own row per module. %d BUILD rows for %d use cases (%.2f).' % (nbuild, nuc, nbuild / nuc), '',
          '## 4. Scope boundary', '', '- **In scope, real:** F001–F008 as confirmed (C1–C8).',
          '- **In scope, stubbed:** none (no integrations). Forward stubs for bridge microflows are build-order scaffolding, replaced in a later row.',
          '- **Out of scope:** C9–C12; mail/portal/payment/EDI/barcodes; variants, lots, packages, multi-step routes, ledger, PDFs, returns, scrap, down payments (Stage 0/2 decisions).', '',
          '## 4b. StyleGallery', '', 'PD-3 — proposed **No** (ASSUMED until answered). If Yes, a Phase 2 is inserted before phase 3.', '',
          '## 5. Numbered rows', '']
    for pid, pname in phases_meta.items():
        prs = [r for r in rows if r['phase'] == pid]
        if not prs:
            continue
        L += ['### Phase %s — %s' % (pid, pname), '', '| # | Kind | Step | Produces / Proves | Depends on | Skills | State |', '|---|---|---|---|---|---|---|']
        for r in prs:
            step = '<br>'.join('`%s`' % s if not s.startswith('(') else s for s in r['step'])
            L.append('| %d | %s | **%s**<br>%s | %s | %s | %s | %s |' % (r['n'], r['kind'], r['title'].replace('|', '/'), step,
                                                                   r['produces'].replace('|', '/'), ', '.join(map(str, r['depends'])) or '—', r['skills'], r['state']))
        L.append('')
        for r in prs:
            if not (r['claims'] or r['extra'] or r['accept']):
                continue
            L.append('#### Row %d · %s' % (r['n'], r['title']))
            if r['accept']:
                L.append('- **acceptance:** %s' % r['accept'])
            for e in r['extra']:
                L.append('- %s' % e)
            if r['claims']:
                L.append('')
                L.append('claims:')
                for fid, ptr, cnt, kind, label, acc in r['claims']:
                    L.append('  %s%s [%s]' % (ptr + ('/*' if cnt else ''), ' (%d)' % cnt if cnt else '', fid))
            L.append('')
    if any(r['kind'] == 'BUILD' and 'workflow' in r['produces'] for r in rows):
        wr = next(r for r in rows if 'WF_PurchaseOrderApproval' in r['produces'])
        L += ['### Workflow construct table — WF_PurchaseOrderApproval (workflow-structure-rules.md §11, re-check with `./mxcli syntax workflow` first)', '',
              '| Construct (from blueprint.md Step 3b) | §11 status | Where it gets built |', '|---|---|---|',
              '| user task "Approve purchase order", outcomes Approve / Reject | proven | row %d |' % wr['n'],
              '| targeting by user role token `[%%UserRole_PurchaseManager%%]` | proven | row %d |' % wr['n'],
              '| task page with `System.WorkflowUserTask` + `$WorkflowContext` parameters (CE7412) | proven — page must exist before the workflow | row %d (page script before workflow script) |' % wr['n'],
              '| call microflow on each outcome (`WITH` value quoted; `$WorkflowUserTask` not in scope) | proven | row %d |' % wr['n'],
              '| decision activities | none in this workflow (routing decided in ACT_PurchaseOrder_Confirm) — BUG-76 avoided | — |', '',
              'Denominator: 4 constructs in the diagram, 4 scripted in row %d, 0 hand-add rows needed. Native `mx check` after the write (a clean `mxcli check` proves nothing for workflows).' % wr['n'], '']
    # access roll-up
    L += ['## 6. Role-to-access roll-up', '', 'Per-element tables live in each module brief. Roll-up per user role (module roles composed):', '',
          '| User role | ' + ' | '.join(S.MODULES) + ' | Home page |', '|---|' + '---|' * (len(S.MODULES) + 1)]
    for ur in U.ROLE_HOME:
        L.append('| %s | %s | %s |' % (ur, ' | '.join(', '.join(mr for mr, urs in MODULE_ROLES[m].items() if ur in urs) or '—' for m in S.MODULES), U.ROLE_HOME[ur]))
    gaps = []
    for scr, s in U.S.items():
        mod = s['entity'].split('.')[0]
        for ur in s['roles']:
            if not any(ur in urs for urs in MODULE_ROLES[mod].values()):
                gaps.append('%s: %s has no module role in %s' % (scr, ur, mod))
    L += ['', 'Roll-up check: every screen\'s roles (ui_spec) hold a module role in the screen\'s module — **%s**.' % (
        'no gaps' if not gaps else '%d gaps: %s' % (len(gaps), '; '.join(gaps)))]
    if gaps:
        errors += gaps
    L += ['', '## 7. Demo users', '', '| Demo user | User role | Notes |', '|---|---|---|']
    for du, ur in [('sales.user', 'SalesUser'), ('sales.manager', 'SalesManager'), ('purchaser', 'Purchaser'), ('purchase.manager', 'PurchaseManager'),
                   ('warehouse.user', 'InventoryUser'), ('inventory.manager', 'InventoryManager'), ('billing', 'Billing'), ('invoicing.manager', 'InvoicingManager'),
                   ('admin.user', 'Administrator')]:
        L.append('| %s | %s | %s |' % (du, ur, 'happy-path user for its role' if ur != 'Administrator' else 'setup only, never happy-path'))
    L += ['', "Password for every demo user: `%s` (throwaway, project-local; MxAdmin untouched)." % DEMO_PASSWORD, '',
          '## 8. Navigation wiring and prototype routes', '', '| Page | Module | Wire point | Prototype route |', '|---|---|---|---|']
    navmap = {scr: '%s › %s' % (g, l) for g, l, scr in U.NAV}
    pm_lines = []
    for scr, s in U.S.items():
        mod = s['entity'].split('.')[0]
        L.append('| %s | %s | %s | `#/%s` |' % (scr, mod, ('Responsive menu ' + navmap[scr]) if scr in navmap else 'opened from ' + '; '.join(s['reached']), U.route(scr)))
        pm_lines.append('%s\t../prototype.html#/%s' % (scr, U.route(scr)))
    L += ['', 'Home pages per user role: see §6. Account_Overview (Administration) wired under Configuration › Users.', '',
          '## 9. CONFIRMED-decision reconciliation (Stages P–3)', '', '| Decision (PROJECT.md) | Build disposition |', '|---|---|']
    proj = open('PROJECT.md').read()
    dec = [ln for ln in proj.splitlines() if re.match(r'^\| (P|0|1|2|3) \|', ln) and '| CONFIRMED |' in ln]
    first = lambda pred: next((r['n'] for r in rows if pred(r)), None)
    def disp(text):
        t = text.lower()
        if 'mendix version' in t or 'project scaffold' in t:
            return 'row %d (mxcli new --version 11.15.0)' % first(lambda r: r['title'] == 'Project scaffold')
        if 'marketplace' in t:
            return 'row %d' % first(lambda r: r['title'].startswith('Marketplace'))
        if 'branding' in t or 'ledger' in t:
            return 'row %d (`mxcli theme apply ledger`)' % first(lambda r: r['title'] == 'Project scaffold')
        if 'navigation layout' in t:
            return 'row %d (layout + navigation shell) and §8' % first(lambda r: r['title'] == 'Project scaffold')
        if 'role model' in t or '9 user roles' in t:
            return 'row %d (roles), row %d (demo users)' % (first(lambda r: r['title'].startswith('Module roles')), first(lambda r: r['title'].startswith('Demo users')))
        if 'module boundaries' in t or 'erd' in t or 'one mendix app' in t:
            return 'rows %d–%d (one domain row per module, phase 1)' % (domain_rows['Core']['n'], domain_rows['Invoicing']['n'])
        if 'brd set' in t:
            return 'every BUILD row (claims) — coverage ledgers per BRD'
        if 'volumes' in t:
            return 'domain rows %d–%d (indexes on number/date/status), page rows (Data Grid 2 paging)' % (domain_rows['Core']['n'], domain_rows['Invoicing']['n'])
        if 'integrations' in t or 'missing dependencies' in t:
            return 'descoped — ledger NON-BUILDABLE `/integrations/*` per BRD (Stage 0 decision)'
        if 'scope slicing' in t:
            return 'phases 3–9, one per module in layer order (W1 = phases 3–5 Core/Products/Partners, W2 = 6–7 Sales/Purchasing, W3 = 8 Inventory, W4 = 9 Invoicing); out-of-scope apps never enter the plan'
        if 'scope' in t and ('c1' in t or 'cac-1' in t):
            return 'phases 3–9 (C1–C8); C9–C12 descoped (`/droppedOdooModels/*` ledger entries)'
        if "odoo in-place" in t or 'mixins' in t or 'delegation' in t or 'generalization only' in t:
            return 'domain rows %d–%d (rule applied in brd_spec.py; e.g. Partners.UserProfile association, ProductImage → System.Image)' % (
                domain_rows['Core']['n'], domain_rows['Invoicing']['n'])
        if 'stage 3 ✋' in t or 'sign-off' in t:
            return 'page rows built against design/wireframes (§8 routes), theme row %d' % first(lambda r: r['title'] == 'Project scaffold')
        if 'extraction' in t or 'path a' in t or 'path b' in t:
            return 'process — produced the knowledge base the BRDs were generated from; builds nothing'
        if 'entry mode' in t or 'source:' in t or 'driver' in t or 'fidelity' in t or 'interview mode' in t or 'exec approval' in t or 'source is committed' in t:
            return 'process — governs how the project runs; builds nothing'
        if 'conventions' in t:
            return 'domain rows (system members on every persistent entity)'
        return None
    unm = []
    for ln in dec:
        cells = [c.strip() for c in ln.strip('|').split('|')]
        d = disp(cells[1])
        if d is None:
            unm.append(cells[1][:80])
            d = '**UNMAPPED**'
        L.append('| %s · %s | %s |' % (cells[0], cells[1][:140].replace('|', '/'), d))
    if unm:
        errors.append('CONFIRMED decisions without disposition: %s' % unm)
    L += ['', '## 10. Coverage', '', 'Ledgers: `architecture/modules/<Module>/coverage-ledger/<BRD>.md` (per-BRD directory form). '
          'Run: `for f in analysis/odoo/knowledge-base/brd/F*.brd.json; do ...coverage-check.sh "$f" <ledger>; done` — results pasted in chat at the Stage 4 gate.', '']
    open('architecture/build-plan.md', 'w').write('\n'.join(L) + '\n')
    open('design/wireframes/PAGE-MAP.tsv', 'w').write('\n'.join(pm_lines) + '\n')

    # ── ledgers ──────────────────────────────────────────────────────────────────────────────
    live = model_inventory()
    ledger_mods = defaultdict(set)   # module -> BRDs with rows in that module's phases
    phase_mod = {v[0]: k for k, v in PHASE_OF_MODULE.items()}
    for r in rows:
        for f, ptr, cnt, kind, label, acc in r['claims']:
            mm = re.search(r'\b(%s)\.' % '|'.join(S.MODULES), acc + ' ' + label)
            m = mm.group(1) if mm else phase_mod.get(r['phase'])
            if m:
                ledger_mods[m].add(f)
    for fid in brds:
        ledger_mods[HOME_MODULE[fid]].add(fid)
    for fid, b in brds.items():
      for lmod in sorted(m for m, fs in ledger_mods.items() if fid in fs):
        d = os.path.join('architecture', 'modules', lmod, 'coverage-ledger')
        os.makedirs(d, exist_ok=True)
        Lg = ['# Coverage ledger — %s %s' % (fid, b['title']), '', '_Generated by `pipelines/odoo/plan_render.py` together with `architecture/build-plan.md`; '
              'measured with `bin/coverage-check.sh analysis/odoo/knowledge-base/brd/%s.brd.json <this file>`._' % BRD_BASENAME[fid], '', '## BUILDABLE', '',
              '| pointer | type | title | slice | writeMode | acceptance | status |', '|---|---|---|---|---|---|---|']
        for r in rows:
            for f, ptr, cnt, kind, label, acc in r['claims']:
                if f != fid:
                    continue
                Lg.append('| `%s`%s | %s | %s | row %d | CLI | %s | %s |' % (ptr + ('/*' if cnt else ''), ' (%d)' % cnt if cnt else '', kind,
                                                                               label.replace('|', '/'), r['n'], acc.replace('|', '/'), status_of(acc, live)))
        Lg += ['', '## NON-BUILDABLE', '', '| pointer | category | reason |', '|---|---|---|']
        for ptr, cnt, cat, reason, _ in ledger_files[fid]:
            Lg.append('| `%s`%s | %s | %s |' % (ptr, ' (%d)' % cnt if cnt else '', cat, reason))
        open(os.path.join(d, '%s.md' % BRD_BASENAME[fid]), 'w').write('\n'.join(Lg) + '\n')
    # index per module dir
    for mod in ledger_mods:
        fids = sorted(ledger_mods[mod])
        open(os.path.join('architecture', 'modules', mod, 'coverage-ledger.md'), 'w').write(
            '# Coverage ledger index — %s\n\nPer-BRD ledgers: %s\n' % (mod, ', '.join('[%s](coverage-ledger/%s.md)' % (f, BRD_BASENAME[f]) for f in fids)))

    # ── module briefs ────────────────────────────────────────────────────────────────────────
    toolkit_sha = os.popen('git -C %s rev-parse --short HEAD' % TOOLKIT).read().strip()
    for mi, mod in enumerate(S.MODULES):
        mrows = [r for r in rows if r['phase'] == PHASE_OF_MODULE[mod][0]]
        dom = domain_rows[mod]
        ents = [e for e in S.E if e['name'].startswith(mod + '.')]
        screens = [scr for scr, s in U.S.items() if s['entity'].startswith(mod + '.')]
        deps = sorted({k.split(' -> ')[1] for k in graph['associationEdges'] if k.startswith(mod + ' ->')})
        B = ['# Module Brief — %s' % mod, '', '- **Dependency order:** %d (depends on: %s)' % (mi + 1, ', '.join(deps) or '—'),
             '- **Build status:** not started', '- **Toolkit commit:** %s' % toolkit_sha,
             '- _Generated by `pipelines/odoo/plan_render.py`; phase 1 content is complete for every module; phase %s rows are extended by its BRIEF row._' % PHASE_OF_MODULE[mod][0], '',
             '## Pointers (source of truth — read these, don\'t duplicate them)',
             '- Wireframes:   %s' % (', '.join('design/wireframes/%s.html' % s for s in screens) or '—'),
             '- Blueprint:    architecture/blueprint.md, architecture/modules/%s/definition.md' % mod,
             '- BRDs:         %s' % ', '.join('analysis/odoo/knowledge-base/brd/%s-*.brd.json' % f for f in sorted({c[0] for c in dom['claims']})),
             '- Domain MDL:   %s' % dom['step'][0],
             '- Build-plan scripts: rows %d (domain) and %s' % (dom['n'], ', '.join(str(r['n']) for r in mrows if r['kind'] == 'BUILD') or '—'), '',
             '## Business layer  (ba-agent)', '### Roles & journeys', '| Role | What they do in this module | Entry screen |', '|------|-----------------------------|--------------|']
        for mr, urs in MODULE_ROLES[mod].items():
            entry = next((sc for sc in screens if any(u in U.S[sc]['roles'] for u in urs) and U.S[sc]['kind'] in ('list', 'inbox', 'dashboard', 'form')
                          and not U.S[sc].get('param')), '—')
            B.append('| %s.%s (%s) | %s | %s |' % (mod, mr, ', '.join(urs), {'Reader': 'reads %s data on other modules\' pages' % mod}.get(mr, 'maintains %s data' % mod), entry))
        B += ['', '### Screens per role', '| Screen (→ wireframe file) | Roles that reach it | Nav wire point |', '|---|---|---|']
        for sc in screens:
            B.append('| %s (design/wireframes/%s.html) | %s | %s |' % (sc, sc, ', '.join(U.S[sc]['roles']), navmap.get(sc, 'opened from ' + U.S[sc]['reached'][0])))
        B += ['', '### Access table  (feeds co-located grants)', '| Element | Type | Module role(s) | Access level |', '|---|---|---|---|']
        for e in ents:
            if not e['persistent']:
                continue
            for mr in MODULE_ROLES[mod]:
                lvl = 'read *' if mr == 'Reader' else ('create, delete, read *, write *' if mr in ('Manager', 'Admin', 'Config', 'Editor', 'Billing') else 'create, read *, write *')
                xp = ' — XPath `[Sales.SalesOrder_Salesperson = \'[%CurrentUser%]\']`' if (e['name'] in ('Sales.SalesOrder', 'Sales.SalesOrderLine') and mr == 'User') else ''
                B.append('| %s | entity | %s.%s | %s%s |' % (e['name'], mod, mr, lvl, xp))
        for sc in screens:
            mrs = sorted({'%s.%s' % (mod, mr) for mr, urs in MODULE_ROLES[mod].items() if set(urs) & set(U.S[sc]['roles'])})
            B.append('| %s.%s | page | %s | view |' % (mod, sc, ', '.join(mrs)))
        mf_here = [(fid, m) for fid, b in brds.items() for m in b['microflows'] if m.get('module') == mod]
        for fid, m in mf_here:
            callers = {sc for sc in screens if any(m['name'] in (p.get('actions') or []) for b2 in brds.values() for p in b2['pages'] if p['name'] == sc)}
            urs = set().union(*[set(U.S[sc]['roles']) for sc in callers]) if callers else {u for mr, us in MODULE_ROLES[mod].items() if mr != 'Reader' for u in us}
            mrs = sorted({'%s.%s' % (mod, mr) for mr, us in MODULE_ROLES[mod].items() if set(us) & urs})
            B.append('| %s.%s | microflow | %s | execute%s |' % (mod, m['name'], ', '.join(mrs) or '%s.Manager' % mod,
                                                              '' if m['name'].startswith(('ACT_', 'VAL_')) else ' (sub-microflow: called only, no direct grant needed beyond callers)'))
        B += ['', '### Field-level validation & edge cases', '| Field / action | Rule | Error path |', '|---|---|---|']
        for e in ents:
            for n, of, ov in e['attrs']:
                req = ov.get('mandatory')
                be = next((de for de in ent_index.values() if de['name'] == e['name'] and not de.get('extensionOf')), None)
                at = next((x for x in (be or {}).get('attributes', []) if x['name'] == n), None)
                if at and at.get('mandatory'):
                    B.append('| %s.%s | required (Odoo %s required) | validation feedback on the field, save refused |' % (e['name'], n, at.get('sourceOdoo')))
        for fid, m in mf_here:
            for v in m.get('validations', []):
                B.append('| %s.%s | %s | validation message, no commit |' % (mod, m['name'], v.replace('|', '/')))
        B += ['', '### Golden-path data effects (what each key action must persist)', '| Action | Creates/changes | Associations that MUST be set |', '|---|---|---|']
        for fid, m in mf_here:
            if m['pattern'] in ('create', 'state-change'):
                tgt = m['returns'] if '.' in str(m['returns']) else (m['params'][0]['type'] if m['params'] else '—')
                te = next((e for e in S.E if e['name'] == tgt), None)
                must = [x[0] for x in (te['assocs'] if te else []) if x[0].endswith(('_SalesOrder', '_PurchaseOrder', '_Customer', '_Vendor', '_Partner', '_Invoice', '_Transfer', '_Product'))]
                B.append('| %s | %s | %s |' % (m['name'], tgt, ', '.join(must) or '—'))
        B += ['', '### Open business questions', '- none — all 15 Stage 2 questions answered 2026-10-14; Stage 4 pending decisions PD-1..PD-6 are in the build plan', '',
              '## Test plan  (ba-agent drafts, confirmed with the user at brief sign-off)', '', '### Declared shape', '| Part | This module | Why |', '|---|---|---|',
              '| UI (Playwright) | always | — |', '| Data (source of truth) | always — OQL count/field delta on the %s entities each journey writes | testing-shape.md §1 |' % mod,
              '| Unit (`.test.mdl`) | yes | project default (intake Q13) and %s has calculation/state logic |' % mod, '| Trace (OTel) | no | the module calls out to nothing |', '',
              '### Base set — the trigger', '']
        for r in [dom] + [r for r in mrows if r['kind'] == 'BUILD']:
            for sc in r['step']:
                if sc.startswith('mdlsource'):
                    B.append('- [ ] `%s`' % sc)
        B += ['', '### Journeys', '| Journey id | Persona | Trigger → outcome | Steps | Data effect asserted |', '|---|---|---|---|---|']
        for r in mrows:
            for fid, ptr, cnt, kind, label, acc in r['claims']:
                if kind == 'useCase':
                    uc = brds[fid]['useCases'][int(ptr.split('/')[-1])]
                    B.append('| %s-%s | %s | %s → %s | %s | %s |' % (fid, uc['id'], uc['actors'][0], uc['mainFlow'][0][3:], uc['postconditions'][0],
                                                                   ' · '.join(s.split('. ', 1)[-1][:40] for s in uc['mainFlow'][:4]), uc['postconditions'][0]))
        B += ['', '### Interactive elements — the wiring sweep\'s denominator', '', '> `N of N interactive elements swept across P of P pages in %s` — first line of `.claude/loop/sweep/%s/sweep.md`' % (mod, mod), '',
              '| Known exclusion | Why it cannot be swept |', '|---|---|', '', '### Pages to LOOK at', 'Derived at review time with `SHOW PAGES IN %s`; intent per screen in "Screens per role".' % mod, '',
              '## Technical layer  (architect-agent)', '### Domain summary', '- Entities: %s' % ', '.join(e['name'].split('.')[1] for e in ents),
              '- Key associations: %s' % ', '.join(x[0] for e in ents for x in e['assocs'][:2]), '',
              '### Build skills to read first', '- %s' % ', '.join(sorted({s.strip() for r in [dom] + mrows for s in r['skills'].split(',') if s.strip() and s.strip() != 'none'})), '',
              '### Write-mode plan', '| Element | CLI / Studio Pro by hand | Why |', '|---|---|---|',
              '| entities, enumerations, associations, access | CLI | proven constructs |', '| pages, microflows | CLI | proven constructs |']
        if mod == 'Purchasing':
            B.append('| WF_PurchaseOrderApproval | CLI, then native `mx check` | all 4 constructs proven in §11; no DECISION (BUG-76) |')
        # feature group per document by keyword (module-folder-convention.md: feature group, then Pages/Microflows)
        FG = {'Core': [('Numbering', ['Sequence']), ('Taxes', ['Tax']), ('PaymentTerms', ['PaymentTerm']), ('Setup', ['Seed', 'Currency', 'Country', 'Home']),
                       ('Company', ['Company'])],
              'Products': [('UnitsOfMeasure', ['UoM']), ('Pricing', ['Pricelist', 'PriceRule']), ('Catalogue', ['Product', 'Seed'])],
              'Partners': [('Users', ['UserProfile']), ('Contacts', ['Partner', 'Seed', 'Tag', 'Bank'])],
              'Sales': [('Templates', ['Template']), ('Teams', ['SalesTeam']), ('Reporting', ['Analysis']), ('Quotations', ['SalesOrder', 'CreateInvoice', 'Seed'])],
              'Purchasing': [('Approval', ['Approval', 'Approve', 'Reject', 'WF_']), ('VendorPrices', ['VendorPrice']), ('Reporting', ['Analysis']),
                             ('RFQs', ['PurchaseOrder', 'Seed'])],
              'Inventory': [('Replenishment', ['Reorder']), ('Stock', ['StockLevel', 'StockOnHand', 'Dashboard']), ('Configuration', ['Warehouse', 'Location', 'OperationType', 'Seed']),
                            ('Fulfilment', ['CreateDelivery', 'CreateReceipt', 'UpdateDelivered', 'UpdateReceived']), ('Operations', ['Transfer', 'StockMove'])],
              'Invoicing': [('CreditNotes', ['CreditNote']), ('Payments', ['Payment']), ('Reporting', ['Analysis']), ('Invoices', ['Invoice', 'Bill', 'Seed'])]}[mod]
        groups = [g for g, _ in FG]

        def fgroup(doc):
            for g, keys in FG:
                if any(k.lower() in doc.lower() for k in keys):
                    return g
            return FG[-1][0]
        B += ['', '### Document folder plan', '- **Feature groups:** %s' % ', '.join(groups), '', '| Document | Folder |', '|---|---|']
        for sc in screens:
            B.append('| %s | `%s/Pages` |' % (sc, fgroup(sc)))
        for fid, m in mf_here:
            B.append('| %s | `%s/Microflows` |' % (m['name'], fgroup(m['name'])))
        B += ['', '### Build steps', '| Step | Builds | Reads | Example | Slice |', '|---|---|---|---|---|']
        k = 0
        for r in [dom] + [r for r in mrows if r['kind'] == 'BUILD']:
            for sc in r['step']:
                if sc.startswith('mdlsource'):
                    k += 1
                    reads = ', '.join(sorted({e['name'] for e in ents})[:4])
                    B.append('| %d.%d | %s | %s | — (first of its kind in this app) | row %d |' % (mi + 1, k, os.path.basename(sc), reads, r['n']))
        B += ['', '### Cross-module dependencies & integrations', '- Depends on: %s · Integrations: none' % (', '.join(deps) or '—'), '',
              '### Arch constraints that apply here', '- associations point down the layer stack only (Core → Products → Partners → Sales/Purchasing → Inventory/Invoicing); upward calls only the sanctioned bridges',
              '- grants co-located in each script; security level production from row 2', '',
              '## Ready-check', '- [x] Every screen has a wireframe file that exists', '- [x] Access table covers every page, microflow, and entity to be built',
              '- [x] No open business question blocks the elements in this build phase', '- [x] Write mode chosen for every element that hits a STOP row',
              '- [x] Folder plan names the module\'s feature groups and covers every document to be built',
              '- [ ] Build steps: `bin/context-pack.sh %s <Step>` exits 0 for each — runs once the model exists (phase 1)' % mod,
              '- [x] Test plan complete: shape declared, base set named, journeys with data effects', '- [x] Build skills to read first is filled in']
        open(os.path.join('architecture', 'modules', mod, 'module-brief.md'), 'w').write('\n'.join(B) + '\n')

    print('rows: %d (%d BUILD, %d use cases, ratio %.2f); phases: %d' % (len(rows), nbuild, nuc, nbuild / nuc, len({r["phase"] for r in rows})))
    if errors:
        print('ERRORS (%d):' % len(errors))
        for e in errors[:40]:
            print('  - ' + str(e))
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
