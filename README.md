# Bet-That

Player prop modeling, odds ingestion, and edge reporting utilities for NFL betting workflows.

## Quickstart

```bash
pyenv install 3.12.11
pyenv local 3.12.11
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Optional VS Code helpers:

```json
{
  "python.defaultInterpreterPath": ".venv/bin/python",
  "python.terminal.activateEnvironment": true
}
```

Copy `config/.env.example` to `config/.env` (or export the variables in your shell) if you plan to use the Odds API poller or override importer settings. Run `python db/migrate.py` once to initialize the SQLite schema if `storage/odds.db` does not exist yet.

## Project structure

- `jobs/` contains repeatable scripts for ingesting source data and producing derived tables.
- `engine/` implements the edge computation logic.
- `storage/odds.db` is the primary SQLite database used by the jobs and UI.
- `storage/imports/` and `storage/exports/` hold CSV snapshots exchanged with external systems.
- `app/streamlit_app.py` powers the local dashboard for exploring edges.

## Daily workflow (local)

Apps Script (15:00 UTC) should export your Google Sheet (odds_raw tab) to `storage/imports/odds_snapshot.csv`.

```bash
./BetThat               # builds ratings, imports odds, computes edges, launches Streamlit

# Or step-by-step:
python jobs/build_defense_ratings.py
python jobs/import_odds_from_csv.py
python jobs/compute_edges.py
# Optional: auto-build defense_ratings if missing during edges computation
# export BUILD_DEFENSE_RATINGS_ON_DEMAND=1
PYTHONPATH="$PWD" streamlit run app/streamlit_app.py

# Weekly or after a slate (open-data ratings, no API credits):
python jobs/build_defense_ratings.py
```

`./BetThat` relies on the project virtualenv (`.venv`) and will surface actionable error messages if the environment is missing.

## Makefile shortcuts

The repo ships with common commands:

```bash
make betthat       # run BetThat one-touch workflow
make db-ratings    # build defense tiers in storage/odds.db
make import-odds   # load the latest odds CSV snapshot
make edges         # recompute projections + edges from the DB
make ui            # launch the Streamlit dashboard (opens a browser)
```

`make` ensures jobs run with the current working directory on `PYTHONPATH` so imports resolve correctly.

## Google Apps Script (Odds API)

- NFL only; rotates Odds API keys; prepends rows to `odds_raw`; scheduled 15:00 UTC.
- Set `ODDS_API_KEYS` in Script Properties; run `installTriggers()` once to create the timer.
- Export the sheet to `storage/imports/odds_snapshot.csv` for local runs and CI.

## CI: edges-daily workflow

- File: `.github/workflows/edges.yml`.
- Triggers: schedule at 15:00 UTC and manual `workflow_dispatch`.
- Steps: checkout → Python 3.12 → cache/install deps → (optional) fetch CSV from `SHEETS_EXPORT_URL` → build ratings → import odds → compute edges → `python tests/smoke_season.py` → upload artifacts.
- Artifacts: `storage/exports/edges_latest.csv` and `.parquet` attached to each run.
- Secrets (optional): `SHEETS_EXPORT_URL` for Google Sheets exports, `ODDS_API_KEYS` for a future Python poller.

## Optional: Python Odds API poller

`jobs/poll_odds.py` is available if you prefer polling The Odds API directly instead of relying on Apps Script. Highlights:

- Reads `ODDS_API_KEYS` and rotates keys based on the day-of-year (`tm_yday % n_keys`).
- Constrains requests to NFL (`americanfootball_nfl`) with a tight default list of books and markets to conserve credits.
- Logs The Odds API usage headers (`X-Requests-Used`, `X-Requests-Remaining`, `X-Requests-Reset`).
- Runs once by default (`python jobs/poll_odds.py --once`). Pass `--loop --sleep <seconds>` for interval polling.

Enable by exporting the desired bookmaker/market lists and ensuring the SQLite schema exists (`python db/migrate.py`). Snapshots are persisted to `odds_snapshots` and the `current_best_lines` helper table refreshes automatically after every run.

## The Odds API (NFL-only, optional)

- Set `ODDS_API_KEYS="key1,key2,..."` in your environment or CI secrets.
- One-touch workflow can poll once before import when `USE_ODDS_API=1`:

```bash
USE_ODDS_API=1 ./BetThat
```

- Standalone dry run:

```bash
python jobs/poll_odds.py --once --sport nfl --markets player_props --region us --dry-run
```

The workflow (`.github/workflows/edges.yml`) includes a conditional step to poll with `ODDS_API_KEYS` if configured. Key rotation and usage tracking are stored in `odds_api_usage`.

## Troubleshooting

- `KeyError: 'season'` → re-run the importer and edge computation; season is inferred from `commence_time`.
- `database is locked` → close Streamlit while importing; the importer retries automatically; rerun the command.
- Missing defensive tiers when computing edges → run `python jobs/build_defense_ratings.py` (or `make db-ratings`). Set `BUILD_DEFENSE_RATINGS_ON_DEMAND=1` before `python jobs/compute_edges.py` to auto-build when the table/view is absent.
- Import or module path issues → launch the UI with `PYTHONPATH="$PWD"` (the `BetThat` script already does this).


## Weekly CLV & Calibration
- Python: 3.12
- Cron: Mondays 09:00 UTC
- Outputs: `reports/weekly/YYYY-WW/CLV_Calibration_Report_YYYY-MM-DD.md|.pdf`, `status.json`
- Gating: writes `config/signal_flags.auto.yaml` and merges with `config/signal_flags.manual.yaml` → `config/signal_flags.effective.yaml`
- Alerts: Slack `[P0]/[P1]/[OK]` to #bet-that-alerts (via `SLACK_WEBHOOK_URL`)
