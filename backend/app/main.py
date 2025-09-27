from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict
import redis.asyncio as redis
from app.api.endpoints import odds, bets

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Redis connection on startup
    app.state.redis = redis.Redis(host='localhost', port=6379, decode_responses=True)
    try:
        await app.state.redis.ping()
        print("✅ Redis connected successfully")
    except Exception as e:
        print(f"⚠️ Redis connection failed: {e}")
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
    redis_status = "connected" if hasattr(app.state, 'redis') and app.state.redis else "disconnected"
    return {"status": "healthy", "service": "bet-that-api", "redis": redis_status}


@app.get("/api/edges/current")
async def get_current_edges() -> Dict[str, Any]:
    """Serve the current betting edges with safety metadata and summary stats."""
    edges_path = Path(__file__).resolve().parent.parent / "data" / "edges_current.json"

    try:
        if not edges_path.exists():
            from scripts.run_strategy_pipeline import run_pipeline

            run_pipeline()

        with edges_path.open("r", encoding="utf-8") as f:
            data: Dict[str, Any] = json.load(f)

    except FileNotFoundError as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=404, detail="No edges available. Run strategy pipeline first.") from exc
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
    """Placeholder validation endpoint for a specific edge during beta."""
    return {
        "edge_id": edge_id,
        "validation_status": "pending",
        "message": "Manual verification required in beta mode",
    }
