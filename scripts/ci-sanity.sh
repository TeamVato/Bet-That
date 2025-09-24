#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "${BASH_SOURCE[0]%/*}" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

TARGETS=(
  repo-status
  repo-fresh
  repo-clean
  audit-quarantine
  pr-fix-dirty-tripwire
)

for target in "${TARGETS[@]}"; do
  echo "==> make DRY=1 $target"
  make "DRY=1" "$target"
  echo
done
