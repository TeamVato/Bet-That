-- Enhanced User Models Migration
-- This migration creates the comprehensive user, bet, edge, and transaction models
-- Run with: sqlite3 storage/odds.db < migrations/002_create_enhanced_user_models.sql

PRAGMA foreign_keys=ON;
PRAGMA journal_mode=WAL;

-- Drop existing simple user tables if they exist (will be recreated with enhanced schema)
DROP TABLE IF EXISTS user_bets;
DROP TABLE IF EXISTS users;

-- Create enhanced users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    external_id TEXT UNIQUE NOT NULL,

    -- Authentication fields
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT,
    email_verified BOOLEAN DEFAULT FALSE NOT NULL,
    email_verified_at DATETIME,

    -- Profile information
    name TEXT,
    first_name TEXT,
    last_name TEXT,
    timezone TEXT DEFAULT 'UTC' NOT NULL,
    phone TEXT,

    -- Account status and verification
    status TEXT DEFAULT 'pending_verification' NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    is_verified BOOLEAN DEFAULT FALSE NOT NULL,
    verification_level TEXT DEFAULT 'basic' NOT NULL,

    -- Risk management fields
    max_bet_size DECIMAL(12,2) DEFAULT 1000.00 NOT NULL,
    daily_bet_limit DECIMAL(12,2) DEFAULT 5000.00 NOT NULL,
    monthly_bet_limit DECIMAL(12,2) DEFAULT 50000.00 NOT NULL,
    risk_tolerance TEXT DEFAULT 'medium' NOT NULL,
    auto_kelly_sizing BOOLEAN DEFAULT FALSE NOT NULL,
    max_kelly_fraction REAL DEFAULT 0.25 NOT NULL,

    -- Preferences (JSON stored as TEXT)
    preferred_sports TEXT,
    notification_preferences TEXT,
    ui_preferences TEXT,

    -- Audit trail
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    last_login_at DATETIME,
    last_activity_at DATETIME,
    created_by TEXT,

    -- Soft delete
    deleted_at DATETIME,

    -- Constraints
    CHECK (max_bet_size > 0),
    CHECK (daily_bet_limit > 0),
    CHECK (monthly_bet_limit >= daily_bet_limit),
    CHECK (max_kelly_fraction > 0 AND max_kelly_fraction <= 1),
    CHECK (risk_tolerance IN ('low', 'medium', 'high')),
    CHECK (verification_level IN ('basic', 'enhanced', 'premium')),
    CHECK (status IN ('active', 'suspended', 'pending_verification', 'banned'))
);

-- Create indexes for users table
CREATE INDEX idx_users_external_id ON users(external_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_status_active ON users(status, is_active);
CREATE INDEX idx_users_last_activity ON users(last_activity_at);
CREATE INDEX idx_users_deleted ON users(deleted_at);

-- Create enhanced bets table
CREATE TABLE bets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- User relationship
    user_id INTEGER NOT NULL REFERENCES users(id),
    external_user_id TEXT NOT NULL, -- Backward compatibility

    -- Core betting information
    event_id TEXT NOT NULL REFERENCES events(event_id),
    edge_id INTEGER REFERENCES edges(edge_id),
    market_type TEXT NOT NULL,
    market_description TEXT NOT NULL,
    selection TEXT NOT NULL,
    line REAL,
    side TEXT,

    -- Financial data
    stake DECIMAL(12,2) NOT NULL,
    odds_american INTEGER NOT NULL,
    odds_decimal REAL NOT NULL,
    potential_return DECIMAL(12,2) NOT NULL,
    actual_return DECIMAL(12,2),
    net_profit DECIMAL(12,2),

    -- Status tracking
    status TEXT DEFAULT 'pending' NOT NULL,
    result TEXT,
    settled_at DATETIME,
    graded_at DATETIME,

    -- Platform integration
    sportsbook_id TEXT NOT NULL,
    sportsbook_name TEXT NOT NULL,
    external_bet_id TEXT,
    external_ticket_id TEXT,

    -- Edge relationship and analytics
    edge_percentage REAL,
    kelly_fraction_used REAL,
    expected_value DECIMAL(12,2),

    -- CLV tracking
    clv_cents REAL,
    beat_close BOOLEAN,
    closing_odds_american INTEGER,
    closing_odds_decimal REAL,

    -- Risk metadata
    risk_score REAL,
    confidence_level REAL,
    model_probability REAL,

    -- Additional metadata
    notes TEXT,
    tags TEXT, -- JSON array
    source TEXT DEFAULT 'manual' NOT NULL,

    -- Timestamps
    placed_at DATETIME,
    expires_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_by TEXT,

    -- Soft delete
    deleted_at DATETIME,

    -- Constraints
    CHECK (stake > 0),
    CHECK (odds_decimal > 0),
    CHECK (potential_return > 0),
    CHECK (odds_american != 0),
    CHECK (result IS NULL OR result IN ('win', 'loss', 'push', 'void')),
    CHECK (source IN ('manual', 'automated', 'copied')),
    CHECK (status IN ('pending', 'matched', 'settled', 'cancelled', 'voided')),
    UNIQUE (external_bet_id, sportsbook_id)
);

