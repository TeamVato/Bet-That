from app.ui_badges import context_key


def test_context_key_stable_normalizes_case():
    assert context_key("Edges", "Main") == "why_open__edges__main"
    assert context_key("edges", "main") == "why_open__edges__main"


def test_context_key_handles_whitespace_and_extra_parts():
    assert context_key("Edges Section", "QB ", 2024) == "why_open__edges_section__qb__2024"
    assert context_key("edges", "book", "FanDuel") == "why_open__edges__book__fanduel"


def test_context_key_handles_special_characters():
    assert context_key("edges", "book", "Fan-Duel") == "why_open__edges__book__fan_duel"
    assert context_key("matchup", "2025-09-07-kc-lv", "Patrick Mahomes") == "why_open__matchup__2025_09_07_kc_lv__patrick_mahomes"
    assert context_key("edges", "pos", None) == "why_open__edges__pos"
