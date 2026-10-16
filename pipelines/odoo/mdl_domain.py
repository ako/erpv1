#!/usr/bin/env python3
"""mdl_domain.py — generate the Phase 1 (layer 1) MDL scripts from the BRDs + module briefs.

Writes, under mdlsource/1-domain/:
  100-security-roles.mdl        module roles (arch_blueprint.MODULE_ROLES) + the 9 user roles
  110..170-<module>-domain.mdl  enumerations, entities, associations, entity access (co-located)
  190-security-demo-users.mdl   one demo user per user role (build-plan row 14)

Sources of truth (never hand-edit the output; edit these and regenerate):
  analysis/odoo/knowledge-base/brd/F*.brd.json   domainEntities / enumerations
  architecture/modules/<M>/module-brief.md        "### Access table" entity rows
  pipelines/odoo/arch_blueprint.py                MODULE_ROLES

Decisions applied here (PROJECT.md / FINDINGS.md):
  - no NOT NULL rules: required-ness lives in VAL_ microflows (CONV015, learned-microflow-patterns.md "validation
    feedback");
  - Odoo uniqueness and range constraints (BRD odooConstraints, disposition implement) ARE entity rules, enforced in the
    database (user 2026-10-16). A composite key gets a stored UniqueKey attribute, filled before commit from the
    referenced entities' AutoNumber KeyNumber (175-domain-composite-keys.mdl);
  - Odoo computed-stored fields become plain stored attributes, written by SUB_ microflows;
  - Odoo `Date` fields are `DateTime not localized`;
  - system members (createdDate/changedDate/owner/changedBy) -> AutoCreatedDate/AutoChangedDate/
    AutoOwner/AutoChangedBy (never bound to a widget: learned-mdl-preflight STOP #4);
  - indexes on document number/date/state attributes only (Stage 3 volumes decision).
Run: python3 -I pipelines/odoo/mdl_domain.py
"""
import glob, json, os, re, sys
from collections import OrderedDict, defaultdict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.dirname(__file__))
from arch_blueprint import MODULE_ROLES  # noqa: E402

MODULES = ['Core', 'Products', 'Partners', 'Sales', 'Purchasing', 'Inventory', 'Invoicing']
NUM = {m: 110 + 10 * i for i, m in enumerate(MODULES)}
OUT = os.path.join(ROOT, 'mdlsource', '1-domain')
DEMO_PASSWORD = 'Erpv1-Demo-2026!'
USER_ROLES = ['Administrator', 'SalesUser', 'SalesManager', 'Purchaser', 'PurchaseManager',
              'InventoryUser', 'InventoryManager', 'Billing', 'InvoicingManager']
DEMO_USERS = [('sales.user', 'SalesUser'), ('sales.manager', 'SalesManager'), ('purchaser', 'Purchaser'),
              ('purchase.manager', 'PurchaseManager'), ('warehouse.user', 'InventoryUser'),
              ('inventory.manager', 'InventoryManager'), ('billing', 'Billing'),
              ('invoicing.manager', 'InvoicingManager'), ('admin.user', 'Administrator')]
ROLE_DESC = {
    'Admin': 'Full configuration of the module', 'Config': 'Maintains the module\'s configuration data',
    'Reader': 'Read-only access (lookups from other modules)', 'Manager': 'Full access incl. configuration and delete',
    'Editor': 'Create and edit records', 'User': 'Day-to-day work on own documents', 'Billing': 'Invoices, bills and payments',
    'Creator': 'Creates invoices from orders (bridge)',
    ('Partners', 'Manager'): 'Manager-only contact actions (archive); data access comes with Editor',
}
SYSTEM_MEMBERS = OrderedDict([('createdDate', ('CreatedDate', 'AutoCreatedDate')),
                              ('changedDate', ('ChangedDate', 'AutoChangedDate')),
                              ('owner', ('Owner', 'AutoOwner')),
                              ('changedBy', ('ChangedBy', 'AutoChangedBy'))])
INDEXED_NAMES = {'Name', 'Number', 'State', 'Status', 'OrderDate', 'InvoiceDate', 'ScheduledDate', 'Date', 'DateOrder'}


def q(name):
    return '"%s"' % name


def qn(qual):
    mod, name = qual.split('.', 1)
    return '%s.%s' % (mod, q(name))


def esc(s):
    return (s or '').replace("'", "''").replace('\n', ' ').strip()


