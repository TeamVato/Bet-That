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
CSV_CONTRACT = Path("tests/fixtures/odds_ingestion_contract.csv")


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


def test_ingestion_contract_end_to_end(monkeypatch, tmp_path):
    """Test complete ingestion contract: book normalization, pos inference, season guarantee."""
    run_import(CSV_CONTRACT)
    with sqlite3.connect("storage/odds.db") as con:
        df = pd.read_sql("SELECT * FROM odds_csv_raw ORDER BY event_id, player, market", con)

    # Contract requirement 1: Book name normalization
    books = df["book"].dropna().unique().tolist()
    expected_normalized = {"DraftKings", "FanDuel", "BetMGM", "Caesars"}
    assert expected_normalized.issubset(set(books)), f"Expected normalized books, got {books}"

    # Should not contain any unnormalized variants
    assert "draftkings" not in books, "Found unnormalized 'draftkings'"
    assert "fanduel" not in books, "Found unnormalized 'fanduel'"
    assert "CAESARS" not in books, "Found unnormalized 'CAESARS'"
    assert "betmgm" not in books, "Found unnormalized 'betmgm'"

    # Contract requirement 2: Position inference and persistence
    # All QB markets should have QB position
    qb_markets = df[df["market"].str.contains("pass", na=False)]
    assert all(qb_markets["pos"] == "QB"), "All passing markets should have QB position"

    # All rushing markets should have RB position
    rb_markets = df[df["market"].str.contains("rush", na=False)]
    assert all(rb_markets["pos"] == "RB"), "All rushing markets should have RB position"

    # All reception markets should have WR position (default for receiving)
    rec_markets = df[df["market"].str.contains("reception", na=False)]
    assert all(rec_markets["pos"] == "WR"), "All reception markets should have WR position"

    # Contract requirement 3: Season guarantee
    assert df["season"].notna().all(), "All rows must have season information"

    # Season values should be reasonable (2020-2030 range)
    seasons = df["season"].dropna().unique()
    assert all(2020 <= season <= 2030 for season in seasons), f"Invalid seasons found: {seasons}"

    # Verify season inference from commence_time
    # 2025-09-25 should infer 2025 season
    expected_season_rows = df[df["event_id"].str.startswith("EVT_CONTRACT")]
    assert all(expected_season_rows["season"] == 2025), "Season should be inferred as 2025"

    # Contract requirement 4: End-to-end data integrity
    # Should have expected number of rows (8 from fixture)
    assert len(df) == 8, f"Expected 8 rows from contract fixture, got {len(df)}"

    # Each event should have Over/Under pairs
    event_counts = df.groupby(["event_id", "player", "market"]).size()
    assert all(count == 2 for count in event_counts), "Each market should have Over/Under pair"

    # Verify devig calculations are applied
    assert df["implied_prob"].notna().any(), "Implied probabilities should be calculated"
    assert df["fair_prob"].notna().any(), "Fair probabilities should be calculated via devig"
