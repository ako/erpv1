# Build log — auto-appended by bin/exec.sh

One line per exec against the model. Written by the script, not by hand, so it is
true even when someone forgets. Read this before assuming the model builds.

`gate` is the mxbuild verdict, and it is never blank:
`pass` verified clean · `fail` verified broken · `skipped` mxbuild/java missing ·
`unverified` errors file unparseable, or mxbuild exited non-zero without checking the
model (wrong version, JDK) · `not-run` the gate was never reached.
Only `pass` means anything looked at the model. A zero exit does not.

| when (ISO-8601 local) | script | gate | result | detail |
|---|---|---|---|---|
| 2026-10-14T20:44:42+0000 | `000-scaffold.mdl` | pass | ⚠️ applied, LINT BLIND | mxbuild clean (no errors file written); lint BLIND: rules reverted to stock (conv010_act_microflow_content.star,data_change_microflows.star,entity_business_key.star,conv009_max_microflow_objects.star) — run sync-project.sh; delta not attributable · change: logic · approval: auto (PROJECT.md) |
