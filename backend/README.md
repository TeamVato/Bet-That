# Bet-That Backend

This backend provides NFL odds data by integrating with The Odds API. It exposes FastAPI endpoints with caching and API key rotation to conserve usage.

## Setup

1. Create a virtual environment and install requirements:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Copy `.env` and replace the placeholder API keys with your credentials.
3. Ensure Redis is running locally (defaults to `redis://localhost:6379/0`).

## Running FastAPI

```bash
uvicorn app.main:app --reload --env-file .env
```

## Utilities

- `scripts/test_api_connection.py` – quick verification of API keys or demo mode
- `scripts/fetch_nfl_odds.py` – fetch and cache the current NFL week odds

See inline docstrings for details on caching, request limits, and key rotation.
