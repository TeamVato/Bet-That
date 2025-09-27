"""Enhanced primary line marking logic for poll_odds.py"""

import pandas as pd
import sqlite3
from typing import Tuple
import datetime as dt


def mark_primary_lines_enhanced(closing_df: pd.DataFrame, primary_book: str = None) -> pd.DataFrame:
    """Mark primary lines with fallback logic when no primary book specified."""
    
    if closing_df.empty:
        return closing_df
        
    closing_df = closing_df.copy()
    closing_df["is_primary"] = 0  # Reset all to non-primary
    
    primary_book_normalized = (primary_book or "").strip().lower()
    
    # Group by market and event to select best line for each
    grouping_cols = ["event_id", "market", "line"]
    if "player" in closing_df.columns:
        grouping_cols.append("player")
    
    total_groups = 0
    primary_marked = 0
    
    for group_key, group_df in closing_df.groupby(grouping_cols, dropna=False):
        total_groups += 1
        
        if len(group_df) == 0:
            continue
        
        # Strategy 1: Use specified primary book if available
        if primary_book_normalized:
            book_matches = group_df[
                group_df["book"].str.lower().str.strip() == primary_book_normalized
            ]
            if len(book_matches) > 0:
                # Mark first matching book as primary
                primary_idx = book_matches.index[0]
                closing_df.loc[primary_idx, "is_primary"] = 1
                primary_marked += 1
                continue
        
        # Strategy 2: Fallback selection criteria
        group_df_copy = group_df.copy()
        scores = pd.Series(0.0, index=group_df_copy.index)
        
        # Recency score (most recent gets higher score)
        if "updated_at" in group_df_copy.columns:
            timestamps = pd.to_datetime(group_df_copy["updated_at"], errors="coerce")
            valid_timestamps = timestamps.dropna()
            if len(valid_timestamps) > 1:
                time_range = valid_timestamps.max() - valid_timestamps.min()
                if time_range.total_seconds() > 0:
                    time_scores = (timestamps - valid_timestamps.min()) / time_range
                    scores += time_scores.fillna(0) * 1.0
        
        # Data quality score
        data_quality = (
            group_df_copy.get("implied_prob", pd.Series()).notna().astype(float) * 0.4 +
            group_df_copy.get("fair_prob_close", pd.Series()).notna().astype(float) * 0.4 +
            group_df_copy.get("overround", pd.Series()).notna().astype(float) * 0.2
        )
        scores += data_quality * 0.8
        
        # Overround score (lower overround is better)
        if "overround" in group_df_copy.columns:
            overround_vals = pd.to_numeric(group_df_copy["overround"], errors="coerce")
            valid_overround = overround_vals.dropna()
            if len(valid_overround) > 0:
                max_overround = valid_overround.max()
                min_overround = valid_overround.min()
                if max_overround > min_overround:
                    overround_scores = 1 - (overround_vals - min_overround) / (max_overround - min_overround)
                    scores += overround_scores.fillna(0.5) * 0.6
        
        # Deterministic tiebreaker: book name (alphabetical)
        book_scores = group_df_copy["book"].fillna("zzz").rank(method="min") / len(group_df_copy)
        scores += book_scores * 0.1
        
        # Select highest scoring line as primary
        if len(scores) > 0:
            best_idx = scores.idxmax()
            closing_df.loc[best_idx, "is_primary"] = 1
            primary_marked += 1
    
    print(f"DEBUG: Primary line marking - {primary_marked}/{total_groups} groups marked with primary lines")
    
    # Emergency fallback if no primary lines marked
    if primary_marked == 0 and len(closing_df) > 0:
        print("WARNING: No primary lines marked - applying emergency fallback")
        for group_key, group_df in closing_df.groupby(grouping_cols, dropna=False):
            if len(group_df) > 0:
                first_idx = group_df.index[0]
                closing_df.loc[first_idx, "is_primary"] = 1
                primary_marked += 1
        print(f"DEBUG: Emergency fallback marked {primary_marked} primary lines")
    
    return closing_df


