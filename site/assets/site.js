// Copy buttons, small-screen menu, and chart tooltips. No dependencies.
document.querySelectorAll('[data-copy]').forEach(btn => btn.addEventListener('click', async () => {
  const el = document.getElementById(btn.dataset.copy);
  try { await navigator.clipboard.writeText(el.textContent); btn.textContent = 'Copied'; }
  catch { const r = document.createRange(); r.selectNodeContents(el); const s = getSelection(); s.removeAllRanges(); s.addRange(r); btn.textContent = 'Selected'; }
  setTimeout(() => { btn.textContent = 'Copy'; }, 1600);
}));

const head = document.querySelector('.masthead');
const menu = document.querySelector('.menu');
menu?.addEventListener('click', () => menu.setAttribute('aria-expanded', String(head.classList.toggle('open'))));

let tip;
function showTip(el) {
  const chart = el.closest('.chart');
  if (!chart) return;
  tip?.remove();
  tip = document.createElement('div');
  tip.className = 'tip';
  tip.setAttribute('role', 'tooltip');
  const b = document.createElement('b');
  b.textContent = el.dataset.tipTitle || '';
  tip.append(b, document.createTextNode(el.dataset.tip || ''));
  chart.append(tip);
  const c = chart.getBoundingClientRect(), r = el.getBoundingClientRect();
  tip.style.left = `${Math.min(Math.max(0, r.left - c.left + r.width / 2 - tip.offsetWidth / 2), c.width - tip.offsetWidth)}px`;
  tip.style.top = `${r.top - c.top - tip.offsetHeight - 8}px`;
}
document.querySelectorAll('[data-tip]').forEach(el => {
  el.tabIndex = 0;
  el.addEventListener('mouseenter', () => showTip(el));
  el.addEventListener('focus', () => showTip(el));
  el.addEventListener('mouseleave', () => tip?.remove());
  el.addEventListener('blur', () => tip?.remove());
});
