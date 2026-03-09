"""
app.py — Dashboard Agro
Entry point utama Flask. Routes, auth, API endpoints.
"""
import json
from datetime import datetime, timedelta
from functools import wraps

from flask import (Flask, render_template, request, redirect, url_for,
                   session, flash, jsonify)
from werkzeug.security import generate_password_hash, check_password_hash

import database as db
from seed import seed

# ── App Init ──────────────────────────────────────────────────────────────────

app = Flask(__name__)
app.secret_key = 'agrodashboard-secret-2026-!xK9#mL'

# ── Template Filters ──────────────────────────────────────────────────────────

@app.template_filter('rupiah')
def rupiah_filter(value):
    try:
        return 'Rp {:,.0f}'.format(float(value)).replace(',', '.')
    except Exception:
        return 'Rp 0'

@app.template_filter('tojson')
def tojson_filter(value):
    return json.dumps(value)

# ── Auth Decorators ───────────────────────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Silakan masuk terlebih dahulu.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login'))
            if session.get('role') not in roles:
                flash('Akses ditolak. Role tidak sesuai.', 'error')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated
    return decorator


# ── Helpers ───────────────────────────────────────────────────────────────────

def current_month_start():
    now = datetime.now()
    return now.replace(day=1, hour=0, minute=0, second=0).strftime('%Y-%m-%d')


def set_session(user):
    session['user_id']   = user['id']
    session['user_name'] = user['name']
    session['role']      = user['role']
    session['company']   = user['company'] or ''


# ── Auth Routes ───────────────────────────────────────────────────────────────

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        user = db.query_one("SELECT * FROM users WHERE lower(email)=? AND is_active=1", (email,))
        if user and check_password_hash(user['password'], password):
            set_session(user)
            return redirect(url_for('dashboard'))
        flash('Email atau password salah.', 'error')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# ── Dashboard ─────────────────────────────────────────────────────────────────

@app.route('/dashboard')
@login_required
def dashboard():
    uid   = session['user_id']
    role  = session['role']
    now   = datetime.now()
    ms    = current_month_start()

    if role == 'admin':
        distributors = db.query_all("SELECT * FROM users WHERE role='distributor' AND is_active=1")
        summary = []
        for d in distributors:
            rev = db.dist_month_revenue(d['id'], ms)
            tx  = db.dist_month_tx(d['id'], ms)
            rc  = db.dist_reseller_count(d['id'])
            pc  = db.dist_product_count(d['id'])
            summary.append({'dist': d, 'revenue': rev, 'transactions': tx,
                            'resellers': rc, 'products': pc})
        total_rev = sum(s['revenue'] for s in summary)
        total_tx  = sum(s['transactions'] for s in summary)
        return render_template('dashboard_admin.html',
                               summary=summary, total_rev=total_rev,
                               total_tx=total_tx, now=now)
    else:
        # Distributor
        month_rev    = db.dist_month_revenue(uid, ms)
        month_tx     = db.dist_month_tx(uid, ms)
        reseller_cnt = db.dist_reseller_count(uid)
        commission   = month_rev * 0.05

        # Top resellers this month
        top_resellers = db.query_all("""
            SELECT r.name, COALESCE(SUM(s.total),0) AS total_sales
            FROM resellers r
            LEFT JOIN sales s ON s.reseller_id = r.id
                AND date(s.sale_date) >= date(?)
            WHERE r.distributor_id = ?
            GROUP BY r.id ORDER BY total_sales DESC LIMIT 5
        """, (ms, uid))

        # Stock with category icon
        stock = db.query_all("""
            SELECT p.*, c.name AS category, c.icon
            FROM products p
            LEFT JOIN categories c ON c.id = p.category_id
            WHERE p.distributor_id = ? AND p.is_active = 1
            ORDER BY p.name
        """, (uid,))

        # 6-month chart data
        chart_data = []
        for i in range(5, -1, -1):
            m_start = (now.replace(day=1) - timedelta(days=i * 30)).replace(day=1)
            m_end   = (m_start.replace(day=28) + timedelta(days=4)).replace(day=1)
            rev = db.scalar(
                "SELECT COALESCE(SUM(total),0) FROM sales "
                "WHERE distributor_id=? AND date(sale_date)>=date(?) AND date(sale_date)<date(?)",
                (uid, m_start.strftime('%Y-%m-%d'), m_end.strftime('%Y-%m-%d'))
            )
            chart_data.append({'label': m_start.strftime('%b'), 'value': rev})

        return render_template('dashboard.html',
                               month_rev=month_rev, month_tx=month_tx,
                               reseller_cnt=reseller_cnt, commission=commission,
                               top_resellers=top_resellers, stock=stock,
                               chart_data=chart_data, now=now)


