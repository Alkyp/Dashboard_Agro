"""
seed.py — Dashboard Agro
Data awal dengan sistem 3-tier role: super_admin, admin_cabang, user
"""
import random
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from database import get_connection, is_seeded, init_schema

random.seed(2026)

CATEGORIES = [
    ('Pupuk', '🌱'), ('Pestisida', '🧪'), ('Benih', '🌾'), ('Alat Tani', '🔧'),
    ('Pakan Ternak', '🐄'), ('Hormon Tanaman', '🧬'), ('Media Tanam', '🪣'), ('Produk Olahan', '🥬'),
]

# (name, email, password, role, company, phone, address)
USERS = [
    # Super Admin (Admin Utama)
    ('Super Admin', 'superadmin@agrodashboard.id', 'admin123', 'super_admin', 'Dashboard Agro HQ', '021-5551000', 'Jakarta Pusat'),
    ('Admin Backup', 'admin2@agrodashboard.id', 'admin123', 'super_admin', 'Dashboard Agro HQ', '021-5551099', 'Jakarta Selatan'),
    # Admin Cabang per perusahaan
    ('Admin PT Subur Makmur', 'cabang1@agrodashboard.id', 'cabang123', 'admin_cabang', 'PT Subur Makmur', '021-5551011', 'Bogor, Jawa Barat'),
    ('Admin CV Hijau Lestari', 'cabang2@agrodashboard.id', 'cabang123', 'admin_cabang', 'CV Hijau Lestari', '031-5552022', 'Malang, Jawa Timur'),
    ('Admin UD Tani Sejahtera', 'cabang3@agrodashboard.id', 'cabang123', 'admin_cabang', 'UD Tani Sejahtera', '022-5553033', 'Bandung, Jawa Barat'),
    ('Admin PT Agro Nusantara', 'cabang4@agrodashboard.id', 'cabang123', 'admin_cabang', 'PT Agro Nusantara', '024-5554044', 'Semarang, Jawa Tengah'),
    # User biasa (distributor) per perusahaan
    ('Budi Santoso', 'dist1@agrodashboard.id', 'user123', 'user', 'PT Subur Makmur', '021-5551001', 'Bogor, Jawa Barat'),
    ('Sari Wahyuni', 'dist1b@agrodashboard.id', 'user123', 'user', 'PT Subur Makmur', '021-5551002', 'Bogor Utara'),
    ('Dewi Rahayu', 'dist2@agrodashboard.id', 'user123', 'user', 'CV Hijau Lestari', '031-5552002', 'Malang, Jawa Timur'),
    ('Hendra Kusuma', 'dist2b@agrodashboard.id', 'user123', 'user', 'CV Hijau Lestari', '031-5552003', 'Batu, Jawa Timur'),
    ('Nita Sari', 'dist3@agrodashboard.id', 'user123', 'user', 'UD Tani Sejahtera', '022-5553003', 'Bandung, Jawa Barat'),
    ('Slamet Riyanto', 'dist4@agrodashboard.id', 'user123', 'user', 'PT Agro Nusantara', '024-5554004', 'Semarang, Jawa Tengah'),
]

PRODUCTS_TEMPLATE = [
    ('Pupuk Urea Premium 50kg',   'PUP-50', 1, 185000, 140000, 320, 80,  'kg'),
    ('Pupuk NPK Mutiara 25kg',    'PNM-25', 1, 145000, 110000, 280, 60,  'kg'),
    ('Pupuk Organik Granul 40kg', 'POG-40', 1,  95000,  70000, 410, 100, 'kg'),
    ('Benih Padi Ciherang 5kg',   'BPC-5',  3,  65000,  48000, 550, 100, 'kg'),
    ('Benih Jagung Hibrida 1kg',  'BJH-1',  3,  85000,  62000, 380, 80,  'kg'),
    ('Pestisida Decis 25EC 100ml','PD-25',  2,  55000,  38000, 430, 100, 'botol'),
    ('Fungisida Antracol 250gr',  'FA-70',  2,  68000,  49000, 350, 80,  'pcs'),
    ('Sprayer Manual 14L',        'SM-14',  4, 185000, 130000, 120, 30,  'unit'),
    ('Cocopit Premium 50L',       'CP-50',  7,  55000,  38000, 340, 80,  'karung'),
    ('Pakan Ayam Broiler 50kg',   'PAB-50', 5, 345000, 265000, 180, 40,  'karung'),
]

RESELLERS_TEMPLATE = [
    ('Ahmad Fauzan',    '081234567890', 'Wilayah Utara',  6.0, 'ahmad@tani.id'),
    ('Rina Wahyuni',    '081234567891', 'Wilayah Selatan',5.5, 'rina@tani.id'),
    ('Eko Prasetyo',    '082345678901', 'Wilayah Barat',  5.0, ''),
    ('Fitri Handayani', '082345678902', 'Wilayah Timur',  4.5, ''),
    ('Agus Hermawan',   '083456789012', 'Wilayah Tengah', 5.0, ''),
]


