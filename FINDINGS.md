# FINDINGS.md — surprises and breakages, with how each was verified

## 2026-10-14 — Mendix 11.15.0 deploy build needs JDK 25; container JAVA_HOME is 21
- **Symptom:** doctor gate self-test FAIL "gate cannot read mxbuild's error file (baseline run)".
- **Cause:** mxbuild 11.15.0 exit 3, `errors[]`: gradle `:compile` → "release version 25 not supported" under
  JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64; `problems[]` empty, so the gate correctly read "?".
- **Fix:** JAVA_HOME=/usr/lib/jvm/java-25-openjdk-amd64 (JDK 25 is installed in the image), pinned in
  `.claude/settings.json` env. **Verified:** direct mxbuild on a scratch copy → BUILD SUCCEEDED; doctor
  self-test → baseline 0 errors, known-bad control 1 error.

## 2026-10-14 — Phase 0/1 build learnings (mxcli nightly-20261014, Mendix 11.15.0)
- **`create or modify microflow` refuses a reshaping change** (MDL-V1-REBUILD: "the Return … is taken out").
  A bare `drop microflow` first then fails the mxbuild gate with CE1613 when a page still calls it (auto-
  restored). Working pattern: drop + full recreate in ONE script (mdlsource/_oneoff/2026-10-14-drop-partner-save.mdl).
- **NPE ↔ PE associations must start in the NPE with owner Default** — `owner Both` on a
  `ReferenceSet` from a non-persistent request entity gave CE0001 at the gate (verified: auto-restored, fixed
  in mdl_domain.py, re-exec 0 errors).
- **A narrowing GRANT merges** (STOP 14 still live): the skeleton kept CREATE/DELETE until an explicit
  `revoke create, delete` ran first.
- **`mxcli new` reverts the toolkit lint rules** in the project root `.claude/lint-rules/` → exec.sh reports
  "LINT BLIND"; `sync-project.sh` restores them.
- `create module if not exists` parses and keeps the roles script idempotent; every 1-domain script re-execs
  as "already in sync" (verified on 140-sales).
- `rename module MyFirstModule to Core` moved the theme dir to themesource/core but left a stale
  themesource/myfirstmodule — deleted by hand.

## 2026-10-15 — Core/Products build learnings
- `create or modify microflow` also refuses adding an @annotation to a Return path, and any branch added before a commit
  (MDL-V1-REBUILD); pattern stays: one-off drop + replay of the owning scripts (mdlsource/_oneoff/2026-10-15-*).
- A `return` inside a loop is CE0068 (`mxcli check` MDL062); a category-chain walk became a recursive SUB.
- Trial runtime caps concurrent sessions: screenshot/journey tools must sign out (layout now has Sign out).
- journey-runner combobox: after a server round-trip with validation feedback the first toggle click is swallowed; runner
  now re-clicks when aria-expanded stays false. helpers.navTo: same-title group/item ("Products" › "Products") needed a scoped click.
- Data grid 2 has no phone column priority: horizontal scroll on phones via Core main.scss.
- Decimal factor 1/12 stored at scale 8 → 120/dozen = 9.9999996/unit; price conversion rounds to 4 decimals (unit test).
- The floating button at the right edge is Mendix's demo-user switcher (demo users enabled), not Feedback.

## 2026-10-15 — Sales build, Partners close
- **Cyclic page/microflow reference blocks one-script exec.** ACT_SalesOrder_New opens SalesOrder_NewEdit, whose buttons call
  603/604 microflows: exec resolves in statement order, so no single ordering works. Split ACT_SalesOrder_New into 615, exec order
  603, 604, 606 (page), 615, 605. Verified with a combined `check --references` over all Sales scripts.
- **Demo-user switcher overlap**: the switcher is a full-height fixed panel off the right edge (`.mx-demouserswitcher`, top -16px,
  844px tall); only `.mx-demouserswitcher-toggle` shows, absolutely positioned at ~25% height. Moving the panel did nothing visible;
  move the toggle. Measured with getComputedStyle in Playwright at 390px.
- **Lint rules re-seeded to stock by the session-start hook after compaction**: exec.sh reported BLIND; sync-project.sh restored
  them. A `git add -A` commit in between had committed the stock copies — check `.claude/lint-rules` diff after any compaction.
- **verify-module leaves a `sleep 1800` holding stdout**: a pipeline `verify-module.sh … | tail` never ends; read the log files
  under `.claude/loop/verify/<M>/` or don't pipe.
- **Journey positive control**: trace-order / trace-negative rungs cannot be proven in this container (no Jaeger at :16686, app not
  run with --trace). Partners now proves 5/7 (country association claim added), same as Products.
