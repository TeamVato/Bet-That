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
    game_id TEXT,
    event_id TEXT,
    player TEXT,
    market TEXT,
    line FLOAT,
    over_odds INT,
    under_odds INT,
    book TEXT,
    season INT,
    def_team TEXT,
    team TEXT,
    game_date TEXT
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
    p_model_shrunk FLOAT,
    ev_per_dollar FLOAT,
    kelly_frac FLOAT,
    strategy_tag TEXT,
    season INT,
    week INT,
    opponent_def_code TEXT,
    team TEXT,
    home_team TEXT,
    away_team TEXT,
    is_home INT,
    game_date TEXT,
    def_tier TEXT,
    def_score FLOAT,
    implied_prob FLOAT,
    fair_prob FLOAT,
    overround FLOAT,
    is_stale INT,
    edge_prob FLOAT,
    edge_fair FLOAT,
    implied_prob_over FLOAT,
    implied_prob_under FLOAT,
    fair_prob_over FLOAT,
    fair_prob_under FLOAT,
    fair_decimal_over FLOAT,
    fair_decimal_under FLOAT
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

CREATE TABLE IF NOT EXISTS team_week_scheme (
    team TEXT,
    season INT,
    week INT,
    proe FLOAT,
    ed_pass_rate FLOAT,
    pace FLOAT,
    plays INT,
    updated_at TEXT,
    PRIMARY KEY (team, season, week)
);

CREATE TABLE IF NOT EXISTS injuries (
    injury_id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id TEXT,
    season INT,
    week INT,
    team TEXT,
    player TEXT,
    position TEXT,
    report_status TEXT,
    report_primary_injury TEXT,
    practice_status TEXT,
    updated_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_injuries_event ON injuries(event_id);

CREATE TABLE IF NOT EXISTS weather (
    event_id TEXT PRIMARY KEY,
    temp_f FLOAT,
    wind_mph FLOAT,
    roof TEXT,
    surface TEXT,
    precip TEXT,
    indoor INT,
    updated_at TEXT
);

CREATE TABLE IF NOT EXISTS wr_cb_public (
    context_id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id TEXT,
    season INT,
    week INT,
    team TEXT,
    player TEXT,
    note TEXT,
    source_url TEXT,
    updated_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_wr_cb_event ON wr_cb_public(event_id);

CREATE TABLE IF NOT EXISTS context_notes (
    note_id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id TEXT,
    note TEXT,
    source_url TEXT,
    created_at TEXT
);
