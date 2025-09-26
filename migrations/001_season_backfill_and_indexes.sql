-- Migration: Season backfill and performance indexes
-- Purpose: Backfill missing season data and add indexes for better performance

-- Step 1: Backfill missing season data in edges table
UPDATE edges
SET season = 2025
WHERE season IS NULL
   OR season = ''
   OR CAST(season AS TEXT) = 'nan';

-- Step 2: Backfill missing season data in current_best_lines table
UPDATE current_best_lines
SET season = 2025
WHERE season IS NULL
   OR season = ''
   OR CAST(season AS TEXT) = 'nan';

-- Step 3: Backfill missing season data in odds_csv_raw table
UPDATE odds_csv_raw
SET season = 2025
WHERE season IS NULL
   OR season = ''
   OR CAST(season AS TEXT) = 'nan';

-- Step 4: Add performance indexes for common queries

-- Index on edges table for season + week + position filtering
CREATE INDEX IF NOT EXISTS idx_edges_season_week_pos
ON edges(season, week, pos);

-- Index on edges table for season + player + market queries
CREATE INDEX IF NOT EXISTS idx_edges_season_player_market
ON edges(season, player, market);

-- Index on current_best_lines for season + week joins
CREATE INDEX IF NOT EXISTS idx_best_lines_season_week
ON current_best_lines(season, week);

-- Index on current_best_lines for player + market lookups
CREATE INDEX IF NOT EXISTS idx_best_lines_player_market
ON current_best_lines(player, market);

-- Index on current_best_lines for event_id lookups
CREATE INDEX IF NOT EXISTS idx_best_lines_event_id
ON current_best_lines(event_id);

-- Index on odds_csv_raw for season + updated_at (staleness queries)
CREATE INDEX IF NOT EXISTS idx_odds_raw_season_updated
ON odds_csv_raw(season, updated_at);

-- Composite index for defense ratings joins
CREATE INDEX IF NOT EXISTS idx_edges_defense_join
ON edges(season, week, opponent_def_code);

-- Index for commence_time filtering (upcoming games)
CREATE INDEX IF NOT EXISTS idx_best_lines_commence_time
ON current_best_lines(commence_time);

-- Index for updated_at filtering (staleness)
CREATE INDEX IF NOT EXISTS idx_best_lines_updated_at
ON current_best_lines(updated_at);

-- Analyze tables for query optimization
ANALYZE edges;
ANALYZE current_best_lines;
ANALYZE odds_csv_raw;