def load():
    ents, enums = OrderedDict(), OrderedDict()
    exts = []
    for f in sorted(glob.glob(os.path.join(ROOT, 'analysis/odoo/knowledge-base/brd/F*.brd.json'))):
        d = json.load(open(f))
        for e in d['domainEntities']:
            if e.get('extensionOf') or e.get('definedInBrd'):
                exts.append((d['id'], e))
            else:
                e = dict(e)
                e['brds'] = [d['id']]
                ents[e['name']] = e
        for en in d.get('enumerations', []):
            enums.setdefault(en['name'], en)
    for fid, x in exts:
        base = ents.get(x['name'])
        if base is None:
            raise SystemExit('extension of unknown entity %s (%s)' % (x['name'], fid))
        have = {a['name'] for a in base['attributes']}
        base['attributes'] = base['attributes'] + [a for a in x.get('attributes', []) if a['name'] not in have]
        haveA = {a['name'] for a in base['associations']}
        base['associations'] = base['associations'] + [a for a in x.get('associations', []) if a['name'] not in haveA]
        base['brds'].append(fid)
    return ents, enums


def attr_type(a, enums):
    t = a['type']
    if t == 'String':
        ln = a.get('length')
        if ln in (None, 'unlimited') or (isinstance(ln, int) and ln > 2000):
            return 'String(unlimited)'
        return 'String(%d)' % int(ln)
    if t == 'Enumeration':
        en = a['enumeration']
        if en not in enums:
            raise SystemExit('unknown enumeration %s' % en)
        return 'Enumeration(%s)' % en
    if t == 'DateTime':
        return 'DateTime not localized' if a.get('odooType') == 'Date' else 'DateTime'
    if t in ('Decimal', 'Integer', 'Boolean', 'Long'):
        return t
    raise SystemExit('unmapped type %s on %s' % (t, a['name']))


def odoo_default(a, enums):
    """Odoo's own default when it is a plain literal (True/False/number/'string'/enum key); functions,
    lambdas and fields.* stay with the microflows that create the object."""
    v = str(a.get('odooDefault', '')).strip()
    if not v or '(' in v or v.startswith(('lambda', 'fields.', '_')):
        return None
    t = a['type']
    if t == 'Boolean':
        return {'True': 'true', '1': 'true', 'False': 'false', '0': 'false'}.get(v)
    if t in ('Decimal', 'Integer', 'Long'):
        try:
            f = float(v)
        except ValueError:
            return None
        return str(int(f)) if t != 'Decimal' or f == int(f) else v
    if t == 'Enumeration' and v[:1] in '\'"':
        key = v.strip('\'"')
        hit = next((x['name'] for x in enums[a['enumeration']]['values'] if str(x.get('odooValue')) == key), None)
        return hit
    if t == 'String' and v[:1] in '\'"':
        return v.strip('\'"')
    return None


def default_clause(a, enums):
    v = a.get('default')
    if v is None:
        v = odoo_default(a, enums)
        if v is None:
            return ''
        if a['type'] == 'Enumeration':
            return ' default %s' % v
        if a['type'] == 'String':
            return " default '%s'" % esc(v)
        return ' default %s' % v
    t = a['type']
    if t == 'Boolean':
        return ' default %s' % ('true' if str(v).lower() in ('true', '1') else 'false')
    if t in ('Decimal', 'Integer', 'Long'):
        try:
            float(v)
        except ValueError:
            return ''
        return ' default %s' % v
    if t == 'Enumeration':
        vals = [x['name'] for x in enums[a['enumeration']]['values']]
        vv = str(v).split('.')[-1]
        return (' default %s' % vv) if vv in vals else ''
    if t == 'String':
        return " default '%s'" % esc(str(v))
    return ''


def parse_access():
    """{entity: [(module_role, rights, xpath)]} from every brief's access table."""
    acc = defaultdict(list)
    row = re.compile(r'^\| ([A-Za-z]+\.[A-Za-z_]+) \| entity \| ([^|]+) \| ([^|]+) \|')
    for m in MODULES:
        p = os.path.join(ROOT, 'architecture/modules/%s/module-brief.md' % m)
        for line in open(p):
            mm = row.match(line)
            if not mm:
                continue
            ent, roles, level = mm.group(1), [r.strip() for r in mm.group(2).split(',')], mm.group(3).strip()
            xp = None
            if '— XPath' in level:
                level, xp = level.split('— XPath', 1)
                xp = xp.strip().strip('`')
            rights = [r.strip() for r in level.strip().split(',') if r.strip()]
            for r in roles:
                acc[ent].append((r, rights, xp))
    return acc


