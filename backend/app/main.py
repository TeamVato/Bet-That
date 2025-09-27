from __future__ import annotations

import logging

from fastapi import FastAPI

from app.api.endpoints.odds import router as odds_router
from app.core.config import get_settings

logging.basicConfig(level=logging.INFO)


def create_application() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="Bet-That Odds API", version="0.1.0", docs_url="/docs")

    @app.get("/health", tags=["health"])
    async def healthcheck() -> dict:
        return {
            "status": "ok",
            "environment": settings.environment,
        }

    app.include_router(odds_router)

    return app


app = create_application()
