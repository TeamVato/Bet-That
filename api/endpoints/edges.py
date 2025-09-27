"""Edges data endpoints"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException

from ..settings import settings

EDGE_FILE_NAME = "edges_current.json"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
EDGE_FILE_LOCATIONS = (
    PROJECT_ROOT / "backend" / "data" / EDGE_FILE_NAME,
    PROJECT_ROOT / "api" / "data" / EDGE_FILE_NAME,
    PROJECT_ROOT / "storage" / EDGE_FILE_NAME,
)

router = APIRouter(prefix="/api/edges", tags=["Edges"])


def _load_edges_file() -> Dict[str, Any]:
    """Load the edges JSON file from the first available location."""
    for candidate in EDGE_FILE_LOCATIONS:
        if candidate.exists():
            try:
                with candidate.open("r", encoding="utf-8") as fh:
                    return json.load(fh)
            except json.JSONDecodeError as exc:  # pragma: no cover - defensive
                raise HTTPException(status_code=500, detail=f"Invalid edges data: {exc}") from exc
    raise HTTPException(status_code=404, detail="edges_current.json not found. Run the strategy pipeline.")



def _normalize_edge(raw: Dict[str, Any]) -> Dict[str, Any]:
    normalized: Dict[str, Any] = dict(raw)
    normalized['type'] = str(raw.get('type') or 'Unknown Edge')
    normalized['player'] = str(raw.get('player') or 'Unknown Player')
    normalized['team'] = str(raw.get('team') or 'Unknown Team')
    normalized['opponent'] = raw.get('opponent') or None
    normalized['confidence'] = _coerce_float(raw.get('confidence'), 0.0)
    normalized['expected_value'] = _coerce_float(raw.get('expected_value'), 0.0)
    normalized['line'] = raw.get('line') or None
    normalized['odds'] = raw.get('odds') or None
    normalized['reasoning'] = raw.get('reasoning') or None
    normalized['notes'] = raw.get('notes') or None
    return normalized


def _build_edge_summary(edges: List[Dict[str, Any]]) -> Dict[str, int]:
    summary: Dict[str, int] = {}
    for edge in edges:
        edge_type = str(edge.get('type') or 'Unknown Edge')
        summary[edge_type] = summary.get(edge_type, 0) + 1
    return summary


def _coerce_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _build_summary(edges: list[Dict[str, Any]], data_quality: float, generated: str | None) -> Dict[str, Any]:
    avg_confidence = _coerce_float(
        sum(_coerce_float(edge.get("confidence"), 0.0) for edge in edges) / len(edges)
        if edges else 0.0
    )

    generated_at = generated or datetime.utcnow().isoformat()

    return {
        "total_edges": len(edges),
        "avg_confidence": avg_confidence,
        "data_freshness": data_quality,
        "generated_at": generated_at,
    }


@router.get("/current")
async def get_current_edges() -> Dict[str, Any]:
    """Serve current betting edges with beta safety metadata."""
    data = _load_edges_file()

    edges = data.get("edges", [])
    if not isinstance(edges, list):
        raise HTTPException(status_code=500, detail="Edges payload malformed: 'edges' must be a list")

    normalized_edges = [_normalize_edge(edge) for edge in edges if isinstance(edge, dict)]

    data_quality = _coerce_float(data.get("data_quality"), 0.0)
    generated = data.get("generated")

    response_payload: Dict[str, Any] = {
        "edges": normalized_edges,
        "beta_mode": True,
        "disclaimer": settings.compliance_disclaimer,
        "view_only": True,
        "data_quality": data_quality,
        "summary": _build_summary(normalized_edges, data_quality, generated),
        "edge_summary": _build_edge_summary(normalized_edges),
    }

    disclaimer = data.get("disclaimer")
    if disclaimer:
        response_payload["disclaimer"] = disclaimer

    extra_fields = {key: value for key, value in data.items() if key not in response_payload}
    response_payload.update(extra_fields)

    response_payload["edges"] = normalized_edges
    response_payload["edge_summary"] = _build_edge_summary(normalized_edges)

    return response_payload
