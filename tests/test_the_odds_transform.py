import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from datetime import datetime, timezone
import json
from pathlib import Path

from adapters.odds.the_odds_api import normalize_odds_response


def test_normalize_sample_payload():
    sample_path = Path("storage/sample_odds_api_response.json")
    payload = json.loads(sample_path.read_text())
    fetched_at = datetime(2023, 9, 10, 12, 30, tzinfo=timezone.utc)
    df = normalize_odds_response(payload, fetched_at=fetched_at)
    assert not df.empty
    assert set(["fetched_at", "sport_key", "event_id", "market_key", "price"]).issubset(df.columns)
    assert len(df) == 12
    first = df.iloc[0]
    assert first["event_id"] == "afc-east-showdown"
    assert first["market_key"] in {"h2h", "spreads", "totals"}
