# Bet-That — NFL betting edge finder MVP

Beginner-friendly, batteries-included starter kit for monitoring NFL odds, building a
transparent QB passing yards projection, and surfacing value edges.

## Features

- ✅ Poll The Odds API with retries, rate-limit awareness, and SQLite persistence
- ✅ Offline-friendly CSV adapter for QB passing props (alt lines supported)
- ✅ Simple QB projection model (recent form + defense + manual news flags + weather stub)
- ✅ Edge engine computes no-vig probabilities, EV, and fractional Kelly stakes
- ✅ Streamlit dashboard plus BI exports (CSV/Parquet) for Tableau/Power BI
- ✅ Optional R EDA script sharing the same SQLite backend
- ✅ Modular adapters so you can plug in premium data providers later

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp config/.env.example .env  # set ODDS_API_KEY and other secrets
python db/migrate.py
```

Populate sample data and compute demo edges (offline):

```bash
python jobs/compute_edges.py
```

Launch the Streamlit UI:

```bash
streamlit run app/streamlit_app.py
```

### Polling live odds

```bash
python jobs/poll_odds.py              # one-time snapshot
python jobs/poll_odds.py --interval 300  # loop every 5 minutes
```

The poller writes line history into `storage/odds.db` and updates the
`current_best_lines` table for quick line shopping. Run `jobs/compute_edges.py`
again after polling to refresh projections and edges.

### BI exports

The edge job writes `storage/exports/edges_latest.csv`/`.parquet`. Generate a full
BI bundle with:

```bash
python jobs/export_bi.py
```

Connect Tableau/Power BI directly to the CSV/Parquet exports or point an ODBC
connection at `storage/odds.db`.

### Streamlit app

The app lets you filter edges by season, odds range, and minimum EV, review line
shopping highlights, view recent steam alerts, and export today’s picks to
`storage/exports/picks_latest.csv` while logging them to the `bets_log` table.

## Architecture

```
+-------------------+       +------------------+      +------------------+
| Odds adapters     |-----> | SQLite (odds.db) | <----| nflverse + CSV   |
| - The Odds API    |       |  - odds history  |      |  projections     |
| - CSV props       |       |  - projections   |      |                  |
+-------------------+       +------------------+      +------------------+
          |                           |                           |
          v                           v                           v
   jobs/poll_odds.py        models/qb_projection.py         engine/edge_engine.py
          |                           |                           |
          +-------------> storage/exports/ <----------------------+
```

Adapters follow a pluggable pattern so you can drop in new providers without
rewriting the engine. Odds snapshots are stored in SQLite with timestamps for
closing-line value analysis and steam detection. Projections join props odds with
nflverse player logs (via `nfl_data_py`) and optional manual overrides from
`storage/player_flags.yaml`.

## Odds ingestion

- Uses The Odds API’s `/sports/{sport}/odds` endpoint (`americanfootball_nfl`)
- Respects region/market/format configuration from `.env`
- Retries with exponential backoff (tenacity) and logs remaining quota
- Deduplicates snapshots with a UNIQUE constraint

## Projection model

- Recent form: rolling mean of last N games (default 8)
- Defense adjustment: compares opponent YPG allowed vs league average
- Weather adjustment: simple multipliers (hooks provided for real API)
- Manual overrides: YAML flags for snap count / injury adjustments
- Sigma: RMSE of recent games clipped to [35, 80]
- Probabilities: normal approximation via `scipy.stats.norm`

## Edge engine

- Converts American odds to no-vig implied probabilities
- Computes EV per $1 and quarter-Kelly stake (capped at 5%)
- Labels strategies (baseline vs alt-line attacks)
- Persists results to `edges` table and exports CSV/Parquet

## Storage layout

- `db/schema.sql` defines tables and indexes
- `db/migrate.py` runs migrations (SQLite only in this MVP)
- `storage/odds.db` holds all application data
- `storage/exports/` contains generated CSV/Parquet reports

## Testing

```bash
pytest
```

Unit tests cover the odds math helpers and normalization of The Odds API payloads.

## Scheduling

See [`jobs/examples.cron.md`](jobs/examples.cron.md) for cron/systemd/Windows Task
Scheduler templates. A sample GitHub Actions workflow is included at
`.github/workflows/poll_odds.yml` (beware of API quotas when enabling it).

## R workflow

Run `Rscript r/eda_qb_model.R` to produce a residuals summary under
`r/exports/eda_summary.csv`. The script shares the same SQLite DB used by the
Python jobs.

## Roadmap ideas

- Integrate real weather data (NWS/Visual Crossing)
- Paid props providers (SportsData.io, etc.) via additional adapters
- Slack/Discord notifications for steam or high-EV edges
- Closing-line value tracker and bet settlement automation
- Optional FastAPI/uvicorn service for headless deployments
- Upgrade to Postgres when scaling beyond the MVP

## Compliance

- Uses only documented APIs/libraries (The Odds API, nfl_data_py)
- No scraping of sportsbook websites
- MIT-licensed for easy reuse
