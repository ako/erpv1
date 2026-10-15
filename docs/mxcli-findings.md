# mxcli and toolkit findings — erpv1

Problems with the tools themselves, kept apart from app findings (FINDINGS.md) so they can be reported upstream.
mxcli `nightly-20261014-78bdfa51a`, Mendix 11.15.0, toolkit `95bf240`. Each entry was checked against the toolkit's
ledger with `bin/bug-lookup.sh`; **Known** names the ledger entry, **New** means nothing there matched.
Upstream: not filed yet — candidates for `bug-logs/pending-github-issues`.

## mxcli

| # | Area | Symptom (measured) | Workaround | Ledger |
|---|---|---|---|---|
| X1 | `check` vs mxbuild — OQL | A view entity using `concat(a, b)` passes `mxcli check --references`; mxbuild refuses: CE0174 "Unknown function 'concat'". Same for comparing to an enum value as `Sales.ENUM_SalesOrderStatus.SalesOrder` in the OQL WHERE: CE0174 "Cannot resolve object name". (608, 2026-10-15; exec.sh auto-restored.) | String `+`; compare to the value name as a string (`o.Status = 'SalesOrder'`). | New (BUG-149 lists other check/mxbuild gaps, not these) |
| X2 | `run --local --watch` | During a burst of execs a rebuild failed: "no rollup.config.mjs and no bundle at …/deployment/web/dist/index.js"; another time "Could not find a part of the path …/deployment/web/pages/Purchasing.PurchaseApproval_Task.js", after which the runtime restart failed with `java.io.EOFException` and the app stayed down. | `run stop`, then `run --local --ensure-db --watch --detach`. | New |
| X2b | `run --local --watch` during exec | 2026-10-16: a watch rebuild that fired mid-exec of a drop-and-replay one-off reported CE0108 "Variable 'Delivery' is defined but not in scope" (×10+, in four microflows), while `mx check` on the stored model and exec.sh's own mxbuild both said 0 errors; a clean boot built fine. Also `mxcli test --local` redeploys the running app, so journeys started right after it abort at preflight. | Trust `mx check`/`docker check` over the watch build after an exec; `run stop` + start, then `run wait` before journeys. | New |
| X3 | Project hooks / `init` | Every session start, resume and compaction re-seeds `.claude/lint-rules/*.star` with the stock rules, overwriting the toolkit's — 5 times in two days. The lint gate then reports BLIND (or a bogus rise). | `git checkout -- .claude/lint-rules` (or `sync-project.sh`) after each session start. | Known (toolkit #264 — "mxcli init re-seeds lint rules"); the trigger here is the session hook, not a manual init |
| X4 | Project hooks | The compact/resume hook prints `Error: opening project: mpr file not found: /home/user/erpv1/project.mpr` — it assumes the MPR at the repo root, not the two-tree layout (`app/erpv1.mpr`) that `mxcli new --output-dir app` creates. | Harmless here; the hook's model check is skipped. | New |
| X5 | `create or modify microflow` | Any reshape (an added/removed activity, a changed branch) is refused (MDL-V1-REBUILD). The only route is `drop` + `create` in one script, which also drops the microflow's grants unless they are restated in that script. Cost: 10 one-off rebuild scripts in this project. | `mdlsource/_oneoff/*-rebuild-*.mdl` (drop + replay the owning script + restate grants). | Not a bug (by design); friction worth raising — an `--allow-rebuild` per statement would remove the one-off pattern |
| X6 | Grants | Re-executing a page script with a narrower `grant execute` leaves the older, wider grant in place. | Emit an explicit `revoke`. | Known (STOP 14, "a narrowing GRANT merges") |
| X7 | `mxcli check` on `.test.mdl` | The `mxcli test` file format terminates tests with `/`; `check` warns MDL-V1-SLASH once per test (30 warnings on one file), burying real warnings. | Ignore MDL-V1-SLASH in test files. | Related to BUG-149 row "check on .test.mdl flags MxTest" — new symptom |
| X8 | XPath `[ID = '[%CurrentUser%]']` on System.User | `check --references` refuses: CE0161 "ID is neither an attribute nor an association". Not retested with lowercase `id`, which is Mendix's XPath spelling. | `retrieve $Roles from $currentUser/System.UserRoles` + `find`. | Unverified — retest with `id` before filing |
| X9 | `mxcli syntax` / CLI | `syntax page widgets` and `syntax workflow user-task` print the topic index, while `syntax page.widgets` / `workflow.user-task` print the content; `-c "SHOW ENUMERATION X"` is a parse error while `DESCRIBE ENUMERATION X` works. | Use the dotted topic path; use DESCRIBE. | New (minor) |

## Toolkit instruments

| # | Instrument | Symptom (measured) | Workaround |
|---|---|---|---|
| T1 | `bin/lib/obligation-check.sh` — LOOK | Picks, per module, the newest `ui-review-*.html` that merely *mentions* the module name; a later module's report that mentions "Sales" in passing becomes Sales' report. All five module reports read as `FAULT 0 of 7`. | One dated review file with a section per module (VALID AT + PROOF-OF-LOOK per section). |
| T2 | LOOK freshness rule | VALID AT must predate the shots; a report stamped with the commit that *saved* the shots reads "screenshots older than their section's VALID AT". | Stamp VALID AT with the model commit the shots were taken on. |
| T3 | `project-bin/coherence-cadence.sh --record` | Records every module verified so far as covered, not the pass's scope (Purchasing was recorded by a pass over 4 other modules). | Note the true scope in the report; run the next cluster over the module anyway. |
| T4 | `tests/e2e/full-app-walkthrough.js` | The WALKTHROUGH block in `project.config.js` is still the toolkit's template (another project's routing-change process); its step vocabulary has no combobox verb, so most ERP flows cannot be expressed. | Not run; configure before Stage 6. |
| T5 | `tests/e2e/journey-runner.js` | No action to open a data-grid row; `fill`/`click` always take the first match, so a list-view row other than the first cannot be driven. | Added `clickRow` (row by visible text) and `nth` on `fill`/`click` locally. |
| T8 | `journey-runner.js` `textPresent` | Reads `body.innerText`, which does not include input values: a form showing the order number in a text box reads "not found in rendered text" (J-INV-01). | Assert such values in the data rung; consider reading `input.value` too. |
| T6 | `bin/verify-module.sh` | Leaves a `sleep 1800` child holding stdout, so `verify-module.sh … \| tail` never returns. | Redirect to a file; don't pipe. |
| T7 | Journey positive control | trace-order / trace-negative rungs are unprovable without Jaeger, and `verify-module` reports the control as FINDING in every module of a container without it. | Accepted per module; record "5 of 7, trace rungs need Jaeger". |
| T9 | `bin/page-fidelity.js` | Data grid 2 columns (`column (Attribute: …, Caption: '…')`) are not counted as content, and association-path / enum columns not as bindings: Transfer_Overview reads content 0/3 and misses Partner/Scheduled date/Status while all are columns of its grid. | Read the misses against the script before acting. |
