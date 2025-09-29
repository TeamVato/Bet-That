"""Odds data endpoints"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import CurrentBestLine, Event
from ..schemas import OddsBestLinesResponse, OddsResponse
from ..utils.odds_conversion import american_to_decimal

router = APIRouter()


@router.get("/best", response_model=OddsBestLinesResponse, tags=["odds"])
async def get_best_odds(
    market: Optional[str] = Query("player_props", description="Market type filter"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum results to return"),
    db: Session = Depends(get_db),
):
    """
    Get current best odds from existing database

    Returns the best lines currently available for the specified market.
    Reads from existing current_best_lines table.
    """
    try:
        # Build query with optional market filter
        query = db.query(CurrentBestLine)

        if market:
            if market != "player_props":
                query = query.filter(CurrentBestLine.market == market)

        # Get limited results
        odds_lines = query.limit(limit).all()

        # Convert to response format
        lines = []
        for line in odds_lines:
            # Convert American odds to decimal (use over_odds for now)
            decimal_odds = american_to_decimal(line.over_odds)

            lines.append(
                OddsResponse(
                    event_id=line.event_id,
                    market=line.market,
                    selection=line.player,
                    book=line.book,
                    odds_american=line.over_odds,
                    odds_decimal=decimal_odds,
                    points=line.line,
                    updated_at=line.updated_at,
                )
            )

        return OddsBestLinesResponse(lines=lines, count=len(lines), market=market or "all")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch odds data: {str(e)}")


@router.get("/event/{event_id}", response_model=List[OddsResponse], tags=["odds"])
async def get_event_odds(event_id: str, db: Session = Depends(get_db)):
    """
    Get all best odds for a specific event

    Returns all current best lines for the specified event.
    """
    try:
        odds_lines = db.query(CurrentBestLine).filter(CurrentBestLine.event_id == event_id).all()

        lines = []
        for line in odds_lines:
            decimal_odds = american_to_decimal(line.over_odds)

            lines.append(
                OddsResponse(
                    event_id=line.event_id,
                    market=line.market,
                    selection=line.player,
                    book=line.book,
                    odds_american=line.over_odds,
                    odds_decimal=decimal_odds,
                    points=line.line,
                    updated_at=line.updated_at,
                )
            )

        return lines

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch event odds: {str(e)}")