def header_path(ent, e, xp, ents):
    """An XPath written against the header (e.g. Sales.SalesOrder_Salesperson) on a line entity:
    prefix the line->header association so the constraint walks line -> header -> salesperson."""
    m = re.match(r"\[([A-Za-z]+)\.([A-Za-z]+)_([A-Za-z]+) = '\[%CurrentUser%\]'\]", xp)
    if not m:
        return xp
    mod, owner_short = m.group(1), m.group(2)
    owner = '%s.%s' % (mod, owner_short)
    if owner == ent:
        return xp
    hop = next((a for a in e['associations'] if a['target'] == owner and a['type'] == 'Reference'), None)
    if not hop:
        raise SystemExit('cannot route XPath %s on %s' % (xp, ent))
    return "[%s.%s/%s/%s.%s_%s = '[%%CurrentUser%%]']" % (mod, hop['name'], owner, mod, owner_short, m.group(3))


def gen_roles():
    L = ['mdl 1;', '-- 100-security-roles.mdl — GENERATED by pipelines/odoo/mdl_domain.py (build-plan row 6).',
         '-- Module roles per arch_blueprint.MODULE_ROLES and the 9 user roles composed of them.',
         '-- Core.User (scaffold role: home page) is kept and given to every user role.', '']
    for m in MODULES:
        L.append('create module if not exists %s;' % m)
    L.append('')
    comp = defaultdict(list)
    for m in MODULES:
        for role, users in MODULE_ROLES[m].items():
            L.append("create or modify module role %s.%s description '%s';" % (m, role, esc(ROLE_DESC.get((m, role), ROLE_DESC.get(role, role)))))
            for u in users:
                comp[u].append('%s.%s' % (m, role))
    L.append('')
    for u in USER_ROLES:
        mods = ['System.User', 'Administration.User', 'Core.User', 'WorkflowCommons.User'] + comp[u]
        extra = ''
        if u == 'Administrator':
            mods = ['System.Administrator', 'Administration.Administrator', 'Core.User', 'WorkflowCommons.Administrator'] + comp[u]
            extra = ',\n  ManageAllRoles: true'
        L.append('create or modify user role %s (\n  ModuleRoles: (%s)%s,\n  CheckSecurity: true\n);' % (u, ', '.join(mods), extra))
    return '\n'.join(L) + '\n'


def rules_of(e):
    """(single-attribute uniques {attr: message}, composite [(members, message)], ranges [(attr, op, value, message)])."""
    attrs = {a['name'] for a in e['attributes']}
    uniq, comp, rng = {}, [], []
    for c in e.get('odooConstraints') or []:
        if c.get('disposition') != 'implement':
            continue
        c = dict(c, message=c['message'].replace(' per company', ''))   # one company (PROJECT.md)
        if c['kind'] == 'unique':
            if len(c['members']) == 1 and c['members'][0] in attrs:
                uniq[c['members'][0]] = c['message']
            else:
                comp.append((c['members'], c['message']))
        elif c['kind'] == 'range' and c['members'][0] in attrs:
            rng.append((c['members'][0], c['operator'], c['value'], c['message']))
    return uniq, comp, rng


def key_targets(ents):
    """Entities referenced by a composite key: they carry an AutoNumber KeyNumber the key is built from."""
    out = set()
    for e in ents.values():
        assocs = {a['name']: a['target'] for a in e['associations']}
        for members, _ in rules_of(e)[1]:
            out |= {assocs[m] for m in members if m in assocs}
    return out


