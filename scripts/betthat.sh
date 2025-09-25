#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

export PYTHONPATH="${PYTHONPATH:-$ROOT}"
export STALE_MINUTES="${STALE_MINUTES:-120}"
export SHRINK_WEIGHT="${SHRINK_WEIGHT:-0.25}"
export DEFAULT_SEASONS="${DEFAULT_SEASONS:-2023,2024,2025}"
export SHRINK_TO_MARKET_WEIGHT="${SHRINK_TO_MARKET_WEIGHT:-$SHRINK_WEIGHT}"

COMMAND="all"
if [ $# -gt 0 ]; then
  COMMAND="$1"
  shift
fi

set -a
if [ -f "$ROOT/.env.local" ]; then
  # shellcheck disable=SC1090
  . "$ROOT/.env.local"
fi
set +a

USE_ODDS_API="${USE_ODDS_API:-0}"

if [ "$USE_ODDS_API" = "1" ] && [ -z "${ODDS_API_KEYS:-}" ] && [ ! -f "$ROOT/.env.local" ]; then
  printf 'Enter The Odds API keys (comma-separated), or leave blank to use CSV: '
  read -r input_keys
  if [ -n "$input_keys" ]; then
    {
      printf 'ODDS_API_KEYS=%s\n' "$input_keys"
      printf 'USE_ODDS_API=1\n'
    } >> "$ROOT/.env.local"
    echo "Saved to .env.local (not committed)."
    # shellcheck disable=SC1090
    . "$ROOT/.env.local"
  fi
fi

timestamp=$(date -u +%FT%TZ)
key_status=""
if [ "$USE_ODDS_API" = "1" ]; then
  if [ -n "${ODDS_API_KEYS:-}" ]; then
    key_status=" (keys set)"
  fi
  source_label="odds_api${key_status}"
else
  source_label="csv"
fi

printf 'Bet-That @ %s\n' "$timestamp"
printf 'Source: %s\n' "$source_label"
printf 'Seasons: %s | STALE_MINUTES=%s | SHRINK_WEIGHT=%s\n' \
  "$DEFAULT_SEASONS" "$STALE_MINUTES" "${SHRINK_WEIGHT:-$SHRINK_TO_MARKET_WEIGHT}"
printf 'Command: %s\n' "$COMMAND"

venv_py="$ROOT/.venv/bin/python"
venv_streamlit="$ROOT/.venv/bin/streamlit"

err() { printf "\n\033[31mERROR:\033[0m %s\n\n" "$*" >&2; exit 1; }

require_python() {
  [ -x "$venv_py" ] || err "Missing .venv. Create it with: python3.12 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt"
}

require_streamlit() {
  [ -x "$venv_streamlit" ] || err "Streamlit not found in .venv; run: . .venv/bin/activate && pip install -r requirements.txt"
}

case "$COMMAND" in
  poll)
    require_python
    echo "==> Polling The Odds API…"
    "$venv_py" "$ROOT/jobs/poll_odds.py" "$@"
    echo "==> Poll completed @ $(date -u +%FT%TZ)"
    ;;
  context)
    require_python
    echo "==> Building defense ratings (open data)…"
    "$venv_py" "$ROOT/jobs/build_defense_ratings.py"
    echo "==> Ensuring weather schema…"
    "$venv_py" "$ROOT/jobs/migrate_weather_schema.py"
    echo "==> Building matchup context (scheme, injuries, weather)…"
    "$venv_py" "$ROOT/jobs/build_matchup_context.py"
    echo "==> Context build complete @ $(date -u +%FT%TZ)"
    ;;
  edges)
    require_python
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
    echo "==> Edges computation complete @ $(date -u +%FT%TZ)"
    ;;
  all|run)
    require_python
    require_streamlit
    echo "==> Building defense ratings (open data)…"
    "$venv_py" "$ROOT/jobs/build_defense_ratings.py"

    echo "==> Ensuring weather schema…"
    "$venv_py" "$ROOT/jobs/migrate_weather_schema.py"

    echo "==> Building matchup context (scheme, injuries, weather)…"
    "$venv_py" "$ROOT/jobs/build_matchup_context.py"

    if [ "${USE_ODDS_API:-0}" = "1" ]; then
      echo "==> Polling The Odds API once (NFL-only)…"
      ODDS_API_KEYS="${ODDS_API_KEYS:-}" \
      "$venv_py" "$ROOT/jobs/poll_odds.py" --once --sport nfl --markets player_props --region us || true
    fi

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
    ;;
  *)
    err "Unknown subcommand: $COMMAND"
    ;;
esac
