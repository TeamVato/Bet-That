"""Enhanced edge computation with debugging and validation."""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm

from engine import odds_math
from utils.teams import (
    infer_is_home,
    infer_offense_team,
    normalize_team_code,
    parse_event_id,
)
from typing import Dict, Optional

SUPPORTED_MARKETS = {
    "player_pass_yds",
    "player_pass_att", 
    "player_rush_yds",
    "player_rush_att",
    "player_rec_yds",
    "player_receptions",
}


def _infer_pos(market: object, explicit: object = None) -> str | None:
    if explicit is not None and not (isinstance(explicit, float) and np.isnan(explicit)):
        text = str(explicit).strip()
        if text:
            return text.upper()
    if not isinstance(market, str):
        return None
    text = market.lower()
    if "pass" in text:
        return "QB"
    if "rush" in text or "carry" in text or "attempt" in text:
        return "RB"
    if "rec" in text or "catch" in text:
        return "WR"
    if "tight" in text or " te" in text or text.startswith("te "):
        return "TE"
    return None


@dataclass
class EdgeEngineConfig:
    database_path: Path
    export_dir: Path = Path("storage/exports")
    kelly_cap: float = 0.05


class EdgeEngine:
    """Compute edges for QB prop markets with enhanced debugging."""

    def __init__(self, config: EdgeEngineConfig, schedule_lookup: Optional[Dict[str, Dict[str, Optional[str]]]] = None) -> None:
        self.config = config
        self.schedule_lookup = schedule_lookup or {}
        self.config.export_dir.mkdir(parents=True, exist_ok=True)

    def _prepare_dataframe(self, props_df: pd.DataFrame, projections_df: pd.DataFrame) -> pd.DataFrame:
        """Prepare merged dataframe with enhanced error handling."""
        print(f"DEBUG: _prepare_dataframe - props: {len(props_df)}, projections: {len(projections_df)}")
        
        if props_df.empty:
            print("WARNING: props_df is empty in _prepare_dataframe")
            return pd.DataFrame()
            
        # Enhanced merge with better error handling
        if projections_df.empty:
            print("WARNING: projections_df is empty - using props data only")
            merged = props_df.copy()
            # Add default projection columns
            merged["mu"] = merged.get("line", 200.0)
            merged["sigma"] = 55.0
        else:
            merged = props_df.merge(
                projections_df,
                on=["event_id", "player"],
                how="left",
                suffixes=("_props", "_proj"),
            )
            merged["mu"] = merged["mu"].fillna(merged["line"])
            merged["sigma"] = merged["sigma"].fillna(55.0)
        
        merged["sigma"] = merged["sigma"].clip(lower=35.0)
        
        # Enhanced market filtering with debugging
        if "market" in merged.columns:
            before_filter = len(merged)
            available_markets = merged["market"].unique()
            print(f"DEBUG: Available markets: {list(available_markets)}")
            print(f"DEBUG: Supported markets: {SUPPORTED_MARKETS}")
            
            # Check if any supported markets exist
            supported_found = merged["market"].isin(SUPPORTED_MARKETS)
            supported_count = supported_found.sum()
            
            if supported_count == 0:
                print(f"WARNING: No supported markets found, processing all {before_filter} rows")
                # Don't filter if no supported markets - allows broader compatibility
            else:
                merged = merged[supported_found].copy()
                print(f"DEBUG: Filtered to {len(merged)}/{before_filter} rows with supported markets")
        
        return merged

    def compute_edges(self, props_df: pd.DataFrame, projections_df: pd.DataFrame) -> pd.DataFrame:
        """Compute edges with enhanced debugging and validation."""
        
        # Input validation with detailed logging
        if props_df.empty:
            print("ERROR: props_df is empty - no odds data available")
            return pd.DataFrame()
        
        print(f"DEBUG: Edge computation input - props: {len(props_df)} rows, projections: {len(projections_df)} rows")
        print(f"DEBUG: Props columns: {list(props_df.columns)}")
        if not projections_df.empty:
            print(f"DEBUG: Projections columns: {list(projections_df.columns)}")
        
        # Validate required columns in props_df
        required_props_cols = ['event_id', 'player', 'line', 'over_odds', 'under_odds']
        missing_props_cols = [col for col in required_props_cols if col not in props_df.columns]
        if missing_props_cols:
            print(f"ERROR: Props missing required columns: {missing_props_cols}")
            return pd.DataFrame()
        
        # Check for valid odds data
        valid_odds_mask = (
            props_df['over_odds'].notna() & 
            props_df['under_odds'].notna() &
            props_df['line'].notna()
        )
        valid_odds_count = valid_odds_mask.sum()
        print(f"DEBUG: Valid odds rows: {valid_odds_count}/{len(props_df)}")
        
        if valid_odds_count == 0:
            print("ERROR: No rows with valid over_odds, under_odds, and line data")
            return pd.DataFrame()
        
        # Filter to only valid odds for processing
        props_valid = props_df[valid_odds_mask].copy()
        
        df = self._prepare_dataframe(props_valid, projections_df)
        print(f"DEBUG: After merge and prepare: {len(df)} rows")
        
        if df.empty:
            print("ERROR: Prepared dataframe is empty after merge")
            return pd.DataFrame()
        
        rows = []
        processed_count = 0
        error_count = 0
        
        for idx, row in df.iterrows():
            processed_count += 1
            
            # Detailed validation for each row
            over_odds = row.get("over_odds")
            under_odds = row.get("under_odds") 
            line = row.get("line")
            
            if pd.isna(over_odds) or pd.isna(under_odds) or pd.isna(line):
                if processed_count <= 5:  # Log first few failures
                    print(f"DEBUG: Row {idx} skipped - missing data: over_odds={over_odds}, under_odds={under_odds}, line={line}")
                continue
                
            try:
                # Extract core data
                market = row.get("market", "unknown")
                pos_sources = [
                    row.get("pos"),
                    row.get("pos_props"), 
                    row.get("pos_proj"),
                ]
                explicit_pos = next((val for val in pos_sources if isinstance(val, str) and val.strip()), None)
                pos = _infer_pos(market, explicit_pos)
                
                event_id = row.get("event_id")
                mu = float(row.get("mu", line))  # Fallback to line if mu missing
                sigma = float(row.get("sigma", 55.0))  # Default sigma
                line_val = float(line)
                
                # Enhanced season handling
                season_val = row.get("season_proj")
                if pd.isna(season_val):
                    season_val = row.get("season_props")
                if pd.isna(season_val):
                    season_val = 2025  # Current season default
                season_val = int(season_val)
                
                # Calculate probability and edge
                if sigma <= 0:
                    sigma = 55.0
                    
                distribution = norm(loc=mu, scale=sigma)
                p_over = float(1 - distribution.cdf(line_val))
                p_under = float(1 - p_over)
                
                # Convert odds to probabilities
                over_odds_int = int(over_odds)
                under_odds_int = int(under_odds)
                
                over_prob_implied = odds_math.american_to_implied_prob(over_odds_int)
                under_prob_implied = odds_math.american_to_implied_prob(under_odds_int)
                
                # Calculate edges
                edge_over = p_over - over_prob_implied
                edge_under = p_under - under_prob_implied
                
                # Calculate EV and Kelly
                ev_over = odds_math.ev_per_dollar(p_over, over_odds_int)
                ev_under = odds_math.ev_per_dollar(p_under, under_odds_int)
                
                kelly_over = min(self.config.kelly_cap, odds_math.kelly_fraction(p_over, over_odds_int))
                kelly_under = min(self.config.kelly_cap, odds_math.kelly_fraction(p_under, under_odds_int))
                
                # Create base record
                base_record = {
                    "event_id": event_id,
                    "player": row.get("player"),
                    "market": market,
                    "pos": pos,
                    "line": line_val,
                    "mu": mu,
                    "sigma": sigma,
                    "model_p_over": p_over,
                    "model_p_under": p_under,
                    "over_odds": over_odds_int,
                    "under_odds": under_odds_int,
                    "edge_over": edge_over,
                    "edge_under": edge_under,
                    "ev_over": ev_over,
                    "ev_under": ev_under,
                    "kelly_over": kelly_over,
                    "kelly_under": kelly_under,
                    "book": row.get("book", "unknown"),
                    "season": season_val,
                    "week": row.get("week", pd.NA),
                    "updated_at": datetime.now(timezone.utc)
                }
                
                # Add records for both sides if edge is significant
                edge_threshold = 0.005  # 0.5% minimum edge threshold
                
                if abs(edge_over) > edge_threshold:
                    rows.append({
                        **base_record,
                        "side": "over",
                        "edge": edge_over,
                        "model_p": p_over,
                        "odds": over_odds_int,
                        "ev": ev_over,
                        "kelly": kelly_over
                    })
                
                if abs(edge_under) > edge_threshold:
                    rows.append({
                        **base_record,
                        "side": "under", 
                        "edge": edge_under,
                        "model_p": p_under,
                        "odds": under_odds_int,
                        "ev": ev_under,
                        "kelly": kelly_under
                    })
                    
            except Exception as e:
                error_count += 1
                if error_count <= 5:
                    print(f"DEBUG: Row {idx} processing error: {e}")
                continue
        
        print(f"DEBUG: Processed {processed_count} rows, {error_count} errors, generated {len(rows)} edge records")
        
        if not rows:
            print("WARNING: No valid edges computed - check thresholds and data quality")
            # Return empty DataFrame with proper columns for consistency
            return pd.DataFrame(columns=[
                'event_id', 'player', 'market', 'pos', 'side', 'line', 'mu', 'sigma',
                'model_p', 'odds', 'edge', 'ev', 'kelly', 'book', 'season', 'week', 'updated_at'
            ])
        
        result = pd.DataFrame(rows)
        print(f"SUCCESS: Edge computation complete - {len(result)} edges generated")
        return result

    def persist_edges(self, edges_df: pd.DataFrame) -> None:
        """Persist edges to database with enhanced error handling."""
        if edges_df.empty:
            print("WARNING: No edges to persist")
            return
            
        try:
            with sqlite3.connect(self.config.database_path) as conn:
                # Clear existing edges (or implement upsert logic)
                conn.execute("DELETE FROM edges WHERE updated_at < datetime('now', '-1 day')")
                
                # Insert new edges
                edges_df.to_sql("edges", conn, if_exists="append", index=False)
                
                print(f"SUCCESS: Persisted {len(edges_df)} edges to database")
                
        except Exception as e:
            print(f"ERROR: Failed to persist edges: {e}")

    def export(self, edges_df: pd.DataFrame) -> None:
        """Export edges with enhanced validation."""
        if edges_df.empty:
            print("WARNING: No edges to export")
            return
            
        try:
            export_path = self.config.export_dir / f"edges_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            edges_df.to_csv(export_path, index=False)
            print(f"SUCCESS: Exported {len(edges_df)} edges to {export_path}")
            
        except Exception as e:
            print(f"ERROR: Failed to export edges: {e}")
