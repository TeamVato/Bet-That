-- Enhanced production-ready schema with comprehensive indexes and constraints
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;
PRAGMA synchronous=NORMAL;

-- Metadata tables
CREATE TABLE IF NOT EXISTS books (
    book_key TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    is_active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS events (
    event_id TEXT PRIMARY KEY,
    sport_key TEXT NOT NULL,
    commence_time TEXT,
    home_team TEXT,
    away_team TEXT,
    season INTEGER,
    week INTEGER,
    venue TEXT,
    region TEXT DEFAULT 'us',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Enhanced indexes for events
CREATE INDEX IF NOT EXISTS idx_events_season_week ON events(season, week);
CREATE INDEX IF NOT EXISTS idx_events_commence_time ON events(commence_time);
CREATE INDEX IF NOT EXISTS idx_events_teams ON events(home_team, away_team);

CREATE TABLE IF NOT EXISTS markets (
    market_key TEXT PRIMARY KEY,
    description TEXT NOT NULL,
    market_type TEXT DEFAULT 'standard',
    is_active INTEGER DEFAULT 1
);

-- Core odds data with enhanced constraints
CREATE TABLE IF NOT EXISTS odds_snapshots (
    snapshot_id INTEGER PRIMARY KEY AUTOINCREMENT,
    fetched_at TEXT NOT NULL,
    sport_key TEXT NOT NULL,
    event_id TEXT NOT NULL,
    market_key TEXT NOT NULL,
    bookmaker_key TEXT NOT NULL,
    line FLOAT,
    price INTEGER NOT NULL CHECK (price != 0 AND price >= -2000 AND price <= 2000),
    outcome TEXT NOT NULL,
    points FLOAT,
    iso_time TEXT,
    odds_raw_json TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (fetched_at, event_id, market_key, bookmaker_key, outcome, COALESCE(points, 0)),
    FOREIGN KEY (event_id) REFERENCES events(event_id)
);

-- Comprehensive indexes for odds_snapshots (production performance)
CREATE INDEX IF NOT EXISTS idx_odds_snapshots_event ON odds_snapshots(event_id);
CREATE INDEX IF NOT EXISTS idx_odds_snapshots_market ON odds_snapshots(market_key);
CREATE INDEX IF NOT EXISTS idx_odds_snapshots_book ON odds_snapshots(bookmaker_key);
CREATE INDEX IF NOT EXISTS idx_odds_snapshots_fetched_at ON odds_snapshots(fetched_at);
CREATE INDEX IF NOT EXISTS idx_odds_snapshots_outcome ON odds_snapshots(outcome);
CREATE INDEX IF NOT EXISTS idx_odds_snapshots_price ON odds_snapshots(price);
CREATE INDEX IF NOT EXISTS idx_odds_snapshots_compound ON odds_snapshots(event_id, market_key, bookmaker_key);

-- Current best lines with enhanced performance
CREATE TABLE IF NOT EXISTS current_best_lines (
    event_id TEXT NOT NULL,
    market_key TEXT NOT NULL,
    outcome TEXT NOT NULL,
    best_book TEXT NOT NULL,
    best_price INTEGER NOT NULL CHECK (best_price != 0),
    best_points FLOAT,
    updated_at TEXT NOT NULL,
    season INTEGER,
    week INTEGER,
    team_code TEXT,
    opponent_def_code TEXT,
    is_stale INTEGER DEFAULT 0,
    PRIMARY KEY (event_id, market_key, outcome),
    FOREIGN KEY (event_id) REFERENCES events(event_id)
);

-- Enhanced indexes for current_best_lines
CREATE INDEX IF NOT EXISTS idx_best_lines_season_week ON current_best_lines(season, week);
CREATE INDEX IF NOT EXISTS idx_best_lines_updated_at ON current_best_lines(updated_at);
CREATE INDEX IF NOT EXISTS idx_best_lines_staleness ON current_best_lines(is_stale);

-- QB props odds (legacy support with validation)
CREATE TABLE IF NOT EXISTS qb_props_odds (
    snapshot_id INTEGER PRIMARY KEY AUTOINCREMENT,
    fetched_at TEXT NOT NULL,
    game_id TEXT,
    event_id TEXT NOT NULL,
    player TEXT NOT NULL,
    market TEXT NOT NULL,
    line FLOAT NOT NULL CHECK (line >= 0 AND line <= 1000),
    over_odds INTEGER NOT NULL CHECK (over_odds != 0 AND over_odds >= -1000 AND over_odds <= 1000),
    under_odds INTEGER NOT NULL CHECK (under_odds != 0 AND under_odds >= -1000 AND under_odds <= 1000),
    book TEXT NOT NULL,
    season INTEGER CHECK (season >= 2020 AND season <= 2030),
    def_team TEXT,
    team TEXT,
    game_date TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES events(event_id)
);

-- Enhanced indexes for QB props
CREATE INDEX IF NOT EXISTS idx_qb_props_event ON qb_props_odds(event_id);
CREATE INDEX IF NOT EXISTS idx_qb_props_player ON qb_props_odds(player);
CREATE INDEX IF NOT EXISTS idx_qb_props_season_week ON qb_props_odds(season);
CREATE INDEX IF NOT EXISTS idx_qb_props_market ON qb_props_odds(market);

-- QB projections with validation
CREATE TABLE IF NOT EXISTS projections_qb (
    event_id TEXT NOT NULL,
    player TEXT NOT NULL,
    mu FLOAT NOT NULL,
    sigma FLOAT NOT NULL CHECK (sigma > 0),
    p_over FLOAT CHECK (p_over >= 0 AND p_over <= 1),
    season INTEGER CHECK (season >= 2020 AND season <= 2030),
    def_team TEXT,
    updated_at TEXT NOT NULL,
    PRIMARY KEY (event_id, player),
    FOREIGN KEY (event_id) REFERENCES events(event_id)
);

-- Enhanced edges table with comprehensive validation
CREATE TABLE IF NOT EXISTS edges (
    edge_id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    event_id TEXT NOT NULL,
    book TEXT NOT NULL,
    player TEXT NOT NULL,
    market TEXT NOT NULL,
    pos TEXT CHECK (pos IN ('QB', 'RB', 'WR', 'TE') OR pos IS NULL),
    line FLOAT NOT NULL CHECK (line >= 0 AND line <= 1000),
    odds_side TEXT NOT NULL CHECK (odds_side IN ('over', 'under', 'Over', 'Under')),
    odds INTEGER NOT NULL CHECK (odds != 0 AND odds >= -1000 AND odds <= 1000),
    model_p FLOAT NOT NULL CHECK (model_p >= 0 AND model_p <= 1),
    p_model_shrunk FLOAT CHECK (p_model_shrunk >= 0 AND p_model_shrunk <= 1),
    ev_per_dollar FLOAT NOT NULL CHECK (ev_per_dollar >= -1.0 AND ev_per_dollar <= 10.0),
    kelly_frac FLOAT NOT NULL CHECK (kelly_frac >= 0 AND kelly_frac <= 1),
    strategy_tag TEXT NOT NULL,
    season INTEGER CHECK (season >= 2020 AND season <= 2030),
    week INTEGER CHECK (week >= 1 AND week <= 22),
    opponent_def_code TEXT,
    team TEXT,
    home_team TEXT,
    away_team TEXT,
    is_home INTEGER CHECK (is_home IN (0, 1) OR is_home IS NULL),
    game_date TEXT,
    def_tier TEXT CHECK (def_tier IN ('generous', 'stingy', 'neutral') OR def_tier IS NULL),
    def_score FLOAT CHECK (def_score >= -10.0 AND def_score <= 10.0),
    implied_prob FLOAT CHECK (implied_prob >= 0 AND implied_prob <= 1),
    fair_prob FLOAT CHECK (fair_prob >= 0 AND fair_prob <= 1),
    overround FLOAT CHECK (overround >= 0),
    is_stale INTEGER DEFAULT 0 CHECK (is_stale IN (0, 1)),
    edge_prob FLOAT,
    edge_fair FLOAT,
    implied_prob_over FLOAT CHECK (implied_prob_over >= 0 AND implied_prob_over <= 1),
    implied_prob_under FLOAT CHECK (implied_prob_under >= 0 AND implied_prob_under <= 1),
    fair_prob_over FLOAT CHECK (fair_prob_over >= 0 AND fair_prob_over <= 1),
    fair_prob_under FLOAT CHECK (fair_prob_under >= 0 AND fair_prob_under <= 1),
    fair_decimal_over FLOAT,
    fair_decimal_under FLOAT,
    FOREIGN KEY (event_id) REFERENCES events(event_id)
);

-- Comprehensive indexes for edges (critical for UI performance)
CREATE INDEX IF NOT EXISTS idx_edges_event ON edges(event_id);
CREATE INDEX IF NOT EXISTS idx_edges_player ON edges(player);
CREATE INDEX IF NOT EXISTS idx_edges_season_week ON edges(season, week);
CREATE INDEX IF NOT EXISTS idx_edges_pos ON edges(pos);
CREATE INDEX IF NOT EXISTS idx_edges_ev ON edges(ev_per_dollar DESC);
CREATE INDEX IF NOT EXISTS idx_edges_kelly ON edges(kelly_frac DESC);
CREATE INDEX IF NOT EXISTS idx_edges_created_at ON edges(created_at);
CREATE INDEX IF NOT EXISTS idx_edges_staleness ON edges(is_stale);
CREATE INDEX IF NOT EXISTS idx_edges_compound_filter ON edges(season, week, pos, is_stale);

-- Defense ratings with enhanced validation
CREATE TABLE IF NOT EXISTS defense_ratings (
    rating_id INTEGER PRIMARY KEY AUTOINCREMENT,
    defteam TEXT NOT NULL CHECK (LENGTH(defteam) >= 2 AND LENGTH(defteam) <= 5),
    season INTEGER NOT NULL CHECK (season >= 2020 AND season <= 2030),
    pos TEXT NOT NULL CHECK (pos IN ('QB_PASS', 'RB_RUSH', 'WR_REC', 'TE_REC')),
    week INTEGER CHECK (week >= 1 AND week <= 22),
    score FLOAT NOT NULL CHECK (score >= -10.0 AND score <= 10.0),
    tier TEXT NOT NULL CHECK (tier IN ('generous', 'stingy', 'neutral')),
    score_adj FLOAT CHECK (score_adj >= -10.0 AND score_adj <= 10.0),
    tier_adj TEXT CHECK (tier_adj IN ('generous', 'stingy', 'neutral')),
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(defteam, season, pos, COALESCE(week, -1))
);

-- Enhanced indexes for defense ratings
CREATE INDEX IF NOT EXISTS idx_defense_ratings_team_season ON defense_ratings(defteam, season);
CREATE INDEX IF NOT EXISTS idx_defense_ratings_pos ON defense_ratings(pos);
CREATE INDEX IF NOT EXISTS idx_defense_ratings_week ON defense_ratings(week);
CREATE INDEX IF NOT EXISTS idx_defense_ratings_compound ON defense_ratings(defteam, season, pos, week);

-- Defense ratings latest view for efficient lookups
CREATE VIEW IF NOT EXISTS defense_ratings_latest AS
SELECT
    r.defteam,
    r.season,
    r.pos,
    r.week,
    r.score,
    r.tier,
    COALESCE(r.score_adj, r.score) AS score_effective,
    COALESCE(r.tier_adj, r.tier) AS tier_effective
FROM defense_ratings AS r
WHERE COALESCE(r.week, -1) = (
    SELECT COALESCE(MAX(r2.week), -1)
    FROM defense_ratings AS r2
    WHERE r2.defteam = r.defteam
      AND r2.season = r.season
      AND r2.pos = r.pos
);

-- Betting log with enhanced tracking
CREATE TABLE IF NOT EXISTS bets_log (
    bet_id INTEGER PRIMARY KEY AUTOINCREMENT,
    placed_at TEXT NOT NULL,
    event_id TEXT NOT NULL,
    book TEXT NOT NULL,
    player TEXT NOT NULL,
    market TEXT NOT NULL,
    line FLOAT NOT NULL,
    odds_side TEXT NOT NULL CHECK (odds_side IN ('over', 'under', 'Over', 'Under')),
    odds INTEGER NOT NULL CHECK (odds != 0),
    stake FLOAT NOT NULL CHECK (stake > 0),
    model_p FLOAT NOT NULL CHECK (model_p >= 0 AND model_p <= 1),
    ev_per_dollar FLOAT NOT NULL,
    kelly_frac FLOAT NOT NULL CHECK (kelly_frac >= 0 AND kelly_frac <= 1),
    strategy_tag TEXT NOT NULL,
    note TEXT,
    result TEXT CHECK (result IN ('win', 'loss', 'push', 'pending') OR result IS NULL),
    profit FLOAT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES events(event_id)
);

-- Enhanced indexes for bets log
CREATE INDEX IF NOT EXISTS idx_bets_event ON bets_log(event_id);
CREATE INDEX IF NOT EXISTS idx_bets_player ON bets_log(player);
CREATE INDEX IF NOT EXISTS idx_bets_placed_at ON bets_log(placed_at);
CREATE INDEX IF NOT EXISTS idx_bets_result ON bets_log(result);

-- Team scheme data
CREATE TABLE IF NOT EXISTS team_week_scheme (
    team TEXT NOT NULL,
    season INTEGER NOT NULL CHECK (season >= 2020 AND season <= 2030),
    week INTEGER NOT NULL CHECK (week >= 1 AND week <= 22),
    proe FLOAT,
    ed_pass_rate FLOAT CHECK (ed_pass_rate >= 0 AND ed_pass_rate <= 1),
    pace FLOAT CHECK (pace > 0),
    plays INTEGER CHECK (plays >= 0),
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (team, season, week)
);

-- Injury tracking
CREATE TABLE IF NOT EXISTS injuries (
    injury_id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id TEXT,
    season INTEGER CHECK (season >= 2020 AND season <= 2030),
    week INTEGER CHECK (week >= 1 AND week <= 22),
    team TEXT NOT NULL,
    player TEXT NOT NULL,
    position TEXT,
    report_status TEXT CHECK (report_status IN ('Out', 'Doubtful', 'Questionable', 'Probable', 'Active') OR report_status IS NULL),
    report_primary_injury TEXT,
    practice_status TEXT,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES events(event_id)
);

-- Enhanced indexes for injuries
CREATE INDEX IF NOT EXISTS idx_injuries_event ON injuries(event_id);
CREATE INDEX IF NOT EXISTS idx_injuries_player ON injuries(player);
CREATE INDEX IF NOT EXISTS idx_injuries_season_week ON injuries(season, week);
CREATE INDEX IF NOT EXISTS idx_injuries_team ON injuries(team);

-- Weather data
CREATE TABLE IF NOT EXISTS weather (
    event_id TEXT PRIMARY KEY,
    temp_f FLOAT CHECK (temp_f >= -20 AND temp_f <= 120),
    wind_mph FLOAT CHECK (wind_mph >= 0 AND wind_mph <= 100),
    roof TEXT CHECK (roof IN ('dome', 'closed', 'open', 'retractable') OR roof IS NULL),
    surface TEXT CHECK (surface IN ('grass', 'turf', 'fieldturf', 'artificial') OR surface IS NULL),
    precip TEXT,
    indoor INTEGER CHECK (indoor IN (0, 1)),
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES events(event_id)
);

-- WR/CB matchup context
CREATE TABLE IF NOT EXISTS wr_cb_public (
    context_id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id TEXT,
    season INTEGER CHECK (season >= 2020 AND season <= 2030),
    week INTEGER CHECK (week >= 1 AND week <= 22),
    team TEXT NOT NULL,
    player TEXT NOT NULL,
    note TEXT,
    source_url TEXT,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES events(event_id)
);

CREATE INDEX IF NOT EXISTS idx_wr_cb_event ON wr_cb_public(event_id);
CREATE INDEX IF NOT EXISTS idx_wr_cb_player ON wr_cb_public(player);

-- General context notes
CREATE TABLE IF NOT EXISTS context_notes (
    note_id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id TEXT,
    note TEXT NOT NULL,
    source_url TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES events(event_id)
);

CREATE INDEX IF NOT EXISTS idx_context_notes_event ON context_notes(event_id);

-- Enhanced closing lines and CLV tracking
CREATE TABLE IF NOT EXISTS closing_lines (
    closing_id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id TEXT NOT NULL,
    market TEXT NOT NULL,
    side TEXT NOT NULL,
    line REAL,
    book TEXT NOT NULL,
    odds_decimal REAL CHECK (odds_decimal > 0),
    odds_american INTEGER CHECK (odds_american != 0),
    implied_prob REAL CHECK (implied_prob >= 0 AND implied_prob <= 1),
    overround REAL CHECK (overround >= 0),
    fair_prob_close REAL CHECK (fair_prob_close >= 0 AND fair_prob_close <= 1),
    ts_close TEXT NOT NULL,
    is_primary INTEGER DEFAULT 0 CHECK (is_primary IN (0, 1)),
    ingest_source TEXT,
    source_run_id TEXT,
    raw_payload_hash TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES events(event_id)
);

CREATE INDEX IF NOT EXISTS idx_closing_lines_key ON closing_lines(event_id, market, side, line, book);
CREATE INDEX IF NOT EXISTS idx_closing_lines_ts_close ON closing_lines(ts_close);
CREATE INDEX IF NOT EXISTS idx_closing_lines_primary ON closing_lines(is_primary);

-- CLV (Closing Line Value) tracking
CREATE TABLE IF NOT EXISTS clv_log (
    clv_id INTEGER PRIMARY KEY AUTOINCREMENT,
    edge_id TEXT,
    bet_id TEXT,
    event_id TEXT NOT NULL,
    market TEXT NOT NULL,
    side TEXT NOT NULL,
    line REAL,
    entry_odds INTEGER,
    close_odds INTEGER,
    entry_prob_fair REAL CHECK (entry_prob_fair >= 0 AND entry_prob_fair <= 1),
    close_prob_fair REAL CHECK (close_prob_fair >= 0 AND close_prob_fair <= 1),
    delta_prob REAL,
    delta_logit REAL,
    clv_cents REAL,
    beat_close INTEGER CHECK (beat_close IN (0, 1)),
    primary_book TEXT,
    match_tolerance REAL CHECK (match_tolerance >= 0),
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES events(event_id)
);

CREATE INDEX IF NOT EXISTS idx_clv_log_event_market ON clv_log(event_id, market, side);
CREATE INDEX IF NOT EXISTS idx_clv_log_beat_close ON clv_log(beat_close);
CREATE INDEX IF NOT EXISTS idx_clv_log_created_at ON clv_log(created_at);

-- Data quality and monitoring tables
CREATE TABLE IF NOT EXISTS pipeline_runs (
    run_id INTEGER PRIMARY KEY AUTOINCREMENT,
    pipeline_type TEXT NOT NULL,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    status TEXT CHECK (status IN ('running', 'completed', 'failed', 'cancelled')),
    rows_processed INTEGER DEFAULT 0,
    rows_inserted INTEGER DEFAULT 0,
    errors_count INTEGER DEFAULT 0,
    warnings_count INTEGER DEFAULT 0,
    config_json TEXT,
    error_details TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_pipeline_runs_type ON pipeline_runs(pipeline_type);
CREATE INDEX IF NOT EXISTS idx_pipeline_runs_status ON pipeline_runs(status);
CREATE INDEX IF NOT EXISTS idx_pipeline_runs_started_at ON pipeline_runs(started_at);

-- Data quality metrics
CREATE TABLE IF NOT EXISTS data_quality_metrics (
    metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_name TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    metric_value REAL NOT NULL,
    threshold_min REAL,
    threshold_max REAL,
    status TEXT CHECK (status IN ('pass', 'warn', 'fail')),
    measured_at TEXT NOT NULL,
    details TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_data_quality_table ON data_quality_metrics(table_name);
CREATE INDEX IF NOT EXISTS idx_data_quality_metric ON data_quality_metrics(metric_name);
CREATE INDEX IF NOT EXISTS idx_data_quality_status ON data_quality_metrics(status);
CREATE INDEX IF NOT EXISTS idx_data_quality_measured_at ON data_quality_metrics(measured_at);

-- Performance optimization: analyze tables after creation
ANALYZE;

-- Create a view for commonly used edge filtering (performance optimization)
CREATE VIEW IF NOT EXISTS edges_filtered AS
SELECT *
FROM edges
WHERE is_stale = 0
  AND season IS NOT NULL
  AND week IS NOT NULL
  AND pos IS NOT NULL
  AND ev_per_dollar > 0;

-- Common queries view for dashboard
CREATE VIEW IF NOT EXISTS dashboard_summary AS
SELECT
    COUNT(*) as total_edges,
    COUNT(CASE WHEN ev_per_dollar > 0 THEN 1 END) as positive_ev_edges,
    COUNT(CASE WHEN kelly_frac > 0.01 THEN 1 END) as significant_edges,
    AVG(ev_per_dollar) as avg_ev,
    MAX(ev_per_dollar) as max_ev,
    COUNT(DISTINCT event_id) as unique_events,
    COUNT(DISTINCT player) as unique_players
FROM edges
WHERE is_stale = 0
  AND season IS NOT NULL
  AND created_at >= DATE('now', '-1 day');

-- Vacuum and optimize
PRAGMA optimize;