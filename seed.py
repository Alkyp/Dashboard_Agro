"""
seed.py — Dashboard Agro
Mengisi database dengan data awal yang realistis untuk demo.
Jalankan: python seed.py
"""
import random
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from database import get_connection, is_seeded, init_schema

random.seed(2026)

# ── DATA DEFINISI ─────────────────────────────────────────────────────────────

CATEGORIES = [
    ('Pupuk', '🌱'),
    ('Pestisida', '🧪'),
    ('Benih', '🌾'),
    ('Alat Tani', '🔧'),
    ('Pakan Ternak', '🐄'),
    ('Hormon Tanaman', '🧬'),
    ('Media Tanam', '🪣'),
    ('Produk Olahan', '🥬'),
]

USERS = [
    # (name, email, password, role, company, phone, address)
    ('Admin Utama', 'admin@agrodasboard.id', 'admin123', 'admin', 'Dashboard Agro HQ', '021-5551000', 'Jakarta Pusat'),
    ('PT Subur Makmur', 'dist1@agrodashboard.id', 'dist123', 'distributor', 'PT Subur Makmur', '021-5551001', 'Bogor, Jawa Barat'),
    ('CV Hijau Lestari', 'dist2@agrodashboard.id', 'dist123', 'distributor', 'CV Hijau Lestari', '031-5552002', 'Malang, Jawa Timur'),
    ('UD Tani Sejahtera', 'dist3@agrodashboard.id', 'dist123', 'distributor', 'UD Tani Sejahtera', '022-5553003', 'Bandung, Jawa Barat'),
    ('PT Agro Nusantara', 'dist4@agrodashboard.id', 'dist123', 'distributor', 'PT Agro Nusantara', '024-5554004', 'Semarang, Jawa Tengah'),
]

PRODUCTS_PER_DIST = {
    1: [  # PT Subur Makmur — fokus pupuk & benih
        ('Pupuk Urea Premium 50kg',   'PUP-50', 1, 185000, 140000, 320, 80,  'kg'),
        ('Pupuk NPK Mutiara 25kg',    'PNM-25', 1, 145000, 110000, 280, 60,  'kg'),
        ('Pupuk Organik Granul 40kg', 'POG-40', 1,  95000,  70000, 410, 100, 'kg'),
        ('Pupuk ZA 50kg',             'PZA-50', 1, 125000,  95000, 200, 50,  'kg'),
        ('Benih Padi Ciherang 5kg',   'BPC-5',  3,  65000,  48000, 550, 100, 'kg'),
        ('Benih Jagung Hibrida 1kg',  'BJH-1',  3,  85000,  62000, 380, 80,  'kg'),
        ('Benih Cabai TM-999 10gr',   'BCT-10', 3,  32000,  22000, 650, 150, 'sachet'),
        ('Benih Tomat Servo F1',      'BTS-F1', 3,  28000,  19000, 480, 100, 'sachet'),
        ('Pupuk Daun Gandasil B',     'PDG-B',  6,  42000,  30000, 390, 80,  'pcs'),
        ('Pupuk KCl 50kg',            'PKC-50', 1, 220000, 170000, 150, 40,  'kg'),
        ('Benih Bayam Raja 100gr',    'BBR-100',3,  15000,  10000, 800, 200, 'sachet'),
        ('Pupuk Growmore 1kg',        'PGM-1',  1,  78000,  58000, 260, 60,  'kg'),
    ],
    2: [  # CV Hijau Lestari — fokus pestisida & hormon
        ('Pestisida Decis 25EC 100ml',    'PD-25', 2,  55000,  38000, 430, 100, 'botol'),
        ('Fungisida Antracol 70WP 250gr', 'FA-70', 2,  68000,  49000, 350,  80, 'pcs'),
        ('Herbisida Roundup 1L',          'HR-1L', 2,  85000,  62000, 280,  60, 'botol'),
        ('Insektisida Prevathon 50ml',    'IP-50', 2,  72000,  52000, 390,  80, 'botol'),
        ('Hormon ZPT Atonik 100ml',       'HZA-1', 6,  38000,  26000, 580, 120, 'botol'),
        ('Hormon Gibro 6% 100ml',         'HG-6',  6,  45000,  32000, 470, 100, 'botol'),
        ('Bakterisida Agrept 20WP',       'BA-20', 2,  62000,  44000, 310,  70, 'pcs'),
        ('Nematisida Petrokur 3G 1kg',    'NP-3',  2,  92000,  68000, 220,  50, 'kg'),
        ('Pestisida Bio Metariz 100gr',   'PBM-1', 2,  48000,  33000, 640, 150, 'pcs'),
        ('Mitisida Omite 570EC 100ml',    'MO-57', 2,  78000,  56000, 290,  60, 'botol'),
    ],
    3: [  # UD Tani Sejahtera — fokus alat & media tanam
        ('Sprayer Manual 14L',          'SM-14', 4, 185000, 130000, 120, 30, 'unit'),
        ('Cangkul Gagang Kayu Jati',    'CGJ-1', 4,  95000,  68000, 210, 50, 'unit'),
        ('Sekop Tanah Super',           'STS-1', 4,  75000,  52000, 180, 40, 'unit'),
        ('Cocopit Premium 50L',         'CP-50', 7,  55000,  38000, 340, 80, 'karung'),
        ('Media Tanam Humus 40kg',      'MTH-40',7,  42000,  29000, 420,100, 'karung'),
        ('Polybag Tanam 30x30cm (100)', 'PT-30', 7,  22000,  14000, 680,150, 'pack'),
        ('Polybag Tanam 40x40cm (50)',  'PT-40', 7,  28000,  18000, 530,120, 'pack'),
        ('Selang Irigasi Tetes 50m',    'SIT-50',4, 145000, 102000, 160, 40, 'roll'),
        ('Gunting Stek Premium',        'GSP-1', 4,  65000,  45000, 240, 50, 'unit'),
        ('Tray Semai 72 Lubang',        'TS-72', 7,  35000,  24000, 490,100, 'pcs'),
        ('Net Shading 65% 4m',          'NS-65', 4,  88000,  62000, 310, 60, 'm'),
        ('Pompa Air Submersible 1/2HP', 'PAS-H', 4, 425000, 310000,  80, 20, 'unit'),
    ],
    4: [  # PT Agro Nusantara — fokus pakan ternak & olahan
        ('Pakan Ayam Broiler BR-1 50kg',    'PAB-50', 5, 345000, 265000, 180, 40, 'karung'),
        ('Pakan Ikan Apung 3mm 10kg',       'PIA-3',  5, 125000,  95000, 320, 80, 'kg'),
        ('Konsentrat Sapi 50kg',            'KS-50',  5, 285000, 215000, 140, 30, 'karung'),
        ('Vitamin Ternak B-Complex 100ml',  'VTB-1',  5,  68000,  48000, 410,100, 'botol'),
        ('Obat Cacing Ternak 100ml',        'OCT-1',  5,  55000,  38000, 380, 80, 'botol'),
        ('Pakan Kambing Super 30kg',        'PKS-30', 5, 215000, 162000, 200, 50, 'karung'),
        ('Tepung Ikan Lokal 25kg',          'TIL-25', 8, 185000, 138000, 160, 40, 'karung'),
        ('Bungkil Kedelai 50kg',            'BK-50',  8, 245000, 185000, 130, 30, 'karung'),
        ('Molases Cair 5L',                 'MC-5',   8,  78000,  55000, 290, 60, 'jerigen'),
        ('Suplemen Probiotik Ternak 1kg',   'SPT-1',  5,  95000,  68000, 340, 70, 'kg'),
        ('Pakan Bebek Layer 20kg',          'PBL-20', 5, 165000, 122000, 220, 50, 'karung'),
    ],
}

