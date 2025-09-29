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


def test_select_key_breaks_ties_on_usage_and_key_order(tmp_path):
    db = tmp_path / "odds.db"
    con = sqlite3.connect(db)
    ensure_usage_table(con)
    keys = ["a_key", "b_key"]
    con.executemany(
        "INSERT INTO odds_api_usage(key,last_remaining,req_month,disabled) VALUES(?,?,?,?)",
        [("a_key", 100, 5, 0), ("b_key", 100, 3, 0)],
    )
    # b_key has same remaining but fewer monthly requests, so should be preferred
    assert select_key(con, keys) == "b_key"
    # If monthly usage equal, prefer lexical order
    con.execute("UPDATE odds_api_usage SET req_month = 5 WHERE key = ?", ("b_key",))
    assert select_key(con, keys) == "a_key"
