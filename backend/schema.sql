-- ============================================================
-- RICKY FINANCE DASHBOARD — SQLite Schema
-- ============================================================

-- Config (fxRate, lastUpdated, income)
CREATE TABLE IF NOT EXISTS config (
  key   TEXT PRIMARY KEY,
  value TEXT NOT NULL
);

-- Bank accounts
CREATE TABLE IF NOT EXISTS banks (
  nick      TEXT PRIMARY KEY,  -- e.g. "BCA 062"
  name      TEXT NOT NULL,
  cat       TEXT,
  type      TEXT,
  acct      TEXT,
  balance   REAL NOT NULL DEFAULT 0,
  updated   TEXT,
  notes     TEXT
);

-- Credit cards
CREATE TABLE IF NOT EXISTS credit_cards (
  name        TEXT PRIMARY KEY,  -- e.g. "CC CIMB"
  issuer      TEXT,
  limit_amt   REAL NOT NULL DEFAULT 0,
  outstanding REAL NOT NULL DEFAULT 0,
  due_date    TEXT,
  notes       TEXT
);

-- Loans (KPR, KTA)
CREATE TABLE IF NOT EXISTS loans (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  type        TEXT NOT NULL,   -- "KPR" | "KTA"
  lender      TEXT,
  remaining   REAL NOT NULL DEFAULT 0,
  monthly     REAL NOT NULL DEFAULT 0,
  rate        REAL DEFAULT 0,
  tenor       INTEGER DEFAULT 0,
  notes       TEXT
);

-- Investments
CREATE TABLE IF NOT EXISTS investments (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  platform      TEXT NOT NULL,
  ticker        TEXT,
  type          TEXT,          -- "Crypto" | "IDX Stocks" | "ETF (US Stock)"
  qty           REAL DEFAULT 0,
  avg_buy       REAL DEFAULT 0,
  currency      TEXT DEFAULT 'IDR',
  cost_basis    REAL DEFAULT 0,
  current_price REAL DEFAULT 0,
  platform_cash REAL DEFAULT 0,
  nbv_override  REAL,
  last_update   TEXT,
  notes         TEXT
);

-- Fixed assets
CREATE TABLE IF NOT EXISTS fixed_assets (
  id                TEXT PRIMARY KEY,  -- e.g. "fa1"
  name              TEXT NOT NULL,
  category          TEXT,
  purchase_date     TEXT NOT NULL,
  cost              REAL NOT NULL,
  useful_life_months INTEGER NOT NULL,
  transaction_ref   TEXT,
  notes             TEXT
);

-- Receivables (piutang)
CREATE TABLE IF NOT EXISTS receivables (
  id          TEXT PRIMARY KEY,  -- e.g. "rcv1"
  name        TEXT NOT NULL,
  amount      REAL NOT NULL,
  date        TEXT NOT NULL,
  due_date    TEXT,
  notes       TEXT,
  status      TEXT DEFAULT 'outstanding',  -- "outstanding" | "settled"
  settled_on  TEXT
);

-- Transactions (main table)
CREATE TABLE IF NOT EXISTS transactions (
  id        TEXT PRIMARY KEY,   -- e.g. "t71"
  date      TEXT NOT NULL,      -- "YYYY-MM-DD"
  type      TEXT NOT NULL,      -- "Out" | "In" | "Transfer" | "Accrual"
  category  TEXT NOT NULL,
  account   TEXT NOT NULL,
  amount    REAL NOT NULL,
  desc      TEXT,
  created_at TEXT DEFAULT (datetime('now','localtime'))
);

-- Budget per category
CREATE TABLE IF NOT EXISTS budgets (
  category  TEXT PRIMARY KEY,
  amount    REAL NOT NULL DEFAULT 0
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_trx_date     ON transactions(date);
CREATE INDEX IF NOT EXISTS idx_trx_type     ON transactions(type);
CREATE INDEX IF NOT EXISTS idx_trx_category ON transactions(category);
CREATE INDEX IF NOT EXISTS idx_trx_account  ON transactions(account);