RESELLERS_PER_DIST = {
    1: [
        ('Budi Santoso',    '081234567890', 'Bogor Selatan',   6.0, 'budi@tani.id'),
        ('Sari Indah',      '081234567891', 'Bogor Utara',     5.5, 'sari@tani.id'),
        ('Rina Wahyuni',    '081234567892', 'Depok',           5.0, ''),
        ('Riko Lestari',    '081234567893', 'Bekasi Barat',    4.5, ''),
        ('Ahmad Fauzan',    '081234567894', 'Cianjur',         5.0, ''),
    ],
    2: [
        ('Dewi Rahayu',     '082345678901', 'Malang Kota',     6.0, 'dewi@agri.id'),
        ('Hendra Kusuma',   '082345678902', 'Batu',            5.5, ''),
        ('Fitriani',        '082345678903', 'Pasuruan',        5.0, ''),
        ('Rudi Hartono',    '082345678904', 'Blitar',          4.5, ''),
    ],
    3: [
        ('Nita Sari',       '083456789012', 'Bandung Utara',   6.5, 'nita@lestari.id'),
        ('Eko Prasetyo',    '083456789013', 'Cimahi',          5.5, ''),
        ('Fitri Handayani', '083456789014', 'Subang',          5.0, ''),
        ('Wawan Setiawan',  '083456789015', 'Purwakarta',      4.5, ''),
        ('Dian Puspita',    '083456789016', 'Sukabumi',        5.0, ''),
        ('Agus Hermawan',   '083456789017', 'Garut',           4.5, ''),
    ],
    4: [
        ('Slamet Riyanto',  '085678901234', 'Semarang Timur',  6.0, 'slamet@agro.id'),
        ('Endah Purnama',   '085678901235', 'Demak',           5.5, ''),
        ('Bambang Suryadi', '085678901236', 'Kudus',           5.0, ''),
        ('Yunita Dewi',     '085678901237', 'Kendal',          5.0, ''),
    ],
}


