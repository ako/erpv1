# pipelines/odoo — Odoo addon extractor (project-local)

Stage 1 / Path A extractor for this project's source (`sources/odoo/`, Odoo 18.0 Community).
Built because no toolkit pipeline reads Python/Odoo (triage.md, Stage 0 decision 2026-10-14).

```bash
pipelines/odoo/run.sh            # extract + validate; exits 0 when the quality score >= 95%
```

| File | Mechanism | Output |
|---|---|---|
| `extractor.py` | Python `ast` (models, fields, methods, decorators), ElementTree (views, menus, actions, groups, rules, crons, sequences), `csv` (ACLs) | `analysis/odoo/knowledge-base/*.json`, `extracted/odoo-odoo.json`, `reports/*.md` |
| `validator.py` | Line regex + paren counting over raw text — deliberately *not* ast/ElementTree/csv | `analysis/odoo/knowledge-base/extracted/extraction-quality.json` |

## What the knowledge base holds

- `entities.json` — persistent models; `structures.json` — transient (wizard) and abstract (mixin) models.
  Each item: attributes (Odoo + Mendix type, required, stored/compute/related, default, `definedIn` addon),
  associations (Many2one/One2many/Many2many with target, inverse, ondelete; `related=` paths resolved),
  `mixins`, `delegates` (`_inherits`), `extendedBy` (addons that `_inherit` it), capability C1–C12 and `inScope`.
- `staticEntities.json` — one enumeration per Selection field (incl. `selection_add` merges); dynamic ones flagged.
- `logics.json` — every model method with kind (action/compute/constraint/onchange/override/helper),
  decorators, called methods, raised user errors, `writesState`, and a `file:line-range` sourceRef.
- `workflows.json` — `state` lifecycles with transitions inferred from state writes.
- `screens.json` (views), `menus.json`, `actions.json`, `roles.json` (groups + ACL + record rules),
  `acl.json`, `recordRules.json`, `timers.json` (ir.cron), `sequences.json`, `serverActions.json`,
  `serviceApis.json` (http routes; portal — out of scope), `extEntities.json` (models only extended here),
  `cross-reference-map.json` (per model: screens, menus, ACL groups, logic count).

## Scored dimensions (Odoo-shaped)

entityFields, typeAccuracy, associations, enumerations, views, menus, security (groups + ACL rows + rules),
endpoints, timers. The toolkit's `testCoverage` is not scored: `tests/` were excluded at import.
Relational fields whose target lives only in addons declared not implemented are listed under
`externalRelations`, not scored. Method *behaviour* is BRD-only (listed in `brdOnly`).

Method log (which mechanism won each disagreement): `SESSION-NOTES.md`.
