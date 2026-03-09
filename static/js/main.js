/**
 * Dashboard Agro — main.js
 * Global utilities: formatting, flash messages, tooltips
 */

'use strict';

// ── Number Formatting ─────────────────────────────────────────────────────────

/**
 * Format angka ke format Rupiah: "Rp 1.234.500"
 * @param {number} value
 * @returns {string}
 */
function formatRupiah(value) {
  if (isNaN(value) || value === null) return 'Rp 0';
  return 'Rp ' + Math.round(value).toLocaleString('id-ID');
}

/**
 * Format angka dengan titik ribuan: "1.234.500"
 */
function formatNumber(value) {
  return Math.round(value).toLocaleString('id-ID');
}

/**
 * Singkat angka besar: 1.5 Jt, 2.3 M
 */
function formatShort(value) {
  if (value >= 1_000_000_000) return (value / 1_000_000_000).toFixed(1) + ' M';
  if (value >= 1_000_000)     return (value / 1_000_000).toFixed(1) + ' Jt';
  if (value >= 1_000)         return (value / 1_000).toFixed(0) + ' rb';
  return value;
}

// ── Toast Notifications ───────────────────────────────────────────────────────

/**
 * Tampilkan toast notifikasi
 * @param {string} message
 * @param {'success'|'error'|'info'} type
 * @param {number} duration ms
 */
