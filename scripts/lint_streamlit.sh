#!/usr/bin/env bash
set -euo pipefail

if rg -n "use_container_width" app; then
  echo "Streamlit deprecated argument 'use_container_width' found." >&2
  exit 1
fi
