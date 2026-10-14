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
| 2026-10-14T20:55:08+0000 | `00-skeleton.mdl` | pass | ⚠️ applied, LINT ROSE | mxbuild clean (no errors file written); lint ROSE: ARCH003 (+1) CONV007 (+2) CONV008 (+2) QUAL004 (+1) SEC008 (+1)  · change: logic · approval: auto (PROJECT.md) |
| 2026-10-14T20:55:09+0000 | `010-navigation.mdl` | not-run | 🚫 blocked | uncommitted model changes — refusing exec to prevent snapshot regression · change: logic · approval: auto (PROJECT.md) |
| 2026-10-14T20:56:13+0000 | `010-navigation.mdl` | pass | ⚠️ applied, LINT ROSE | mxbuild clean (no errors file written); lint ROSE: ARCH003 (+1) CONV007 (+2) CONV008 (+2) CONV019 (+1) SEC008 (+1)  · change: logic · approval: auto (PROJECT.md) |
| 2026-10-14T20:58:40+0000 | `00-skeleton.mdl` | pass | ⚠️ applied, LINT ROSE | mxbuild clean (no errors file written); lint ROSE: ARCH003 (+1) CONV007 (+2) CONV008 (+2) SEC008 (+1)  · change: logic · approval: auto (PROJECT.md) |
| 2026-10-14T21:01:01+0000 | `000-scaffold.mdl` | pass | ⚠️ applied, LINT ROSE | mxbuild clean (no errors file written); lint ROSE: ARCH003 (+1) CONV007 (+2) CONV008 (+2) SEC008 (+1)  · change: logic · approval: auto (PROJECT.md) |
| 2026-10-14T21:01:59+0000 | `00-skeleton.mdl` | pass | ⚠️ applied, LINT ROSE | mxbuild clean (no errors file written); lint ROSE: ARCH003 (+1) CONV007 (+2) CONV008 (+2) SEC008 (+1)  · change: logic · approval: auto (PROJECT.md) |
| 2026-10-14T21:07:02+0000 | `100-security-roles.mdl` | pass | ⚠️ applied, LINT ROSE | mxbuild clean (no errors file written); lint ROSE: ARCH003 (+1) CONV007 (+2) CONV008 (+13) SEC008 (+1)  · change: logic · approval: auto (PROJECT.md) |
| 2026-10-14T21:08:13+0000 | `110-core-domain.mdl` | pass | ⚠️ applied, LINT ROSE | mxbuild clean (no errors file written); lint ROSE: ARCH002 (+7) ARCH003 (+8) CONV001 (+5) CONV002 (+3) CONV006 (+7) CONV007 (+37) CONV008 (+13) DESIGN001 (+1) QUAL002 (+1) SEC008 (+2)  · change: logic · approval: auto (PROJECT.md) |
| 2026-10-14T21:09:16+0000 | `120-products-domain.mdl` | pass | ⚠️ applied, LINT ROSE | mxbuild clean (no errors file written); lint ROSE: ARCH002 (+15) ARCH003 (+16) CONV001 (+9) CONV002 (+3) CONV006 (+15) CONV007 (+61) CONV008 (+13) DESIGN001 (+2) QUAL002 (+4) SEC008 (+2)  · change: logic · approval: auto (PROJECT.md) |
| 2026-10-14T21:10:38+0000 | `110-core-domain.mdl` | pass | ⚠️ applied, LINT ROSE | mxbuild clean (no errors file written); lint ROSE: ARCH002 (+15) ARCH003 (+16) CONV001 (+9) CONV002 (+3) CONV006 (+15) CONV007 (+61) CONV008 (+13) DESIGN001 (+2) QUAL002 (+3) SEC008 (+2)  · change: logic · approval: auto (PROJECT.md) |
| 2026-10-14T21:11:39+0000 | `120-products-domain.mdl` | pass | ⚠️ applied, LINT ROSE | mxbuild clean (no errors file written); lint ROSE: ARCH002 (+15) ARCH003 (+16) CONV001 (+9) CONV002 (+3) CONV006 (+15) CONV007 (+61) CONV008 (+13) DESIGN001 (+2) SEC008 (+2)  · change: logic · approval: auto (PROJECT.md) |
| 2026-10-14T21:12:39+0000 | `130-partners-domain.mdl` | pass | ⚠️ applied, LINT ROSE | mxbuild clean (no errors file written); lint ROSE: ARCH002 (+18) ARCH003 (+19) CONV001 (+12) CONV002 (+3) CONV006 (+19) CONV007 (+79) CONV008 (+13) DESIGN001 (+3) SEC008 (+2)  · change: logic · approval: auto (PROJECT.md) |
| 2026-10-14T21:13:44+0000 | `140-sales-domain.mdl` | fail | ❌ gate failed | 1 error(s): CE0001 — script rolled back · change: logic · approval: auto (PROJECT.md) |
| 2026-10-14T21:15:20+0000 | `150-purchasing-domain.mdl` | pass | ⚠️ applied, LINT ROSE | mxbuild clean (no errors file written); lint ROSE: ARCH002 (+21) ARCH003 (+22) CONV001 (+13) CONV002 (+3) CONV006 (+22) CONV007 (+94) CONV008 (+13) DESIGN001 (+5) SEC008 (+2)  · change: logic · approval: auto (PROJECT.md) |
| 2026-10-14T21:15:23+0000 | `160-inventory-domain.mdl` | not-run | 🚫 blocked | mxcli check failed pre-exec — nothing written to the model · change: logic · approval: auto (PROJECT.md) |
| 2026-10-14T21:15:25+0000 | `170-invoicing-domain.mdl` | not-run | 🚫 blocked | mxcli check failed pre-exec — nothing written to the model · change: logic · approval: auto (PROJECT.md) |
| 2026-10-14T21:16:41+0000 | `140-sales-domain.mdl` | pass | ⚠️ applied, LINT ROSE | mxbuild clean (no errors file written); lint ROSE: ARCH002 (+26) ARCH003 (+27) CONV001 (+17) CONV002 (+3) CONV006 (+27) CONV007 (+115) CONV008 (+13) DESIGN001 (+7) SEC008 (+2)  · change: logic · approval: auto (PROJECT.md) |
| 2026-10-14T21:17:46+0000 | `160-inventory-domain.mdl` | pass | ⚠️ applied, LINT ROSE | mxbuild clean (no errors file written); lint ROSE: ARCH002 (+33) ARCH003 (+34) CONV001 (+26) CONV002 (+3) CONV006 (+34) CONV007 (+150) CONV008 (+13) DESIGN001 (+7) SEC008 (+2)  · change: logic · approval: auto (PROJECT.md) |
| 2026-10-14T21:18:54+0000 | `170-invoicing-domain.mdl` | pass | ⚠️ applied, LINT ROSE | mxbuild clean (no errors file written); lint ROSE: ARCH002 (+37) ARCH003 (+38) CONV001 (+26) CONV002 (+3) CONV006 (+38) CONV007 (+174) CONV008 (+13) DESIGN001 (+8) SEC008 (+2)  · change: logic · approval: auto (PROJECT.md) |
| 2026-10-14T21:20:01+0000 | `2026-10-14-drop-scaffold-user-role.mdl` | pass | ⚠️ applied, LINT ROSE | mxbuild clean (no errors file written); lint ROSE: ARCH002 (+37) ARCH003 (+38) CONV001 (+26) CONV002 (+3) CONV006 (+38) CONV007 (+174) CONV008 (+13) DESIGN001 (+8) SEC008 (+2)  · change: logic · approval: auto (PROJECT.md) |
| 2026-10-14T21:20:57+0000 | `190-security-demo-users.mdl` | pass | ⚠️ applied, LINT ROSE | mxbuild clean (no errors file written); lint ROSE: ARCH002 (+37) ARCH003 (+38) CONV001 (+26) CONV002 (+3) CONV006 (+38) CONV007 (+174) CONV008 (+13) DESIGN001 (+8) SEC008 (+2)  · change: logic · approval: auto (PROJECT.md) |
| 2026-10-14T21:22:11+0000 | `140-sales-domain.mdl` | pass | ⚠️ applied, LINT ROSE | mxbuild clean (no errors file written); lint ROSE: ARCH002 (+37) ARCH003 (+38) CONV001 (+26) CONV002 (+3) CONV006 (+38) CONV007 (+174) CONV008 (+13) DESIGN001 (+8) SEC008 (+2)  · change: logic · approval: auto (PROJECT.md) |
