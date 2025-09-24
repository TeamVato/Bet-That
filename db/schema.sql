PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS books (
    book_key TEXT PRIMARY KEY,
    title TEXT
);

CREATE TABLE IF NOT EXISTS events (
    event_id TEXT PRIMARY KEY,
    sport_key TEXT,
    commence_time TEXT,
    home_team TEXT,
    away_team TEXT,
    season INTEGER,
    week INTEGER,
    venue TEXT,
    region TEXT
);

CREATE TABLE IF NOT EXISTS markets (
    market_key TEXT PRIMARY KEY,
    description TEXT
);

CREATE TABLE IF NOT EXISTS odds_snapshots (
    snapshot_id INTEGER PRIMARY KEY AUTOINCREMENT,
    fetched_at TEXT,
    sport_key TEXT,
    event_id TEXT,
    market_key TEXT,
    bookmaker_key TEXT,
    line FLOAT,
    price INT,
    outcome TEXT,
    points FLOAT,
    iso_time TEXT,
    odds_raw_json TEXT,
    UNIQUE (fetched_at, event_id, market_key, bookmaker_key, outcome, points)
);
CREATE INDEX IF NOT EXISTS idx_odds_snapshots_event ON odds_snapshots(event_id);
CREATE INDEX IF NOT EXISTS idx_odds_snapshots_market ON odds_snapshots(market_key);
CREATE INDEX IF NOT EXISTS idx_odds_snapshots_book ON odds_snapshots(bookmaker_key);

CREATE TABLE IF NOT EXISTS current_best_lines (
    event_id TEXT,
    market_key TEXT,
    outcome TEXT,
    best_book TEXT,
    best_price INT,
    best_points FLOAT,
    updated_at TEXT,
    PRIMARY KEY (event_id, market_key, outcome)
);

CREATE TABLE IF NOT EXISTS qb_props_odds (
    snapshot_id INTEGER PRIMARY KEY AUTOINCREMENT,
    fetched_at TEXT,
    event_id TEXT,
    player TEXT,
    market TEXT,
    line FLOAT,
    over_odds INT,
    under_odds INT,
    book TEXT,
    season INT,
    def_team TEXT
);
CREATE INDEX IF NOT EXISTS idx_qb_props_event ON qb_props_odds(event_id);
CREATE INDEX IF NOT EXISTS idx_qb_props_player ON qb_props_odds(player);

CREATE TABLE IF NOT EXISTS projections_qb (
    event_id TEXT,
    player TEXT,
    mu FLOAT,
    sigma FLOAT,
    p_over FLOAT,
    season INT,
    def_team TEXT,
    updated_at TEXT,
    PRIMARY KEY (event_id, player)
);

CREATE TABLE IF NOT EXISTS edges (
    edge_id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT,
    event_id TEXT,
    book TEXT,
    player TEXT,
    market TEXT,
    line FLOAT,
    odds_side TEXT,
    odds INT,
    model_p FLOAT,
    ev_per_dollar FLOAT,
    kelly_frac FLOAT,
    strategy_tag TEXT
);
CREATE INDEX IF NOT EXISTS idx_edges_event ON edges(event_id);
CREATE INDEX IF NOT EXISTS idx_edges_player ON edges(player);

CREATE TABLE IF NOT EXISTS bets_log (
    bet_id INTEGER PRIMARY KEY AUTOINCREMENT,
    placed_at TEXT,
    event_id TEXT,
    book TEXT,
    player TEXT,
    market TEXT,
    line FLOAT,
    odds_side TEXT,
    odds INT,
    stake FLOAT,
    model_p FLOAT,
    ev_per_dollar FLOAT,
    kelly_frac FLOAT,
    strategy_tag TEXT,
    note TEXT
);
CREATE INDEX IF NOT EXISTS idx_bets_event ON bets_log(event_id);
CREATE INDEX IF NOT EXISTS idx_bets_player ON bets_log(player);
