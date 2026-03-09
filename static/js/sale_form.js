/**
 * Dashboard Agro — sale_form.js
 * Handles dynamic behavior on tambah/edit penjualan form:
 * - Load produk & reseller berdasarkan distributor (admin mode)
 * - Auto-fill harga satuan dari produk terpilih
 * - Hitung total otomatis
 * - Validasi sebelum submit
 */

'use strict';

// ── State ────────────────────────────────────────────────────────────────────

const SaleForm = {
  productData: {},   // { id: { name, price, stock, unit } }
  resellerData: {},  // { id: { name } }

  /** Referensi elemen */
  els: {
    distSelect:    null,
    productSelect: null,
    resellerSelect: null,
    qtyInput:      null,
    priceInput:    null,
    discInput:     null,
    totalInput:    null,
    stockHint:     null,
    unitLabel:     null,
  },

  init() {
    this.els.distSelect     = document.getElementById('dist-select');
    this.els.productSelect  = document.getElementById('product-select');
    this.els.resellerSelect = document.getElementById('reseller-select');
    this.els.qtyInput       = document.getElementById('qty-input');
    this.els.priceInput     = document.getElementById('price-input');
    this.els.discInput      = document.getElementById('disc-input');
    this.els.totalInput     = document.getElementById('total-input');
    this.els.stockHint      = document.getElementById('stock-hint');
    this.els.unitLabel      = document.getElementById('unit-label');

    if (this.els.distSelect) {
      this.els.distSelect.addEventListener('change', () => this.onDistChange());
    }
    if (this.els.productSelect) {
      this.els.productSelect.addEventListener('change', () => this.onProductChange());
    }
    if (this.els.qtyInput)   this.els.qtyInput.addEventListener('input', () => this.calcTotal());
    if (this.els.priceInput) this.els.priceInput.addEventListener('input', () => this.calcTotal());
    if (this.els.discInput)  this.els.discInput.addEventListener('input', () => this.calcTotal());

    const form = document.getElementById('sale-form');
    if (form) form.addEventListener('submit', e => this.onSubmit(e));

    // Pre-load product data from inline JSON (non-admin mode)
    const inlineData = document.getElementById('product-data-json');
    if (inlineData) {
      try {
        const arr = JSON.parse(inlineData.textContent);
        arr.forEach(p => { this.productData[p.id] = p; });
      } catch {}
    }
  },

  // ── Admin: load products & resellers for selected distributor ──
  async onDistChange() {
    const distId = this.els.distSelect?.value;
    if (!distId) return;

    this.setSelectLoading(this.els.productSelect, 'Memuat produk...');
    this.setSelectLoading(this.els.resellerSelect, 'Memuat reseller...');

    try {
      const [prods, resellers] = await Promise.all([
        fetch(`/api/products/${distId}`).then(r => r.json()),
        fetch(`/api/resellers/${distId}`).then(r => r.json()),
      ]);

      // Products
      this.productData = {};
      prods.forEach(p => { this.productData[p.id] = p; });
      this.populateSelect(this.els.productSelect, prods, '-- Pilih Produk --',
        p => `${p.name} · ${formatRupiah(p.price)} / ${p.unit}`);

      // Resellers
      this.resellerData = {};
      resellers.forEach(r => { this.resellerData[r.id] = r; });
      this.populateSelect(this.els.resellerSelect, resellers, '-- Tanpa Reseller (opsional) --',
        r => r.name + (r.area ? ` — ${r.area}` : ''));

      this.resetTotal();
    } catch (err) {
      showToast('Gagal memuat data distributor.', 'error');
      console.error(err);
    }
  },

  // ── Product selected → fill price & show stock ──
  onProductChange() {
    const pid = this.els.productSelect?.value;
    if (!pid) { this.resetTotal(); return; }

    const prod = this.productData[pid];
    if (!prod) return;

    if (this.els.priceInput)  this.els.priceInput.value = prod.price;
    if (this.els.stockHint)   this.els.stockHint.textContent = `Stok tersedia: ${prod.stock} ${prod.unit || ''}`;
    if (this.els.unitLabel)   this.els.unitLabel.textContent = prod.unit || 'pcs';
    if (this.els.qtyInput)    this.els.qtyInput.max = prod.stock;

    this.calcTotal();
  },

  // ── Calculate total from qty × price × (1 - disc%) ──
  calcTotal() {
    const qty   = parseFloat(this.els.qtyInput?.value)   || 0;
    const price = parseFloat(this.els.priceInput?.value)  || 0;
    const disc  = parseFloat(this.els.discInput?.value)   || 0;
    const total = qty * price * (1 - disc / 100);

    if (this.els.totalInput) {
      this.els.totalInput.value = Math.round(total);
      // Visual display
      const display = document.getElementById('total-display');
      if (display) display.textContent = formatRupiah(total);
    }
  },

  // ── Validate & submit ──
  onSubmit(e) {
    const qty   = parseFloat(this.els.qtyInput?.value) || 0;
    const price = parseFloat(this.els.priceInput?.value) || 0;
    const pid   = this.els.productSelect?.value;

    if (!pid) {
      e.preventDefault();
      showToast('Pilih produk terlebih dahulu.', 'error');
      return;
    }
    if (qty <= 0) {
      e.preventDefault();
      showToast('Jumlah harus lebih dari 0.', 'error');
      this.els.qtyInput?.focus();
      return;
    }
    if (price <= 0) {
      e.preventDefault();
      showToast('Harga satuan tidak valid.', 'error');
      return;
    }

    // Check stock
    const prod = this.productData[pid];
    if (prod && qty > prod.stock) {
      if (!confirm(`Qty (${qty}) melebihi stok tersedia (${prod.stock}). Lanjutkan?`)) {
        e.preventDefault();
      }
    }
  },

  // ── Helpers ──
  setSelectLoading(sel, text) {
    if (!sel) return;
    sel.innerHTML = `<option value="">${text}</option>`;
    sel.disabled = true;
  },

  populateSelect(sel, items, placeholder, labelFn) {
    if (!sel) return;
    sel.innerHTML = `<option value="">${placeholder}</option>`;
    items.forEach(item => {
      const opt = document.createElement('option');
      opt.value = item.id;
      opt.textContent = labelFn(item);
      sel.appendChild(opt);
    });
    sel.disabled = false;
  },

  resetTotal() {
    if (this.els.totalInput)  this.els.totalInput.value = '';
    if (this.els.stockHint)   this.els.stockHint.textContent = '';
    if (this.els.unitLabel)   this.els.unitLabel.textContent = '';
    const display = document.getElementById('total-display');
    if (display) display.textContent = 'Rp 0';
  },
};

document.addEventListener('DOMContentLoaded', () => SaleForm.init());
