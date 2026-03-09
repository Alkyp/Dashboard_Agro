"""
database.py — Dashboard Agro
Semua koneksi DB, query helper, dan inisialisasi schema.
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'agro.db')
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), 'schema.sql')


# ── CONNECTION ────────────────────────────────────────────────────────────────

def get_connection():
    """Buka koneksi SQLite dengan row_factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ── QUERY HELPERS ─────────────────────────────────────────────────────────────

def query_all(sql: str, args: tuple = ()) -> list:
    """Jalankan SELECT, return list of Row."""
    conn = get_connection()
    try:
        rows = conn.execute(sql, args).fetchall()
        return rows
    finally:
        conn.close()


def query_one(sql: str, args: tuple = ()):
    """Jalankan SELECT, return satu Row atau None."""
    conn = get_connection()
    try:
        return conn.execute(sql, args).fetchone()
    finally:
        conn.close()


def execute(sql: str, args: tuple = ()) -> int:
    """Jalankan INSERT/UPDATE/DELETE, return lastrowid."""
    conn = get_connection()
    try:
        cur = conn.execute(sql, args)
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def execute_many(sql: str, rows: list) -> None:
    """Batch insert."""
    conn = get_connection()
    try:
        conn.executemany(sql, rows)
        conn.commit()
    finally:
        conn.close()


def scalar(sql: str, args: tuple = (), default=0):
    """Return nilai kolom pertama baris pertama, atau default."""
    row = query_one(sql, args)
    if row is None:
        return default
    val = row[0]
    return val if val is not None else default


# ── SCHEMA INIT ───────────────────────────────────────────────────────────────

def init_schema():
    """Buat tabel dari schema.sql jika belum ada."""
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        ddl = f.read()
    conn = get_connection()
    try:
        conn.executescript(ddl)
        conn.commit()
    finally:
        conn.close()


def is_seeded() -> bool:
    """Cek apakah data seed sudah ada."""
    return scalar("SELECT COUNT(*) FROM users") > 0


# ── STATS HELPERS ─────────────────────────────────────────────────────────────

def dist_month_revenue(dist_id: int, month_start: str) -> float:
    return scalar(
        "SELECT COALESCE(SUM(total),0) FROM sales "
        "WHERE distributor_id=? AND date(sale_date)>=date(?)",
        (dist_id, month_start)
    )


def dist_month_tx(dist_id: int, month_start: str) -> int:
    return scalar(
        "SELECT COUNT(*) FROM sales "
        "WHERE distributor_id=? AND date(sale_date)>=date(?)",
        (dist_id, month_start)
    )


def dist_reseller_count(dist_id: int) -> int:
    return scalar(
        "SELECT COUNT(*) FROM resellers WHERE distributor_id=? AND is_active=1",
        (dist_id,)
    )


def dist_product_count(dist_id: int) -> int:
    return scalar(
        "SELECT COUNT(*) FROM products WHERE distributor_id=? AND is_active=1",
        (dist_id,)
    )
