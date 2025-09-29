import sqlite3
from pathlib import Path
from typing import Iterable, List

import nfl_data_py as nfl
import numpy as np
import pandas as pd
from sklearn.linear_model import RidgeCV

SEASONS = [2023, 2024, 2025]  # adjust as needed
DATA_DIR = Path("storage/imports/PlayerProfiler")
LOCAL_PBP = {
    2025: DATA_DIR / "Advanced Play by Play" / "2025-Advanced-PBP-Data.csv",
}
LOCAL_ROSTERS = {
    2025: DATA_DIR / "Weekly Roster Key" / "2025-Weekly-Roster-Key.csv",
}


def _ensure_latest_view(connection: sqlite3.Connection) -> None:
    """Refresh the helper view exposing latest defensive tiers per season."""

    connection.execute("DROP VIEW IF EXISTS defense_ratings_latest")
    cols = {row[1] for row in connection.execute("PRAGMA table_info(defense_ratings)")}
    select_cols = [
        "r.defteam",
        "r.season",
        "r.pos",
        "r.week",
        "r.score",
        "r.tier",
    ]
    if "score_adj" in cols:
        select_cols.append("r.score_adj")
    else:
        select_cols.append("NULL AS score_adj")
    if "tier_adj" in cols:
        select_cols.append("r.tier_adj")
    else:
        select_cols.append("NULL AS tier_adj")
    select_sql = ",\n               ".join(select_cols)
    connection.execute(
        f"""
        CREATE VIEW defense_ratings_latest AS
        SELECT {select_sql}
        FROM defense_ratings AS r
        WHERE COALESCE(r.week, -1) = (
            SELECT COALESCE(MAX(r2.week), -1)
            FROM defense_ratings AS r2
            WHERE r2.defteam = r.defteam
              AND r2.season = r.season
              AND r2.pos = r.pos
        )
        """
    )