- **DataGrid 2 `ColumnWidth: autoFit` starves the remaining columns** (Sales list Number/Customer/Salesperson collapsed to ~15px,
  analysis grid unusable at 390). Reverted; default autoFill for every column. Seen in shots 2026-10-15d, fixed in -15e.
- **A delete button disappears when the role lacks entity delete** — no build or lint signal. Line Remove links need delete on the line entity.
- **OQL in a view entity**: no `concat()` (use `+`), and an enum is compared to its value name as a string (`o.Status = 'SalesOrder'`);
  `Sales.ENUM_X.Value` is CE0174 "Cannot resolve object name". `mxcli check` passes both; only mxbuild catches them.
- **Charts columnchart with a 'YYYY-MM' string x-axis is plotted as dates** (timestamps on the axis); `customLayout:
  '{"xaxis": {"type": "category"}}'` fixes it.
- **`mxcli run --watch` build failed with "no bundle at deployment/web/dist/index.js"** after a domain + microflow burst; `run stop`
  then `run --local --watch --detach` rebuilt it cleanly.
- **Ledger status "built" counts stubs**: Inventory.SUB_SalesOrder_CreateDelivery reads built while it is a log-only stub (800).

## 2026-10-15 — Coherence pass 1, Purchasing build
- **Workflow outcome branches run asynchronously after the task page closes.** With the domain work in the outcome branch,
  the approval inbox still listed an approved order (journey J-PURCH-02 FAIL "page does NOT say P00019"). Moving the work into
  the task button's SUB (synchronous, with refresh) was not enough either: a Data grid 2 on the page underneath does not
  re-query after `close page`. Fix: the decision ACT ends in `show page <inbox>` (fresh instance). Verified 9/9 + 8/8.
- **Task page takes $WorkflowUserTask AND $WorkflowContext** (toolkit workflow-structure-rules §11) — no data-source microflow
  is needed, which also removes the workflow→page→DS→workflow cycle. `mxcli check` refuses a user task without a page
  (MDL-WF01), so the page must exist first.
- **XPath `[ID = '[%CurrentUser%]']` on System.User is rejected** (CE0161 "ID is neither attribute nor association"); check a
  role with `retrieve $Roles from $currentUser/System.UserRoles` + `find ... where $currentObject/Name = 'X'`.
- **Mendix hides a microflow button the user may not execute** — the cleanest way to hide New from read-only roles is to grant
  its microflow only to roles that can open the form (generator, coherence C1-01). A regenerated grant does not remove an old
  one: emit an explicit `revoke`.
- **`mxcli run --watch` restart failed with EOFException** after "Could not find a part of the path …/deployment/web/pages/
  Purchasing.PurchaseApproval_Task.js" during a burst of execs; `run stop` + `run --local --ensure-db --watch --detach` fixed it.
  A new container also needs `--ensure-db` (Postgres not running → boot failed).
- **journey-runner has no row click**: added `clickRow` (row of a grid by visible text) to tests/e2e/journey-runner.js.

## 2026-10-16 — Inventory close-out

- **Stock count Apply raced the row's save (fixed).** The Stock list saved a typed count on leave, and the page-level
  Apply counts read counts from the database. A count typed and Apply clicked at once applied nothing, and a late save
  then put back an already-applied count, so a second Apply would add the stock twice. Reproduced with J-INV-04
  (count 21 typed: Apply corrected 0 levels; row Apply: 20 → 25, then the count of 25 reappeared). Fix: the count input no
  longer saves on leave; a row Apply (ACT_StockLevel_ApplyCount) saves that row and applies. The page-level button was
  removed — Odoo's "Apply all" is not offered (register row). Verified: J-INV-04 8/8 on two consecutive runs.
