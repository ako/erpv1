#!/usr/bin/env node
// render-workflow-map.js — renders docs/workflow-map.json (tools/extract-workflow-map.js) into ONE self-contained
// docs/workflow-map.html: no external scripts, styles or fonts; the JSON is embedded. Read-only on everything else.
// Regenerate both after every gate:  node tools/extract-workflow-map.js && node tools/render-workflow-map.js
'use strict';
const fs = require('fs');
const path = require('path');
const ROOT = path.resolve(process.argv[2] || path.join(__dirname, '..'));
const data = JSON.parse(fs.readFileSync(path.join(ROOT, 'docs', 'workflow-map.json'), 'utf8'));
const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

// Visual language: blue = done/PASS · amber = gates and PENDING · red = FAIL only · grey = WAIVED / not in this mode.
function tone(v) {
  const s = String(v || '').toUpperCase();
  if (/^(PASS|PRESENT|CONFIRMED)/.test(s)) return 'pass';
  if (/^FAIL/.test(s)) return 'fail';
  if (/^(WAIVED|OPTIONAL|NOT YET DUE|N\/A)/.test(s)) return 'grey';
  if (/^(PENDING|MANUAL|STALE|NOT IN LAST|ASSUMED|MISSING)/.test(s)) return 'warn';
  return 'unk';
}
const SHAPE = { pass: '✓', warn: '○', fail: '✕', grey: '–', unk: '?' };
const badge = (v, extra = '') => `<span class="badge ${tone(v)}" title="${esc(v)}"><b>${SHAPE[tone(v)]}</b>${esc(v)}${extra}</span>`;
const decText = c => {
  const parts = [];
  if (c.CONFIRMED) parts.push(`${c.CONFIRMED} CONFIRMED`);
  if (c.ASSUMED) parts.push(`${c.ASSUMED} ASSUMED`);
  if (c.other) parts.push(`${c.other} other`);
  return parts.length ? parts.join(' · ') : 'no decisions';
};
const art = Object.fromEntries(data.artifacts.map(a => [a.id, a]));
const artChip = (id, extra = '') => {
  const a = art[id];
  const v = a ? (a.absence === 'optin' && !a.optedIn ? 'OPTIONAL — not opted in' : (a.exists ? 'PRESENT' : 'MISSING')) : 'unknown';
  const t = v === 'MISSING' ? 'warn' : tone(v);
  return `<button class="chip ${t}" data-kind="artifact" data-id="${esc(id)}" title="${esc(a ? a.paths.join(' | ') : id)}"><b>${SHAPE[t]}</b>${esc(id)}${extra}</button>`;
};

