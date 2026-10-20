#!/usr/bin/env node
// extract-workflow-map.js — READ-ONLY. Extracts the project's workflow, as the mxcli-project-toolkit defines it, into
// docs/workflow-map.json. Renders nothing (tools/render-workflow-map.js does) and writes nothing else: no .mpr, no
// PROJECT.md / intake.md / build plan; gate-check runs with --no-html so index.html is not regenerated.
//
// Sources (TOOLKIT = the "Toolkit root" row of CLAUDE.local.md's Wiring table):
//   TOOLKIT/skills/conversion-runbook.md      Entry Modes table, §2 checkpoint table, every "### Stage X" section
//   TOOLKIT/skills/checkpoints/checkpoint-*.md title + "Fires after" line
//   TOOLKIT/bin/lib/artifact-manifest.tsv     one row per artifact (kept: rows whose modes include the entry mode)
//   TOOLKIT/bin/lib/obligations.tsv           per-module / per-project passes
//   TOOLKIT/agents/*.md                       roles
//   PROJECT.md, architecture/build-plan.md, docs/BUILD-LOG.md, and the per-module proof files the obligations name
//   TOOLKIT/bin/gate-check.sh --no-html, TOOLKIT/bin/status.sh (both read-only)
// Rule: nothing is invented. A value the sources do not state is written as "unknown" and listed in json.unknowns.
'use strict';
const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');

const ROOT = path.resolve(process.argv[2] || path.join(__dirname, '..'));
const OUT = path.join(ROOT, 'docs', 'workflow-map.json');
const rd = p => fs.readFileSync(p, 'utf8');
const ex = p => { try { return fs.statSync(p).size > 0; } catch (e) { return false; } };
const unknowns = [];
const unknown = (what, why) => { unknowns.push({ what, why }); return 'unknown'; };

// ── toolkit location and commit ────────────────────────────────────────────────────────────────
const local = rd(path.join(ROOT, 'CLAUDE.local.md'));
const TOOLKIT = (local.match(/\|\s*Toolkit root\s*\|\s*`([^`]+)`/) || [])[1];
if (!TOOLKIT) throw new Error('no "Toolkit root" row in CLAUDE.local.md');
const git = (args, cwd) => { try { return execFileSync('git', args, { cwd, encoding: 'utf8' }).trim(); } catch (e) { return ''; } };
const toolkitHead = git(['rev-parse', '--short=8', 'HEAD'], TOOLKIT) || unknown('toolkit HEAD', 'git rev-parse failed');
const project = rd(path.join(ROOT, 'PROJECT.md'));
const registerCommit = (project.match(/^Toolkit commit:\s*(\S+)/m) || [])[1] || unknown('register toolkit commit', 'no "Toolkit commit:" line in PROJECT.md');

// ── runbook ────────────────────────────────────────────────────────────────────────────────────
const RUNBOOK = path.join(TOOLKIT, 'skills', 'conversion-runbook.md');
const rb = rd(RUNBOOK);
const rbLines = rb.split('\n');
const lineOf = idx => rb.slice(0, idx).split('\n').length;
const STAGE_ORDER = ['P', '0', '1', '2', '3', '4', '5', '6', '7'];
const stages = [];
const secRe = /^### Stage ([P0-9]) — (.+)$/gm;
let m;
const heads = [];
while ((m = secRe.exec(rb))) heads.push({ id: m[1], title: m[2].trim(), at: m.index });
heads.forEach((h, i) => {
  const end = rb.indexOf('\n### ', h.at + 5);
  const body = rb.slice(h.at, end < 0 ? rb.length : end);
  const rows = {};
  for (const r of body.split('\n')) {
    const mm = r.match(/^\|\s*\*\*([^*]+)\*\*\s*\|\s*(.*)\|\s*$/);
    if (mm) rows[mm[1].replace('✋', '').trim()] = mm[2].trim();
  }
  const hard = /✋/.test(h.title) || /\*\*Gate ✋\*\*/.test(body);
  const skills = [...new Set((body.match(/`([a-z0-9-]+\.md)`/g) || []).map(s => s.replace(/`/g, '')))];
  const owner = rows['Owner'] || unknown(`Stage ${h.id} owner`, 'no Owner row in its runbook section');
  stages.push({
    id: h.id, name: h.title.replace(/\s*✋\s*$/, '').trim(), hard,
    source: `skills/conversion-runbook.md:${lineOf(h.at)}`,
    userDefines: rows['User defines'] || unknown(`Stage ${h.id} user defines`, 'no "User defines" row'),
    agentProduces: rows['Agent produces'] || unknown(`Stage ${h.id} agent produces`, 'no "Agent produces" row'),
    surface: rows['Surface'] || null,
    gate: rows['Gate'] || unknown(`Stage ${h.id} gate`, 'no Gate row in its runbook section'),
    owner, ownerAgents: [...new Set((owner.match(/[a-z]+-agent/g) || []))],
    skillsCited: skills,
  });
});
stages.sort((a, b) => STAGE_ORDER.indexOf(a.id) - STAGE_ORDER.indexOf(b.id));
if (stages.length !== 9) unknown('stage count', `runbook has ${stages.length} "### Stage" sections, expected P + 0..7`);
const runbookStageIds = stages.map(s => s.id);
const ownerUnknownStages = stages.filter(s => s.surface === null).map(s => s.id);

