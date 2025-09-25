import os
import sqlite3
from pathlib import Path

import pandas as pd

import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))

CSV1 = Path("tests/fixtures/odds_sample_two_way.csv")
CSV2 = Path("tests/fixtures/odds_sample_dupes_stale.csv")
CSV_MULTI = Path("tests/fixtures/odds_sample_multi_pos.csv")
CSV_NORM = Path("tests/fixtures/odds_book_pos_normalization.csv")


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


def test_book_normalization_and_pos_inference(monkeypatch, tmp_path):
    """Test that mixed-case books are normalized and pos is inferred from market names."""
    run_import(CSV_NORM)
    with sqlite3.connect("storage/odds.db") as con:
        df = pd.read_sql("SELECT book, market, pos FROM odds_csv_raw ORDER BY book, market", con)

    # Test book normalization
    books = df["book"].dropna().unique().tolist()
    expected_books = {"DraftKings", "FanDuel", "BetMGM", "Caesars"}
    assert expected_books.issubset(set(books)), f"Expected normalized books, got {books}"

    # Ensure no mixed-case variants remain
    assert "draftkings" not in books
    assert "dk" not in books
    assert "fanduel" not in books
    assert "betmgm" not in books
    assert "CAESARS" not in books

    # Test pos inference for different market types
    pass_rows = df[df["market"] == "player_pass_yds"]
    assert all(pass_rows["pos"] == "QB"), "Pass yards should infer QB position"

    rush_rows = df[df["market"].str.contains("rush", na=False)]
    assert all(rush_rows["pos"] == "RB"), "Rush markets should infer RB position"

    rec_rows = df[df["market"] == "player_receptions"]
    assert all(rec_rows["pos"] == "WR"), "Receptions should infer WR position by default"

    longest_rec_rows = df[df["market"] == "longest reception"]
    assert all(longest_rec_rows["pos"] == "WR"), "Longest reception should infer WR position"

    # Verify all rows have non-empty pos where inferable
    inferable_markets = df[df["market"].isin([
        "player_pass_yds", "player_rush_yds", "player_receptions",
        "longest reception", "rushing attempts"
    ])]
    assert inferable_markets["pos"].notna().all(), "All inferable markets should have pos"
