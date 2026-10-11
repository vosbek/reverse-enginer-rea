"""Self-contained HTML report.

One file, no external requests: a strict Content-Security-Policy forbids
loading anything, and all target-derived text is inserted with textContent,
so content from the analyzed code can never become markup or script.
"""

from __future__ import annotations

import html
import json

CSS = r"""
:root{
  /* Light table: cool paper, deep ink, a cyan lens accent, and a highlighter for evidence */
  --paper:#eef2f3; --panel:#f9fbfb; --ink:#14232b; --muted:#56676f; --rule:#cfd8dc;
  --accent:#0e6e78; --accent-ink:#ffffff; --mark:#f4d94a; --mark-ink:#14232b;
  --high:#b4332b; --medium:#a8620a; --low:#4c6e2e; --info:#6b7a82;
  --sans: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  --mono: ui-monospace, "SF Mono", "Cascadia Mono", Menlo, Consolas, "Liberation Mono", monospace;
}
@media (prefers-color-scheme: dark){ :root:not([data-theme="light"]){
  --paper:#0e171c; --panel:#142229; --ink:#d9e4e8; --muted:#90a3ab; --rule:#27373f;
  --accent:#5cc4cf; --accent-ink:#0e171c; --mark:#e6cb3c; --mark-ink:#0e171c;
  --high:#ef7a70; --medium:#e0a24a; --low:#9cc77a; --info:#90a3ab; color-scheme:dark }}
:root[data-theme="dark"]{
  --paper:#0e171c; --panel:#142229; --ink:#d9e4e8; --muted:#90a3ab; --rule:#27373f;
  --accent:#5cc4cf; --accent-ink:#0e171c; --mark:#e6cb3c; --mark-ink:#0e171c;
  --high:#ef7a70; --medium:#e0a24a; --low:#9cc77a; --info:#90a3ab; color-scheme:dark }
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font:15px/1.55 var(--sans)}
a{color:var(--accent)}
a:focus-visible,button:focus-visible,input:focus-visible,summary:focus-visible,tr:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.wrap{max-width:1200px;margin:0 auto;padding-inline:20px;padding-block:28px 64px}
header.top{display:grid;gap:14px;padding-bottom:22px;border-bottom:1px solid var(--rule)}
.eyebrow{font:600 12px/1 var(--mono);letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}
h1{font-size:clamp(26px,4vw,40px);line-height:1.1;margin:0;letter-spacing:-.01em;text-wrap:balance}
h1 .target{font-family:var(--mono);font-weight:600;background:var(--mark);color:var(--mark-ink);padding:0 .2em;border-radius:3px}
.lede{max-width:70ch;color:var(--muted);margin:0}
.proof{display:flex;flex-wrap:wrap;gap:8px 18px;font:13px/1.4 var(--mono);color:var(--muted);overflow-wrap:anywhere}
.proof b{color:var(--ink);font-weight:600}
.layout{display:grid;grid-template-columns:210px minmax(0,1fr);gap:36px;margin-top:26px}
nav.toc{position:sticky;top:16px;align-self:start;display:grid;gap:2px;font-size:14px}
nav.toc a{color:var(--muted);text-decoration:none;padding:5px 8px;border-left:2px solid transparent}
nav.toc a:hover{color:var(--ink);border-left-color:var(--accent)}
section.sec{padding-block:6px 30px;border-bottom:1px solid var(--rule);margin-bottom:26px;min-width:0}
section.sec>h2{font-size:22px;margin:0 0 4px;text-wrap:balance}
section.sec>p.q{margin:0 0 18px;color:var(--muted);max-width:75ch;overflow-wrap:anywhere}
.view{margin:0 0 22px;min-width:0}
.vhead{display:flex;flex-wrap:wrap;align-items:baseline;gap:6px 12px;margin-bottom:8px}
.vhead h3{font-size:15px;margin:0}
.pill{font:600 11px/1 var(--mono);letter-spacing:.06em;text-transform:uppercase;border:1px solid var(--rule);color:var(--muted);padding:4px 6px;border-radius:999px}
.pill.parsed{border-color:var(--accent);color:var(--accent)}
.count{font:12px var(--mono);color:var(--muted)}
.note{font-size:13px;color:var(--muted);margin:8px 0 0;max-width:80ch}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:1px;background:var(--rule);border:1px solid var(--rule)}
.tile{background:var(--panel);padding:14px 14px 12px;display:grid;gap:2px;align-content:start}
.tile .v{font:600 26px/1.1 var(--mono);font-variant-numeric:tabular-nums}
.tile .l{font-size:13px;font-weight:600}
.tile .h{font-size:12px;color:var(--muted)}
.bars{display:grid;gap:6px}
.bar{display:grid;grid-template-columns:minmax(90px,180px) minmax(0,1fr) 90px;gap:10px;align-items:center;font-size:13px}
.bar .track{height:10px;background:color-mix(in srgb,var(--rule) 55%,transparent);border-radius:2px;overflow:hidden}
.bar .fill{height:100%;background:var(--accent)}
.bar .n{font-family:var(--mono);font-variant-numeric:tabular-nums;text-align:right;color:var(--muted)}
.scroll{overflow-x:auto;border:1px solid var(--rule);background:var(--panel)}
table{border-collapse:collapse;width:100%;font-size:13px}
th{font:600 11px/1.2 var(--mono);letter-spacing:.06em;text-transform:uppercase;color:var(--muted);text-align:left;padding:9px 10px;border-bottom:1px solid var(--rule);white-space:nowrap;background:var(--panel);position:sticky;top:0}
td{padding:7px 10px;border-bottom:1px solid color-mix(in srgb,var(--rule) 60%,transparent);vertical-align:top;overflow-wrap:anywhere}
td.num{font-family:var(--mono);font-variant-numeric:tabular-nums;text-align:right;white-space:nowrap}
td.path{font-family:var(--mono);font-size:12.5px}
tr.row{cursor:pointer}
tr.row:hover td{background:color-mix(in srgb,var(--accent) 7%,transparent)}
tr.row.open td{background:color-mix(in srgb,var(--accent) 10%,transparent)}
tr.evrow td{background:var(--paper);padding:10px 12px}
.sev{font:600 11px var(--mono);text-transform:uppercase;letter-spacing:.05em}
.sev.high{color:var(--high)} .sev.medium{color:var(--medium)} .sev.low{color:var(--low)} .sev.info{color:var(--info)}
.ev{display:grid;gap:6px}
.evline{display:grid;grid-template-columns:auto minmax(0,1fr);gap:0;font:12.5px/1.5 var(--mono);border:1px solid var(--rule);background:var(--panel)}
.evline .loc{padding:5px 8px;background:var(--mark);color:var(--mark-ink);font-weight:600;white-space:nowrap}
.evline .loc a{color:inherit}
.evline code{padding:5px 10px;white-space:pre-wrap;overflow-wrap:anywhere;font:inherit}
.evline .sha{grid-column:1/-1;padding:3px 8px;border-top:1px solid var(--rule);color:var(--muted);font-size:11px}
.filter{display:flex;gap:8px;align-items:center;margin-bottom:8px}
.filter input{font:13px var(--mono);padding:6px 9px;border:1px solid var(--rule);background:var(--panel);color:var(--ink);border-radius:3px;width:min(320px,100%)}
.showall{margin-top:8px;font:600 12px var(--mono);color:var(--accent);background:transparent;border:1px solid var(--accent);padding:6px 10px;border-radius:3px;cursor:pointer}
.showall:hover{background:color-mix(in srgb,var(--accent) 10%,transparent)}
.matrix td,.matrix th{text-align:center;padding:4px;min-width:34px;font-family:var(--mono);font-variant-numeric:tabular-nums}
.matrix th.col{writing-mode:vertical-rl;transform:rotate(180deg);text-transform:none;letter-spacing:0;font-weight:500;max-height:180px;white-space:nowrap;position:static}
.matrix th.rowh{text-align:right;text-transform:none;letter-spacing:0;font-weight:500;position:static}
.matrix td.diag{outline:1px solid var(--rule);outline-offset:-1px}
ol.steps{list-style:none;margin:0;padding:0;display:grid;gap:10px;counter-reset:s}
ol.steps>li{counter-increment:s;display:grid;grid-template-columns:34px minmax(0,1fr);gap:4px 12px;border:1px solid var(--rule);background:var(--panel);padding:12px}
ol.steps>li::before{content:counter(s);font:600 15px/1 var(--mono);color:var(--accent-ink);background:var(--accent);width:28px;height:28px;display:grid;place-items:center;border-radius:2px}
ol.steps h4{margin:3px 0 6px;font-size:14px;overflow-wrap:anywhere}
ol.steps pre{margin:0 0 8px;font:12.5px/1.55 var(--mono);white-space:pre-wrap;overflow-wrap:anywhere;color:var(--ink)}
ol.steps .stepbody{grid-column:2;min-width:0}
.empty{color:var(--muted);font-style:italic;font-size:14px}
ul.blind{margin:0;padding:0;list-style:none;display:grid;gap:8px}
ul.blind li{border:1px dashed var(--medium);padding:10px 12px;background:color-mix(in srgb,var(--medium) 6%,transparent)}
ul.safety{margin:0;padding-left:18px;display:grid;gap:4px}
details.ledger>summary{cursor:pointer;font-weight:600}
footer{margin-top:30px;color:var(--muted);font-size:13px}
@media (max-width:820px){.layout{grid-template-columns:minmax(0,1fr)}nav.toc{position:static;display:flex;flex-wrap:wrap;gap:4px}
  nav.toc a{border-left:0;border:1px solid var(--rule);padding:4px 8px}.bar{grid-template-columns:minmax(70px,120px) minmax(0,1fr) 70px}}
@media (prefers-reduced-motion:no-preference){tr.row td{transition:background .12s}}
"""