def seed():
    if is_seeded():
        print("Database sudah berisi data. Skip seeding.")
        return

    conn = get_connection()
    c = conn.cursor()

    # ── Categories
    for name, icon in CATEGORIES:
        c.execute("INSERT INTO categories (name, icon) VALUES (?, ?)", (name, icon))

    # ── Users
    user_ids = {}
    for i, (name, email, pw, role, company, phone, address) in enumerate(USERS):
        c.execute(
            "INSERT INTO users (name,email,password,role,company,phone,address,avatar_char) "
            "VALUES (?,?,?,?,?,?,?,?)",
            (name, email, generate_password_hash(pw), role, company, phone, address, name[0].upper())
        )
        uid = c.lastrowid
        if role == 'distributor':
            user_ids[i] = uid  # key 1..4 → index 1..4

    # Map dist position (1-based) to real id
    dist_map = {}  # {dist_pos: real_id}
    pos = 1
    for i in range(1, 5):
        dist_map[i] = user_ids[i]

    # ── Products
    prod_map = {}  # {dist_pos: [prod_id, ...]}
    for dist_pos, products in PRODUCTS_PER_DIST.items():
        dist_id = dist_map[dist_pos]
        prod_map[dist_pos] = []
        for name, sku, cat_id, price, cost, stock, stock_min, unit in products:
            c.execute(
                "INSERT INTO products (distributor_id,category_id,name,sku,price,cost_price,stock,stock_min,unit) "
                "VALUES (?,?,?,?,?,?,?,?,?)",
                (dist_id, cat_id, name, sku, price, cost, stock, stock_min, unit)
            )
            prod_map[dist_pos].append(c.lastrowid)

    # ── Resellers
    res_map = {}  # {dist_pos: [res_id, ...]}
    for dist_pos, resellers in RESELLERS_PER_DIST.items():
        dist_id = dist_map[dist_pos]
        res_map[dist_pos] = []
        for name, phone, area, comm, email in resellers:
            c.execute(
                "INSERT INTO resellers (distributor_id,name,phone,email,area,commission_pct) "
                "VALUES (?,?,?,?,?,?)",
                (dist_id, name, phone, email, area, comm)
            )
            res_map[dist_pos].append(c.lastrowid)

    # ── Sales (120 transaksi per distributor, 4 bulan terakhir)
    today = datetime.now()
    for dist_pos in range(1, 5):
        dist_id = dist_map[dist_pos]
        pids = prod_map[dist_pos]
        rids = res_map[dist_pos]
        for _ in range(120):
            days_ago = random.randint(0, 120)
            sale_date = today - timedelta(days=days_ago)
            pid = random.choice(pids)
            rid = random.choice(rids)
            # ambil harga produk dari insert sebelumnya — pakai index sederhana
            # kita sudah tahu harga dari PRODUCTS_PER_DIST
            products_list = PRODUCTS_PER_DIST[dist_pos]
            prod_idx = pids.index(pid)
            price = products_list[prod_idx][4]  # index 4 = price
            qty = random.randint(3, 40)
            disc = random.choice([0, 0, 0, 2, 5])
            total = qty * price * (1 - disc / 100)
            c.execute(
                "INSERT INTO sales (distributor_id,reseller_id,product_id,quantity,unit_price,discount_pct,total,sale_date) "
                "VALUES (?,?,?,?,?,?,?,?)",
                (dist_id, rid, pid, qty, price, disc, total,
                 sale_date.strftime('%Y-%m-%d %H:%M:%S'))
            )
            # Stock movement out
            c.execute(
                "INSERT INTO stock_movements (product_id,type,quantity,note,moved_at) "
                "VALUES (?,?,?,?,?)",
                (pid, 'out', qty, f'Penjualan ke reseller', sale_date.strftime('%Y-%m-%d %H:%M:%S'))
            )

    # ── Targets (periode bulan ini dan bulan lalu)
    for month_offset in [0, 1]:
        if month_offset == 0:
            period = today.strftime('%Y-%m')
        else:
            first = today.replace(day=1)
            prev = first - timedelta(days=1)
            period = prev.strftime('%Y-%m')

        for dist_pos in range(1, 5):
            dist_id = dist_map[dist_pos]
            # Target distributor
            target = random.randint(40, 80) * 1_000_000
            achieved = random.uniform(0.6, 1.15) * target
            c.execute(
                "INSERT INTO targets (distributor_id,reseller_id,period,target_amount,achieved) "
                "VALUES (?,NULL,?,?,?)",
                (dist_id, period, target, min(achieved, target * 1.2))
            )
            # Target per reseller
            for rid in res_map[dist_pos]:
                t = random.randint(8, 20) * 1_000_000
                a = random.uniform(0.5, 1.1) * t
                c.execute(
                    "INSERT INTO targets (distributor_id,reseller_id,period,target_amount,achieved) "
                    "VALUES (?,?,?,?,?)",
                    (dist_id, rid, period, t, min(a, t * 1.2))
                )

    conn.commit()
    conn.close()
    print("✅ Seeding selesai!")
    print("\nAkun Demo:")
    for name, email, pw, role, company, *_ in USERS:
        print(f"  [{role:12s}] {email}  /  {pw}  — {company}")


if __name__ == '__main__':
    init_schema()
    seed()
