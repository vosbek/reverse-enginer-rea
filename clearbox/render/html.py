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
  /* Clearbox report: white paper, near-black ink, one teal accent; amber marks the exact evidence line. */
  --bg:#f6f7f7; --surface:#ffffff; --surface-2:#f1f3f3; --ink:#0f1a1f; --ink-2:#3a4a51; --muted:#64737a;
  --line:#e2e7e8; --line-2:#cdd5d8; --accent:#00786e; --accent-soft:#e2f1ef; --accent-ink:#ffffff;
  --mark:#fbe7b5; --mark-ink:#4a3200; --data-1:#008a7e;
  --high:#b42f25; --medium:#9a5b00; --low:#3d7a36; --info:#64737a;
  --sans: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  --mono: ui-monospace, "SF Mono", "Cascadia Mono", Menlo, Consolas, "Liberation Mono", monospace;
}
@media (prefers-color-scheme: dark){ :root:not([data-theme="light"]){
  --bg:#0b1013; --surface:#11181c; --surface-2:#172126; --ink:#e4ecef; --ink-2:#b9c6cc; --muted:#8b9ba2;
  --line:#1f2a30; --line-2:#2c3a41; --accent:#3cc2b5; --accent-soft:#11302d; --accent-ink:#06211e;
  --mark:#4a3a12; --mark-ink:#ffe3a3; --data-1:#19a99d;
  --high:#f08378; --medium:#e2a94e; --low:#8fca83; --info:#8b9ba2; color-scheme:dark }}
:root[data-theme="dark"]{
  --bg:#0b1013; --surface:#11181c; --surface-2:#172126; --ink:#e4ecef; --ink-2:#b9c6cc; --muted:#8b9ba2;
  --line:#1f2a30; --line-2:#2c3a41; --accent:#3cc2b5; --accent-soft:#11302d; --accent-ink:#06211e;
  --mark:#4a3a12; --mark-ink:#ffe3a3; --data-1:#19a99d;
  --high:#f08378; --medium:#e2a94e; --low:#8fca83; --info:#8b9ba2; color-scheme:dark }
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 var(--sans);-webkit-font-smoothing:antialiased}
a{color:var(--accent)}
a:focus-visible,button:focus-visible,input:focus-visible,summary:focus-visible,tr:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.wrap{max-width:1240px;margin:0 auto;padding-inline:24px;padding-block:0 72px}
.bar-top{display:flex;justify-content:space-between;align-items:center;gap:12px;padding-block:14px;border-bottom:1px solid var(--line);font-size:13px;color:var(--muted)}
.logo{display:inline-flex;align-items:center;gap:8px;font-weight:700;color:var(--ink);letter-spacing:-.01em;font-size:15px}
.logo i{width:16px;height:16px;border:2px solid var(--ink);border-radius:3px;position:relative;display:inline-block}
.logo i::after{content:"";position:absolute;inset:3px;border-radius:1px;background:var(--accent)}
header.top{display:grid;gap:14px;padding-block:36px 28px}
.eyebrow{font:600 12px/1 var(--sans);letter-spacing:.08em;text-transform:uppercase;color:var(--accent)}
h1{font-size:clamp(28px,4vw,42px);line-height:1.08;margin:0;letter-spacing:-.025em;text-wrap:balance;font-weight:750}
h1 .target{font-family:var(--mono);font-weight:600;letter-spacing:-.03em}
.lede{max-width:72ch;color:var(--ink-2);margin:0;font-size:16px}
.proof{display:flex;flex-wrap:wrap;gap:4px 22px;margin-top:6px;font-size:13.5px;color:var(--muted);overflow-wrap:anywhere}
.proof b{color:var(--ink-2);font-weight:600}
.proof code{font:12.5px var(--mono);color:var(--muted)}
.layout{display:grid;grid-template-columns:220px minmax(0,1fr);gap:40px;margin-top:8px}
nav.toc{position:sticky;top:16px;align-self:start;display:grid;gap:1px;font-size:14px;padding-top:6px}
nav.toc a{color:var(--muted);text-decoration:none;padding:6px 10px;border-radius:6px}
nav.toc a:hover{color:var(--ink);background:var(--surface-2)}
section.sec{padding-block:6px 34px;margin-bottom:24px;min-width:0;border-bottom:1px solid var(--line)}
section.sec>h2{font-size:22px;margin:0 0 4px;text-wrap:balance;letter-spacing:-.015em}
section.sec>p.q{margin:0 0 20px;color:var(--ink-2);max-width:75ch;overflow-wrap:anywhere}
.view{margin:0 0 26px;min-width:0}
.vhead{display:flex;flex-wrap:wrap;align-items:center;gap:6px 10px;margin-bottom:10px}
.vhead h3{font-size:15px;margin:0;font-weight:650}
.pill{font:12.5px var(--sans);color:var(--muted)}
.pill::before{content:"· "}
.count{font:12px var(--sans);color:var(--muted)}
.note{font-size:13px;color:var(--muted);margin:10px 0 0;max-width:85ch}
.kv{width:auto;min-width:min(560px,100%);border-top:1px solid var(--line)}
.kv th{background:none;text-transform:none;letter-spacing:0;font:500 14px var(--sans);color:var(--ink-2);padding:9px 24px 9px 0;border-bottom:1px solid var(--line)}
.kv td{padding:9px 24px 9px 0;font-variant-numeric:tabular-nums;font-weight:600}
.kv td.h{font-weight:400;color:var(--muted);font-size:13px}
.bars{display:grid;gap:8px;background:var(--surface);border:1px solid var(--line);border-radius:4px;padding:16px}
.bar{display:grid;grid-template-columns:minmax(90px,200px) minmax(0,1fr) 90px;gap:12px;align-items:center;font-size:13px}
.bar .track{height:12px}
.bar .fill{height:100%;background:var(--data-1);border-radius:0 4px 4px 0;min-width:2px}
.bar .n{font-variant-numeric:tabular-nums;text-align:right;color:var(--ink-2)}
.scroll{overflow-x:auto;border:1px solid var(--line);background:var(--surface);border-radius:4px}
table{border-collapse:collapse;width:100%;font-size:13.5px}
th{font:600 11.5px/1.2 var(--sans);letter-spacing:.04em;text-transform:uppercase;color:var(--muted);text-align:left;padding:10px 12px;border-bottom:1px solid var(--line);white-space:nowrap;background:var(--surface-2)}
td{padding:9px 12px;border-bottom:1px solid var(--line);vertical-align:top;overflow-wrap:break-word}
tr:last-child td{border-bottom:0}
td.num{font-variant-numeric:tabular-nums;text-align:right;white-space:nowrap}
td.path{font-family:var(--mono);font-size:12.5px;min-width:24ch;overflow-wrap:anywhere}
tr.row{cursor:pointer}
tr.row:hover td{background:var(--surface-2)}
tr.row.open td{background:var(--accent-soft)}
tr.evrow td{background:var(--surface-2);padding:12px 14px}
.sev{display:inline-flex;align-items:center;gap:6px;font:600 12px var(--sans);text-transform:capitalize}
.sev::before{content:"";width:8px;height:8px;border-radius:50%;background:currentColor}
.sev.high{color:var(--high)} .sev.medium{color:var(--medium)} .sev.low{color:var(--low)} .sev.info{color:var(--info)}
.ev{display:grid;gap:6px}
.evline{display:grid;grid-template-columns:auto minmax(0,1fr);font:12.5px/1.5 var(--mono);border:1px solid var(--line);background:var(--surface);border-radius:6px;overflow:hidden}
.evline .loc{padding:6px 10px;background:var(--mark);color:var(--mark-ink);font-weight:600;white-space:nowrap}
.evline .loc a{color:inherit}
.evline code{padding:6px 12px;white-space:pre-wrap;overflow-wrap:anywhere;font:inherit}
.evline .sha{grid-column:1/-1;padding:4px 10px;border-top:1px solid var(--line);color:var(--muted);font-size:11px}
.filter{display:flex;gap:8px;align-items:center;margin-bottom:10px}
.filter input{font:13px var(--sans);padding:8px 11px;border:1px solid var(--line-2);background:var(--surface);color:var(--ink);border-radius:8px;width:min(340px,100%)}
.showall{margin-top:10px;font:600 13px var(--sans);color:var(--accent);background:var(--surface);border:1px solid var(--line-2);padding:7px 12px;border-radius:8px;cursor:pointer}
.showall:hover{border-color:var(--accent)}
.matrix td,.matrix th{text-align:center;padding:5px;min-width:36px;font-variant-numeric:tabular-nums;border-bottom:0}
.matrix th.col{writing-mode:vertical-rl;transform:rotate(180deg);text-transform:none;letter-spacing:0;font-weight:500;max-height:200px;white-space:nowrap;background:var(--surface);font-family:var(--mono);font-size:11.5px}
.matrix th.rowh{text-align:right;text-transform:none;letter-spacing:0;font-weight:500;background:var(--surface);font-family:var(--mono);font-size:11.5px}
.matrix td{border-radius:3px}
.matrix td.diag{box-shadow:inset 0 0 0 1px var(--line-2)}
ol.steps{list-style:none;margin:0;padding:0;display:grid;gap:10px;counter-reset:s}
ol.steps>li{counter-increment:s;display:grid;grid-template-columns:32px minmax(0,1fr);gap:4px 14px;border:1px solid var(--line);background:var(--surface);padding:14px;border-radius:4px}
ol.steps>li::before{content:counter(s) ".";font:600 15px/1.6 var(--sans);color:var(--muted)}
ol.steps h4{margin:4px 0 8px;font-size:14px;overflow-wrap:anywhere}
ol.steps pre{margin:0 0 8px;font:12.5px/1.6 var(--mono);white-space:pre-wrap;overflow-wrap:anywhere;color:var(--ink-2)}
ol.steps .stepbody{grid-column:2;min-width:0}
.empty{color:var(--muted);font-size:14px;padding:14px 16px;border:1px dashed var(--line-2);border-radius:4px;margin:0}
ul.blind{margin:0;padding:0;list-style:none;display:grid;gap:8px}
ul.blind li{border:1px solid var(--line);border-left:3px solid var(--medium);padding:10px 14px;background:var(--surface);border-radius:6px}
ul.safety{margin:0;padding-left:18px;display:grid;gap:4px;color:var(--ink-2)}
details.ledger>summary{cursor:pointer;font-weight:600;color:var(--accent)}
footer{margin-top:30px;color:var(--muted);font-size:13px}
@media (max-width:860px){.layout{grid-template-columns:minmax(0,1fr)}nav.toc{position:static;display:flex;flex-wrap:wrap;gap:6px}
  nav.toc a{border:1px solid var(--line);background:var(--surface)}.bar{grid-template-columns:minmax(70px,120px) minmax(0,1fr) 70px}}
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
  if (v.confidence) { const p = $('span','pill ' + v.confidence, {parsed:'Parsed',pattern:'Pattern match',heuristic:'Heuristic'}[v.confidence] || v.confidence); p.title = {parsed:'Read by a real parser',pattern:'Matched a documented pattern',heuristic:'Inferred from scores or structure'}[v.confidence] || ''; h.append(p); }
  if (v.kind === 'table') h.append($('span','count', v.total > v.rows.length ? `${fmt(v.rows.length)} of ${fmt(v.total)}` : `${fmt(v.total)} ${v.total === 1 ? 'row' : 'rows'}`));
  return h;
}
function stats(v){ const t = $('table','kv'); const tb = $('tbody'); v.items.forEach(it => { const tr = $('tr'); tr.append($('th',null,it.label), $('td',null,fmt(it.value)), $('td','h',it.hint||'')); tb.append(tr); }); t.append(tb); return t; }
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
  // A column whose every row holds the same value says it once, above the table.
  if (v.rows.length > 1 && v.id !== 'ledger'){
    const same = v.columns.filter(c => typeof v.rows[0][c.key] !== 'object' && v.rows.every(r => r[c.key] === v.rows[0][c.key]));
    if (same.length && same.length < v.columns.length){
      v = {...v, columns: v.columns.filter(c => !same.includes(c)), shared: same.map(c => `${c.label}: ${fmt(v.rows[0][c.key])}`)};
      frag.append($('p','count', 'All rows · ' + v.shared.join(' · ')));
      frag.lastChild.style.margin = '0 0 8px';
    }
  }
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
    params = "".join(f" · {esc(k)}=“{esc(str(v))}”" for k, v in m["params"].items())
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
<div class="bar-top"><span class="logo"><i></i>Clearbox</span><span>Static analysis · nothing in this report came from running the target</span></div>
<header class="top">
  <span class="eyebrow">{esc(m['template']['name'])}</span>
  <h1><span class="target">{esc(m['target'])}</span></h1>
  <p class="lede">{esc(m['template']['summary'])}</p>
  <div class="proof">
    <span><b>{m['files_read']:,}</b> files read ({mb:.1f} MB) in {m['duration_s']} s</span>
    <span>nothing executed</span>
    <span><b>{sev.get('high', 0)}</b> high and <b>{sev.get('medium', 0)}</b> medium capability sites</span>
    <span><b>{len(report['blind_spots'])}</b> blind spots</span>
    <span><code>ledger {esc(m['ledger_sha256'][:12])} · content {esc(m['content_sha256'][:12])} · Clearbox {esc(report['clearbox'])}{params}</code></span>
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