JS = r"""
(function(){
const R = JSON.parse(document.getElementById('report-data').textContent);
const M = R.manifest;
const $ = (t, c, txt) => { const e = document.createElement(t); if (c) e.className = c; if (txt != null) e.textContent = txt; return e; };
const fmt = v => typeof v === 'number' ? v.toLocaleString('en-US') : String(v ?? '');
const NUMERIC = new Set(['files','loc','hits','test_hits','fan_in','fan_out','score','links','size','count','total','packages','line']);
const PATHY = new Set(['path','file','target','manifest','members','covers','area']);

function linkFor(ev){
  const t = M.link_template;
  if (!t || !/^https:\/\//.test(t)) return null;
  return t.replace('{path}', ev.path.split('/').map(encodeURIComponent).join('/')).replace('{line}', ev.line || 1);
}
function evidence(evs){
  const box = $('div','ev');
  (evs || []).forEach(ev => {
    const line = $('div','evline');
    const loc = $('span','loc');
    const label = ev.path + (ev.line ? ':' + ev.line : '');
    const href = linkFor(ev);
    if (href){ const a = $('a', null, label); a.href = href; a.target = '_blank'; a.rel = 'noopener noreferrer'; loc.append(a); }
    else loc.textContent = label;
    line.append(loc, $('code', null, ev.snippet || '(whole file)'));
    if (ev.sha256) line.append($('span','sha','sha256 ' + ev.sha256));
    box.append(line);
  });
  if (!box.childElementCount) box.append($('span','empty','No line-level evidence for this row.'));
  return box;
}
function head(v){
  const h = $('div','vhead');
  h.append($('h3', null, v.title || ''));
  if (v.confidence) { const p = $('span','pill ' + v.confidence, v.confidence); p.title = {parsed:'Read by a real parser',pattern:'Matched a documented pattern',heuristic:'Inferred from scores or structure'}[v.confidence] || ''; h.append(p); }
  if (v.kind === 'table') h.append($('span','count', v.total > v.rows.length ? `${fmt(v.rows.length)} of ${fmt(v.total)}` : `${fmt(v.total)} rows`));
  return h;
}
function stats(v){ const g = $('div','tiles'); v.items.forEach(it => { const t = $('div','tile'); t.append($('span','v',fmt(it.value)), $('span','l',it.label), $('span','h',it.hint||'')); g.append(t); }); return g; }
function bars(v){
  const g = $('div','bars'); const max = Math.max(1, ...v.items.map(i => i.value));
  v.items.forEach(it => { const r = $('div','bar'); const tr = $('div','track'); const f = $('div','fill'); f.style.width = (100*it.value/max).toFixed(1)+'%'; tr.append(f);
    r.append($('span',null,it.label), tr, $('span','n',fmt(it.value))); g.append(r); });
  if (!v.items.length) g.append($('p','empty','Nothing to chart.'));
  return g;
}
function table(v){
  const frag = $('div');
  if (!v.rows.length){ frag.append($('p','empty','Nothing found.')); return frag; }
  const wrap = $('div','scroll'); const t = $('table'); const thead = $('thead'); const hr = $('tr');
  v.columns.forEach(c => hr.append($('th', null, c.label))); thead.append(hr); t.append(thead);
  const tb = $('tbody'); t.append(tb); wrap.append(t);
  const rows = v.rows.map(r => {
    const tr = $('tr','row'); tr.tabIndex = 0;
    v.columns.forEach(c => {
      const val = r[c.key];
      const td = $('td', NUMERIC.has(c.key) ? 'num' : (PATHY.has(c.key) ? 'path' : null));
      if (c.key === 'severity'){ td.append($('span','sev ' + val, val)); } else td.textContent = fmt(val);
      tr.append(td);
    });
    let open = null;
    const toggle = () => { if (open){ open.remove(); open = null; tr.classList.remove('open'); return; }
      open = $('tr','evrow'); const td = $('td'); td.colSpan = v.columns.length; td.append(evidence(r._ev)); open.append(td); tr.after(open); tr.classList.add('open'); };
    tr.addEventListener('click', toggle);
    tr.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' '){ e.preventDefault(); toggle(); } });
    tr._text = Object.values(r).filter(x => typeof x !== 'object').join(' ').toLowerCase();
    return tr;
  });
  rows.forEach(r => tb.append(r));
  const CAP = 15; let expanded = rows.length <= CAP; let more = null;
  const apply = q => rows.forEach((r, i) => { r.hidden = q ? !r._text.includes(q) : (!expanded && i >= CAP);
    if (r.nextSibling && r.nextSibling.classList && r.nextSibling.classList.contains('evrow')) r.nextSibling.hidden = r.hidden; });
  if (v.rows.length > 12){
    const f = $('div','filter'); const inp = $('input'); inp.type = 'search'; inp.placeholder = 'Filter rows'; inp.id = 'f-' + v.id; inp.setAttribute('aria-label','Filter ' + (v.title||'rows'));
    inp.addEventListener('input', () => { apply(inp.value.toLowerCase()); if (more) more.hidden = !!inp.value; });
    f.append(inp); frag.append(f);
  }
  frag.append(wrap);
  if (!expanded){
    more = $('button','showall', `Show all ${fmt(rows.length)} rows`); more.type = 'button';
    more.addEventListener('click', () => { expanded = true; apply(''); more.remove(); more = null; });
    frag.append(more); apply('');
  }
  return frag;
}
function matrix(v){
  const wrap = $('div','scroll'); const t = $('table','matrix');
  const max = Math.max(1, ...v.cells.flat());
  const hr = $('tr'); hr.append($('th','rowh','imports ↓ →'));
  v.labels.forEach(l => { const th = $('th','col', l); th.title = l; hr.append(th); });
  t.append(hr);
  v.labels.forEach((l, i) => {
    const tr = $('tr'); tr.append($('th','rowh', l));
    v.cells[i].forEach((n, j) => { const td = $('td', i === j ? 'diag' : null, n ? fmt(n) : '');
      if (n){ const pct = Math.round(12 + 70*Math.log(1+n)/Math.log(1+max)); td.style.background = `color-mix(in srgb, var(--accent) ${pct}%, transparent)`; if (pct > 55) td.style.color = 'var(--accent-ink)'; }
      td.title = `${l} imports ${v.labels[j]}: ${n}`; tr.append(td); });
    t.append(tr);
  });
  wrap.append(t); return wrap;
}
function steps(v){
  if (!v.items.length) return $('p','empty','Nothing to show.');
  const ol = $('ol','steps');
  v.items.forEach(it => { const li = $('li'); const body = $('div','stepbody'); body.append($('h4',null,it.title));
    if (it.body) body.append($('pre',null,it.body));
    if (it.ev && it.ev.length){ const d = $('details'); d.append($('summary','count', `evidence (${it.ev.length})`), evidence(it.ev)); body.append(d); }
    li.append(body); ol.append(li); });
  return ol;
}
function view(v){
  const fig = $('div','view'); fig.append(head(v));
  const k = v.kind;
  fig.append(k === 'stats' ? stats(v) : k === 'bars' ? bars(v) : k === 'table' ? table(v) : k === 'matrix' ? matrix(v) : k === 'steps' ? steps(v) : $('p', null, v.body || ''));
  if (v.note) fig.append($('p','note', v.note));
  return fig;
}
const main = document.getElementById('sections'); const toc = document.getElementById('toc');
R.sections.forEach((s, i) => {
  const sec = $('section','sec'); sec.id = 's' + (i+1);
  sec.append($('h2', null, s.title)); if (s.question) sec.append($('p','q', s.question));
  s.views.forEach(v => sec.append(view(v)));
  main.append(sec);
  const a = $('a', null, s.title); a.href = '#' + sec.id; toc.append(a);
});
const blind = $('section','sec'); blind.id = 'blind'; blind.append($('h2',null,'Blind spots'), $('p','q','What this run could not see. Read these before trusting a conclusion.'));
const ul = $('ul','blind'); (R.blind_spots.length ? R.blind_spots : ['None recorded.']).forEach(b => ul.append($('li',null,b))); blind.append(ul); main.append(blind);
const la = $('a',null,'Blind spots'); la.href = '#blind'; toc.append(la);

const led = $('section','sec'); led.id = 'ledger';
led.append($('h2',null,'What Clearbox read'), $('p','q', `Every file this report is based on, with the SHA-256 of the exact bytes analyzed. Ledger digest ${M.ledger_sha256}.`));
const d = $('details','ledger'); d.append($('summary',null, `Show the ledger (${fmt(R.ledger.length)} files)`));
d.addEventListener('toggle', () => { if (!d.open || d._done) return; d._done = true;
  d.append(table({id:'ledger', kind:'table', title:'', columns:[{key:'path',label:'File'},{key:'size',label:'Bytes'},{key:'mode',label:'Mode'},{key:'sha256',label:'SHA-256'},{key:'readers',label:'Analyzers'}],
    rows: R.ledger.map(e => ({...e, readers: e.readers.join(', '), sha256: e.sha256 || '(sniffed first bytes only)', _ev: [{path:e.path,line:null,snippet:'',sha256:e.sha256}]})), total: R.ledger.length})); });
led.append(d);
const sc = $('h3',null,'Safety contract'); sc.style.margin = '20px 0 8px'; led.append(sc);
const sl = $('ul','safety'); M.safety.forEach(s => sl.append($('li',null,s))); led.append(sl);
main.append(led);
const lla = $('a',null,'Ledger & safety'); lla.href = '#ledger'; toc.append(lla);
})();
"""