def write_closing_snapshot_enhanced(
    con: sqlite3.Connection,
    normalized: pd.DataFrame,
    ts_run: dt.datetime = None,
    primary_book: str = None,
    run_id: str = None,
    source_label: str = "poll_odds",
) -> Tuple[int, float]:
    """Enhanced closing snapshot writer with robust primary line marking."""
    
    if ts_run is None:
        ts_run = dt.datetime.now(dt.timezone.utc)
    
    required_cols = {"event_id", "market", "book", "side", "line", "odds"}
    missing_cols = required_cols - set(normalized.columns)
    if missing_cols:
        print(f"ERROR: Missing required columns: {missing_cols}")
        return 0, 0.0
    
    working = normalized.copy()
    working = working.dropna(subset=list(required_cols))
    if working.empty:
        print("ERROR: No valid rows after filtering for required columns")
        return 0, 0.0

    working["updated_at"] = pd.to_datetime(working["updated_at"], errors="coerce", utc=True)
    working = working[working["updated_at"].notna()]
    if working.empty:
        print("ERROR: No valid rows after timestamp parsing")
        return 0, 0.0

    if "commence_time" in working.columns:
        working["commence_ts"] = pd.to_datetime(working["commence_time"], errors="coerce", utc=True)
    else:
        working["commence_ts"] = pd.NaT

    # Select closing lines (most recent per market/event/book combination)
    key_cols = ["event_id", "market", "side", "line", "book"]
    selections = []
    
    for _, group in working.groupby(key_cols, dropna=False):
        group = group.sort_values("updated_at")
        commence = group["commence_ts"].dropna().max()
        choice = None
        
        if pd.notna(commence):
            before = group[group["updated_at"] <= commence]
            if not before.empty:
                choice = before.iloc[-1]
            else:
                fallback_cutoff = commence - pd.Timedelta(minutes=2)
                fallback = group[group["updated_at"] <= fallback_cutoff]
                if not fallback.empty:
                    choice = fallback.iloc[-1]
        
        if choice is None:
            choice = group.iloc[-1]
        selections.append(choice)

    if not selections:
        print("ERROR: No closing line selections made")
        return 0, 0.0

    closing_df = pd.DataFrame(selections).reset_index(drop=True)
    
    # Apply enhanced primary line marking
    closing_df = mark_primary_lines_enhanced(closing_df, primary_book)
    
    # Validate primary lines were marked
    primary_count = (closing_df["is_primary"] == 1).sum()
    if primary_count == 0:
        print("ERROR: No primary lines marked after enhancement")
        return 0, 0.0
    else:
        print(f"SUCCESS: {primary_count} primary lines marked for database insertion")
    
    # Calculate devigged probabilities and other metrics
    closing_df["line"] = pd.to_numeric(closing_df.get("line"), errors="coerce")
    closing_df["odds"] = pd.to_numeric(closing_df.get("odds"), errors="coerce")
    
    def _safe_decimal(odds):
        try:
            if pd.isna(odds):
                return None
            return abs(odds) / 100.0 + 1.0 if odds >= 0 else 100.0 / abs(odds) + 1.0
        except:
            return None
    
    def _safe_implied(decimal):
        try:
            if pd.isna(decimal) or decimal <= 0:
                return None
            return 1.0 / decimal
        except:
            return None
    
    def _normalize_side(side):
        if pd.isna(side):
            return "unknown"
        s = str(side).lower().strip()
        if s in ("over", "o"):
            return "over"
        elif s in ("under", "u"):
            return "under"
        return s
    
    def proportional_devig_two_way(p1, p2):
        """Simple proportional devig for two-way markets."""
        total = p1 + p2
        if total <= 0:
            return p1, p2
        return p1 / total, p2 / total
    
    closing_df["odds_decimal"] = closing_df["odds"].apply(_safe_decimal)
    closing_df["implied_prob"] = closing_df["odds_decimal"].apply(_safe_implied)
    closing_df["side_norm"] = closing_df["side"].apply(_normalize_side)
    closing_df["fair_prob_close"] = pd.NA
    closing_df["overround"] = pd.NA

    # Calculate fair probabilities for over/under pairs
    grouped = closing_df.groupby(["event_id", "market", "line", "book"], dropna=False)
    for _, group in grouped:
        over_idx = group[group["side_norm"] == "over"].index
        under_idx = group[group["side_norm"] == "under"].index
        
        if len(over_idx) == 1 and len(under_idx) == 1:
            over_prob = closing_df.loc[over_idx[0], "implied_prob"]
            under_prob = closing_df.loc[under_idx[0], "implied_prob"]
            
            if pd.notna(over_prob) and pd.notna(under_prob) and over_prob >= 0 and under_prob >= 0:
                fair_over, fair_under = proportional_devig_two_way(float(over_prob), float(under_prob))
                overround = float(over_prob + under_prob)
                
                closing_df.loc[over_idx[0], "fair_prob_close"] = fair_over
                closing_df.loc[under_idx[0], "fair_prob_close"] = fair_under
                closing_df.loc[[over_idx[0], under_idx[0]], "overround"] = overround

    # Calculate coverage
    coverage = 0.0
    pair_counts = grouped["side_norm"].nunique()
    if len(pair_counts) > 0:
        coverage = float((pair_counts >= 2).sum() / len(pair_counts))

    # Database operations
    ensure_closing_tables(con)

    def _coerce_optional(val):
        """Convert value to appropriate type for database storage."""
        if pd.isna(val):
            return None
        try:
            if isinstance(val, (int, float)):
                return float(val)
            return val
        except:
            return None

    # Insert into database
    delete_sql = (
        "DELETE FROM closing_lines WHERE event_id=? AND market=? AND side=? AND "
        "((line IS NULL AND ? IS NULL) OR line=?) AND book=?"
    )
    insert_sql = (
        """
        INSERT INTO closing_lines (
            event_id, market, side, line, book,
            odds_decimal, odds_american, implied_prob, overround,
            fair_prob_close, ts_close, is_primary,
            ingest_source, source_run_id, raw_payload_hash
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
    )

    run_identifier = run_id or f"poll/{ts_run.isoformat()}"
    inserted = 0

    for row in closing_df.to_dict("records"):
        odds_american = row.get("odds")
        if pd.notna(odds_american):
            try:
                odds_american = int(odds_american)
            except:
                odds_american = None
        else:
            odds_american = None

        ts_close = row.get("updated_at")
        if isinstance(ts_close, pd.Timestamp):
            ts_close = ts_close.to_pydatetime().isoformat()

        line_value = _coerce_optional(row.get("line"))
        odds_decimal = _coerce_optional(row.get("odds_decimal"))
        implied_prob = _coerce_optional(row.get("implied_prob"))
        overround_val = _coerce_optional(row.get("overround"))
        fair_prob_close = _coerce_optional(row.get("fair_prob_close"))
        is_primary = int(row.get("is_primary", 0))

        import hashlib
        import json
        payload_hash = hashlib.sha256(
            json.dumps(row, default=str, sort_keys=True).encode()
        ).hexdigest()

        delete_params = (
            row.get("event_id"),
            row.get("market"),
            row.get("side"),
            line_value,
            line_value,
            row.get("book"),
        )
        
        params = (
            row.get("event_id"),
            row.get("market"),
            row.get("side"),
            line_value,
            row.get("book"),
            odds_decimal,
            odds_american,
            implied_prob,
            overround_val,
            fair_prob_close,
            ts_close,
            is_primary,
            source_label,
            run_identifier,
            payload_hash,
        )
        
        con.execute(delete_sql, delete_params)
        con.execute(insert_sql, params)
        inserted += 1

    print(f"SUCCESS: Inserted {inserted} closing lines with {primary_count} primary lines")
    return inserted, coverage


def ensure_closing_tables(con: sqlite3.Connection) -> None:
    """Ensure closing_lines table exists with proper schema."""
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS closing_lines (
            event_id TEXT,
            market TEXT,
            side TEXT,
            line REAL,
            book TEXT,
            odds_decimal REAL,
            odds_american INTEGER,
            implied_prob REAL,
            overround REAL,
            fair_prob_close REAL,
            ts_close TEXT,
            is_primary INTEGER DEFAULT 0,
            ingest_source TEXT,
            source_run_id TEXT,
            raw_payload_hash TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