# ── Sales ─────────────────────────────────────────────────────────────────────

@app.route('/sales')
@login_required
def sales():
    uid          = session['user_id']
    role         = session['role']
    page         = max(1, int(request.args.get('page', 1)))
    per_page     = 20
    offset       = (page - 1) * per_page
    dist_filter  = request.args.get('dist', '').strip()

    if role == 'distributor':
        fid = uid
    elif dist_filter:
        fid = int(dist_filter)
    else:
        fid = None

    if fid:
        total_rows = db.scalar(
            "SELECT COUNT(*) FROM sales WHERE distributor_id=?", (fid,))
        rows = db.query_all("""
            SELECT s.*, p.name AS product_name, r.name AS reseller_name, u.company AS dist_name
            FROM sales s
            JOIN products p ON p.id = s.product_id
            LEFT JOIN resellers r ON r.id = s.reseller_id
            JOIN users u ON u.id = s.distributor_id
            WHERE s.distributor_id = ?
            ORDER BY s.sale_date DESC LIMIT ? OFFSET ?
        """, (fid, per_page, offset))
    else:
        total_rows = db.scalar("SELECT COUNT(*) FROM sales")
        rows = db.query_all("""
            SELECT s.*, p.name AS product_name, r.name AS reseller_name, u.company AS dist_name
            FROM sales s
            JOIN products p ON p.id = s.product_id
            LEFT JOIN resellers r ON r.id = s.reseller_id
            JOIN users u ON u.id = s.distributor_id
            ORDER BY s.sale_date DESC LIMIT ? OFFSET ?
        """, (per_page, offset))

    distributors  = db.query_all("SELECT id,company FROM users WHERE role='distributor' AND is_active=1") if role == 'admin' else []
    total_pages   = max(1, (total_rows + per_page - 1) // per_page)

    return render_template('sales.html', rows=rows, page=page,
                           total_pages=total_pages,
                           distributors=distributors,
                           dist_filter=dist_filter)


@app.route('/sales/add', methods=['GET', 'POST'])
@login_required
def add_sale():
    uid  = session['user_id']
    role = session['role']

    if request.method == 'POST':
        dist_id    = uid if role == 'distributor' else int(request.form['distributor_id'])
        product_id = int(request.form['product_id'])
        quantity   = int(request.form['quantity'])
        unit_price = float(request.form['unit_price'])
        disc_pct   = float(request.form.get('discount_pct', 0) or 0)
        total      = float(request.form['total'])
        notes      = request.form.get('notes', '')
        sale_date  = request.form.get('sale_date') or datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        reseller_id = request.form.get('reseller_id') or None

        sale_id = db.execute(
            "INSERT INTO sales (distributor_id,reseller_id,product_id,quantity,unit_price,discount_pct,total,notes,sale_date) "
            "VALUES (?,?,?,?,?,?,?,?,?)",
            (dist_id, reseller_id, product_id, quantity, unit_price, disc_pct, total, notes, sale_date)
        )
        # Reduce stock
        db.execute("UPDATE products SET stock=MAX(stock-?,0), updated_at=datetime('now','localtime') WHERE id=?",
                   (quantity, product_id))
        # Log stock movement
        db.execute("INSERT INTO stock_movements (product_id,type,quantity,note) VALUES (?,?,?,?)",
                   (product_id, 'out', quantity, f'Sale #{sale_id}'))

        flash('Penjualan berhasil disimpan!', 'success')
        return redirect(url_for('sales'))

    # GET
    if role == 'distributor':
        products  = db.query_all("SELECT id,name,price,stock,unit FROM products WHERE distributor_id=? AND is_active=1", (uid,))
        resellers = db.query_all("SELECT id,name,area FROM resellers WHERE distributor_id=? AND is_active=1", (uid,))
        products_json = json.dumps([dict(p) for p in products])
        distributors  = []
    else:
        products  = []
        resellers = []
        products_json = '[]'
        distributors  = db.query_all("SELECT id,company FROM users WHERE role='distributor' AND is_active=1")

    return render_template('add_sale.html',
                           products=products, resellers=resellers,
                           products_json=products_json,
                           distributors=distributors)


# ── Products ──────────────────────────────────────────────────────────────────

@app.route('/products')
@login_required
def products():
    uid         = session['user_id']
    role        = session['role']
    dist_filter = request.args.get('dist', '').strip()

    if role == 'distributor':
        rows = db.query_all("""
            SELECT p.*, c.name AS category, c.icon, u.company
            FROM products p
            LEFT JOIN categories c ON c.id = p.category_id
            JOIN users u ON u.id = p.distributor_id
            WHERE p.distributor_id = ? AND p.is_active = 1
            ORDER BY c.name, p.name
        """, (uid,))
    elif dist_filter:
        rows = db.query_all("""
            SELECT p.*, c.name AS category, c.icon, u.company
            FROM products p
            LEFT JOIN categories c ON c.id = p.category_id
            JOIN users u ON u.id = p.distributor_id
            WHERE p.distributor_id = ? AND p.is_active = 1
            ORDER BY c.name, p.name
        """, (dist_filter,))
    else:
        rows = db.query_all("""
            SELECT p.*, c.name AS category, c.icon, u.company
            FROM products p
            LEFT JOIN categories c ON c.id = p.category_id
            JOIN users u ON u.id = p.distributor_id
            WHERE p.is_active = 1
            ORDER BY u.company, c.name, p.name
        """)

    distributors = db.query_all("SELECT id,company FROM users WHERE role='distributor' AND is_active=1") if role == 'admin' else []
    return render_template('products.html', rows=rows, distributors=distributors, dist_filter=dist_filter)


@app.route('/products/add', methods=['GET', 'POST'])
@login_required
def add_product():
    if request.method == 'POST':
        dist_id = session['user_id'] if session['role'] == 'distributor' else int(request.form['distributor_id'])
        db.execute(
            "INSERT INTO products (distributor_id,category_id,name,sku,price,cost_price,stock,stock_min,unit,description) "
            "VALUES (?,?,?,?,?,?,?,?,?,?)",
            (dist_id,
             request.form.get('category_id') or None,
             request.form['name'],
             request.form.get('sku', ''),
             float(request.form['price']),
             float(request.form.get('cost_price', 0) or 0),
             int(request.form['stock']),
             int(request.form.get('stock_min', 50) or 50),
             request.form.get('unit', 'pcs'),
             request.form.get('description', ''))
        )
        flash('Produk berhasil ditambahkan!', 'success')
        return redirect(url_for('products'))

    categories   = db.query_all("SELECT * FROM categories ORDER BY name")
    distributors = db.query_all("SELECT id,company FROM users WHERE role='distributor' AND is_active=1") if session['role'] == 'admin' else []
    return render_template('product_form.html', prod=None, categories=categories, distributors=distributors)


@app.route('/products/edit/<int:pid>', methods=['GET', 'POST'])
@login_required
def edit_product(pid):
    prod = db.query_one("SELECT * FROM products WHERE id=?", (pid,))
    if not prod:
        flash('Produk tidak ditemukan.', 'error')
        return redirect(url_for('products'))
    if session['role'] == 'distributor' and prod['distributor_id'] != session['user_id']:
        flash('Akses ditolak.', 'error')
        return redirect(url_for('products'))

    if request.method == 'POST':
        db.execute(
            "UPDATE products SET category_id=?,name=?,sku=?,price=?,cost_price=?,"
            "stock=?,stock_min=?,unit=?,description=?,updated_at=datetime('now','localtime') WHERE id=?",
            (request.form.get('category_id') or None,
             request.form['name'],
             request.form.get('sku', ''),
             float(request.form['price']),
             float(request.form.get('cost_price', 0) or 0),
             int(request.form['stock']),
             int(request.form.get('stock_min', 50) or 50),
             request.form.get('unit', 'pcs'),
             request.form.get('description', ''),
             pid)
        )
        flash('Produk berhasil diperbarui!', 'success')
        return redirect(url_for('products'))

    categories   = db.query_all("SELECT * FROM categories ORDER BY name")
    distributors = []
    return render_template('product_form.html', prod=prod, categories=categories, distributors=distributors)


@app.route('/products/delete/<int:pid>', methods=['POST'])
@login_required
def delete_product(pid):
    prod = db.query_one("SELECT * FROM products WHERE id=?", (pid,))
    if not prod:
        flash('Produk tidak ditemukan.', 'error')
        return redirect(url_for('products'))
    if session['role'] == 'distributor' and prod['distributor_id'] != session['user_id']:
        flash('Akses ditolak.', 'error')
        return redirect(url_for('products'))
    # Cek apakah produk sudah dipakai di sales
    sales_count = db.scalar("SELECT COUNT(*) FROM sales WHERE product_id=?", (pid,))
    if sales_count > 0:
        # Soft delete — jangan hapus riwayat transaksi
        db.execute("UPDATE products SET is_active=0, updated_at=datetime('now','localtime') WHERE id=?", (pid,))
        flash(f'Produk "{prod["name"]}" dinonaktifkan (ada {sales_count} transaksi terkait).', 'success')
    else:
        db.execute("DELETE FROM products WHERE id=?", (pid,))
        flash(f'Produk "{prod["name"]}" berhasil dihapus.', 'success')
    return redirect(url_for('products'))


# ── Resellers ─────────────────────────────────────────────────────────────────

@app.route('/resellers')
@login_required
def resellers():
    uid  = session['user_id']
    role = session['role']
    if role == 'distributor':
        rows = db.query_all("""
            SELECT r.*, COALESCE(SUM(s.total),0) AS total_sales
            FROM resellers r
            LEFT JOIN sales s ON s.reseller_id = r.id
            WHERE r.distributor_id = ? AND r.is_active = 1
            GROUP BY r.id ORDER BY total_sales DESC
        """, (uid,))
    else:
        rows = db.query_all("""
            SELECT r.*, u.company, COALESCE(SUM(s.total),0) AS total_sales
            FROM resellers r
            JOIN users u ON u.id = r.distributor_id
            LEFT JOIN sales s ON s.reseller_id = r.id
            WHERE r.is_active = 1
            GROUP BY r.id ORDER BY total_sales DESC
        """)
    return render_template('resellers.html', rows=rows)


@app.route('/resellers/add', methods=['GET', 'POST'])
@login_required
def add_reseller():
    if request.method == 'POST':
        dist_id = session['user_id'] if session['role'] == 'distributor' else int(request.form['distributor_id'])
        db.execute(
            "INSERT INTO resellers (distributor_id,name,phone,email,address,area,commission_pct) VALUES (?,?,?,?,?,?,?)",
            (dist_id,
             request.form['name'],
             request.form.get('phone', ''),
             request.form.get('email', ''),
             request.form.get('address', ''),
             request.form.get('area', ''),
             float(request.form.get('commission_pct', 5) or 5))
        )
        flash('Reseller berhasil ditambahkan!', 'success')
        return redirect(url_for('resellers'))

    distributors = db.query_all("SELECT id,company FROM users WHERE role='distributor' AND is_active=1") if session['role'] == 'admin' else []
    return render_template('add_reseller.html', distributors=distributors)


@app.route('/resellers/edit/<int:rid>', methods=['GET', 'POST'])
@login_required
def edit_reseller(rid):
    r = db.query_one("SELECT * FROM resellers WHERE id=?", (rid,))
    if not r:
        flash('Reseller tidak ditemukan.', 'error')
        return redirect(url_for('resellers'))
    if session['role'] == 'distributor' and r['distributor_id'] != session['user_id']:
        flash('Akses ditolak.', 'error')
        return redirect(url_for('resellers'))

    if request.method == 'POST':
        db.execute(
            "UPDATE resellers SET name=?,phone=?,email=?,address=?,area=?,commission_pct=? WHERE id=?",
            (request.form['name'],
             request.form.get('phone', ''),
             request.form.get('email', ''),
             request.form.get('address', ''),
             request.form.get('area', ''),
             float(request.form.get('commission_pct', 5) or 5),
             rid)
        )
        flash('Reseller berhasil diperbarui!', 'success')
        return redirect(url_for('resellers'))

    return render_template('edit_reseller.html', r=r)


@app.route('/resellers/delete/<int:rid>', methods=['POST'])
@login_required
def delete_reseller(rid):
    r = db.query_one("SELECT * FROM resellers WHERE id=?", (rid,))
    if not r:
        flash('Reseller tidak ditemukan.', 'error')
        return redirect(url_for('resellers'))
    if session['role'] == 'distributor' and r['distributor_id'] != session['user_id']:
        flash('Akses ditolak.', 'error')
        return redirect(url_for('resellers'))
    # Soft delete
    db.execute("UPDATE resellers SET is_active=0 WHERE id=?", (rid,))
    flash(f'Reseller "{r["name"]}" berhasil dihapus.', 'success')
    return redirect(url_for('resellers'))


@app.route('/sales/edit/<int:sid>', methods=['GET', 'POST'])
@login_required
def edit_sale(sid):
    sale = db.query_one("SELECT * FROM sales WHERE id=?", (sid,))
    if not sale:
        flash('Transaksi tidak ditemukan.', 'error')
        return redirect(url_for('sales'))
    if session['role'] == 'distributor' and sale['distributor_id'] != session['user_id']:
        flash('Akses ditolak.', 'error')
        return redirect(url_for('sales'))

    if request.method == 'POST':
        old_qty    = sale['quantity']
        new_qty    = int(request.form['quantity'])
        unit_price = float(request.form['unit_price'])
        disc_pct   = float(request.form.get('discount_pct', 0) or 0)
        total      = float(request.form['total'])
        notes      = request.form.get('notes', '')
        sale_date  = request.form.get('sale_date') or sale['sale_date']
        reseller_id = request.form.get('reseller_id') or None

        db.execute(
            "UPDATE sales SET reseller_id=?,quantity=?,unit_price=?,discount_pct=?,total=?,notes=?,sale_date=? WHERE id=?",
            (reseller_id, new_qty, unit_price, disc_pct, total, notes, sale_date, sid)
        )
        # Adjust stock: kembalikan stok lama, kurangi stok baru
        qty_diff = new_qty - old_qty
        if qty_diff != 0:
            db.execute("UPDATE products SET stock=MAX(stock-?,0), updated_at=datetime('now','localtime') WHERE id=?",
                       (qty_diff, sale['product_id']))
        flash('Transaksi berhasil diperbarui!', 'success')
        return redirect(url_for('sales'))

    uid  = session['user_id']
    role = session['role']
    dist_id = sale['distributor_id']
    products  = db.query_all("SELECT id,name,price,stock,unit FROM products WHERE distributor_id=? AND is_active=1", (dist_id,))
    resellers = db.query_all("SELECT id,name,area FROM resellers WHERE distributor_id=? AND is_active=1", (dist_id,))
    products_json = json.dumps([dict(p) for p in products])
    # Get product name for display
    prod = db.query_one("SELECT name FROM products WHERE id=?", (sale['product_id'],))
    sale_dict = dict(sale)
    sale_dict['product_name'] = prod['name'] if prod else '—'
    return render_template('edit_sale.html', sale=sale_dict, products=products,
                           resellers=resellers, products_json=products_json)


@app.route('/sales/delete/<int:sid>', methods=['POST'])
@login_required
def delete_sale(sid):
    sale = db.query_one("SELECT * FROM sales WHERE id=?", (sid,))
    if not sale:
        flash('Transaksi tidak ditemukan.', 'error')
        return redirect(url_for('sales'))
    if session['role'] == 'distributor' and sale['distributor_id'] != session['user_id']:
        flash('Akses ditolak.', 'error')
        return redirect(url_for('sales'))
    # Kembalikan stok
    db.execute("UPDATE products SET stock=stock+?, updated_at=datetime('now','localtime') WHERE id=?",
               (sale['quantity'], sale['product_id']))
    db.execute("DELETE FROM sales WHERE id=?", (sid,))
    flash('Transaksi berhasil dihapus dan stok dikembalikan.', 'success')
    return redirect(url_for('sales'))


# ── Targets ───────────────────────────────────────────────────────────────────

@app.route('/targets')
@login_required
def targets():
    uid  = session['user_id']
    role = session['role']
    if role == 'distributor':
        rows = db.query_all("""
            SELECT t.*, r.name AS reseller_name
            FROM targets t
            LEFT JOIN resellers r ON r.id = t.reseller_id
            WHERE t.distributor_id = ? ORDER BY t.period DESC, t.reseller_id NULLS FIRST
        """, (uid,))
    else:
        rows = db.query_all("""
            SELECT t.*, r.name AS reseller_name, u.company AS dist_name
            FROM targets t
            LEFT JOIN resellers r ON r.id = t.reseller_id
            JOIN users u ON u.id = t.distributor_id
            ORDER BY t.period DESC, u.company
        """)
    return render_template('targets.html', rows=rows)


# ── Leaderboard ───────────────────────────────────────────────────────────────

@app.route('/leaderboard')
@login_required
def leaderboard():
    uid  = session['user_id']
    role = session['role']
    ms   = current_month_start()

    if role == 'distributor':
        rows = db.query_all("""
            SELECT r.name, r.area AS sub, COALESCE(SUM(s.total),0) AS total_sales, COUNT(s.id) AS tx_count
            FROM resellers r
            LEFT JOIN sales s ON s.reseller_id = r.id AND date(s.sale_date) >= date(?)
            WHERE r.distributor_id = ? AND r.is_active = 1
            GROUP BY r.id ORDER BY total_sales DESC
        """, (ms, uid))
    else:
        rows = db.query_all("""
            SELECT u.company AS name, u.name AS sub,
                   COALESCE(SUM(s.total),0) AS total_sales, COUNT(s.id) AS tx_count
            FROM users u
            LEFT JOIN sales s ON s.distributor_id = u.id AND date(s.sale_date) >= date(?)
            WHERE u.role = 'distributor' AND u.is_active = 1
            GROUP BY u.id ORDER BY total_sales DESC
        """, (ms,))

    return render_template('leaderboard.html', rows=rows)


# ── Users ─────────────────────────────────────────────────────────────────────

@app.route('/users')
@role_required('admin')
def users():
    rows = db.query_all("SELECT * FROM users ORDER BY role, name")
    return render_template('users.html', rows=rows)


@app.route('/users/add', methods=['GET', 'POST'])
@role_required('admin')
def add_user():
    if request.method == 'POST':
        try:
            db.execute(
                "INSERT INTO users (name,email,password,role,company,phone,address,avatar_char,is_active) "
                "VALUES (?,?,?,?,?,?,?,?,1)",
                (request.form['name'],
                 request.form['email'].strip().lower(),
                 generate_password_hash(request.form['password']),
                 request.form['role'],
                 request.form.get('company', ''),
                 request.form.get('phone', ''),
                 request.form.get('address', ''),
                 request.form['name'][0].upper())
            )
            flash('Pengguna berhasil ditambahkan!', 'success')
            return redirect(url_for('users'))
        except Exception as e:
            flash(f'Gagal menambahkan pengguna: {e}', 'error')
    return render_template('add_user.html')


@app.route('/users/edit/<int:uid_target>', methods=['GET', 'POST'])
@role_required('admin')
def edit_user(uid_target):
    user = db.query_one("SELECT * FROM users WHERE id=?", (uid_target,))
    if not user:
        flash('Pengguna tidak ditemukan.', 'error')
        return redirect(url_for('users'))

    if request.method == 'POST':
        name    = request.form.get('name', '').strip()
        company = request.form.get('company', '').strip()
        phone   = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        role    = request.form.get('role', user['role'])
        new_pw  = request.form.get('new_password', '').strip()

        if new_pw:
            db.execute(
                "UPDATE users SET name=?,company=?,phone=?,address=?,role=?,password=?,avatar_char=?,updated_at=datetime('now','localtime') WHERE id=?",
                (name, company, phone, address, role, generate_password_hash(new_pw), name[0].upper(), uid_target)
            )
        else:
            db.execute(
                "UPDATE users SET name=?,company=?,phone=?,address=?,role=?,avatar_char=?,updated_at=datetime('now','localtime') WHERE id=?",
                (name, company, phone, address, role, name[0].upper(), uid_target)
            )
        flash('Pengguna berhasil diperbarui!', 'success')
        return redirect(url_for('users'))

    return render_template('edit_user.html', user=user)


@app.route('/users/delete/<int:uid_target>', methods=['POST'])
@role_required('admin')
def delete_user(uid_target):
    if uid_target == session['user_id']:
        flash('Tidak dapat menghapus akun sendiri.', 'error')
        return redirect(url_for('users'))
    user = db.query_one("SELECT * FROM users WHERE id=?", (uid_target,))
    if not user:
        flash('Pengguna tidak ditemukan.', 'error')
        return redirect(url_for('users'))
    # Soft delete
    db.execute("UPDATE users SET is_active=0, updated_at=datetime('now','localtime') WHERE id=?", (uid_target,))
    flash(f'Pengguna "{user["name"]}" berhasil dihapus.', 'success')
    return redirect(url_for('users'))


# ── Profile ───────────────────────────────────────────────────────────────────

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    uid = session['user_id']
    if request.method == 'POST':
        name    = request.form.get('name', '').strip()
        company = request.form.get('company', '').strip()
        phone   = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        new_pw  = request.form.get('new_password', '').strip()

        if new_pw:
            db.execute(
                "UPDATE users SET name=?,company=?,phone=?,address=?,password=?,avatar_char=?,updated_at=datetime('now','localtime') WHERE id=?",
                (name, company, phone, address, generate_password_hash(new_pw), name[0].upper(), uid)
            )
        else:
            db.execute(
                "UPDATE users SET name=?,company=?,phone=?,address=?,avatar_char=?,updated_at=datetime('now','localtime') WHERE id=?",
                (name, company, phone, address, name[0].upper(), uid)
            )
        session['user_name'] = name
        session['company']   = company
        flash('Profil berhasil diperbarui!', 'success')

    user = db.query_one("SELECT * FROM users WHERE id=?", (uid,))
    return render_template('profile.html', user=user)


# ── API Endpoints ─────────────────────────────────────────────────────────────

@app.route('/api/products/<int:dist_id>')
@login_required
def api_products(dist_id):
    prods = db.query_all(
        "SELECT id, name, price, stock, unit FROM products WHERE distributor_id=? AND is_active=1",
        (dist_id,)
    )
    return jsonify([dict(p) for p in prods])


@app.route('/api/resellers/<int:dist_id>')
@login_required
def api_resellers(dist_id):
    rs = db.query_all(
        "SELECT id, name, area FROM resellers WHERE distributor_id=? AND is_active=1",
        (dist_id,)
    )
    return jsonify([dict(r) for r in rs])


# ── Startup ───────────────────────────────────────────────────────────────────

def startup():
    db.init_schema()
    if not db.is_seeded():
        print("🌱 Database kosong, menjalankan seed data...")
        seed()

if __name__ == '__main__':
    startup()
    app.run(debug=True, port=5000)
