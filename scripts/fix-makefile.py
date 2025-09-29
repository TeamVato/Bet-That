#!/usr/bin/env python3
"""Auto-fixer for the repository Makefile.

Features:
- Normalises line endings to LF.
- Resolves merge-conflict markers by keeping the first (ours) section.
- Converts space-indented recipes to use tabs.
- Ensures the standard SHELL, DRY variable, and run helper block exist.

Use --check to exit with code 2 when changes would be made.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable, List, Tuple

EXPECTED_SHELL_LINE = "SHELL := /bin/bash"
EXPECTED_DRY_LINE = "DRY ?= 0"
RUN_BLOCK = [
    "define run",
    "\t@cmd='$(1)'; \\",
    '\tif [ "$(DRY)" = "1" ]; then \\',
    "\t\tprintf '[DRY] %s\\n' \"$$cmd\"; \\",
    "\telse \\",
    "\t\tprintf '+ %s\\n' \"$$cmd\"; \\",
    '\t\teval "$$cmd"; \\',
    "\tfi",
    "endef",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fix common Makefile issues")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Do not write changes; exit 2 if fixes are needed.",
    )
    parser.add_argument(
        "--makefile",
        default="Makefile",
        help="Path to the Makefile (default: Makefile)",
    )
    return parser.parse_args()


def normalise_newlines(text: str) -> Tuple[str, bool]:
    result = text.replace("\r\n", "\n").replace("\r", "\n")
    return result, result != text


def resolve_conflicts(lines: List[str]) -> Tuple[List[str], bool]:
    resolved: List[str] = []
    changed = False
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("<<<<<<<"):
            changed = True
            ours: List[str] = []
            theirs: List[str] = []
            i += 1
            while i < len(lines) and not lines[i].startswith("======="):
                ours.append(lines[i])
                i += 1
            if i < len(lines) and lines[i].startswith("======="):
                i += 1
                while i < len(lines) and not lines[i].startswith(">>>>>>>"):
                    theirs.append(lines[i])
                    i += 1
            if i < len(lines) and lines[i].startswith(">>>>>>>"):
                i += 1
            resolved.extend(ours or theirs)
            continue
        resolved.append(line)
        i += 1
    return resolved, changed


def is_target_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return False
    if ":=" in stripped or "::=" in stripped or "?=" in stripped or "+=" in stripped:
        return False
    if ":" not in stripped:
        return False
    return True


def enforce_recipe_tabs(lines: List[str]) -> Tuple[List[str], bool]:
    updated: List[str] = []
    changed = False
    in_recipe = False
    for line in lines:
        stripped = line.strip()
        if is_target_line(line):
            in_recipe = True
        elif not line[:1].isspace():
            in_recipe = False
        elif line.startswith("\t"):
            in_recipe = True
        elif stripped == "":
            in_recipe = False
        if in_recipe and line.startswith(" "):
            updated.append("\t" + line.lstrip(" "))
            changed = True
        else:
            updated.append(line)
    return updated, changed


def ensure_line(lines: List[str], new_line: str) -> Tuple[List[str], bool]:
    if any(l.strip() == new_line for l in lines):
        return lines, False
    insert_at = 0
    for idx, line in enumerate(lines):
        if line.strip() and not line.strip().startswith("#"):
            insert_at = idx
            break
    else:
        insert_at = len(lines)
    return lines[:insert_at] + [new_line, ""] + lines[insert_at:], True


def ensure_run_helper(lines: List[str]) -> Tuple[List[str], bool]:
    for line in lines:
        if line.strip() == "define run":
            return lines, False
    block = ["", *RUN_BLOCK, ""]
    # place run helper after DRY definition if possible
    try:
        insert_after = next(i for i, line in enumerate(lines) if line.strip().startswith("DRY")) + 1
    except StopIteration:
        insert_after = len(lines)
    return lines[:insert_after] + block + lines[insert_after:], True


def ensure_expectations(lines: List[str]) -> Tuple[List[str], bool]:
    changed = False
    lines, added_shell = ensure_line(lines, EXPECTED_SHELL_LINE)
    changed = changed or added_shell
    lines, added_dry = ensure_line(lines, EXPECTED_DRY_LINE)
    changed = changed or added_dry
    lines, added_run = ensure_run_helper(lines)
    changed = changed or added_run
    return lines, changed


def apply_fixes(text: str) -> Tuple[str, bool]:
    normalised, nl_changed = normalise_newlines(text)
    lines = normalised.splitlines()
    lines, conflict_changed = resolve_conflicts(lines)
    lines, tab_changed = enforce_recipe_tabs(lines)
    lines, ensure_changed = ensure_expectations(lines)
    result = "\n".join(lines).rstrip("\n") + "\n"
    changed = nl_changed or conflict_changed or tab_changed or ensure_changed
    if result == text:
        changed = False
    return result, changed


def main() -> int:
    args = parse_args()
    path = Path(args.makefile)
    try:
        current = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"error: {path} not found", file=sys.stderr)
        return 1
    updated, changed = apply_fixes(current)
    if args.check:
        if changed:
            print("Makefile requires formatting fixes", file=sys.stderr)
            return 2
        return 0
    if changed:
        path.write_text(updated, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