// Entry modes table: "| **Legacy source code** … | **Migration** | P, 0–7 (all) | … |"
const modes = [];
for (const l of rbLines) {
  const mm = l.match(/^\|\s*\*\*(.+?)\*\*.*?\|\s*\*\*(Migration|Requirements-driven|Greenfield|Change an existing app)\*\*\s*\|\s*([^|]+)\|/);
  if (mm) modes.push({ mode: mm[2], startingFrom: mm[1], stagesThatRun: mm[3].trim() });
}

// Checkpoint table (§2): "| Stage 0 | `checkpoint-scope.md` (CAC-1) | question |"
const checkpoints = [];
for (const l of rbLines) {
  const mm = l.match(/^\|\s*Stage ([P0-9])( \([^)]+\))?\s*\|\s*`(checkpoint-[a-z]+\.md)`\s*\(([^)]+)\)\s*\|\s*(.+?)\s*\|\s*$/);
  if (!mm) continue;
  const file = path.join(TOOLKIT, 'skills', 'checkpoints', mm[3]);
  let title = null, firesAfter = null;
  if (fs.existsSync(file)) {
    const t = rd(file);
    title = (t.match(/^# (.+)$/m) || [])[1] || null;
    firesAfter = (t.match(/^\*\*Fires (?:after|at the close of):\*\*\s*(.+)$/m) || [])[1] || null;
  }
  checkpoints.push({ stage: mm[1], qualifier: (mm[2] || '').trim().replace(/[()]/g, '') || null, file: `skills/checkpoints/${mm[3]}`,
    cac: mm[4], question: mm[5], title, firesAfter, hard: /✋/.test(mm[5]) });
}

// ── entry mode + register lines ────────────────────────────────────────────────────────────────
const modeRow = project.match(/^\|\s*P\s*\|\s*Entry mode:\s*\*\*([^*]+)\*\*([^|]*)\|\s*(\w+)\s*\|/m);
const entryMode = modeRow ? modeRow[1].trim() : unknown('entry mode', 'no Stage-P "Entry mode:" decision row in PROJECT.md');
const entryModeStatus = modeRow ? modeRow[3] : 'unknown';
const MODE_KEY = { Migration: 'migration', 'Requirements-driven': 'requirements', Greenfield: 'greenfield', 'Change an existing app': 'existing-app-change' };
const modeKey = MODE_KEY[entryMode] || unknown('entry mode key', `entry mode "${entryMode}" is not one of the runbook's four`);
const modeInfo = modes.find(x => x.mode === entryMode) || null;
const registerLines = project.split('\n').filter(l => /^(Adopted at stage|Waived( stage| stages| obligation| artifact)?|Opt-in artifact|Skeleton proven|Size tier)\b/.test(l)).map(l => l.trim());
const adopted = (project.match(/^Adopted at stage:\s*(\S+)\s*—?\s*(.*)$/m) || null);
const waivedStages = {};
for (const l of registerLines) {
  let mm = l.match(/^Waived stage ([P0-9]):\s*(.*)$/); if (mm) waivedStages[mm[1]] = mm[2];
  mm = l.match(/^Waived stages:\s*([P0-9, ]+)\s*—\s*(.*)$/); if (mm) mm[1].split(',').forEach(s => { waivedStages[s.trim()] = mm[2]; });
}
const currentStage = (project.match(/^## Current stage\s*\n+([^\n]+)/m) || [])[1] || null;

// Decisions: the table under "## Decisions" only (other sections hold numeric-first tables too)
function section(md, title) {
  const i = md.indexOf(`\n## ${title}`);
  if (i < 0) return '';
  const j = md.indexOf('\n## ', i + 4);
  return md.slice(i, j < 0 ? md.length : j);
}
const cells = l => l.split('|').slice(1, -1).map(c => c.trim());
const decisions = [];
for (const l of section(project, 'Decisions').split('\n')) {
  if (!/^\|/.test(l) || /^\|\s*(Stage|-)/.test(l)) continue;
  const c = cells(l);
  if (c.length < 3) continue;
  const stage = (c[0].match(/^([P0-9])/) || [])[1] || unknown(`decision stage "${c[0]}"`, 'stage column not P/0-7');
  decisions.push({ stage, stageCell: c[0], decision: c[1], status: c[2], notes: c[3] || '' });
}
const openQuestions = [];
for (const l of section(project, 'Open questions').split('\n')) {
  if (!/^\|/.test(l) || /^\|\s*(#|-|Question)/.test(l)) continue;
  const c = cells(l); if (c.length >= 3) openQuestions.push({ id: c[0], question: c[1], raised: c[2], status: c[3] || '' });
}
const assumptions = section(project, 'Assumptions (ASSUMED, unresolved)').split('\n').filter(l => /^(-|\|)/.test(l) && !/^\|\s*-/.test(l)).map(l => l.trim());

// ── manifest ───────────────────────────────────────────────────────────────────────────────────
const manifestRows = rd(path.join(TOOLKIT, 'bin', 'lib', 'artifact-manifest.tsv')).split('\n')
  .filter(l => l.trim() && !l.startsWith('#')).map(l => l.split('\t'));
const mHead = manifestRows.shift();
if (mHead[0] !== 'artifact') unknown('manifest header', `first data row is "${mHead[0]}", expected the header`);
const allArtifacts = manifestRows.map(c => ({ id: c[0], stage: c[1], paths: c[2].split('|'), producer: c[3], consumers: c[4],
  modes: c[5].split(',').map(s => s.trim()), absence: c[6] }));
const artifacts = allArtifacts.filter(a => a.modes.includes(modeKey));
const excludedByMode = allArtifacts.filter(a => !a.modes.includes(modeKey)).map(a => ({ id: a.id, stage: a.stage, modes: a.modes }));

// Path existence, checked here (not taken from gate-check): single "*" segments and |-alternatives, also under analysis/*/
const journeyDir = (() => {
  if (process.env.JOURNEY_DIR) return process.env.JOURNEY_DIR;
  for (const f of [path.join(ROOT, '.claude', 'toolkit.env'), path.join(process.env.HOME || '', '.mxcli-toolkit.env')]) {
    if (fs.existsSync(f)) { const mm = rd(f).match(/^JOURNEY_DIR=(.+)$/m); if (mm) return mm[1].trim(); }
  }
  return 'journeys';
})();
function expand(pattern) {
  const segs = pattern.replace('${JOURNEY_DIR}', journeyDir).split('/');
  let cur = [''];
  for (const seg of segs) {
    const next = [];
    for (const base of cur) {
      if (!seg.includes('*')) { next.push(base ? `${base}/${seg}` : seg); continue; }
      const dir = path.join(ROOT, base || '.');
      let names = [];
      try { names = fs.readdirSync(dir); } catch (e) { continue; }
      const re = new RegExp('^' + seg.replace(/[.+^${}()|[\]\\]/g, '\\$&').replace(/\*/g, '.*') + '$');
      names.filter(n => re.test(n)).sort().forEach(n => next.push(base ? `${base}/${n}` : n));
    }
    cur = next;
  }
  return cur.filter(p => ex(path.join(ROOT, p)));
}
for (const a of artifacts) {
  const hits = new Set();
  for (const p of a.paths) { expand(p).forEach(h => hits.add(h)); if (!p.startsWith('analysis/')) expand('analysis/*/' + p).forEach(h => hits.add(h)); }
  a.found = [...hits];
  a.exists = a.found.length > 0;
}

// Inputs of a stage: artifacts of EARLIER stages whose consumers column names that stage's check (check_stage_N),
// its runbook section ("Stage-N"/"§2 Stage N"), or a skill its runbook section cites. The matching token is kept.
for (const s of stages) {
  s.inputs = [];
  const idx = STAGE_ORDER.indexOf(s.id);
  for (const a of artifacts) {
    if (STAGE_ORDER.indexOf(a.stage) >= idx) continue;
    const tokens = [`check_stage_${s.id}`, `Stage-${s.id} `, `Stage ${s.id} `, ...s.skillsCited];
    if (s.id === '5') tokens.push('build-ready');
    const hit = tokens.find(t => a.consumers.includes(t));
    if (hit) s.inputs.push({ artifact: a.id, fromStage: a.stage, matchedBy: hit.trim() });
  }
  s.outputs = artifacts.filter(a => a.stage === s.id).map(a => a.id);
}

// ── agents ─────────────────────────────────────────────────────────────────────────────────────
const agents = fs.readdirSync(path.join(TOOLKIT, 'agents')).filter(f => /-agent\.md$/.test(f)).sort().map(f => {
  const t = rd(path.join(TOOLKIT, 'agents', f));
  const desc = ((t.match(/^description:\s*"?(.+?)"?\s*$/m) || [])[1] || '').replace(/\{\{PROJECT\}\}/g, 'erpv1');
  const role = f.replace(/-agent\.md$/, '');
  const fromDesc = [];
  const sm = desc.match(/Stages? ([P0-9][^)(.;]*?)(?:\)|\.|;| for | —)/);
  if (sm) sm[1].replace(/and/g, ',').split(',').forEach(x => {
    const r = x.trim().match(/^([P0-9])\s*-\s*([0-9])$/);
    if (r) { for (let i = STAGE_ORDER.indexOf(r[1]); i <= STAGE_ORDER.indexOf(r[2]); i++) fromDesc.push(STAGE_ORDER[i]); }
    else if (/^[P0-9]$/.test(x.trim())) fromDesc.push(x.trim());
  });
  (desc.match(/Stage ([0-9])/g) || []).forEach(x => fromDesc.push(x.slice(-1)));
  const fromOwner = stages.filter(s => s.ownerAgents.includes(`${role}-agent`)).map(s => s.id);
  return { role, file: `agents/${f}`, description: desc, stagesFromDescription: [...new Set(fromDesc)], stagesFromRunbookOwner: fromOwner };
});
for (const s of stages) s.roles = agents.filter(a => a.stagesFromDescription.includes(s.id) || a.stagesFromRunbookOwner.includes(s.id)).map(a => a.role);

// ── gate-check (--no-html) and status.sh ──────────────────────────────────────────────────────
const run = (cmd, args) => { try { return execFileSync(cmd, args, { cwd: ROOT, encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] }); } catch (e) { return (e.stdout || '') + (e.stderr || ''); } };
const gc = run(path.join(TOOLKIT, 'bin', 'gate-check.sh'), ['--no-html', ROOT]);
const gcStage = {};
for (const l of gc.split('\n')) {
  const mm = l.match(/^Stage ([P0-9]) \(([^)]+)\):\s*([A-Z]+)\s*·?\s*(.*)$/);
  if (mm) gcStage[mm[1]] = { verdict: mm[3], detail: mm[4].trim(), label: mm[2] };
}
const gcArtifact = {};
for (const l of gc.split('\n')) {
  const mm = l.match(/^Artifact (\S+)\s+([A-Z]+)\s+—\s+(.*)$/);
  if (mm) gcArtifact[mm[1]] = { verdict: mm[2], detail: mm[3].trim() };
}
const optLine = (gc.match(/^Artifacts optional, not opted in:\s*(.+)$/m) || [])[1] || '';
const notOptedIn = [...optLine.matchAll(/([a-z0-9-]+) \(stage ([0-9])\)/g)].map(x => x[1]);
const gcObl = {};
for (const l of gc.split('\n')) {
  let mm = l.match(/^Obligation (\S+)\s+(PASS|PENDING|FAIL|WAIVED|NOT YET DUE)\s+—\s+(.*)$/);
  if (mm) { gcObl[mm[1]] = Object.assign(gcObl[mm[1]] || {}, { verdict: mm[2], detail: mm[3].trim(),
    notDone: ((mm[3].match(/NOT DONE:\s*([A-Za-z ]+?)\s+—/) || [])[1] || '').split(/\s+/).filter(Boolean) }); continue; }
  mm = l.match(/^Obligation (\S+)\s+STALE:\s*(.*)$/);
  if (mm) gcObl[mm[1]] = Object.assign(gcObl[mm[1]] || {}, { stale: mm[2].trim() });
}
const gcSummary = (gc.match(/^Summary:\s*(.+)$/m) || [])[1] || unknown('gate-check summary', 'no Summary line in gate-check output');
const st = run(path.join(TOOLKIT, 'bin', 'status.sh'), [ROOT]);
const nextAction = ((st.match(/^NEXT\s+→\s+(.+)$/m) || [])[1] || unknown('next action', 'status.sh printed no NEXT line')).trim();
const statusHeadline = (st.split('\n').find(l => /^erpv1 — /.test(l)) || '').trim();

// ── stage verdict + greying ───────────────────────────────────────────────────────────────────
const runsInMode = (() => {
  if (!modeInfo) return null;
  const t = modeInfo.stagesThatRun;
  if (/0–7 \(all\)/.test(t)) return STAGE_ORDER.slice();
  return null;
})();
if (!runsInMode) unknown('stages run in this mode', `entry-mode row "${modeInfo && modeInfo.stagesThatRun}" not parsed for this mode`);
for (const s of stages) {
  s.verdict = gcStage[s.id] ? gcStage[s.id].verdict : unknown(`Stage ${s.id} verdict`, 'gate-check printed no line for it');
  s.verdictDetail = gcStage[s.id] ? gcStage[s.id].detail : '';
  s.inMode = runsInMode ? runsInMode.includes(s.id) : null;
  s.greyReason = waivedStages[s.id] ? `Waived: ${waivedStages[s.id]}` : (adopted && STAGE_ORDER.indexOf(s.id) < STAGE_ORDER.indexOf(adopted[1]) && s.id !== 'P' ? `Adopted at stage ${adopted[1]}: ${adopted[2]}` : (s.inMode === false ? `Not run in ${entryMode} mode` : null));
  const ds = decisions.filter(d => d.stage === s.id);
  s.decisionCounts = ds.reduce((o, d) => { const k = /^(CONFIRMED|ASSUMED)/.test(d.status) ? d.status.match(/^(CONFIRMED|ASSUMED)/)[1] : 'other'; o[k] = (o[k] || 0) + 1; return o; }, {});
  s.checkpoints = checkpoints.filter(c => c.stage === s.id);
}

// ── Stage 5 modules (build plan order) and their obligations ──────────────────────────────────
const plan = rd(path.join(ROOT, 'architecture', 'build-plan.md'));
const modules = [...plan.matchAll(/\*\*([A-Za-z]+) module close\*\*/g)].map(x => x[1]);
if (!modules.length) unknown('modules', 'no "**<Module> module close**" rows in architecture/build-plan.md');
const obligations = rd(path.join(TOOLKIT, 'bin', 'lib', 'obligations.tsv')).split('\n').filter(l => l.trim() && !l.startsWith('#'))
  .map(l => l.split('\t')).filter(c => c[0] !== 'obligation')
  .map(c => ({ id: c[0], performer: c[1], scope: c[2], match: c[3], artifact: c[4], denominator: c[5], degradable: c[6], fromStage: c[7], skill: c[8],
    gate: gcObl[c[0]] || null }));
const waivedObl = registerLines.map(l => l.match(/^Waived obligation (\S+?)\/(\S+?):\s*(.*)$/)).filter(Boolean).map(x => ({ id: x[1], module: x[2], reason: x[3] }));
const reviewReports = fs.readdirSync(path.join(ROOT, 'design', 'ui-reviews')).filter(f => /^ui-review-.*\.html$/.test(f)).sort();
const latestReview = reviewReports[reviewReports.length - 1];
const reviewHead = latestReview ? (rd(path.join(ROOT, 'design', 'ui-reviews', latestReview)).match(/(\d+) of (\d+) pages reviewed \(([^)]*)\)/) || null) : null;
const fidelityRows = ex(path.join(ROOT, 'docs', 'PAGE-FIDELITY.tsv')) ? rd(path.join(ROOT, 'docs', 'PAGE-FIDELITY.tsv')).split('\n').filter(l => l && !l.startsWith('#') && !l.startsWith('date\t')).map(l => l.split('\t')) : [];
const coherenceTsv = path.join(ROOT, '.claude', 'loop', 'coherence', 'last-cluster-pass.tsv');
const coherenceModules = ex(coherenceTsv) ? rd(coherenceTsv).split('\n').map(l => l.split('\t')[0].trim()).filter(x => /^[A-Z][A-Za-z]+$/.test(x)) : [];
const buildLog = rd(path.join(ROOT, 'docs', 'BUILD-LOG.md')).split('\n').filter(l => /^\| 20/.test(l)).map(cells);
const moduleRows = modules.map(mod => {
  const lower = mod.toLowerCase();
  const scripts = buildLog.filter(c => new RegExp(`\\b\\d{3}-${lower}-`).test(c[1] || ''));
  const obls = obligations.filter(o => o.scope === 'module' && Number(o.fromStage) <= 5).map(o => {
    const g = o.gate;
    const waived = waivedObl.find(w => w.id === o.id && w.module === mod);
    let status = !g ? 'unknown' : waived ? 'WAIVED' : g.notDone.includes(mod) ? 'PENDING' : g.verdict === 'PENDING' ? 'PASS' : g.verdict;
    if (!g) unknown(`obligation ${o.id}`, 'gate-check printed no Obligation line for it');
    let denominator = null, proof = o.artifact.replace('<Module>', mod), note = null;
    if (o.id === 'look' && reviewHead) { const mm = reviewHead[3].match(new RegExp(`${mod} (\\d+) of (\\d+)`)); if (mm) denominator = `${mm[1]}/${mm[2]} pages`; proof = `design/ui-reviews/${latestReview}`; if (g && g.stale && g.stale.includes(mod + '(')) note = 'STALE: ' + (g.stale.match(new RegExp(`${mod}\\((.*?) since\\)`)) || [])[1] + ' since'; }
    if (o.id === 'sweep') { const f = path.join(ROOT, o.artifact.replace('<Module>', mod)); if (ex(f)) { const mm = rd(f).split('\n')[0].match(/(\d+) of (\d+) interactive elements swept, (\d+) of (\d+) pages/); if (mm) denominator = `${mm[1]}/${mm[2]} elements · ${mm[3]}/${mm[4]} pages`; } }
    if (o.id === 'journeys') { const f = path.join(ROOT, o.artifact.replace('<Module>', mod)); if (ex(f)) { const rows = rd(f).split('\n').filter(l => /^journeys/.test(l)).map(l => l.split('\t')); denominator = rows.map(r => `${/positive control/.test(r[0]) ? 'control' : 'journey'} ${r[1]}`).join(' · '); } }
    if (o.id === 'fidelity') { const n = new Set(fidelityRows.filter(r => r[2] === mod).map(r => r[1])).size; denominator = `${n} page(s) scored`; proof = 'docs/PAGE-FIDELITY.tsv'; }
    if (o.id === 'dispatch') { proof = o.artifact.replace('<Module>', mod); }
    return { id: o.id, performer: o.performer, skill: o.skill, status, denominator, proof, proofExists: ex(path.join(ROOT, proof)) || /\*/.test(proof), note, waived: waived ? waived.reason : null };
  });
  const cl = obligations.find(o => o.id === 'coherence');
  obls.push({ id: 'coherence', performer: cl.performer, skill: cl.skill, status: coherenceModules.includes(mod) ? 'PASS' : 'not in last cluster pass',
    denominator: `cluster of ${coherenceModules.length}`, proof: cl.artifact, proofExists: ex(coherenceTsv),
    note: `last cluster pass: ${coherenceModules.join(', ') || 'none'}`, waived: null });
  return { module: mod, order: modules.indexOf(mod) + 1, scriptsInBuildLog: scripts.length,
    lastLog: scripts.length ? { when: scripts[scripts.length - 1][0], script: scripts[scripts.length - 1][1].replace(/`/g, ''), result: scripts[scripts.length - 1][2] } : null,
    obligations: obls };
});
const projectObligations = obligations.filter(o => o.scope === 'project').map(o => ({ id: o.id, performer: o.performer, skill: o.skill, fromStage: o.fromStage, artifact: o.artifact,
  exists: ex(path.join(ROOT, o.artifact)), verdict: o.gate ? o.gate.verdict : unknown(`obligation ${o.id}`, 'no gate-check line'), detail: o.gate ? o.gate.detail : '' }));

// ── assemble ──────────────────────────────────────────────────────────────────────────────────
for (const a of artifacts) {
  const g = gcArtifact[a.id];
  a.verdict = g ? g.verdict : (notOptedIn.includes(a.id) ? 'OPTIONAL — not opted in' : unknown(`artifact ${a.id} verdict`, 'gate-check printed no Artifact line for it'));
  a.verdictDetail = g ? g.detail : '';
  a.optedIn = a.absence !== 'optin' ? null : registerLines.some(l => l.startsWith(`Opt-in artifact ${a.id}:`));
}
// The runbook names an owner AGENT per stage and cites several skills; it names no single owning skill per stage.
const owningSkillNote = unknown('owning skill per stage', 'each runbook stage section names an Owner agent and cites several skills, not one owning skill — shown as "unknown" with the cited skills listed');
for (const s of stages) { s.owningSkill = 'unknown'; s.owningSkillNote = owningSkillNote === 'unknown' ? 'runbook names an owner agent, not one skill' : ''; }
for (const s of ownerUnknownStages) unknown(`Stage ${s} surface`, 'its runbook section has no Surface row');
const out = {
  generatedAt: new Date().toISOString(),
  project: path.basename(ROOT), root: ROOT,
  entryMode, entryModeStatus, modeKey, modeRow: modeInfo, currentStage,
  toolkit: { root: TOOLKIT, head: toolkitHead, registerCommit },
  nextAction, statusHeadline, gateCheckSummary: gcSummary,
  registerLines, decisions, openQuestions, assumptions,
  stages, checkpoints, agents, artifacts, excludedByMode, modules: moduleRows, projectObligations,
  counts: {
    runbookStages: runbookStageIds.length, stagesShown: stages.length,
    manifestRowsTotal: allArtifacts.length, manifestRowsForMode: artifacts.length,
    outputsShown: stages.reduce((n, s) => n + s.outputs.length, 0),
    buildPlanModules: modules.length, modulesShown: moduleRows.length,
  },
  sources: {
    runbook: 'skills/conversion-runbook.md', checkpoints: 'skills/checkpoints/checkpoint-*.md', manifest: 'bin/lib/artifact-manifest.tsv',
    obligations: 'bin/lib/obligations.tsv', agents: 'agents/*.md', register: 'PROJECT.md', buildPlan: 'architecture/build-plan.md', buildLog: 'docs/BUILD-LOG.md',
    gateCheck: 'bin/gate-check.sh --no-html (read-only)', status: 'bin/status.sh (read-only; calls gate-check --no-html)',
  },
  unknowns,
};
fs.writeFileSync(OUT, JSON.stringify(out, null, 1));
console.log(`wrote ${path.relative(ROOT, OUT)} — stages ${out.counts.stagesShown}/${out.counts.runbookStages}, outputs ${out.counts.outputsShown}/${out.counts.manifestRowsForMode}, modules ${out.counts.modulesShown}/${out.counts.buildPlanModules}, unknowns ${unknowns.length}`);
