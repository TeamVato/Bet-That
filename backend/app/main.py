import json
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import redis.asyncio as redis
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import sys
from pathlib import Path

# Ensure backend is in path for imports
backend_path = Path(__file__).parent.parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from app.api.endpoints import bets, odds  # type: ignore
from app.core.config import settings  # type: ignore

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Redis connection on startup
    app.state.redis = redis.from_url(settings.redis_url, decode_responses=True)
    try:
        await app.state.redis.ping()
        logger.info("Redis connected successfully")
    except Exception as e:
        logger.warning("Redis connection failed: %s", e)
        app.state.redis = None
    yield
    if app.state.redis:
        await app.state.redis.close()


app = FastAPI(title="Bet-That API", version="1.0.0", lifespan=lifespan)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(odds.router, prefix="/api/v1/odds", tags=["odds"])
app.include_router(bets.router, prefix="/api/v1/bets", tags=["bets"])


@app.get("/health")
async def health_check():
    redis_status = (
        "connected" if hasattr(app.state, "redis") and app.state.redis else "disconnected"
    )
    return {"status": "healthy", "service": "bet-that-api", "redis": redis_status}


@app.get("/api/edges/current")
async def get_current_edges() -> Dict[str, Any]:
    """Return the latest computed betting edges along with beta metadata.

    The endpoint wraps the raw JSON snapshot produced by the strategy pipeline
    with derived summary statistics and hard-coded beta safety rails. If the
    underlying data file is missing we attempt to rebuild it once before
    returning an HTTP 404 so the UI can surface a helpful retry prompt.

    Returns:
        Dict[str, Any]: Edge payload augmented with summary, disclaimer, and
        beta/view-only flags consumed by the frontend dashboard.

    Raises:
        HTTPException: `404` when the source file is missing after a rebuild
        attempt, or `500` when the JSON payload cannot be parsed.
    """
    edges_path = settings.edges_snapshot_path.expanduser()
    if not edges_path.is_absolute():
        edges_path = Path.cwd() / edges_path
    edges_path = edges_path.resolve()

    try:
        if not edges_path.exists():
            # Add project root to path for scripts import
            project_root = Path(__file__).parent.parent.parent
            if str(project_root) not in sys.path:
                sys.path.insert(0, str(project_root))
            from scripts.run_strategy_pipeline import run_pipeline  # type: ignore

            run_pipeline()

        with edges_path.open("r", encoding="utf-8") as f:
            data: Dict[str, Any] = json.load(f)

    except FileNotFoundError as exc:  # pragma: no cover - defensive
        raise HTTPException(
            status_code=404, detail="No edges available. Run strategy pipeline first."
        ) from exc
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    edges = data.get("edges", [])

    data["beta_mode"] = True
    data["disclaimer"] = "Beta recommendations - verify before betting"
    data["view_only"] = True

    if edges:
        avg_confidence = sum(edge.get("confidence", 0.0) for edge in edges) / len(edges)
    else:
        avg_confidence = 0.0

    data["summary"] = {
        "total_edges": len(edges),
        "avg_confidence": avg_confidence,
        "data_freshness": data.get("data_quality", 0.0),
        "generated_at": data.get("generated", datetime.utcnow().isoformat()),
    }

    return data


@app.get("/api/edges/validate/{edge_id}")
async def validate_edge(edge_id: str) -> Dict[str, Any]:
    """Indicate the manual validation status for a particular edge.

    Args:
        edge_id: Identifier supplied by the frontend (derived from the model).

    Returns:
        Dict[str, Any]: Lightweight status marker while the program operates in
        beta mode. Extend this handler to incorporate real validation results
        once the review workflow is automated.
    """
    return {
        "edge_id": edge_id,
        "validation_status": "pending",
        "message": "Manual verification required in beta mode",
    }
