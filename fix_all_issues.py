#!/usr/bin/env python3
"""One-click fix for Bet-That beta blockers."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Optional
from urllib.error import URLError
from urllib.request import urlopen

PROJECT_ROOT = Path("/Users/vato/work/Bet-That")
BACKEND_ROOT = PROJECT_ROOT / "backend"
MAIN_FILE = BACKEND_ROOT / "app" / "main.py"
UVICORN_HOST = "0.0.0.0"
UVICORN_PORT = 8000
FRONTEND_ORIGIN = "http://localhost:5173"


def fix_cors() -> Dict[str, str]:
    """Ensure FastAPI includes permissive CORS for localhost frontend."""
    if not MAIN_FILE.exists():
        return {"status": "error", "detail": f"main.py not found at {MAIN_FILE}"}

    content = MAIN_FILE.read_text()
    updated = False

    if "fastapi.middleware.cors import CORSMiddleware" not in content:
        needle = "from fastapi import FastAPI\n\n"
        if needle in content:
            content = content.replace(
                needle,
                "from fastapi import FastAPI\nfrom fastapi.middleware.cors import CORSMiddleware\n\n",
                1,
            )
            updated = True
        else:
            return {"status": "error", "detail": "Unable to locate FastAPI import for CORS injection"}

    cors_snippet = (
        "    app.add_middleware(\n"
        "        CORSMiddleware,\n"
        f"        allow_origins=[\"{FRONTEND_ORIGIN}\"],\n"
        "        allow_credentials=True,\n"
        "        allow_methods=['*'],\n"
        "        allow_headers=['*'],\n"
        "    )\n"
    )

    if FRONTEND_ORIGIN not in content:
        anchor = "    app = FastAPI("
        idx = content.find(anchor)
        if idx == -1:
            return {"status": "error", "detail": "Unable to locate FastAPI application factory"}
        insert_pos = content.find("\n", idx)
        if insert_pos == -1:
            insert_pos = idx
        insert_pos = content.find("\n", insert_pos + 1)
        if insert_pos == -1:
            insert_pos = idx
        content = content[: insert_pos + 1] + cors_snippet + content[insert_pos + 1 :]
        updated = True

    if updated:
        MAIN_FILE.write_text(content)
        return {"status": "updated", "detail": "CORS middleware injected"}
    return {"status": "noop", "detail": "CORS already configured"}


def ensure_redis() -> Dict[str, str]:
    """Start Redis if available, otherwise surface actionable guidance."""
    redis_server = shutil.which("redis-server")
    if not redis_server:
        return {"status": "error", "detail": "redis-server not installed"}
    try:
        subprocess.run([redis_server, "--daemonize", "yes"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as exc:
        return {"status": "error", "detail": f"redis-server failed: {exc.stderr.decode().strip()}"}
    return {"status": "started", "detail": "redis-server daemonized"}


def launch_backend() -> Dict[str, str]:
    """Boot uvicorn backend server in the background."""
    uvicorn_cmd = [sys.executable, "-m", "uvicorn", "app.main:app", "--host", UVICORN_HOST, "--port", str(UVICORN_PORT)]
    try:
        proc = subprocess.Popen(
            uvicorn_cmd,
            cwd=str(BACKEND_ROOT),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        return {"status": "error", "detail": "Failed to locate python executable for uvicorn"}
    time.sleep(2)
    return {"status": "started", "detail": "uvicorn running", "pid": str(proc.pid)}


def restart_services() -> Dict[str, str]:
    """Restart Redis (if available) and backend server."""
    results = {}
    results["redis"] = ensure_redis()
    backend_status = launch_backend()
    results["backend"] = backend_status
    return {"status": "completed", "detail": json.dumps(results)}


def check_endpoint(path: str) -> Dict[str, Optional[str]]:
    url = f"http://127.0.0.1:{UVICORN_PORT}{path}"
    try:
        with urlopen(url, timeout=5) as resp:
            body = resp.read(2048).decode()
            return {"status": str(resp.status), "detail": body}
    except URLError as exc:
        return {"status": "error", "detail": str(exc)}


def validate_fixes() -> Dict[str, str]:
    """Confirm backend endpoints respond after fixes."""
    health = check_endpoint("/health")
    edges = check_endpoint("/api/v1/odds/edges")
    tokens = check_endpoint("/api/v1/odds/token-status")
    summary = {
        "health": health,
        "edges": edges,
        "token_status": tokens,
    }
    return {"status": "completed", "detail": json.dumps(summary)}


def main() -> int:
    report = {
        "fix_cors": fix_cors(),
        "restart_services": restart_services(),
        "validate_fixes": validate_fixes(),
    }
    print(json.dumps(report, indent=2))
    print("✅ All issues processed. Verify services before beta launch.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
