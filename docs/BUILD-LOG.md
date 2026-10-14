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
| 2026-10-14T20:49:31+0000 | `00-skeleton.mdl` | pass | ⚠️ applied, LINT ROSE | mxbuild clean (no errors file written); lint ROSE: ARCH003 (+1) CONV006 (+1) CONV007 (+2) CONV008 (+2) CONV010 (+2) CONV015 (+1) QUAL004 (+1) SEC008 (+1)  · change: logic · approval: auto (PROJECT.md) |
| 2026-10-14T20:50:37+0000 | `2026-10-14-drop-partner-save.mdl` | not-run | 🚫 blocked | uncommitted model changes — refusing exec to prevent snapshot regression · change: logic · approval: auto (PROJECT.md) |
| 2026-10-14T20:50:40+0000 | `00-skeleton.mdl` | not-run | 🚫 blocked | uncommitted model changes — refusing exec to prevent snapshot regression · change: logic · approval: auto (PROJECT.md) |
| 2026-10-14T20:51:42+0000 | `2026-10-14-drop-partner-save.mdl` | fail | ❌ gate failed | 2 error(s): CE1613 — script rolled back · change: logic · approval: auto (PROJECT.md) |
| 2026-10-14T20:51:45+0000 | `00-skeleton.mdl` | not-run | 🚫 blocked | mxcli check failed pre-exec — nothing written to the model · change: logic · approval: auto (PROJECT.md) |
| 2026-10-14T20:53:46+0000 | `2026-10-14-drop-partner-save.mdl` | pass | ⚠️ applied, LINT ROSE | mxbuild clean (no errors file written); lint ROSE: ARCH003 (+1) CONV006 (+1) CONV007 (+2) CONV008 (+2) QUAL004 (+1) SEC008 (+1)  · change: logic · approval: auto (PROJECT.md) |
