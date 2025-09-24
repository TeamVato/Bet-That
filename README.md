# Bet-That

Player prop modeling, odds ingestion, and edge reporting utilities for NFL betting workflows.

## Project structure

- `jobs/` contains repeatable scripts for ingesting source data and producing derived tables.
- `engine/` implements the edge computation logic.
- `storage/odds.db` is the primary SQLite database used by the jobs and UI.
- `storage/imports/` and `storage/exports/` hold CSV snapshots exchanged with external systems.
- `app/streamlit_app.py` powers the local dashboard for exploring edges.

## Requirements & environment

1. Install dependencies with `python -m pip install -r requirements.txt`.
2. Copy `config/.env.example` to your own `.env` (or export the variables in your shell) if you plan to use the The Odds API poller or override importer settings.
3. Run `python db/migrate.py` once to initialize the SQLite schema if `storage/odds.db` does not exist yet.

Key environment variables:

- `ODDS_API_KEYS` – comma separated Odds API keys used by the poller (`jobs/poll_odds.py`). Keys rotate daily based on the day-of-year. You can also set a single `ODDS_API_KEY` for ad-hoc runs.
- `CSV_PATH`, `CSV_BATCH_SIZE`, `SQLITE_LOCK_RETRIES`, `SQLITE_LOCK_SLEEP` – optional overrides for the CSV importer.
- `SHEETS_EXPORT_URL` – optional, used by GitHub Actions when pulling the daily CSV from Google Sheets.

## Makefile shortcuts

The repo ships with common commands:

```bash
make db-ratings     # build defense tiers in storage/odds.db
make import-odds    # load the latest odds CSV snapshot
make edges          # recompute projections + edges from the DB
make ui             # launch the Streamlit dashboard (opens a browser)
```

`make` ensures jobs run with the current working directory on `PYTHONPATH` so imports resolve correctly.

## Daily runbook

1. **Weekly (recommended Monday AM):** `make db-ratings` to refresh defensive tiers using nflverse play-by-play and roster data.
2. **Daily after Apps Script / Sheets export finishes:** download the CSV snapshot into `storage/imports/odds_snapshot.csv`, then run `make import-odds edges`.
   - `make import-odds` truncates and reloads `odds_csv_raw` inside `storage/odds.db` using WAL mode and retry-on-lock semantics.
   - `make edges` persists refreshed QB projections, merges defense tiers if available, and exports `storage/exports/edges_latest.csv`.
3. **Ad-hoc UI checks:** run `make ui` to open the Streamlit interface against the latest database contents.

If defense ratings are missing (for example, during preseason), projections and edge computation continue to work. The code fails open and simply omits the defense adjustments.

## Optional: Python Odds API poller

`jobs/poll_odds.py` is available if you prefer polling The Odds API directly instead of relying on Apps Script. Highlights:

- Reads `ODDS_API_KEYS` and rotates keys based on the day-of-year (`tm_yday % n_keys`).
- Constrains requests to NFL (`americanfootball_nfl`) with a tight default list of books and markets to conserve credits.
- Logs The Odds API usage headers (`X-Requests-Used`, `X-Requests-Remaining`, `X-Requests-Reset`).
- Runs once by default (`python jobs/poll_odds.py --once`). Pass `--loop --sleep <seconds>` for interval polling.

Enable by exporting the desired bookmaker/market lists and ensuring the SQLite schema exists (`python db/migrate.py`). Snapshots are persisted to `odds_snapshots` and the `current_best_lines` helper table refreshes automatically after every run.

## Automation (GitHub Actions)

`.github/workflows/edges.yml` schedules a daily run at 15:00 UTC (09:00 Denver). It executes the same sequence as the runbook:

1. Install dependencies.
2. Build defense ratings.
3. (Optionally) download the Sheets export via `SHEETS_EXPORT_URL`.
4. Import the CSV and recompute edges.

Populate repository secrets:

- `ODDS_API_KEYS` – required if you want the workflow to use the Python poller instead of Google Sheets.
- `SHEETS_EXPORT_URL` – optional public export URL for the Sheets snapshot when sticking with Apps Script.

Disable the `schedule` trigger or switch to `workflow_dispatch` only if you prefer to run the workflow manually.

## Smoke tests

After updating dependencies or logic, run the jobs end-to-end:

```bash
python jobs/build_defense_ratings.py
python jobs/import_odds_from_csv.py
python jobs/compute_edges.py
```

Verify outputs with:

```bash
test -f storage/exports/edges_latest.csv
sqlite3 storage/odds.db "select count(*) from defense_ratings;"
sqlite3 storage/odds.db "select defteam, pos, season, week, tier, round(score,3) from defense_ratings limit 5;"
```

Successful runs should not require access to services beyond the public nflverse CSV files.