function showToast(message, type = 'success', duration = 3500) {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.style.cssText = `
      position: fixed; bottom: 24px; right: 24px; z-index: 9999;
      display: flex; flex-direction: column; gap: 10px;
      max-width: 340px;
    `;
    document.body.appendChild(container);
  }

  const icons = {
    success: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="16" height="16"><polyline points="20,6 9,17 4,12"/></svg>`,
    error:   `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="16" height="16"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>`,
    info:    `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="16" height="16"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>`,
  };

  const colors = {
    success: { bg: '#F0FBF5', border: '#52B788', color: '#1B5E3B' },
    error:   { bg: '#FFF4F0', border: '#E07C5C', color: '#7B2D10' },
    info:    { bg: '#EFF6FF', border: '#6BAED6', color: '#154360' },
  };
  const c = colors[type] || colors.info;

  const toast = document.createElement('div');
  toast.style.cssText = `
    background: ${c.bg}; border: 1px solid ${c.border}; color: ${c.color};
    padding: 12px 16px; border-radius: 10px; font-size: 13.5px; font-weight: 500;
    display: flex; align-items: center; gap: 10px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.12);
    animation: toastIn 0.3s ease;
    font-family: 'Plus Jakarta Sans', sans-serif;
  `;
  toast.innerHTML = icons[type] + `<span>${message}</span>`;

  if (!document.getElementById('toast-style')) {
    const style = document.createElement('style');
    style.id = 'toast-style';
    style.textContent = `
      @keyframes toastIn  { from { opacity:0; transform: translateY(12px); } to { opacity:1; transform: translateY(0); } }
      @keyframes toastOut { from { opacity:1; transform: translateY(0);    } to { opacity:0; transform: translateY(12px); } }
    `;
    document.head.appendChild(style);
  }

  container.appendChild(toast);
  setTimeout(() => {
    toast.style.animation = 'toastOut 0.3s ease forwards';
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

// ── Flash → Toast ─────────────────────────────────────────────────────────────

/**
 * Konversi flash messages di DOM menjadi toast
 */
function initFlashToasts() {
  const list = document.querySelector('.flash-list');
  if (!list) return;
  list.querySelectorAll('.flash').forEach(el => {
    const type = el.classList.contains('flash-success') ? 'success'
               : el.classList.contains('flash-error')   ? 'error' : 'info';
    const text = el.querySelector('span')?.textContent || el.textContent.trim();
    showToast(text, type);
    el.remove();
  });
  if (!list.children.length) list.remove();
}

// ── Active Nav ────────────────────────────────────────────────────────────────

function initActiveNav() {
  const path = window.location.pathname;
  document.querySelectorAll('.nav-item').forEach(link => {
    const href = link.getAttribute('href') || '';
    if (href && href !== '/' && path.startsWith(href)) {
      link.classList.add('active');
    } else if (href === path) {
      link.classList.add('active');
    }
  });
}

// ── Delete Confirmation Modal ─────────────────────────────────────────────────

/**
 * Tampilkan modal konfirmasi hapus yang elegan.
 * @param {object} opts
 * @param {string}   opts.title    - Judul modal
 * @param {string}   opts.message  - Pesan konfirmasi
 * @param {string}   opts.action   - URL POST untuk hapus
 * @param {string}   [opts.label]  - Label tombol hapus (default: 'Ya, Hapus')
 */
function showDeleteModal({ title = 'Konfirmasi Hapus', message = 'Yakin ingin menghapus data ini?', action, label = 'Ya, Hapus' }) {
  // Remove existing modal
  document.getElementById('_del-modal')?.remove();

  const overlay = document.createElement('div');
  overlay.id = '_del-modal';
  overlay.style.cssText = `
    position: fixed; inset: 0; z-index: 9998;
    background: rgba(15,35,24,0.55); backdrop-filter: blur(4px);
    display: flex; align-items: center; justify-content: center;
    padding: 20px;
    animation: modalBgIn 0.2s ease;
  `;

  overlay.innerHTML = `
    <div style="
      background: #fff; border-radius: 18px;
      width: 100%; max-width: 400px;
      box-shadow: 0 20px 60px rgba(15,35,24,0.25);
      overflow: hidden;
      animation: modalIn 0.25s cubic-bezier(0.34,1.56,0.64,1);
      font-family: 'Plus Jakarta Sans', sans-serif;
    ">
      <!-- Header -->
      <div style="padding:22px 24px 16px;border-bottom:1px solid #E8F0EA;">
        <div style="display:flex;align-items:center;gap:12px;">
          <div style="
            width:40px;height:40px;border-radius:12px;
            background:rgba(224,124,92,0.12);
            display:flex;align-items:center;justify-content:center;flex-shrink:0;
          ">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#E07C5C" stroke-width="2.2">
              <polyline points="3 6 5 6 21 6"/>
              <path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/>
              <path d="M10 11v6M14 11v6"/>
              <path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/>
            </svg>
          </div>
          <div>
            <div style="font-weight:700;font-size:1rem;color:#1A2E1F;">${title}</div>
          </div>
        </div>
      </div>
      <!-- Body -->
      <div style="padding:18px 24px 20px;">
        <p style="font-size:0.88rem;color:#7A9882;line-height:1.65;margin:0;">${message}</p>
      </div>
      <!-- Footer -->
      <div style="padding:14px 24px;border-top:1px solid #E8F0EA;display:flex;gap:10px;justify-content:flex-end;background:#F8F4EF;">
        <button id="_del-cancel" style="
          padding:9px 18px;border-radius:10px;font-size:0.87rem;font-weight:600;
          background:#fff;color:#3D5C47;border:1.5px solid #D5E8DA;cursor:pointer;
          font-family:'Plus Jakarta Sans',sans-serif;transition:background 0.15s;
        ">Batal</button>
        <button id="_del-confirm" style="
          padding:9px 18px;border-radius:10px;font-size:0.87rem;font-weight:600;
          background:#E07C5C;color:#fff;border:none;cursor:pointer;
          font-family:'Plus Jakarta Sans',sans-serif;transition:all 0.15s;
        ">${label}</button>
      </div>
    </div>
  `;

  // Add keyframe if not exists
  if (!document.getElementById('_modal-style')) {
    const s = document.createElement('style');
    s.id = '_modal-style';
    s.textContent = `
      @keyframes modalBgIn { from{opacity:0} to{opacity:1} }
      @keyframes modalIn   { from{opacity:0;transform:scale(0.88) translateY(10px)} to{opacity:1;transform:scale(1) translateY(0)} }
    `;
    document.head.appendChild(s);
  }

  const close = () => {
    overlay.style.animation = 'modalBgIn 0.15s ease reverse';
    setTimeout(() => overlay.remove(), 140);
  };

  overlay.addEventListener('click', (e) => { if (e.target === overlay) close(); });
  document.addEventListener('keydown', function esc(e) {
    if (e.key === 'Escape') { close(); document.removeEventListener('keydown', esc); }
  });

  document.body.appendChild(overlay);

  document.getElementById('_del-cancel').addEventListener('click', close);
  document.getElementById('_del-confirm').addEventListener('click', () => {
    // Submit via hidden form (POST)
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = action;
    document.body.appendChild(form);
    form.submit();
  });

  document.getElementById('_del-confirm').addEventListener('mouseenter', function() {
    this.style.background = '#C9603E';
  });
  document.getElementById('_del-confirm').addEventListener('mouseleave', function() {
    this.style.background = '#E07C5C';
  });
}


// ── Tooltip ───────────────────────────────────────────────────────────────────

function initTooltips() {
  document.querySelectorAll('[data-tip]').forEach(el => {
    el.style.position = 'relative';
    el.style.cursor = 'help';
    el.addEventListener('mouseenter', () => {
      const tip = document.createElement('div');
      tip.className = '_tip';
      tip.textContent = el.dataset.tip;
      tip.style.cssText = `
        position: absolute; bottom: calc(100% + 6px); left: 50%; transform: translateX(-50%);
        background: #1B4332; color: #fff; font-size: 0.75rem; font-weight: 500;
        padding: 5px 10px; border-radius: 6px; white-space: nowrap; z-index: 999;
        pointer-events: none; box-shadow: 0 2px 8px rgba(0,0,0,0.2);
      `;
      el.appendChild(tip);
    });
    el.addEventListener('mouseleave', () => {
      el.querySelector('._tip')?.remove();
    });
  });
}

// ── Format input as currency live ─────────────────────────────────────────────

function maskRupiah(input) {
  input.addEventListener('input', () => {
    const raw = input.value.replace(/[^\d]/g, '');
    // keep numeric, will be read as raw by backend
    input.dataset.raw = raw;
  });
}

// ── Date helpers ──────────────────────────────────────────────────────────────

/**
 * Return 'YYYY-MM-DDThh:mm' untuk input datetime-local
 */
function nowDatetimeLocal() {
  const now = new Date();
  const pad = n => String(n).padStart(2, '0');
  return `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}T${pad(now.getHours())}:${pad(now.getMinutes())}`;
}

// ── Init ──────────────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  initFlashToasts();
  initActiveNav();
  initTooltips();

  // Auto-set datetime inputs to now if empty
  document.querySelectorAll('input[type="datetime-local"]').forEach(inp => {
    if (!inp.value) inp.value = nowDatetimeLocal();
  });
});