-- Create indexes for bets table
CREATE INDEX idx_bets_user_id ON bets(user_id);
CREATE INDEX idx_bets_external_user_id ON bets(external_user_id);
CREATE INDEX idx_bets_event_id ON bets(event_id);
CREATE INDEX idx_bets_edge_id ON bets(edge_id);
CREATE INDEX idx_bets_user_status ON bets(user_id, status);
CREATE INDEX idx_bets_event_market ON bets(event_id, market_type);
CREATE INDEX idx_bets_sportsbook_status ON bets(sportsbook_id, status);
CREATE INDEX idx_bets_placed_at ON bets(placed_at);
CREATE INDEX idx_bets_created_at ON bets(created_at);
CREATE INDEX idx_bets_deleted ON bets(deleted_at);
CREATE INDEX idx_bets_external_bet_id ON bets(external_bet_id);

-- Create enhanced edges table
CREATE TABLE edges (
    edge_id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Market identification
    sport_key TEXT NOT NULL,
    event_id TEXT NOT NULL REFERENCES events(event_id),
    market_type TEXT NOT NULL,
    market_description TEXT NOT NULL,
    player TEXT,
    position TEXT,

    -- Line information
    line REAL,
    side TEXT NOT NULL,

    -- Arbitrage opportunity data
    best_odds_american INTEGER NOT NULL,
    best_odds_decimal REAL NOT NULL,
    best_sportsbook TEXT NOT NULL,
    implied_probability REAL NOT NULL,
    fair_probability REAL NOT NULL,

    -- Profitability metrics
    edge_percentage REAL NOT NULL,
    expected_value_per_dollar REAL NOT NULL,
    kelly_fraction REAL NOT NULL,
    recommended_stake DECIMAL(12,2),
    max_stake DECIMAL(12,2),

    -- Model data
    model_probability REAL NOT NULL,
    model_confidence REAL,
    shrunk_probability REAL,
    strategy_tag TEXT NOT NULL,

    -- Temporal data
    discovered_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    expires_at DATETIME,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    last_odds_check DATETIME,

    -- Status and validation
    status TEXT DEFAULT 'active' NOT NULL,
    is_stale BOOLEAN DEFAULT FALSE NOT NULL,
    is_arbitrage BOOLEAN DEFAULT FALSE NOT NULL,
    validation_score REAL,

    -- Context data
    season INTEGER,
    week INTEGER,
    team TEXT,
    opponent_team TEXT,
    home_team TEXT,
    away_team TEXT,
    is_home BOOLEAN,

    -- Defense context
    defense_tier TEXT,
    defense_score REAL,
    opponent_defense_code TEXT,

    -- Market depth
    market_liquidity TEXT,
    bet_limit DECIMAL(12,2),
    overround REAL,

    -- Tracking metadata
    source TEXT,
    calculation_version TEXT,
    raw_data_hash TEXT,

    -- Audit fields
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_by TEXT,

    -- Soft delete
    deleted_at DATETIME,

    -- Constraints
    CHECK (edge_percentage >= -1.0 AND edge_percentage <= 5.0),
    CHECK (expected_value_per_dollar >= -1.0 AND expected_value_per_dollar <= 10.0),
    CHECK (kelly_fraction >= 0 AND kelly_fraction <= 1),
    CHECK (implied_probability >= 0 AND implied_probability <= 1),
    CHECK (fair_probability >= 0 AND fair_probability <= 1),
    CHECK (model_probability >= 0 AND model_probability <= 1),
    CHECK (best_odds_american != 0),
    CHECK (best_odds_decimal > 0),
    CHECK (side IN ('over', 'under', 'home', 'away', 'yes', 'no')),
    CHECK (defense_tier IS NULL OR defense_tier IN ('generous', 'stingy', 'neutral')),
    CHECK (status IN ('active', 'expired', 'stale', 'invalid')),
    UNIQUE (event_id, market_type, COALESCE(player, ''), side, COALESCE(line, 0), best_sportsbook)
);

