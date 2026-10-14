# intake.md — Stage P Kickoff Interview

Replace each "_Not yet asked._" line below with a real answer, in one of two forms:

  Answered (CONFIRMED): ...          the question was asked and answered
  Unverified — how to verify: ...    the question WAS asked, the answer is not known yet,
                                     and this line says how it will be established

Both forms pass gate-check's Stage P. "_Not yet asked._" passes nothing, deliberately: this
file is generated before the interview happens, and a scaffold must never be able to certify
an interview that never took place. Per conversion-runbook.md's interview protocol, every
question is asked in chat and the turn ends to wait for the answer; unknowns the user hands
back ("you decide") are recorded as ASSUMED in PROJECT.md rather than blocking Stage P.

**These are the questions only the human can answer.** Anything derivable — where the source
sits, what documents exist, which Mendix version the .mpr targets, whether prior analysis is
present — is the agent's homework, brought back as "I found X, confirm?" rather than asked
here. Do that homework FIRST: it is what turns each question below into a recommendation
with evidence instead of a blank prompt.

## 1. Entry mode: migration, requirements-driven, greenfield, or change an existing app?

Answered (CONFIRMED): Migration. Legacy source = Odoo 18.0 Community (Python ORM + XML views), rebuilt as a Mendix 11.15 app. Confirmed in chat 2026-10-14.

## 2. What is this project, and what is driving it?

Answered (CONFIRMED): (a) POC / demo / test use — will not be used in production, no hard date. Speed and a convincing, working slice over completeness; no data migration, hardening or cutover to production. User, chat 2026-10-14.

## 3. Fidelity: port as-is, or improve as we go?

Answered (CONFIRMED): Improve as we go — "Odoo-inspired, but do what makes most sense from a Mendix perspective." Odoo is the functional reference, not a model to replicate: every Stage 3 fit-gap finding is an opportunity to take the Mendix-native route (workflows, view entities, generalization only where it fits, simpler data model). User, chat 2026-10-14.

## 4. What are we working on: the whole application, or a part of it — and what else does that touch?

Answered (CONFIRMED): a part of Odoo, sliced in waves (confirmed in chat 2026-10-14): W1 Core (base partners/companies/users/currency, uom, product), W2 Sales & Purchasing (sales_team, sale, sale_management, purchase), W3 Inventory (stock, sale_stock, purchase_stock), W4 Invoicing (account, analytic, stock_account — invoices first, full ledger later). Explicitly OUT for now: website/eCommerce, POS, MRP, HR, mail/chatter/activities, portal, payment providers, QWeb reports, multi-company. Input documents: none beyond the Odoo source in `sources/odoo/` (see its SOURCE.md).

## 5. Of what we touch, what must stay exactly as it is?

Answered (CONFIRMED): nothing must stay as-is — no integrations, data contracts or Odoo compatibility required (POC). User, chat 2026-10-14.

## 6. Are there licence/security constraints on storing this client's source in this workspace?

Answered (CONFIRMED): Odoo Community is public LGPL-3.0 source; committing the imported subset to this repo is allowed (LICENSE kept in `sources/odoo/`). Enterprise (proprietary) code is not used. Decided 2026-10-14 when the user asked to import Odoo 18.0.

## 7. Is an SME available — who, and at what cadence?

Answered (CONFIRMED): the user (project owner) is the SME for all decision classes, answering in chat during sessions. User, chat 2026-10-14.

## 8. Anything else — scope, priorities, or worries?

Answered (CONFIRMED): nothing further. User, chat 2026-10-14.

## 9. Interview mode: attended (default) or unattended?

Answered (CONFIRMED): interactive — Interview mode: steering (every gate question asked in chat, agent waits). User, chat 2026-10-14.

## 10. Is any of this already done outside the toolkit — and where does the pipeline pick up?

Answered (CONFIRMED): starting from scratch here — nothing done outside the toolkit, no stages adopted or waived. User, chat 2026-10-14.

## 11. Exec approval: `auto` (default) or `ask`?

Answered (CONFIRMED): auto — scripts run through bin/exec.sh (mxbuild-gated) without asking each time; STOP-table operations are still announced. User, chat 2026-10-14.

## 12. Claude Code permissions: `project` (default), `wrappers`, or `full`?

Answered (CONFIRMED): project. User, chat 2026-10-14.

## 13. Unit tests (`.test.mdl`): project default `no` (default) or `yes`?

Answered (CONFIRMED): yes — every module gets `.test.mdl` unit tests by default. User, chat 2026-10-14.
