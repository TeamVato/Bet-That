#!/usr/bin/env bash
set -euo pipefail

makefile=${1:-Makefile}

if [[ ! -f "$makefile" ]]; then
  echo "error: $makefile not found" >&2
  exit 1
fi

status=0

if LC_ALL=C grep -n $'\r' "$makefile" >/dev/null; then
  echo "error: CRLF line endings detected in $makefile" >&2
  LC_ALL=C grep -n $'\r' "$makefile" >&2
  status=1
fi

if grep -nE '^(<<<<<<<|=======|>>>>>>>)' "$makefile" >/dev/null; then
  echo "error: merge conflict markers detected in $makefile" >&2
  grep -nE '^(<<<<<<<|=======|>>>>>>>)' "$makefile" >&2
  status=1
fi

awk 'function is_target(line) {
        gsub(/^[ \t]+/, "", line)
        if (line ~ /^#/ || line == "") {
            return 0
        }
        if (line ~ /:=/ || line ~ /::=/ || line ~ /\?=/ || line ~ /\+=/) {
            return 0
        }
        return line ~ /:/
     }
     {
        raw = $0
        if (is_target(raw)) {
            in_recipe = 1
        } else if (raw ~ /^\t/) {
            in_recipe = 1
        } else if (raw ~ /^[^ \t]/ || raw ~ /^[ \t]*$/) {
            in_recipe = 0
        }
        if (in_recipe && raw ~ /^ +/) {
            printf("%d:%s\n", NR, raw) > "/dev/stderr"
            bad = 1
        }
     }
     END { exit bad }
' "$makefile" || {
  echo "error: space-indented recipe lines detected in $makefile" >&2
  status=1
}

exit $status