def seed():
    if is_seeded():
        print("Database sudah berisi data. Skip seeding.")
        return

    conn = get_connection()
    c = conn.cursor()

    # Categories
    for name, icon in CATEGORIES:
        c.execute("INSERT INTO categories (name, icon) VALUES (?, ?)", (name, icon))

    # Users
    user_ids = {}
    super_admin_id = None
    for i, (name, email, pw, role, company, phone, address) in enumerate(USERS):
        c.execute(
            "INSERT INTO users (name,email,password,role,company,phone,address,avatar_char) "
            "VALUES (?,?,?,?,?,?,?,?)",
            (name, email, generate_password_hash(pw), role, company, phone, address, name[0].upper())
        )
        uid = c.lastrowid
        user_ids[i] = uid
        if role == 'super_admin' and super_admin_id is None:
            super_admin_id = uid

    # Users yang bisa jadi distributor (role 'user', index 6..11)
    dist_users = [(6, 'PT Subur Makmur'), (7, 'PT Subur Makmur'),
                  (8, 'CV Hijau Lestari'), (9, 'CV Hijau Lestari'),
                  (10, 'UD Tani Sejahtera'), (11, 'PT Agro Nusantara')]

    # Products & Resellers per distributor
    prod_map = {}
    res_map  = {}

    for idx, (user_idx, company) in enumerate(dist_users):
        dist_id = user_ids[user_idx]
        prod_map[dist_id] = []
        # Products: pakai template dengan suffix berbeda
        for j, (name, sku, cat_id, price, cost, stock, stock_min, unit) in enumerate(PRODUCTS_TEMPLATE):
            c.execute(
                "INSERT INTO products (distributor_id,category_id,name,sku,price,cost_price,stock,stock_min,unit) "
                "VALUES (?,?,?,?,?,?,?,?,?)",
                (dist_id, cat_id, name, f"{sku}-{idx+1}", price, cost,
                 stock + random.randint(-50, 50), stock_min, unit)
            )
            prod_map[dist_id].append(c.lastrowid)

        res_map[dist_id] = []
        for name, phone, area, comm, email in RESELLERS_TEMPLATE:
            c.execute(
                "INSERT INTO resellers (distributor_id,name,phone,email,area,commission_pct) "
                "VALUES (?,?,?,?,?,?)",
                (dist_id, name, phone, email, area, comm)
            )
            res_map[dist_id].append(c.lastrowid)

    # Sales (80 transaksi per distributor, 4 bulan terakhir)
    today = datetime.now()
    for user_idx, _ in dist_users:
        dist_id = user_ids[user_idx]
        pids = prod_map[dist_id]
        rids = res_map[dist_id]
        for _ in range(80):
            days_ago  = random.randint(0, 120)
            sale_date = today - timedelta(days=days_ago)
            pid = random.choice(pids)
            rid = random.choice(rids)
            prod_idx = pids.index(pid)
            price = PRODUCTS_TEMPLATE[prod_idx][3]
            qty   = random.randint(3, 30)
            disc  = random.choice([0, 0, 0, 2, 5])
            total = qty * price * (1 - disc / 100)
            c.execute(
                "INSERT INTO sales (distributor_id,reseller_id,product_id,quantity,unit_price,discount_pct,total,sale_date) "
                "VALUES (?,?,?,?,?,?,?,?)",
                (dist_id, rid, pid, qty, price, disc, total,
                 sale_date.strftime('%Y-%m-%d %H:%M:%S'))
            )
            c.execute(
                "INSERT INTO stock_movements (product_id,type,quantity,note,moved_at) "
                "VALUES (?,?,?,?,?)",
                (pid, 'out', qty, 'Penjualan', sale_date.strftime('%Y-%m-%d %H:%M:%S'))
            )

    # Targets
    for month_offset in [0, 1]:
        if month_offset == 0:
            period = today.strftime('%Y-%m')
        else:
            first = today.replace(day=1)
            prev  = first - timedelta(days=1)
            period = prev.strftime('%Y-%m')
        for user_idx, _ in dist_users:
            dist_id = user_ids[user_idx]
            target  = random.randint(40, 80) * 1_000_000
            achieved = random.uniform(0.6, 1.15) * target
            c.execute(
                "INSERT INTO targets (distributor_id,reseller_id,period,target_amount,achieved) "
                "VALUES (?,NULL,?,?,?)",
                (dist_id, period, target, min(achieved, target * 1.2))
            )
            for rid in res_map[dist_id]:
                t = random.randint(8, 20) * 1_000_000
                a = random.uniform(0.5, 1.1) * t
                c.execute(
                    "INSERT INTO targets (distributor_id,reseller_id,period,target_amount,achieved) "
                    "VALUES (?,?,?,?,?)",
                    (dist_id, rid, period, t, min(a, t * 1.2))
                )

    conn.commit()
    conn.close()
    print("✅ Seeding selesai!\n")
    print("═" * 65)
    print(f"{'AKUN DEMO':^65}")
    print("═" * 65)
    print(f"{'ROLE':<16} {'EMAIL':<32} {'PASSWORD'}")
    print("─" * 65)
    for name, email, pw, role, company, *_ in USERS:
        lbl = {'super_admin':'Super Admin','admin_cabang':'Admin Cabang','user':'User'}.get(role, role)
        print(f"  {lbl:<14} {email:<32} {pw}")
    print("═" * 65)


if __name__ == '__main__':
    init_schema()
    seed()
