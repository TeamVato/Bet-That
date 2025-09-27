from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.services.odds_api_manager import DailyLimitReached, OddsAPIManager, OddsAPIError, get_odds_manager

router = APIRouter(prefix="/api/odds", tags=["odds"])


@router.get("/nfl-week")
async def get_current_week_odds(manager: OddsAPIManager = Depends(get_odds_manager)) -> dict:
    """Return cached NFL odds for the current week."""
    try:
        odds = await manager.fetch_current_week_odds()
        return {"data": odds, "source": "cache" if odds else "demo"}
    except DailyLimitReached as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(exc),
        ) from exc
    except OddsAPIError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@router.get("/token-status")
async def get_token_status(manager: OddsAPIManager = Depends(get_odds_manager)) -> dict:
    """Expose aggregated API token usage information."""
    usage = await manager.get_usage_stats()
    return usage


@router.post("/fetch-fresh")
async def fetch_fresh_odds(
    manager: OddsAPIManager = Depends(get_odds_manager),
) -> dict:
    """Force refresh NFL odds, respecting rate limits."""
    try:
        odds = await manager.force_refresh()
        return {"data": odds, "source": "live"}
    except DailyLimitReached as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(exc),
        ) from exc
    except OddsAPIError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
