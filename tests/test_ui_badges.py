from app.ui_badges import context_key


def test_context_key_stable_normalizes_case():
    # The function normalizes case in the base key but includes hash of original
    # So different case inputs produce different full keys but same normalized parts
    key1 = context_key("Edges", "Main")
    key2 = context_key("edges", "main")

    # Both should have the same normalized base parts
    assert key1.startswith("why_open__edges__main__")
    assert key2.startswith("why_open__edges__main__")

    # But different hashes due to original case difference
    assert key1 != key2
    assert len(key1.split("__")) == len(key2.split("__")) == 4  # why_open, edges, main, hash


def test_context_key_handles_whitespace_and_extra_parts():
    # Test whitespace handling and multiple parts
    key1 = context_key("Edges Section", "QB ", 2024)
    assert key1.startswith("why_open__edges_section__qb__2024__")

    key2 = context_key("edges", "book", "FanDuel")
    assert key2.startswith("why_open__edges__book__fanduel__")


def test_context_key_handles_special_characters():
    # Test special character handling
    key1 = context_key("edges", "book", "Fan-Duel")
    assert key1.startswith("why_open__edges__book__fan_duel__")

    key2 = context_key("matchup", "2025-09-07-kc-lv", "Patrick Mahomes")
    assert key2.startswith("why_open__matchup__2025_09_07_kc_lv__patrick_mahomes__")

    key3 = context_key("edges", "pos", None)
    assert key3.startswith("why_open__edges__pos__")
