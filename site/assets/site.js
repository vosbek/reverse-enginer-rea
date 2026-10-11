// Copy buttons, mobile nav, and chart tooltips. No dependencies.
document.querySelectorAll('[data-copy]').forEach(btn => btn.addEventListener('click', async () => {
  const el = document.getElementById(btn.dataset.copy);
  try { await navigator.clipboard.writeText(el.textContent); btn.textContent = 'Copied'; }
  catch { const r = document.createRange(); r.selectNodeContents(el); const s = getSelection(); s.removeAllRanges(); s.addRange(r); btn.textContent = 'Selected'; }
  setTimeout(() => { btn.textContent = 'Copy'; }, 1600);
}));

const nav = document.querySelector('.nav');
const toggle = document.querySelector('.nav-toggle');
toggle?.addEventListener('click', () => {
  const open = nav.classList.toggle('open');
  toggle.setAttribute('aria-expanded', String(open));
});

// Tooltips for chart marks: any element with data-tip-title / data-tip inside a .chart.
let tip;
function showTip(target) {
  const chart = target.closest('.chart');
  if (!chart) return;
  tip?.remove();
  tip = document.createElement('div');
  tip.className = 'tip';
  tip.setAttribute('role', 'tooltip');
  const b = document.createElement('b');
  b.textContent = target.dataset.tipTitle || '';
  tip.append(b, document.createTextNode(target.dataset.tip || ''));
  chart.style.position = 'relative';
  chart.append(tip);
  const c = chart.getBoundingClientRect(), r = target.getBoundingClientRect();
  const left = Math.min(Math.max(8, r.left - c.left + r.width / 2 - tip.offsetWidth / 2), c.width - tip.offsetWidth - 8);
  tip.style.left = `${left}px`;
  tip.style.top = `${r.top - c.top - tip.offsetHeight - 8}px`;
}
document.querySelectorAll('[data-tip]').forEach(el => {
  el.tabIndex = 0;
  el.addEventListener('mouseenter', () => showTip(el));
  el.addEventListener('focus', () => showTip(el));
  el.addEventListener('mouseleave', () => tip?.remove());
  el.addEventListener('blur', () => tip?.remove());
});