-- Create indexes for edges table
CREATE INDEX idx_edges_sport_key ON edges(sport_key);
CREATE INDEX idx_edges_event_id ON edges(event_id);
CREATE INDEX idx_edges_market_type ON edges(market_type);
CREATE INDEX idx_edges_player ON edges(player);
CREATE INDEX idx_edges_best_sportsbook ON edges(best_sportsbook);
CREATE INDEX idx_edges_edge_percentage ON edges(edge_percentage DESC);
CREATE INDEX idx_edges_expected_value_per_dollar ON edges(expected_value_per_dollar DESC);
CREATE INDEX idx_edges_kelly_fraction ON edges(kelly_fraction DESC);
CREATE INDEX idx_edges_discovered_at ON edges(discovered_at);
CREATE INDEX idx_edges_expires_at ON edges(expires_at);
CREATE INDEX idx_edges_status ON edges(status);
CREATE INDEX idx_edges_is_stale ON edges(is_stale);
CREATE INDEX idx_edges_season_week ON edges(season, week);
CREATE INDEX idx_edges_strategy_tag ON edges(strategy_tag);
CREATE INDEX idx_edges_event_market ON edges(event_id, market_type);
CREATE INDEX idx_edges_player_market ON edges(player, market_type);
CREATE INDEX idx_edges_status_stale ON edges(status, is_stale);
CREATE INDEX idx_edges_deleted ON edges(deleted_at);

-- Create transactions table
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- User relationship
    user_id INTEGER NOT NULL REFERENCES users(id),

    -- Bet relationship (optional)
    bet_id INTEGER REFERENCES bets(id),

    -- Financial data
    amount DECIMAL(12,2) NOT NULL,
    currency TEXT DEFAULT 'USD' NOT NULL,
    transaction_type TEXT NOT NULL,
    status TEXT DEFAULT 'pending' NOT NULL,

    -- Platform/sportsbook tracking
    sportsbook_id TEXT,
    sportsbook_name TEXT,
    external_transaction_id TEXT UNIQUE,

    -- Transaction details
    description TEXT,
    reference TEXT,
    category TEXT,

    -- Financial reconciliation
    running_balance DECIMAL(12,2),
    fee_amount DECIMAL(12,2) DEFAULT 0.00 NOT NULL,
    net_amount DECIMAL(12,2) NOT NULL,

    -- Processing information
    processed_at DATETIME,
    processing_details TEXT, -- JSON
    failure_reason TEXT,
    retry_count INTEGER DEFAULT 0 NOT NULL,

    -- Audit trail
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_by TEXT,

    -- Constraints
    CHECK (amount != 0),
    CHECK (fee_amount >= 0),
    CHECK (retry_count >= 0),
    CHECK (currency IN ('USD', 'EUR', 'GBP', 'CAD')),
    CHECK (category IS NULL OR category IN ('betting', 'account', 'bonus', 'fee', 'adjustment')),
    CHECK (transaction_type IN ('deposit', 'withdrawal', 'bet_placed', 'bet_payout', 'bet_refund', 'bonus', 'fee')),
    CHECK (status IN ('pending', 'completed', 'failed', 'cancelled'))
);

