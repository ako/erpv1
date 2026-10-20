#!/usr/bin/env node
// render-workflow-map.js — injects docs/workflow-map.json (tools/extract-workflow-map.js) into the pipeline template
// tools/workflow-map-template.html at its /*__DATA__*/null marker and writes docs/workflow-map.html. Read-only on
// everything else. Regenerate after every gate:  node tools/extract-workflow-map.js && node tools/render-workflow-map.js
'use strict';
const fs = require('fs');
const path = require('path');
const ROOT = path.resolve(process.argv[2] || path.join(__dirname, '..'));
const j = JSON.parse(fs.readFileSync(path.join(ROOT, 'docs', 'workflow-map.json'), 'utf8'));
const tpl = fs.readFileSync(path.join(__dirname, 'workflow-map-template.html'), 'utf8');
const MARK = '/*__DATA__*/null';
if (!tpl.includes(MARK)) throw new Error(`template has no ${MARK} marker`);

const t = j.template;
const byStage = {};
for (const s of j.stages) byStage[s.id] = { verdict: s.verdict, detail: s.verdictDetail, greyReason: s.greyReason,
  decisions: j.decisions.filter(d => d.stage === s.id).map(d => ({ status: d.status, decision: d.decision, notes: d.notes })) };
const art = {};
for (const a of t.artifacts) {
  const own = j.artifacts.find(x => x.id === a.artifact);
  const st = j.allArtifactStatus[a.artifact] || { exists: false, found: [] };
  art[a.artifact] = { exists: st.exists, found: st.found, verdict: own ? own.verdict : (st.exists ? 'PRESENT' : 'N/A — not owed in this entry mode'),
    detail: own ? own.verdictDetail : '', optedIn: own ? own.optedIn : null };
}
const currentStageId = ((j.currentStage || '').match(/Stage\s+([P0-9])/) || [])[1] || null;
const DATA = Object.assign({}, t, {
  project: { name: j.project, modeKey: j.modeKey, entryMode: j.entryMode, entryModeStatus: j.entryModeStatus, currentStageId,
    generatedAt: j.generatedAt.replace('T', ' ').slice(0, 16) + ' UTC', toolkitHead: j.toolkit.head, registerCommit: j.toolkit.registerCommit,
    nextAction: j.nextAction, gateCheckSummary: j.gateCheckSummary, counts: j.counts, unknowns: j.unknowns },
  status: { stage: byStage, art, obl: j.obligationLines, modules: j.modules },
});
const html = tpl.replace(MARK, JSON.stringify(DATA).replace(/</g, '\\u003c'));
fs.writeFileSync(path.join(ROOT, 'docs', 'workflow-map.html'), html);
console.log(`wrote docs/workflow-map.html (${(html.length / 1024).toFixed(0)} KB) from tools/workflow-map-template.html`);