def gen_module(m, ents, enums, acc):
    L = ['mdl 1;', '-- %d-%s-domain.mdl — GENERATED by pipelines/odoo/mdl_domain.py (build-plan Phase 1).' % (NUM[m], m.lower()),
         '-- Enumerations, entities, associations owned by %s, then entity access (co-located grants).' % m,
         '-- Create/delete rights follow the approved access table; document state rules live in ACT_/SUB_ microflows.', '']
    mod_enums = [en for n, en in enums.items() if en['module'] == m]
    for en in mod_enums:
        doc = 'Values of Odoo %s.' % en.get('sourceOdoo', en['name'])
        if en.get('note'):
            doc += ' ' + esc(en['note'])
        L.append('/** %s */' % esc(doc))
        vals = ',\n'.join("  %s '%s'" % (q(v['name']), esc(v['caption'])) for v in en['values'])
        L.append('create or modify enumeration %s (\n%s\n) folder \'Enumerations\';' % (qn(en['name']), vals))
        L.append('')
    mod_ents = [e for n, e in ents.items() if n.split('.')[0] == m]
    for e in mod_ents:
        cols = []
        uniq, comp, rng = rules_of(e)
        for a in e['attributes']:
            u = (" unique error message '%s'" % esc(uniq[a['name']])) if a['name'] in uniq else ''
            cols.append('  %s: %s%s%s' % (q(a['name']), attr_type(a, enums), default_clause(a, enums), u))
        for members, msg in comp:
            cols.append("  \"UniqueKey\": String(200) unique error message '%s'" % esc(msg))
        if e['name'] in KEY_TARGETS:
            cols.append('  "KeyNumber": AutoNumber default 1')
        for key in e.get('systemMembers') or []:
            nm, tp = SYSTEM_MEMBERS[key]
            cols.append('  %s: %s' % (nm, tp))
        kind = 'persistent' if e.get('persistent', True) else 'non-persistent'
        ext = ' extends %s' % e['generalization'] if e.get('generalization') else ''
        doc = esc(e.get('purpose')) + (' (Odoo %s; %s)' % (e.get('sourceOdoo'), ', '.join(e['brds'])))
        L.append('/** %s */' % doc)
        body = ',\n'.join(cols)
        stmt = 'create or modify %s entity %s%s (\n%s\n)' % (kind, qn(e['name']), ext, body) if cols else \
               'create or modify %s entity %s%s ()' % (kind, qn(e['name']), ext)
        idx = [a['name'] for a in e['attributes'] if a['name'] in INDEXED_NAMES] if kind == 'persistent' else []
        if idx:
            stmt += '\nindex (%s)' % ', '.join(q(i) for i in idx)
        L.append(stmt + ';')
        L.append('')
    for e in mod_ents:
        for a in e['associations']:
            amod = e['name'].split('.')[0]
            doc = esc(a.get('note') or ('Odoo %s' % a.get('sourceOdoo', 'new')))
            L.append('/** %s */' % doc)
            L.append('create or modify association %s.%s\n  from %s to %s\n  type %s%s;' % (
                amod, q(a['name']), qn(e['name']), qn(a['target']), a['type'],
                # CE0001: an NPE->PE association starts in the NPE with owner Default
                '\n  owner Both' if a['type'] == 'ReferenceSet' and e.get('persistent', True)
                and ents.get(a['target'], {}).get('persistent', True) else ''))
    ranges = [(e, r) for e in mod_ents for r in rules_of(e)[2]]
    if ranges:
        L.append('')
        L.append('-- Odoo range constraints as entity validation rules (bounds are inclusive: "> 0" = the smallest step of the type)')
    for e, (an, op, v, msg) in ranges:
        a = next(x for x in e['attributes'] if x['name'] == an)
        lo = v if op == '>=' else ('1' if a['type'] in ('Integer', 'Long') else '0.00000001')
        L.append("create validation rule for %s.%s range from %s error message '%s';" % (qn(e['name']), q(an), lo, esc(msg)))
    L.append('')
    L.append('-- Entity access (module-brief.md "Access table"; narrowing a rule = revoke first, STOP 14)')
    for e in mod_ents:
        rows = acc.get(e['name'], [])
        persistent = e.get('persistent', True)
        for role, rights, xp in rows:
            if not persistent:
                rights = [r for r in rights if r not in ('create', 'delete')] or ['read *', 'write *']
            where = ''
            if xp:
                where = ' where %s' % header_path(e['name'], e, xp, ents)
            L.append('grant %s on entity %s to %s%s;' % (', '.join(rights), qn(e['name']), role, where))
    return '\n'.join(L) + '\n'


def gen_demo():
    L = ['mdl 1;', '-- 190-security-demo-users.mdl — GENERATED by pipelines/odoo/mdl_domain.py (build-plan row 14).',
         "-- One demo user per user role; throwaway password recorded in architecture/build-plan.md. MxAdmin untouched.", '']
    for u, r in DEMO_USERS:
        L.append("create or modify demo user '%s' ( Password: '%s', UserRoles: (%s) );" % (u, DEMO_PASSWORD, r))
    return '\n'.join(L) + '\n'


KEY_TARGETS = set()


def main():
    ents, enums = load()
    KEY_TARGETS.update(key_targets(ents))
    acc = parse_access()
    missing = [n for n, e in ents.items() if e.get('persistent', True) and not acc.get(n)]
    if missing:
        print('WARNING: persistent entities without access rows: %s' % missing)
    os.makedirs(OUT, exist_ok=True)
    files = {'100-security-roles.mdl': gen_roles(), '190-security-demo-users.mdl': gen_demo()}
    for m in MODULES:
        files['%d-%s-domain.mdl' % (NUM[m], m.lower())] = gen_module(m, ents, enums, acc)
    for n, s in files.items():
        target = os.path.join(OUT, 'done-' + n) if os.path.exists(os.path.join(OUT, 'done-' + n)) else os.path.join(OUT, n)
        open(target, 'w').write(s)
    print('wrote %d scripts; %d entities, %d enumerations, %d associations' % (
        len(files), len(ents), len(enums), sum(len(e['associations']) for e in ents.values())))


if __name__ == '__main__':
    main()
