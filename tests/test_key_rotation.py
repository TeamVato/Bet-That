import sqlite3

from jobs.poll_odds import ensure_usage_table, select_key


def test_select_key_prefers_non_disabled_with_more_remaining(tmp_path):
    db = tmp_path / "odds.db"
    con = sqlite3.connect(db)
    ensure_usage_table(con)
    keys = ["k1", "k2", "k3"]
    con.executemany(
        "INSERT INTO odds_api_usage(key,last_remaining,req_month,disabled) VALUES(?,?,?,?)",
        [("k1", 50, 10, 0), ("k2", 100, 20, 0), ("k3", 0, 5, 1)],
    )
    k = select_key(con, keys)
    assert k == "k2"

