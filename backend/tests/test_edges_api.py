from __future__ import annotations

import json
import sys
from contextlib import contextmanager
from pathlib import Path
from types import ModuleType
from typing import Generator

import pytest
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_PATH = PROJECT_ROOT / "backend"
if str(BACKEND_PATH) not in sys.path:
    sys.path.insert(0, str(BACKEND_PATH))

from app.main import app

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
EDGES_FILE = DATA_DIR / "edges_current.json"

client = TestClient(app)


def _sample_edges_payload() -> dict:
    return {
        "generated": "2024-01-01T00:00:00Z",
        "data_quality": 0.92,
        "edges": [
            {
                "id": "edge-1",
                "player": "Mock Player",
                "team": "Mock Team",
                "confidence": 0.76,
                "expected_value": 0.13,
                "type": "Player Prop",
            }
        ],
    }


@contextmanager
def _stub_run_pipeline() -> Generator[None, None, None]:
    """Temporarily replace the heavy pipeline with a no-op for tests."""
    module_name = "scripts.run_strategy_pipeline"
    package_name = "scripts"
    original_module = sys.modules.get(module_name)
    original_package = sys.modules.get(package_name)

    stub_module = ModuleType(module_name)
    stub_module.run_pipeline = lambda: None  # type: ignore[attr-defined]

    stub_package = ModuleType(package_name)
    setattr(stub_package, "run_strategy_pipeline", stub_module)

    sys.modules[package_name] = stub_package
    sys.modules[module_name] = stub_module
    try:
        yield
    finally:
        if original_package is not None:
            sys.modules[package_name] = original_package
        else:
            sys.modules.pop(package_name, None)
        if original_module is not None:
            sys.modules[module_name] = original_module
        else:
            sys.modules.pop(module_name, None)


@pytest.fixture(autouse=True)
def edges_file_fixture() -> Generator[Path, None, None]:
    """Ensure the edges file exists with a predictable payload for each test."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    previous_contents = EDGES_FILE.read_text(encoding="utf-8") if EDGES_FILE.exists() else None

    EDGES_FILE.write_text(json.dumps(_sample_edges_payload()), encoding="utf-8")
    try:
        yield EDGES_FILE
    finally:
        if previous_contents is None:
            EDGES_FILE.unlink(missing_ok=True)
        else:
            EDGES_FILE.write_text(previous_contents, encoding="utf-8")


def test_current_edges_returns_expected_shape() -> None:
    response = client.get("/api/edges/current", headers={"Origin": "http://localhost:5173"})

    assert response.status_code == 200
    payload = response.json()

    assert payload["beta_mode"] is True
    assert payload["summary"]["total_edges"] == len(payload["edges"])
    assert payload["summary"]["avg_confidence"] >= 0
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_current_edges_missing_file_returns_404(edges_file_fixture: Path) -> None:
    with _stub_run_pipeline():
        edges_file_fixture.unlink()
        response = client.get("/api/edges/current")

    assert response.status_code == 404
    assert "No edges available" in response.json()["detail"]


def test_validate_endpoint_includes_edge_id() -> None:
    response = client.get("/api/edges/validate/edge-123")

    assert response.status_code == 200
    payload = response.json()
    assert payload["edge_id"] == "edge-123"
    assert payload["validation_status"] == "pending"
