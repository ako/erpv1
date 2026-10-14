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
