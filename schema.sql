-- ============================================================
-- Dashboard Agro — Database Schema
-- SQLite
-- ============================================================

PRAGMA foreign_keys = ON;

-- ── USERS ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    email       TEXT    NOT NULL UNIQUE,
    password    TEXT    NOT NULL,
    role        TEXT    NOT NULL DEFAULT 'distributor'
                        CHECK(role IN ('admin','distributor')),
    company     TEXT,
    phone       TEXT,
    address     TEXT,
    avatar_char TEXT,
    is_active   INTEGER NOT NULL DEFAULT 1,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
    updated_at  TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
);

-- ── CATEGORIES ───────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS categories (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    icon TEXT DEFAULT '🌿'
);

-- ── PRODUCTS ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS products (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    distributor_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category_id    INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    name           TEXT    NOT NULL,
    sku            TEXT,
    description    TEXT,
    price          REAL    NOT NULL DEFAULT 0,
    cost_price     REAL    DEFAULT 0,
    stock          INTEGER NOT NULL DEFAULT 0,
    stock_min      INTEGER NOT NULL DEFAULT 50,
    unit           TEXT    DEFAULT 'pcs',
    is_active      INTEGER NOT NULL DEFAULT 1,
    created_at     TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
    updated_at     TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
);

-- ── RESELLERS ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS resellers (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    distributor_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name           TEXT    NOT NULL,
    phone          TEXT,
    email          TEXT,
    address        TEXT,
    area           TEXT,
    commission_pct REAL    NOT NULL DEFAULT 5.0,
    is_active      INTEGER NOT NULL DEFAULT 1,
    joined_at      TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
);

-- ── SALES ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS sales (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    distributor_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    reseller_id    INTEGER REFERENCES resellers(id) ON DELETE SET NULL,
    product_id     INTEGER NOT NULL REFERENCES products(id) ON DELETE RESTRICT,
    quantity       INTEGER NOT NULL CHECK(quantity > 0),
    unit_price     REAL    NOT NULL CHECK(unit_price >= 0),
    discount_pct   REAL    NOT NULL DEFAULT 0,
    total          REAL    NOT NULL,
    notes          TEXT,
    sale_date      TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
);

-- ── TARGETS ──────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS targets (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    distributor_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    reseller_id    INTEGER REFERENCES resellers(id) ON DELETE CASCADE,
    period         TEXT    NOT NULL,          -- format: YYYY-MM
    target_amount  REAL    NOT NULL DEFAULT 0,
    achieved       REAL    NOT NULL DEFAULT 0,
    created_at     TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
);

-- ── STOCK MOVEMENTS ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS stock_movements (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id  INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    type        TEXT    NOT NULL CHECK(type IN ('in','out','adjustment')),
    quantity    INTEGER NOT NULL,
    note        TEXT,
    moved_at    TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
);

-- ── INDEXES ──────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_products_dist    ON products(distributor_id);
CREATE INDEX IF NOT EXISTS idx_resellers_dist   ON resellers(distributor_id);
CREATE INDEX IF NOT EXISTS idx_sales_dist       ON sales(distributor_id);
CREATE INDEX IF NOT EXISTS idx_sales_date       ON sales(sale_date);
CREATE INDEX IF NOT EXISTS idx_sales_reseller   ON sales(reseller_id);
CREATE INDEX IF NOT EXISTS idx_targets_dist     ON targets(distributor_id);
CREATE INDEX IF NOT EXISTS idx_stock_product    ON stock_movements(product_id);