function stageRow(s) {
  const greyed = !!s.greyReason;
  const dec = data.decisions.filter(d => d.stage === s.id);
  const inputs = s.inputs.length ? s.inputs.map(i => artChip(i.artifact, ` <span class="from" data-kind="stage" data-id="${esc(i.fromStage)}">← ${esc(i.fromStage)}</span>`)).join('')
    : '<span class="none">none cited — no earlier artifact\'s consumers column names this stage\'s checks or skills</span>';
  const outputs = s.outputs.length ? s.outputs.map(id => `<div class="out">${artChip(id)}<span class="path">${esc((art[id].found[0] || art[id].paths[0]))}${art[id].found.length > 1 ? ` <i>+${art[id].found.length - 1}</i>` : ''}</span></div>`).join('')
    : '<span class="none">no manifest rows for this stage (the manifest gives Stage-7 outputs no row: nothing reads them)</span>';
  const decisions = dec.length ? dec.map((d, i) => `<button class="dec" data-kind="decision" data-id="${data.decisions.indexOf(d)}">${badge(/^(CONFIRMED|ASSUMED)/.test(d.status) ? d.status.match(/^(CONFIRMED|ASSUMED)/)[1] : d.status).replace('badge', 'badge mini')}<span>${esc(d.decision.replace(/\*\*/g, ''))}</span></button>`).join('')
    : '<span class="none">none recorded at this stage</span>';
  const modules = s.id === '5' ? `<div class="grp"><h4>Modules — build-plan order</h4>${data.modules.map(moduleRow).join('')}
      <div class="projobl"><h5>Project-level obligations</h5>${data.projectObligations.map(o => `<span class="obl ${tone(o.verdict)}" title="${esc(o.detail)}"><b>${SHAPE[tone(o.verdict)]}</b>${esc(o.id)} <em>${esc(o.verdict)}</em></span>`).join('')}</div></div>` : '';
  return `<details class="stage${greyed ? ' greyed' : ''}" id="stage-${s.id}" data-id="${s.id}">
    <summary data-kind="stage" data-id="${s.id}">
      <span class="num">${esc(s.id)}</span><span class="name">${esc(s.name)}${s.hard ? ' <span class="hand" title="hard gate">✋</span>' : ''}</span>
      <span class="skill" title="${esc(s.owningSkillNote || '')}">skill: <em>${esc(s.owningSkill)}</em> · ${esc(s.ownerAgents.join(', ') || s.owner)}</span>
      ${badge(s.verdict)}<span class="dc">${esc(decText(s.decisionCounts))}</span>
    </summary>
    ${greyed ? `<div class="greynote">${esc(s.greyReason)}</div>` : ''}
    <div class="body">
      <div class="grp"><h4>Inputs</h4><div class="chips">${inputs}</div></div>
      <div class="grp"><h4>Outputs <small>${s.outputs.length} manifest row(s)</small></h4>${outputs}</div>
      <div class="grp"><h4>Decisions <small>${dec.length}</small></h4>${decisions}</div>
      ${modules}
    </div>
  </details>`;
}
function moduleRow(m) {
  return `<details class="module" data-id="${esc(m.module)}"><summary data-kind="module" data-id="${esc(m.module)}"><span class="num">${m.order}</span><span class="name">${esc(m.module)}</span>
    <span class="obls">${m.obligations.map(o => `<span class="obl ${tone(o.status)}" title="${esc(o.status)}${o.note ? ' · ' + esc(o.note) : ''}"><b>${SHAPE[tone(o.status)]}</b>${esc(o.id)}${o.denominator ? ` <em>${esc(o.denominator)}</em>` : ''}</span>`).join('')}</span></summary>
    <div class="body small">${m.scriptsInBuildLog} BUILD-LOG row(s)${m.lastLog ? ` · last: <code>${esc(m.lastLog.script)}</code> ${esc(m.lastLog.result)} (${esc(m.lastLog.when)})` : ''}</div></details>`;
}
function gateRow(s, next) {
  const cps = s.checkpoints;
  const cp = cps.length ? cps.map(c => `<button class="cp" data-kind="gate" data-id="${s.id}">${esc(c.cac)} ${esc(c.file.replace('skills/checkpoints/', '').replace('.md', ''))}${c.qualifier ? ` <i>(${esc(c.qualifier)})</i>` : ''}</button>`).join('')
    : '<span class="none">no checkpoint fires at this close</span>';
  return `<div class="gate${s.greyReason ? ' greyed' : ''}" data-kind="gate" data-id="${s.id}"><span class="diamond${s.hard ? ' hard' : ''}">${s.hard ? '✋' : '◆'}</span>
    <span class="glabel">gate ${esc(s.id)} → ${esc(next ? next.id : 'end')}</span>${cp}${badge(s.verdict)}</div>`;
}