-- Create indexes for transactions table
CREATE INDEX idx_transactions_user_id ON transactions(user_id);
CREATE INDEX idx_transactions_bet_id ON transactions(bet_id);
CREATE INDEX idx_transactions_user_type ON transactions(user_id, transaction_type);
CREATE INDEX idx_transactions_user_status ON transactions(user_id, status);
CREATE INDEX idx_transactions_sportsbook_id ON transactions(sportsbook_id);
CREATE INDEX idx_transactions_created_at ON transactions(created_at);
CREATE INDEX idx_transactions_processed_at ON transactions(processed_at);
CREATE INDEX idx_transactions_reference ON transactions(reference);
CREATE INDEX idx_transactions_external_transaction_id ON transactions(external_transaction_id);
CREATE INDEX idx_transactions_transaction_type ON transactions(transaction_type);
CREATE INDEX idx_transactions_status ON transactions(status);

-- Update events table to add missing fields for relationships
ALTER TABLE events ADD COLUMN status TEXT DEFAULT 'scheduled';
ALTER TABLE events ADD COLUMN home_score INTEGER;
ALTER TABLE events ADD COLUMN away_score INTEGER;
ALTER TABLE events ADD COLUMN completed_at DATETIME;
ALTER TABLE events ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE events ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP;

-- Add events indexes for better performance
CREATE INDEX IF NOT EXISTS idx_events_status ON events(status);

-- Create triggers for updated_at timestamps
CREATE TRIGGER IF NOT EXISTS update_users_timestamp
    AFTER UPDATE ON users
    BEGIN
        UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

CREATE TRIGGER IF NOT EXISTS update_bets_timestamp
    AFTER UPDATE ON bets
    BEGIN
        UPDATE bets SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

CREATE TRIGGER IF NOT EXISTS update_edges_timestamp
    AFTER UPDATE ON edges
    BEGIN
        UPDATE edges SET last_updated = CURRENT_TIMESTAMP WHERE edge_id = NEW.edge_id;
    END;

CREATE TRIGGER IF NOT EXISTS update_transactions_timestamp
    AFTER UPDATE ON transactions
    BEGIN
        UPDATE transactions SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

CREATE TRIGGER IF NOT EXISTS update_events_timestamp
    AFTER UPDATE ON events
    BEGIN
        UPDATE events SET updated_at = CURRENT_TIMESTAMP WHERE event_id = NEW.event_id;
    END;

-- Create a view for active edges with calculated fields
CREATE VIEW IF NOT EXISTS active_edges AS
SELECT
    e.*,
    ev.home_team as event_home_team,
    ev.away_team as event_away_team,
    ev.commence_time as event_commence_time,
    ev.season as event_season,
    ev.week as event_week
FROM edges e
JOIN events ev ON e.event_id = ev.event_id
WHERE e.status = 'active'
  AND e.is_stale = FALSE
  AND e.deleted_at IS NULL
  AND (e.expires_at IS NULL OR e.expires_at > CURRENT_TIMESTAMP);

-- Create a view for user bet statistics
CREATE VIEW IF NOT EXISTS user_bet_stats AS
SELECT
    u.id as user_id,
    u.email,
    COUNT(b.id) as total_bets,
    COUNT(CASE WHEN b.status = 'settled' THEN 1 END) as settled_bets,
    COUNT(CASE WHEN b.result = 'win' THEN 1 END) as winning_bets,
    COUNT(CASE WHEN b.result = 'loss' THEN 1 END) as losing_bets,
    COALESCE(SUM(CASE WHEN b.result = 'win' THEN b.net_profit ELSE 0 END), 0) as total_winnings,
    COALESCE(SUM(CASE WHEN b.result = 'loss' THEN b.net_profit ELSE 0 END), 0) as total_losses,
    COALESCE(SUM(b.net_profit), 0) as net_profit,
    COALESCE(SUM(b.stake), 0) as total_staked,
    COALESCE(AVG(CASE WHEN b.beat_close IS NOT NULL THEN b.clv_cents END), 0) as avg_clv_cents
FROM users u
LEFT JOIN bets b ON u.id = b.user_id AND b.deleted_at IS NULL
WHERE u.deleted_at IS NULL
GROUP BY u.id, u.email;

-- Analyze tables for better query performance
ANALYZE;
