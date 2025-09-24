#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

venv_py="$ROOT/.venv/bin/python"
venv_streamlit="$ROOT/.venv/bin/streamlit"

err() { printf "\n\033[31mERROR:\033[0m %s\n\n" "$*" >&2; exit 1; }

# Preconditions
[ -x "$venv_py" ] || err "Missing .venv. Create it with: python3.12 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt"
[ -x "$venv_streamlit" ] || err "Streamlit not found in .venv; run: . .venv/bin/activate && pip install -r requirements.txt"

echo "==> Building defense ratings (open data)…"
"$venv_py" "$ROOT/jobs/build_defense_ratings.py"

# Odds CSV presence hint (Apps Script should have produced it)
CSV="$ROOT/storage/imports/odds_snapshot.csv"
if [ ! -f "$CSV" ]; then
  echo "==> NOTE: $CSV not found."
  echo "    Export your Google Sheet to this path (Apps Script runs daily at 15:00 UTC)."
  echo "    Continuing anyway (import will create tables but may be empty)."
fi

echo "==> Importing odds CSV -> SQLite…"
"$venv_py" "$ROOT/jobs/import_odds_from_csv.py"

echo "==> Computing edges…"
"$venv_py" "$ROOT/jobs/compute_edges.py"

echo "==> Launching Streamlit UI… (Ctrl+C to stop)"
PYTHONPATH="$ROOT" "$venv_streamlit" run "$ROOT/app/streamlit_app.py"
