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

_Not yet asked._ Sets stakes, urgency and the default for Q3 in one answer. (a) POC/demo —
prove feasibility, throwaway output, speed over completeness. (b) Production replacement with
a hard date — licence expiry, platform EOL, contract; fidelity and speed win, improvements
deferred. (c) Production replacement, open-ended — modernisation is part of the goal. Only
the user knows; record the date itself if there is one.

## 3. Fidelity: port as-is, or improve as we go?

_Not yet asked._ Default inherited from Q2 — (b) implies as-is, (c) licenses redesign — so
put the inherited default to the user and ask what to override. This decides whether every
Stage 3 fit-gap finding is a gap to close or an opportunity to take.

## 4. What are we working on: the whole application, or a part of it — and what else does that touch?

Answered (CONFIRMED): a part of Odoo, sliced in waves (confirmed in chat 2026-10-14): W1 Core (base partners/companies/users/currency, uom, product), W2 Sales & Purchasing (sales_team, sale, sale_management, purchase), W3 Inventory (stock, sale_stock, purchase_stock), W4 Invoicing (account, analytic, stock_account — invoices first, full ledger later). Explicitly OUT for now: website/eCommerce, POS, MRP, HR, mail/chatter/activities, portal, payment providers, QWeb reports, multi-company. Input documents: none beyond the Odoo source in `sources/odoo/` (see its SOURCE.md).

## 5. Of what we touch, what must stay exactly as it is?

_Not yet asked._ Integrations, data contracts, external URLs, scheduled jobs, reports other
systems consume. These are the constraints that invalidate an architecture late and cheaply
if found now; they are rarely visible in the source, because they live in its consumers. For
an existing app the default is that nothing beyond the ask changes — this question names the
things the change must not break.

## 6. Are there licence/security constraints on storing this client's source in this workspace?

Answered (CONFIRMED): Odoo Community is public LGPL-3.0 source; committing the imported subset to this repo is allowed (LICENSE kept in `sources/odoo/`). Enterprise (proprietary) code is not used. Decided 2026-10-14 when the user asked to import Odoo 18.0.

## 7. Is an SME available — who, and at what cadence?

_Not yet asked._ Availability is not the useful half: an SME who exists but answers in two
weeks reshapes the plan as much as no SME at all. Ask who, for which class of decision, and
what the realistic turnaround is.

## 8. Anything else — scope, priorities, or worries?

_Not yet asked._ The standing open-floor question the runbook requires at every checkpoint
(§1). Closed questions capture decisions; they never surface what the user wanted to say
unprompted. "Nothing further" is a valid answer — but it has to be the user's, not assumed.

## 9. Interview mode: attended (default) or unattended?

_Not yet asked._ How to verify: ask the user; default is `steering`. Record it as
`Interview mode:` in PROJECT.md: `steering` = every gate question is asked in chat and the agent
waits; `assist` = questions batched at gates, low-consequence ones assumed and reported; `auto`
(opt-in only, explicit request required) = nothing blocks, positions recorded as ASSUMED for
reconciliation. `attended` / `unattended` are accepted aliases for `steering` / `auto`.

## 10. Is any of this already done outside the toolkit — and where does the pipeline pick up?

_Not yet asked._ Only relevant when the project did not start here: a build already underway,
analysis that lives in Confluence, a design system someone else owns. Name the stage the toolkit
picks up at and record it — `bin/gate-check.sh <project> --adopt <stage> --reason "..."` — so the
earlier stages report WAIVED instead of a red row nobody can ever clear. Answer "starting from
scratch here" and nothing is waived, which is the right answer for most projects. Do NOT infer
this from what happens to be on disk: a missing artifact and an artifact produced elsewhere look
identical, and guessing wrong either nags forever or waives a stage that genuinely still matters.

## 11. Exec approval: `auto` (default) or `ask`?

_Not yet asked._ How to verify: ask the user; default is `auto`. Full rule text (what it
gates, the resolution order, the STOP-table carve-out): `bin/lib/wiring-item3.sh` — the same
text every agent's Start-here stamp carries. See `bin/exec-approval.sh --explain` for what is
currently resolved and why; the user switches it, never the agent on its own judgement.

## 12. Claude Code permissions: `project` (default), `wrappers`, or `full`?

_Not yet asked._ How to verify: ask the user; default is `project`. `wrappers` = only the
toolkit's safe wrappers run without a prompt. `project` = those plus edits inside this folder and
the everyday test/npm/docker/git-commit commands. `full` = everything, on this person's machine
only (`.claude/settings.local.json`); force-push, `git reset --hard`, `git clean` and `sudo`
still prompt. Record it as `Permission profile:` in PROJECT.md, then run
`bin/install-harness-permissions.sh <project> --profile <answer>`; `bin/doctor.sh <project>`
shows what is in effect.

## 13. Unit tests (`.test.mdl`): project default `no` (default) or `yes`?

_Not yet asked._ How to verify: ask the user; default is `no`. Every module already gets UI
journeys and data assertions. Unit tests cost a closed Studio Pro and a snapshot per run, and
agents ran them everywhere when no default was set (toolkit issue #274). With `no`, a module
still flips to `yes` in its brief when it has calculation, mapping or date/money logic, calls Java or REST, or had a bug fixed in that flow (`testing-shape.md` §2). Record it as
`Unit tests default:` in PROJECT.md.
