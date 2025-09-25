from adapters.stats_provider import import_weekly_stats


def test_import_weekly_stats_returns_df():
    df = import_weekly_stats([2024])
    assert hasattr(df, "columns")
    for col in ["season", "week", "player_id", "team", "position"]:
        assert col in df.columns
