/**
 * Dashboard Agro — charts.js
 * Vanilla JS bar chart renderer (no dependencies)
 */

'use strict';

/**
 * Render bar chart ke dalam container element.
 *
 * @param {HTMLElement} container - element dengan data-chart-json attr
 * @param {Array<{label: string, value: number, prev?: number}>} data
 * @param {object} opts
 */
function renderBarChart(container, data, opts = {}) {
  const {
    barColor    = 'var(--leaf)',
    prevColor   = 'rgba(82,183,136,0.3)',
    showPrev    = false,
    showTooltip = true,
    height      = 150,
    formatter   = (v) => formatRupiah(v),
  } = opts;

  if (!data || !data.length) return;

  const maxVal = Math.max(...data.map(d => Math.max(d.value, d.prev || 0)), 1);

  container.innerHTML = '';
  container.style.cssText = `
    display: flex; align-items: flex-end;
    gap: 8px; height: ${height}px;
    padding-top: 10px;
  `;

  data.forEach(d => {
    const col = document.createElement('div');
    col.style.cssText = `
      flex: 1; display: flex; flex-direction: column;
      align-items: center; height: 100%; gap: 5px;
    `;

    const inner = document.createElement('div');
    inner.style.cssText = `flex: 1; width: 100%; display: flex; align-items: flex-end; gap: 3px;`;

    // Main bar
    const bar = document.createElement('div');
    const pct = Math.max((d.value / maxVal) * 100, 2);
    bar.style.cssText = `
      flex: 1; border-radius: 5px 5px 0 0; min-height: 4px;
      height: ${pct}%; cursor: default;
      background: linear-gradient(180deg, var(--leaf-light) 0%, var(--leaf) 100%);
      transition: opacity 0.2s, filter 0.2s;
    `;
    bar.addEventListener('mouseenter', () => {
      bar.style.filter = 'brightness(1.08)';
      if (showTooltip) showChartTooltip(bar, d.label, formatter(d.value));
    });
    bar.addEventListener('mouseleave', () => {
      bar.style.filter = '';
      removeChartTooltip();
    });

    inner.appendChild(bar);

    // Prev bar (if enabled)
    if (showPrev && d.prev !== undefined) {
      const pbar = document.createElement('div');
      const ppct = Math.max((d.prev / maxVal) * 100, 2);
      pbar.style.cssText = `
        flex: 1; border-radius: 5px 5px 0 0; min-height: 4px;
        height: ${ppct}%; cursor: default;
        background: ${prevColor};
        transition: opacity 0.2s;
      `;
      inner.appendChild(pbar);
    }

    // Label
    const label = document.createElement('div');
    label.style.cssText = `
      font-size: 0.70rem; color: var(--text-muted);
      font-weight: 500; white-space: nowrap;
      font-family: 'Plus Jakarta Sans', sans-serif;
    `;
    label.textContent = d.label;

    col.appendChild(inner);
    col.appendChild(label);
    container.appendChild(col);
  });
}

let _tipEl = null;

function showChartTooltip(anchor, label, value) {
  removeChartTooltip();
  _tipEl = document.createElement('div');
  _tipEl.style.cssText = `
    position: fixed; z-index: 9000;
    background: var(--forest-deep); color: #D0E8D8;
    padding: 7px 12px; border-radius: 8px;
    font-size: 0.78rem; font-weight: 600; pointer-events: none;
    box-shadow: 0 4px 16px rgba(0,0,0,0.25);
    font-family: 'Plus Jakarta Sans', sans-serif;
    white-space: nowrap;
  `;
  _tipEl.innerHTML = `<div style="color:var(--text-muted);font-size:0.70rem;">${label}</div><div style="color:var(--leaf-light)">${value}</div>`;
  document.body.appendChild(_tipEl);

  const rect = anchor.getBoundingClientRect();
  _tipEl.style.left = (rect.left + rect.width / 2 - _tipEl.offsetWidth / 2) + 'px';
  _tipEl.style.top  = (rect.top - _tipEl.offsetHeight - 8) + 'px';
}

function removeChartTooltip() {
  if (_tipEl) { _tipEl.remove(); _tipEl = null; }
}

/**
 * Render mini donut / ring progress
 * @param {HTMLCanvasElement} canvas
 * @param {number} pct  0-100
 * @param {string} color CSS color
 */
function renderRingProgress(canvas, pct, color = '#52B788') {
  const size = canvas.width;
  const ctx = canvas.getContext('2d');
  const cx = size / 2, cy = size / 2;
  const r = size * 0.38;
  const lw = size * 0.1;
  const start = -Math.PI / 2;
  const end = start + (Math.PI * 2 * Math.min(pct, 100) / 100);

  ctx.clearRect(0, 0, size, size);

  // Track
  ctx.beginPath();
  ctx.arc(cx, cy, r, 0, Math.PI * 2);
  ctx.strokeStyle = 'rgba(82,183,136,0.12)';
  ctx.lineWidth = lw;
  ctx.stroke();

  // Progress
  ctx.beginPath();
  ctx.arc(cx, cy, r, start, end);
  ctx.strokeStyle = color;
  ctx.lineWidth = lw;
  ctx.lineCap = 'round';
  ctx.stroke();
}

/**
 * Init semua chart dari data-chart attribute di halaman
 */
function initCharts() {
  document.querySelectorAll('[data-chart]').forEach(el => {
    try {
      const raw  = el.getAttribute('data-chart');
      const opts = el.dataset.chartOpts ? JSON.parse(el.dataset.chartOpts) : {};
      const data = JSON.parse(raw);
      renderBarChart(el, data, opts);
    } catch (e) {
      console.warn('Chart render error:', e);
    }
  });

  document.querySelectorAll('canvas[data-ring]').forEach(canvas => {
    const pct   = parseFloat(canvas.dataset.ring) || 0;
    const color = canvas.dataset.ringColor || '#52B788';
    renderRingProgress(canvas, pct, color);
  });
}

document.addEventListener('DOMContentLoaded', initCharts);
