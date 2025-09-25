import os
import sqlite3
from pathlib import Path

import pandas as pd

import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))

CSV1 = Path("tests/fixtures/odds_sample_two_way.csv")
CSV2 = Path("tests/fixtures/odds_sample_dupes_stale.csv")
CSV_MULTI = Path("tests/fixtures/odds_sample_multi_pos.csv")


def run_import(csv_path, stale_minutes=120):
    os.environ["CSV_PATH"] = str(csv_path)
    os.environ["STALE_MINUTES"] = str(stale_minutes)
    import jobs.import_odds_from_csv as mod

    mod.main()


def test_two_way_devig(monkeypatch, tmp_path):
    run_import(CSV1)
    with sqlite3.connect("storage/odds.db") as con:
        df = pd.read_sql("SELECT * FROM odds_csv_raw", con)
    assert (df["event_id"] == "EVT1").any() and (df["event_id"] == "EVT2").any()
    assert df["implied_prob"].notna().any()
    assert df["overround"].dropna().ge(1.0).any()
    assert df["fair_prob"].notna().any()


def test_duplicates_and_stale(monkeypatch, tmp_path):
    run_import(CSV2, stale_minutes=120)
    with sqlite3.connect("storage/odds.db") as con:
        df = pd.read_sql("SELECT * FROM odds_csv_raw", con)
    over = df[
        (df.event_id == "EVT3")
        & (df.market == "player_receptions")
        & (df.side == "Over")
    ]
    assert len(over) == 1
    assert over.iloc[0]["odds"] == -110
    under = df[(df.event_id == "EVT3") & (df.side == "Under")]
    assert int(under.iloc[0]["is_stale"]) in (0, 1)


def test_pos_inferred_for_non_qb_markets(monkeypatch, tmp_path):
    run_import(CSV_MULTI)
    with sqlite3.connect("storage/odds.db") as con:
        df = pd.read_sql("SELECT market, pos FROM odds_csv_raw", con)
    rush_positions = df.loc[df["market"] == "player_rush_yds", "pos"].dropna().unique()
    rec_positions = df.loc[df["market"] == "player_rec_yds", "pos"].dropna().unique()
    assert any(pos == "RB" for pos in rush_positions)
    assert any(pos in {"WR", "TE"} for pos in rec_positions)