const outline = data.stages.map((s, i) => stageRow(s) + gateRow(s, data.stages[i + 1])).join('\n');
const c = data.counts;
const html = `<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Workflow map — ${esc(data.project)}</title>
<style>
:root{--bg:#f8fafc;--surface:#ffffff;--ink:#1e293b;--ink-soft:#64748b;--ink-faint:#94a3b8;--line:#e2e8f0;--accent:#0f4c81;
--pass-bg:#dbeafe;--pass-ink:#1e40af;--warn-bg:#fef3c7;--warn-ink:#92400e;--fail-bg:#fee2e2;--fail-ink:#991b1b;--grey-bg:#f1f5f9;--grey-ink:#64748b;
--radius:10px;--font:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;--mono:ui-monospace,'SF Mono',Menlo,monospace}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#0f172a;--surface:#111c33;--ink:#e2e8f0;--ink-soft:#94a3b8;--ink-faint:#64748b;--line:#24324d;--accent:#7cb3ec;
--pass-bg:#1e3a5f;--pass-ink:#bfdbfe;--warn-bg:#3d2f0b;--warn-ink:#fcd34d;--fail-bg:#4c1414;--fail-ink:#fecaca;--grey-bg:#1e293b;--grey-ink:#94a3b8}}
*{box-sizing:border-box}html,body{margin:0}body{background:var(--bg);color:var(--ink);font:13px/1.45 var(--font)}
header{padding:12px 20px;border-bottom:1px solid var(--line);background:var(--surface);display:flex;flex-wrap:wrap;gap:6px 22px;align-items:baseline}
header h1{font-size:15px;margin:0 8px 0 0}header .kv{color:var(--ink-soft)}header .kv b{color:var(--ink);font-weight:600}
.next{flex-basis:100%;font-size:12.5px;color:var(--warn-ink);background:var(--warn-bg);border-radius:6px;padding:4px 8px;overflow-wrap:anywhere}
.legend{flex-basis:100%;display:flex;gap:12px;color:var(--ink-soft);font-size:12px;flex-wrap:wrap}
main{display:grid;grid-template-columns:minmax(0,1fr) 380px;gap:0;min-height:calc(100vh - 110px)}
#outline{padding:12px 16px 40px;min-width:0}#detail{border-left:1px solid var(--line);background:var(--surface);padding:14px 16px;position:sticky;top:0;align-self:start;max-height:100vh;overflow:auto}
details.stage{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);margin:0}
details summary{list-style:none;cursor:pointer;display:flex;align-items:center;gap:10px;padding:7px 10px;min-width:0}
details summary::-webkit-details-marker{display:none}
details.stage>summary::before,details.module>summary::before{content:'▸';color:var(--ink-faint);width:10px;flex:none}
details[open]>summary::before{content:'▾'}
.num{font-family:var(--mono);font-weight:700;color:var(--accent);width:18px;flex:none;text-align:center}
.name{font-weight:600;white-space:nowrap}.hand{font-weight:400}
.skill{color:var(--ink-soft);font-size:12px;flex:1 1 auto;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.skill em{font-style:normal;color:var(--warn-ink)}
.dc{color:var(--ink-soft);font-size:12px;white-space:nowrap;flex:none}
.badge{display:inline-flex;gap:4px;align-items:center;border-radius:5px;padding:1px 7px;font-size:11.5px;font-weight:600;white-space:nowrap;flex:none}
.badge b,.chip b,.obl b{font-weight:700}.badge.mini{font-size:10.5px;padding:0 5px}
.pass{background:var(--pass-bg);color:var(--pass-ink)}.warn{background:var(--warn-bg);color:var(--warn-ink)}.fail{background:var(--fail-bg);color:var(--fail-ink)}
.grey,.unk{background:var(--grey-bg);color:var(--grey-ink)}
.greyed{opacity:.62}.greyed .num{color:var(--ink-faint)}.greynote{margin:0 10px 6px 38px;color:var(--grey-ink);font-style:italic}
.body{padding:2px 12px 10px 38px;display:grid;grid-template-columns:minmax(0,1fr);gap:8px;min-width:0}.body.small{padding:0 12px 6px 46px;color:var(--ink-soft);font-size:12px}
.grp h4{margin:4px 0 4px;font-size:11px;text-transform:uppercase;letter-spacing:.05em;color:var(--ink-soft)}.grp h4 small{text-transform:none;letter-spacing:0;font-weight:400;color:var(--ink-faint)}
.grp h5{margin:8px 0 4px;font-size:11px;color:var(--ink-soft)}
.chips{display:flex;flex-wrap:wrap;gap:4px}
button{font:inherit;color:inherit;cursor:pointer}
.chip{border:1px solid transparent;border-radius:5px;padding:1px 7px;font-family:var(--mono);font-size:11.5px;display:inline-flex;gap:4px;align-items:center}
.chip:hover,.dec:hover,.cp:hover,.obl:hover{outline:1px solid var(--accent)}
.chip.sel,.dec.sel,.cp.sel,summary.sel{outline:2px solid var(--accent)}
.from{color:var(--ink-soft);font-family:var(--font);font-size:11px}
.out{display:flex;gap:8px;align-items:baseline;min-width:0;margin:1px 0}.out .path{font-family:var(--mono);font-size:11px;color:var(--ink-soft);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;min-width:0}
.dec{display:flex;gap:6px;align-items:baseline;text-align:left;background:none;border:0;padding:2px 0;width:100%;min-width:0}
.dec span:last-child{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;min-width:0}
.none{color:var(--ink-faint);font-style:italic}
.gate{display:flex;align-items:center;gap:8px;margin:0 0 0 22px;padding:5px 10px;border-left:2px dashed var(--warn-ink);min-height:30px;flex-wrap:wrap;cursor:pointer}
.diamond{color:var(--warn-ink);font-size:13px;width:16px;text-align:center}.glabel{color:var(--ink-soft);font-family:var(--mono);font-size:11.5px}
.cp{background:var(--warn-bg);color:var(--warn-ink);border:0;border-radius:5px;padding:1px 7px;font-size:11.5px}
details.module{border-top:1px solid var(--line)}details.module>summary{padding:4px 4px;flex-wrap:wrap}
.obls{display:flex;flex-wrap:wrap;gap:4px;flex:1 1 300px;min-width:0}
.obl{border-radius:5px;padding:0 6px;font-size:11px;display:inline-flex;gap:3px;align-items:baseline;flex-wrap:wrap;max-width:100%;overflow-wrap:anywhere}.obl em{font-style:normal;opacity:.85}
.projobl{display:flex;flex-wrap:wrap;gap:4px;align-items:baseline}.projobl h5{flex-basis:100%;margin:6px 0 2px}
#detail h2{font-size:14px;margin:0 0 4px}#detail .kind{font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:var(--ink-soft)}
#detail dl{margin:8px 0;display:grid;grid-template-columns:96px minmax(0,1fr);gap:4px 10px}#detail dt{color:var(--ink-soft);font-size:12px}
#detail dd{margin:0;overflow-wrap:anywhere}#detail code{font-family:var(--mono);font-size:11.5px}
#detail ul{margin:4px 0;padding-left:18px}#detail .src{color:var(--ink-faint);font-size:11px;margin-top:10px}
footer{padding:10px 20px;color:var(--ink-soft);font-size:12px;border-top:1px solid var(--line)}
@media (max-width:900px){main{grid-template-columns:minmax(0,1fr)}#detail{position:static;border-left:0;border-top:1px solid var(--line);max-height:none}
.skill,.dc{display:none}#outline{padding:10px 16px}}
</style></head><body>
<header>
  <h1>${esc(data.project)} — workflow</h1>
  <span class="kv">entry mode <b>${esc(data.entryMode)}</b> (${esc(data.entryModeStatus)}; runs ${esc(data.modeRow ? data.modeRow.stagesThatRun : 'unknown')})</span>
  <span class="kv">toolkit <b>${esc(data.toolkit.head)}</b> (register pins ${esc(data.toolkit.registerCommit)})</span>
  <span class="kv">generated <b>${esc(data.generatedAt.replace('T', ' ').slice(0, 16))} UTC</b></span>
  <span class="kv">gate-check: ${esc(data.gateCheckSummary)}</span>
  <div class="next">NEXT (bin/status.sh) → ${esc(data.nextAction)}</div>
  <div class="legend"><span>${badge('PASS')} done</span><span>${badge('PENDING')} gate / pending / manual</span><span>${badge('FAIL')} fail</span><span>${badge('WAIVED')} waived / optional / not in mode</span><span>${badge('CONFIRMED')} ${badge('ASSUMED')} decisions</span><span>◆ gate · ✋ hard gate</span>
    <span>${c.stagesShown} of ${c.runbookStages} stages · ${c.outputsShown} of ${c.manifestRowsForMode} manifest rows · ${c.modulesShown} of ${c.buildPlanModules} modules</span></div>
</header>
<main>
  <div id="outline">${outline}</div>
  <aside id="detail"><div class="kind">detail</div><h2>Select a stage, gate, artifact, decision or module</h2>
    <p class="none">Everything here comes from docs/workflow-map.json; "unknown" means the sources do not state it.</p></aside>
</main>
<footer>Regenerate: <code>node tools/extract-workflow-map.js && node tools/render-workflow-map.js</code> · read-only (gate-check runs with --no-html) ·
${data.unknowns.length} unknown(s): ${data.unknowns.map(u => esc(u.what)).join('; ') || 'none'}</footer>
<script id="data" type="application/json">${JSON.stringify(data).replace(/</g, '\\u003c')}</script>
<script>
(function(){
  var D = JSON.parse(document.getElementById('data').textContent);
  var esc = function(s){ return String(s==null?'':s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];}); };
  var md = function(s){ return esc(s).replace(/\\*\\*([^*]+)\\*\\*/g,'<b>$1</b>').replace(/\`([^\`]+)\`/g,'<code>$1</code>'); };
  var pane = document.getElementById('detail');
  var row = function(k,v){ return v==null||v===''?'':'<dt>'+k+'</dt><dd>'+v+'</dd>'; };
  var list = function(a){ return a&&a.length?'<ul>'+a.map(function(x){return '<li>'+x+'</li>';}).join('')+'</ul>':'<span class="none">none</span>'; };
  var stage = function(id){ return D.stages.filter(function(s){return s.id===id;})[0]; };
  function show(kind,id){
    var h='';
    if(kind==='artifact'){
      var a=D.artifacts.filter(function(x){return x.id===id;})[0]; if(!a) return;
      var consumers=D.stages.filter(function(s){return s.inputs.some(function(i){return i.artifact===id;});}).map(function(s){return 'Stage '+s.id+' ('+esc(s.name)+')';});
      h='<div class="kind">artifact · stage '+esc(a.stage)+'</div><h2><code>'+esc(a.id)+'</code></h2><dl>'+
        row('verdict', esc(a.verdict)+(a.verdictDetail?' — '+md(a.verdictDetail):''))+
        row('exists', a.exists?'yes — checked on disk':'<b>no</b> — no path below matches a non-empty file')+
        row('paths', list(a.paths.map(function(p){return '<code>'+esc(p)+'</code>';})))+
        row('found', list(a.found.slice(0,12).map(function(p){return '<code>'+esc(p)+'</code>';}).concat(a.found.length>12?['… +'+(a.found.length-12)+' more']:[])))+
        row('producer', md(a.producer))+row('consumers', md(a.consumers))+
        row('input to', list(consumers))+row('absence', esc(a.absence)+(a.absence==='optin'?' — '+(a.optedIn?'opted in (register line)':'not opted in'):''))+
        row('modes', esc(a.modes.join(', ')))+'</dl><div class="src">bin/lib/artifact-manifest.tsv · gate-check --no-html</div>';
    } else if(kind==='stage'){
      var s=stage(id); if(!s) return;
      h='<div class="kind">stage</div><h2>'+esc(s.id)+' — '+esc(s.name)+(s.hard?' ✋':'')+'</h2><dl>'+
        row('verdict', esc(s.verdict)+(s.verdictDetail?' — '+md(s.verdictDetail):''))+
        (s.greyReason?row('greyed',esc(s.greyReason)):'')+
        row('owner', md(s.owner))+row('roles', esc(s.roles.join(', ')||'none'))+
        row('owning skill', esc(s.owningSkill)+' <span class="none">('+esc(s.owningSkillNote)+')</span>')+
        row('skills cited', esc(s.skillsCited.join(', ')||'none'))+
        row('user defines', md(s.userDefines))+row('agent produces', md(s.agentProduces))+
        row('surface', s.surface?md(s.surface):'<span class="none">no Surface row</span>')+
        row('gate', md(s.gate))+'</dl><div class="src">'+esc(s.source)+'</div>';
    } else if(kind==='gate'){
      var g=stage(id); if(!g) return;
      var ds=D.decisions.filter(function(d){return d.stage===id;});
      h='<div class="kind">gate after stage '+esc(id)+(g.hard?' · hard ✋':'')+'</div><h2>'+esc(g.name)+' → '+(D.stages[D.stages.indexOf(g)+1]?esc(D.stages[D.stages.indexOf(g)+1].name):'end')+'</h2><dl>'+
        row('state', esc(g.verdict)+(g.verdictDetail?' — '+md(g.verdictDetail):''))+
        row('criteria', md(g.gate))+row('owner', md(g.owner))+
        row('checkpoint', g.checkpoints.length?list(g.checkpoints.map(function(c){return '<b>'+esc(c.cac)+'</b> <code>'+esc(c.file)+'</code>'+(c.qualifier?' ('+esc(c.qualifier)+')':'')+'<br>'+md(c.question)+(c.firesAfter?'<br><span class="none">fires after: '+md(c.firesAfter)+'</span>':'');})):'<span class="none">none fires at this close</span>')+
        row('decisions', list(ds.map(function(d){return '<b>'+esc(d.status)+'</b> '+md(d.decision);})))+'</dl><div class="src">skills/conversion-runbook.md §2 + Stage section · PROJECT.md</div>';
    } else if(kind==='decision'){
      var d=D.decisions[+id]; if(!d) return;
      h='<div class="kind">decision · stage '+esc(d.stageCell)+'</div><h2>'+esc(d.status)+'</h2><dl>'+row('decision',md(d.decision))+row('notes',md(d.notes))+'</dl><div class="src">PROJECT.md ## Decisions</div>';
    } else if(kind==='module'){
      var m=D.modules.filter(function(x){return x.module===id;})[0]; if(!m) return;
      h='<div class="kind">module · build order '+m.order+'</div><h2>'+esc(m.module)+'</h2><dl>'+
        m.obligations.map(function(o){ return row(esc(o.id), '<b>'+esc(o.status)+'</b>'+(o.denominator?' · '+esc(o.denominator):'')+(o.note?' · '+esc(o.note):'')+(o.waived?'<br>waived: '+esc(o.waived):'')+
          '<br><code>'+esc(o.proof)+'</code> '+(o.proofExists?'(exists)':'<b>(missing)</b>')+'<br><span class="none">'+esc(o.performer)+'-agent · '+esc(o.skill)+'</span>'); }).join('')+
        row('build log', esc(m.scriptsInBuildLog)+' row(s)'+(m.lastLog?'<br>last: <code>'+esc(m.lastLog.script)+'</code> '+esc(m.lastLog.result):''))+
        '</dl><div class="src">bin/lib/obligations.tsv · gate-check obligation lines · per-module proof files</div>';
    }
    pane.innerHTML=h;
  }
  document.addEventListener('click',function(e){
    var t=e.target.closest('[data-kind]'); if(!t) return;
    var kind=t.getAttribute('data-kind'), id=t.getAttribute('data-id');
    if(kind!=='stage'&&kind!=='module') e.preventDefault();
    if(t.classList.contains('from')){ e.preventDefault(); e.stopPropagation(); var d=document.getElementById('stage-'+id); if(d){d.open=true; d.scrollIntoView({block:'start'});} kind='stage'; }
    document.querySelectorAll('.sel').forEach(function(x){x.classList.remove('sel');}); t.classList.add('sel');
    show(kind,id);
  });
})();
</script>
</body></html>`;
fs.writeFileSync(path.join(ROOT, 'docs', 'workflow-map.html'), html);
console.log(`wrote docs/workflow-map.html (${(html.length / 1024).toFixed(0)} KB)`);