def _compute_qb_pass_adjusted_scores(pbp: pd.DataFrame) -> pd.DataFrame:
    """Return opponent-adjusted QB pass defense scores (weekly, per team)."""

    if pbp.empty:
        return pd.DataFrame()

    pass_df = pbp.loc[pbp["is_pass"] == 1].copy()
    pass_df = pass_df.dropna(subset=["defteam", "posteam"])
    if pass_df.empty:
        return pd.DataFrame()
    pass_df["defteam"] = pass_df["defteam"].str.upper().str.strip()
    pass_df["posteam"] = pass_df["posteam"].str.upper().str.strip()
    pass_df["season"] = pd.to_numeric(pass_df["season"], errors="coerce").astype("Int64")
    pass_df["week"] = pd.to_numeric(pass_df["week"], errors="coerce").astype("Int64")
    pass_df = pass_df.dropna(subset=["season", "week"])

    pass_df["epa"] = pd.to_numeric(pass_df.get("epa"), errors="coerce")
    metric_col = "epa"
    if pass_df["epa"].notna().sum() == 0:
        metric_col = "successful"
    metric_series = pd.to_numeric(pass_df[metric_col], errors="coerce")
    pass_df["metric_value"] = metric_series
    pass_df = pass_df.dropna(subset=["metric_value"])
    if pass_df.empty:
        return pd.DataFrame()

    group_cols = ["season", "week", "defteam", "posteam"]
    agg = (
        pass_df.groupby(group_cols, as_index=False)
        .agg(metric_value=("metric_value", "mean"), plays=("metric_value", "count"))
        .rename(columns={"metric_value": "metric_mean"})
    )
    agg = agg[agg["plays"] > 0]
    if agg.empty:
        return pd.DataFrame()

    agg = agg.sort_values(["season", "week"]).reset_index(drop=True)
    off_teams = sorted(agg["posteam"].dropna().unique())
    def_teams = sorted(agg["defteam"].dropna().unique())
    if len(off_teams) <= 1 or len(def_teams) <= 1:
        return pd.DataFrame()

    off_cols = [f"off_{team}" for team in off_teams[1:]]
    def_cols = [f"def_{team}" for team in def_teams[1:]]
    columns = off_cols + def_cols
    X = pd.DataFrame(0.0, index=agg.index, columns=columns)
    for team, col in zip(off_teams[1:], off_cols):
        X.loc[agg["posteam"] == team, col] = 1.0
    for team, col in zip(def_teams[1:], def_cols):
        X.loc[agg["defteam"] == team, col] = 1.0

    y = agg["metric_mean"].astype(float).values
    ordinal = agg["season"].astype(int) * 100 + agg["week"].astype(int)
    decay = 6.0
    recency_weight = np.exp((ordinal - ordinal.max()) / decay)
    weights = agg["plays"].astype(float).values * recency_weight

    alphas = [0.01, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
    model = RidgeCV(alphas=alphas, fit_intercept=True)
    model.fit(X.values, y, sample_weight=weights)

    coef = pd.Series(model.coef_, index=columns)
    offense_effect = {off_teams[0]: 0.0}
    for team, col in zip(off_teams[1:], off_cols):
        offense_effect[team] = float(coef.get(col, 0.0))
    defense_effect = {def_teams[0]: 0.0}
    for team, col in zip(def_teams[1:], def_cols):
        defense_effect[team] = float(coef.get(col, 0.0))

    agg["off_effect"] = agg["posteam"].map(offense_effect).fillna(0.0)
    agg["def_effect"] = agg["defteam"].map(defense_effect).fillna(0.0)
    agg["adjusted_value"] = agg["metric_mean"] - agg["off_effect"] - model.intercept_

    weekly_rows = []
    for (season, week, defteam), group in agg.groupby(["season", "week", "defteam"]):
        plays = group["plays"].astype(float).values
        values = group["adjusted_value"].astype(float).values
        total = plays.sum()
        if total <= 0:
            continue
        weighted = float(np.average(values, weights=plays))
        weekly_rows.append(
            {
                "season": int(season),
                "week": int(week),
                "defteam": defteam,
                "score_adj": weighted,
                "exposure": total,
            }
        )

    weekly_df = pd.DataFrame(weekly_rows)
    if weekly_df.empty:
        return pd.DataFrame()

    weekly_df = weekly_df.sort_values(["defteam", "season", "week"]).reset_index(drop=True)

    def _smooth(group: pd.DataFrame, alpha: float = 0.35) -> pd.DataFrame:
        ema = None
        scores = []
        for value in group["score_adj"].astype(float):
            if ema is None:
                ema = value
            else:
                ema = alpha * value + (1 - alpha) * ema
            scores.append(ema)
        group = group.copy()
        group["score_adj"] = scores
        return group

    weekly_df = (
        weekly_df.groupby(["defteam", "season"], group_keys=False)
        .apply(_smooth)
        .reset_index(drop=True)
    )

    def _assign_tiers(group: pd.DataFrame) -> pd.DataFrame:
        group = group.copy()
        values = group["score_adj"].astype(float)
        if values.notna().sum() < 3:
            ranks = values.rank(pct=True)
            tiers = np.where(ranks >= 0.8, "generous", np.where(ranks <= 0.2, "stingy", "neutral"))
            group["tier_adj"] = tiers
            return group
        try:
            tiers = pd.qcut(values, q=[0, 0.2, 0.8, 1], labels=["stingy", "neutral", "generous"])
            group["tier_adj"] = tiers.astype(str)
        except ValueError:
            ranks = values.rank(pct=True)
            group["tier_adj"] = np.where(
                ranks >= 0.8, "generous", np.where(ranks <= 0.2, "stingy", "neutral")
            )
        return group

    weekly_df = (
        weekly_df.groupby(["season", "week"], group_keys=False)
        .apply(_assign_tiers)
        .reset_index(drop=True)
    )

    weekly_df["pos"] = "QB_PASS"
    return weekly_df[["defteam", "season", "week", "pos", "score_adj", "tier_adj"]]


def _prepare_local_pbp(path: Path, season: int) -> pd.DataFrame:
    df = pd.read_csv(path, low_memory=False)
    rename_map = {
        "defense": "defteam",
        "targeted_receiver_id": "receiver_player_id",
        "runner_id": "rusher_player_id",
        "gamekey_internal": "game_id",
    }
    df = df.rename(columns=rename_map)
    df["season"] = season
    for col in ["week", "yards_gained", "distance", "yards_to_endzone", "first_down_gained"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df["play_type"] = df["play_type"].str.upper().fillna("")
    df["pass"] = (df["play_type"] == "PASS").astype(int)
    df["rush"] = (df["play_type"] == "RUSH").astype(int)
    df["yards_gained"] = df["yards_gained"].fillna(0)
    df["distance"] = df.get("distance", np.nan)
    df["first_down_gained"] = df.get("first_down_gained", 0).fillna(0)
    df["epa"] = np.nan  # placeholder when advanced dataset lacks EPA
    df["successful"] = (df.get("first_down_gained", 0) == 1) | (
        df["yards_gained"] >= df.get("distance", np.nan)
    )
    df["explosive_pass"] = (df["pass"] == 1) & (df["yards_gained"] >= 20)
    df["explosive_rush"] = (df["rush"] == 1) & (df["yards_gained"] >= 10)
    return df


def _prepare_local_roster(path: Path, season: int) -> pd.DataFrame:
    df = pd.read_csv(path, low_memory=False)
    df = df.rename(columns={"team": "recent_team"})
    df["season"] = season
    for col in ["week"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df["position"] = df["position"].str.upper().str.strip()
    return df[["player_id", "position"] + [c for c in ["season", "week"] if c in df.columns]]


def load_pbp_data(seasons: Iterable[int]) -> pd.DataFrame:
    frames: List[pd.DataFrame] = []
    remote_seasons: List[int] = []
    for season in seasons:
        local_path = LOCAL_PBP.get(season)
        if local_path and local_path.exists():
            print(f"     Using local PBP for {season} ({local_path.name})")
            frames.append(_prepare_local_pbp(local_path, season))
        else:
            remote_seasons.append(season)
    if remote_seasons:
        print(f"     Fetching nflverse PBP for seasons: {remote_seasons}")
        frames.append(nfl.import_pbp_data(remote_seasons))
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True, sort=False)


def load_weekly_rosters(seasons: Iterable[int]) -> pd.DataFrame:
    frames: List[pd.DataFrame] = []
    remote_seasons: List[int] = []
    for season in seasons:
        local_path = LOCAL_ROSTERS.get(season)
        if local_path and local_path.exists():
            print(f"     Using local roster for {season} ({local_path.name})")
            frames.append(_prepare_local_roster(local_path, season))
        else:
            remote_seasons.append(season)
    if remote_seasons:
        print(f"     Fetching nflverse rosters for seasons: {remote_seasons}")
        remote_frames: List[pd.DataFrame] = []
        for season in remote_seasons:
            try:
                remote_frames.append(nfl.import_weekly_rosters([season]))
            except Exception as exc:
                print(f"       Warning: failed to load rosters for {season} ({exc})")
        if remote_frames:
            remote = pd.concat(remote_frames, ignore_index=True, sort=False)
            frames.append(remote[["player_id", "position", "season", "week"]])
    if not frames:
        return pd.DataFrame(columns=["player_id", "position", "season", "week"])
    roster = pd.concat(frames, ignore_index=True, sort=False)
    roster["position"] = roster["position"].str.upper().str.strip()
    roster = roster.drop_duplicates(subset=["player_id"], keep="last")
    return roster[["player_id", "position", "season", "week"]]


print("[1/5] Loading play-by-play...")
pbp = load_pbp_data(SEASONS)
print(f"     Rows: {len(pbp):,}")

print("[2/5] Loading weekly rosters for positions...")
rosters = load_weekly_rosters(SEASONS)[["player_id", "position"]]

# Basic flags
pbp["pass"] = pd.to_numeric(pbp.get("pass", 0), errors="coerce").fillna(0)
pbp["rush"] = pd.to_numeric(pbp.get("rush", 0), errors="coerce").fillna(0)
pbp["yards_gained"] = pd.to_numeric(pbp.get("yards_gained", 0), errors="coerce").fillna(0)
pbp["ydstogo"] = pd.to_numeric(pbp.get("ydstogo"), errors="coerce")
pbp["distance"] = pd.to_numeric(pbp.get("distance"), errors="coerce")
pbp["is_pass"] = pbp["pass"] == 1
pbp["is_rush"] = pbp["rush"] == 1
pbp["first_down"] = pd.to_numeric(pbp.get("first_down"), errors="coerce")
pbp["first_down_gained"] = pd.to_numeric(pbp.get("first_down_gained"), errors="coerce")
if "epa" in pbp.columns:
    pbp["epa"] = pd.to_numeric(pbp["epa"], errors="coerce")
    epa_series = pbp["epa"]
else:
    epa_series = pd.Series(np.nan, index=pbp.index)
success_from_epa = epa_series.notna() & (epa_series > 0)
# Fallback success metric for datasets without EPA
distance_metric = pbp["ydstogo"].fillna(pbp["distance"]).fillna(np.inf)
success_alt = (pbp["first_down"].fillna(0) == 1) | (pbp["first_down_gained"].fillna(0) == 1)
success_alt |= pbp["yards_gained"] >= distance_metric
pbp["successful"] = success_from_epa | success_alt
pbp["explosive_pass"] = pbp["is_pass"] & (pbp["yards_gained"] >= 20)
pbp["explosive_rush"] = pbp["is_rush"] & (pbp["yards_gained"] >= 10)

# Join positions for targeted receiver / rusher (may be NaN early in season)
pbp = pbp.merge(
    rosters.add_prefix("rec_"), left_on="receiver_player_id", right_on="rec_player_id", how="left"
)
pbp = pbp.merge(
    rosters.add_prefix("rush_"), left_on="rusher_player_id", right_on="rush_player_id", how="left"
)


def agg(df: pd.DataFrame) -> pd.Series:
    return pd.Series(
        {
            "plays": len(df),
            "epa_per_play": df["epa"].mean(),
            "success_rate": df["successful"].mean(),
            "yards_per_play": df["yards_gained"].mean(),
            "explosive_rate": (
                df["explosive_pass"].mean() if df["is_pass"].any() else df["explosive_rush"].mean()
            ),
        }
    )


print("[3/5] Aggregating by defense & position buckets...")
buckets = {
    "QB_PASS": pbp.loc[pbp["is_pass"]],
    "RB_RUSH": pbp.loc[pbp["is_rush"] & (pbp["rush_position"] == "RB")],
    "RB_REC": pbp.loc[pbp["is_pass"] & (pbp["rec_position"] == "RB")],
    "WR": pbp.loc[pbp["is_pass"] & (pbp["rec_position"] == "WR")],
    "TE": pbp.loc[pbp["is_pass"] & (pbp["rec_position"] == "TE")],
}

parts = []
for pos, df in buckets.items():
    if df.empty:
        continue
    working = df.copy()
    if pos in {"QB_PASS", "RB_REC", "WR", "TE"}:
        source_col = "explosive_pass"
    else:
        source_col = "explosive_rush"
    working["explosive_metric"] = pd.to_numeric(working.get(source_col), errors="coerce")
    grouped = working.groupby(["defteam", "season", "week"], as_index=False).agg(
        plays=("epa", "size"),
        epa_per_play=("epa", "mean"),
        success_rate=("successful", "mean"),
        yards_per_play=("yards_gained", "mean"),
        explosive_rate=("explosive_metric", "mean"),
    )
    grouped["pos"] = pos
    parts.append(grouped)

ratings = pd.concat(parts, ignore_index=True)
ratings = ratings.sort_values(["defteam", "pos", "season", "week"])

# Rolling last-8 with min 4 games to stabilize
MIN_ROLL_GAMES = 4
for col in ["plays", "epa_per_play", "yards_per_play", "explosive_rate", "success_rate"]:
    if col == "plays":
        ratings["roll_plays8"] = ratings.groupby(["defteam", "pos"])[col].transform(
            lambda s: s.rolling(8, min_periods=MIN_ROLL_GAMES).sum()
        )
    else:
        ratings[f"roll_{col}8"] = ratings.groupby(["defteam", "pos"])[col].transform(
            lambda s: s.rolling(8, min_periods=MIN_ROLL_GAMES).mean()
        )
for col in [
    "roll_epa_per_play8",
    "roll_yards_per_play8",
    "roll_explosive_rate8",
    "roll_success_rate8",
]:
    if col not in ratings.columns:
        ratings[col] = np.nan


def safe_z(x: pd.Series) -> pd.Series:
    mu = x.mean()
    sd = x.std(ddof=0)
    if not np.isfinite(sd) or sd == 0:
        return pd.Series(np.zeros(len(x)), index=x.index)
    return (x - mu) / sd


print("[4/5] Computing league z-scores and tiers...")


def league_scores(df: pd.DataFrame) -> pd.DataFrame:
    # higher score => more generous defense to that position
    components: List[pd.Series] = []
    weights: List[float] = []
    if "roll_epa_per_play8" in df and df["roll_epa_per_play8"].notna().any():
        components.append(safe_z(df["roll_epa_per_play8"]))
        weights.append(0.5)
    elif "roll_success_rate8" in df and df["roll_success_rate8"].notna().any():
        components.append(safe_z(df["roll_success_rate8"]))
        weights.append(0.5)
    if "roll_yards_per_play8" in df and df["roll_yards_per_play8"].notna().any():
        components.append(safe_z(df["roll_yards_per_play8"]))
        weights.append(0.3)
    if "roll_explosive_rate8" in df and df["roll_explosive_rate8"].notna().any():
        components.append(safe_z(df["roll_explosive_rate8"]))
        weights.append(0.2)
    if not components:
        score = pd.Series(np.zeros(len(df)), index=df.index)
    else:
        total_weight = sum(weights)
        score = sum(w * comp.fillna(0) for w, comp in zip(weights, components)) / total_weight
    out = df[["defteam", "season", "week", "pos"]].copy()
    out["score"] = score
    # tiers: bottom 20% stingy, mid neutral, top 20% generous
    # If too few teams for qcut, fall back to labels by rank
    try:
        out["tier"] = pd.qcut(
            out["score"], q=[0, 0.2, 0.8, 1], labels=["stingy", "neutral", "generous"]
        )
    except ValueError:
        ranks = out["score"].rank(pct=True)
        out["tier"] = np.where(
            ranks >= 0.8, "generous", np.where(ranks <= 0.2, "stingy", "neutral")
        )
    return out


metric_cols = [
    "roll_epa_per_play8",
    "roll_yards_per_play8",
    "roll_explosive_rate8",
    "roll_success_rate8",
]
valid_mask = ratings[metric_cols].notna().any(axis=1)
league = (
    ratings.loc[valid_mask]
    .groupby(["season", "week", "pos"], as_index=False)
    .apply(league_scores)
    .reset_index(drop=True)
)

qb_pass_adj = _compute_qb_pass_adjusted_scores(pbp)
if qb_pass_adj.empty:
    league["score_adj"] = pd.NA
    league["tier_adj"] = pd.NA
else:
    league = league.merge(
        qb_pass_adj,
        on=["defteam", "season", "week", "pos"],
        how="left",
    )
    league["score_adj"] = pd.to_numeric(league["score_adj"], errors="coerce")
    mask = league["score_adj"].notna()
    tier_col = league.get("tier_adj")
    if isinstance(tier_col, pd.Series):
        league.loc[mask, "tier"] = league.loc[mask, "tier_adj"].where(
            league.loc[mask, "tier_adj"].notna(), league.loc[mask, "tier"]
        )
    league.loc[mask, "score"] = league.loc[mask, "score_adj"]
    if "tier_adj" not in league.columns:
        league["tier_adj"] = pd.NA

for col in ("score_adj", "tier_adj"):
    if col not in league.columns:
        league[col] = pd.NA

league["score_adj"] = pd.to_numeric(league["score_adj"], errors="coerce")
league["tier_adj"] = league["tier_adj"].astype("string")
league = league[["defteam", "season", "week", "pos", "score", "tier", "score_adj", "tier_adj"]]

print("[5/5] Writing to SQLite...")
with sqlite3.connect("storage/odds.db") as con:
    con.execute(
        """
      CREATE TABLE IF NOT EXISTS defense_ratings (
        defteam TEXT, season INT, week INT, pos TEXT,
        score REAL, tier TEXT,
        score_adj REAL, tier_adj TEXT,
        PRIMARY KEY(defteam, season, week, pos)
      )
    """
    )
    existing_cols = {row[1] for row in con.execute("PRAGMA table_info(defense_ratings)")}
    if "score_adj" not in existing_cols:
        con.execute("ALTER TABLE defense_ratings ADD COLUMN score_adj REAL")
    if "tier_adj" not in existing_cols:
        con.execute("ALTER TABLE defense_ratings ADD COLUMN tier_adj TEXT")
    con.execute("DELETE FROM defense_ratings;")
    league.to_sql("defense_ratings", con, if_exists="append", index=False)
    _ensure_latest_view(con)

print("Done. Rows:", len(league))
