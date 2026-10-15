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
