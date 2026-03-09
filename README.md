# 🌿 Dashboard Agro — Platform Distribusi Pertanian

Sistem dashboard distribusi berbasis Flask dengan multi-role (Admin & Distributor), database SQLite terstruktur, dan tampilan modern bertema pertanian.

---

## 🚀 Cara Menjalankan

```bash
# 1. Install dependensi
pip install flask werkzeug

# 2. Jalankan aplikasi (seed data otomatis)
python app.py

# 3. Buka browser
http://localhost:5000
```

---

## 🔑 Akun Demo

| Role        | Email                         | Password | Keterangan              |
|-------------|-------------------------------|----------|------------------------|
| Admin       | admin@agrodasboard.id         | admin123 | Melihat semua data     |
| Distributor | dist1@agrodashboard.id        | dist123  | PT Subur Makmur (Pupuk & Benih)     |
| Distributor | dist2@agrodashboard.id        | dist123  | CV Hijau Lestari (Pestisida & Hormon) |
| Distributor | dist3@agrodashboard.id        | dist123  | UD Tani Sejahtera (Alat & Media Tanam) |
| Distributor | dist4@agrodashboard.id        | dist123  | PT Agro Nusantara (Pakan Ternak)    |

---

## 🏗️ Struktur Proyek

```
dashboard_agro/
├── app.py              ← Flask routes, auth, API endpoints
├── database.py         ← Koneksi DB, query helpers, init schema
├── seed.py             ← Data awal (users, produk, reseller, penjualan, target)
├── schema.sql          ← DDL schema SQLite lengkap
├── agro.db             ← Database SQLite (auto-generated)
│
├── static/
│   ├── css/
│   │   ├── main.css    ← Variables, reset, typography, utilities, buttons, layout
│   │   ├── sidebar.css ← Sidebar navigation styles
│   │   ├── tables.css  ← Data table, leaderboard, filter bar
│   │   └── forms.css   ← Form, input, stat cards, charts, dashboard components
│   └── js/
│       ├── main.js     ← Utilities: format rupiah, toast, active nav, tooltip
│       ├── charts.js   ← Vanilla JS bar chart renderer (no dependencies)
│       └── sale_form.js ← Dinamis: load produk/reseller, hitung total, validasi
│
└── templates/
    ├── base.html            ← Layout: sidebar + topbar + flash messages
    ├── login.html           ← Halaman login (standalone)
    ├── dashboard.html       ← Dashboard distributor
    ├── dashboard_admin.html ← Dashboard admin (semua distributor)
    ├── sales.html           ← Daftar penjualan + filter + pagination
    ├── add_sale.html        ← Form tambah penjualan (dinamis)
    ├── products.html        ← Daftar produk + filter
    ├── product_form.html    ← Form tambah/edit produk
    ├── resellers.html       ← Daftar reseller
    ├── add_reseller.html    ← Form tambah reseller
    ├── targets.html         ← Target penjualan + progress bar
    ├── leaderboard.html     ← Peringkat reseller/distributor
    ├── users.html           ← Manajemen pengguna (admin only)
    ├── add_user.html        ← Form tambah pengguna
    └── profile.html        ← Edit profil & password
```

---

## 🌾 Fitur

### Admin
- ✅ Dashboard global semua distributor
- ✅ Filter penjualan & produk per distributor
- ✅ Perbandingan performa antar distributor
- ✅ Manajemen pengguna (tambah distributor/admin)

### Distributor
- ✅ Dashboard personal (pendapatan, transaksi, stok, komisi)
- ✅ Data **sepenuhnya terpisah** antar distributor
- ✅ Kelola produk sendiri (dengan kategori & stok minimum)
- ✅ Kelola reseller sendiri
- ✅ Input penjualan dengan kalkulasi otomatis
- ✅ Leaderboard reseller
- ✅ Tracking target

### Database
- ✅ Schema SQL terpisah (`schema.sql`)
- ✅ Foreign keys dengan `ON DELETE CASCADE`
- ✅ Indexes untuk performa query
- ✅ Tabel: users, products, categories, resellers, sales, targets, stock_movements

---

## 🎨 Design System

- **Fonts**: Fraunces (display serif) + Plus Jakarta Sans (body) + JetBrains Mono (angka/kode)
- **Palette**: Forest green (#1B4332), Leaf (#52B788), Wheat (#E9C46A), Earth (#8B5E3C)
- **Tema**: Organic agricultural — earthy, premium, trustworthy
