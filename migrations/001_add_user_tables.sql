-- Non-destructive migration to add user tables
-- Run once: sqlite3 storage/odds.db < migrations/001_add_user_tables.sql

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    external_id TEXT UNIQUE NOT NULL,
    email TEXT NOT NULL,
    name TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX IF NOT EXISTS idx_users_external_id ON users(external_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

CREATE TABLE IF NOT EXISTS user_bets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    external_user_id TEXT NOT NULL,
    game_id TEXT NOT NULL,
    market TEXT NOT NULL,
    selection TEXT NOT NULL,
    stake REAL NOT NULL,
    odds REAL NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    clv_cents REAL,
    beat_close BOOLEAN,
    is_settled BOOLEAN DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_user_bets_user_id ON user_bets(user_id);
CREATE INDEX IF NOT EXISTS idx_user_bets_external_user_id ON user_bets(external_user_id);
CREATE INDEX IF NOT EXISTS idx_user_bets_created_at ON user_bets(created_at);

CREATE TABLE IF NOT EXISTS subscriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    frequency TEXT DEFAULT 'weekly',
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_subscriptions_email ON subscriptions(email);
CREATE INDEX IF NOT EXISTS idx_subscriptions_active ON subscriptions(is_active);