- **Lint close-out.** CONV010 (retrieves/commits in five ACTs) and CONV009 (four microflows over 15 activities) were fixed
  by moving work into SUBs (one drop-and-replay one-off). Remaining rises are the baselined classes (ARCH001 pickers,
  CONV003 page names, CUSTOM002 ASU_/SCE_ — SCE_ReorderRules_Run is the BRD's name, so it stays).
- **Journeys consume demo stock.** J-SALES-01 + J-INV-01 use 5 chairs each run; once below 5 the delivery is Waiting and
  J-INV-01 reads INVALID (no Ready delivery). J-INV-04 now counts 5 above what is recorded, so running it first tops up.
- **Validate ignored typed quantities (fixed).** On the transfer form, quantities typed on the lines are unsaved until a
  call carries them; Validate's microflows read moves by XPath from the database, so they saw the reserved quantity and
  validated 5 when 3 was typed (J-INV-01's backorder walk, screenshot J-INV-01-step3-NOT-REACHED.png). The validate path now
  retrieves over the association. General rule for this app: a microflow behind a form button reads the form's objects
  over associations, never by XPath.
- **Identity pickers on editable lists (fixed).** verify-module's monkey cleared product and location on both stock rows;
  the pickers saved on change. They are now editable only while empty. Data repaired through the UI.

## 2026-10-16 — Validation (user: uniqueness in the database, as entity rules)

- **Odoo's constraints never reached the BRDs** (KB: 55 SQL constraints, 93 @api.constrains on in-scope models). Fixed at
  the root: brd_generator carries them per entity with a disposition (brd_content.CONSTRAINT_TRIAGE): 18 implemented as
  entity rules, 10 in VAL_ microflows, 6 already covered by logic, 3 deferred to Invoicing, 67 not applicable (out-of-scope
  features), 1 waiting (tax name + scope: 13 duplicate journey taxes must go first).
- **Uniqueness is enforced in Postgres**: 12 unique indexes (uniq_<table>_<column>) verified with pg_indexes after the
  restart. Mendix numbers existing rows when an AutoNumber attribute is added (Product 1..14 verified). A composite key
  (one reorder rule per product + location) is a stored UniqueKey filled before commit from the two AutoNumbers; an
  incomplete row keeps an empty key, which the database does not compare (test: two new rules both commit).
- **The new rule caught a real violation**: an Inventory unit test created a second chair rule at WH/Stock.
- **Entity range rules raise past every error handler** in mxcli test (mxcli X12): the refusal and its message are
  correct, the tests are parked with the evidence.
- **A "Price is required" row check could never fire**: a new decimal is 0, not empty — caught by its own unit test.
- Inline lists (Sequences, Vendor prices, Reorder rules) now save rows through ACT_<E>_SaveRow → VAL_<E>_Row.

### Why the lint baseline accepts entity validation rules and two event handlers (2026-10-16)

- **CONV015 0 -> 13** (`NoEntityValidationRules`: "use VAL_ microflows instead"). The rule's premise is UX: a VAL_
  microflow flags fields on a form, an entity rule fails the commit. That premise does not hold for uniqueness: a VAL_
  that retrieves "is there another row with this code?" checks one transaction's view of the data, so two users saving
  at once both pass and both commit. Only the database can refuse the second one. The user decided (2026-10-16) that
  uniqueness is enforced in the database, as entity rules; Mendix turns a `unique` rule into a unique index
  (12 + 1 indexes verified in pg_indexes). Range rules are the same kind of invariant: they must hold on every commit
  path (microflows, inline-list rows that save on change, startup seeds), not only the forms that call a VAL_.
  Form-level checks (required, conditional, cross-field) stay in VAL_ microflows — CONV015 still holds for those.
- **CONV016 0 -> 2** (`NoEventHandlers`). A Mendix unique rule covers one attribute; Odoo's composite keys (one reorder
  rule per product + location; one tax per name + scope) are stored UniqueKey attributes. They must be filled on EVERY
  commit or the database cannot compare them, and a before-commit handler is the one place every commit passes through
  (inline rows save with "save changes", which calls no microflow). Seeds commit without events, so each startup
  backfills keys after its seed (SUB_*_BackfillKeys).
- **CUSTOM002 7 -> 9**: the two handlers are named BCo_ (Mendix's own before-commit prefix); the rule's prefix list does
  not include it.
- Evidence: tests/Constraints (17 tests: duplicates refused by the database, distinct rows and empty keys accepted,
  Odoo VAL checks), all 12 journeys green, Core journey re-runnable twice.

## 2026-10-16 — Invoicing popups and form buttons

- `ItemSelection: Multi` on a data grid is silently ignored; the MDL key is `Selection: Multi` (mxcli-findings X13). Found by
  mxbuild CE0117 on the selection-driven Register payment button, verified by the clean build after the rename.
- An `alter page … insert` cannot re-run (X14). The invoice form's popup buttons now come from a second, complete
  `create or modify` of the page (913), run after the popups; exec'd twice, the second run reported the model unchanged.
- Popups on non-persistent request entities need entity access rows in the module brief, or mxbuild reports CE2729 once the
  popup becomes reachable; not before. RegisterPaymentRequest / CreditNoteRequest rows added (read/write, Billing + Manager).
- Page-role grants: a selection button's action keeps the grant of its defining script (906: Billing, Manager). Otherwise the
  invoice list's sales/purchase-manager viewers would have reached the payment popup (CE2729 found it).