def render_html(report: dict) -> str:
    m = report["manifest"]
    payload = {k: v for k, v in report.items() if k not in ("findings", "skipped")}
    data = json.dumps(payload, default=str, separators=(",", ":")).replace("<", "\\u003c").replace(
        "\u2028", "\\u2028").replace("\u2029", "\\u2029")
    esc = html.escape
    params = "".join(f" · <b>{esc(k)}</b>=“{esc(str(v))}”" for k, v in m["params"].items())
    sev = m.get("severity_counts", {})
    mb = m["bytes_read"] / (1024 * 1024)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; base-uri 'none'; form-action 'none'">
<meta name="referrer" content="no-referrer">
<title>{esc(m['template']['name'])} · {esc(m['target'])}</title>
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
<header class="top">
  <span class="eyebrow">Clearbox report · {esc(m['template']['id'])}</span>
  <h1>{esc(m['template']['name'])} of <span class="target">{esc(m['target'])}</span></h1>
  <p class="lede">{esc(m['template']['summary'])}</p>
  <div class="proof">
    <span><b>{m['files_read']:,}</b> files read ({mb:.1f} MB)</span>
    <span><b>0</b> executed</span>
    <span><b>0</b> network calls</span>
    <span><b>{sev.get('high', 0)}</b> high / <b>{sev.get('medium', 0)}</b> medium capability sites</span>
    <span>{m['duration_s']}s</span>
    <span>ledger <b>{esc(m['ledger_sha256'][:12])}</b></span>
    <span>content <b>{esc(m['content_sha256'][:12])}</b></span>
    <span>Clearbox {esc(report['clearbox'])}{params}</span>
  </div>
</header>
<div class="layout">
  <nav class="toc" id="toc" aria-label="Sections"></nav>
  <main id="sections"></main>
</div>
<footer>Generated by Clearbox, a static reverse-engineering tool. Nothing in this report was produced by running the target.
Click any row to see the exact lines behind it.</footer>
</div>
<script type="application/json" id="report-data">{data}</script>
<script>{JS}</script>
</body>
</html>
"""
