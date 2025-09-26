"""Health check endpoints"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text, func
from sqlalchemy.orm import Session
from ..database import get_db, check_database_health
from ..models import CurrentBestLine, Event, User
from ..schemas import HealthResponse, DeepHealthResponse

router = APIRouter()

@router.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check():
    """Basic health status of the API"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        version="0.2.0",
        database="storage/odds.db"
    )

@router.get("/healthz/deep", response_model=DeepHealthResponse, tags=["health"])
async def deep_health_check(db: Session = Depends(get_db)):
    """Detailed health status including database stats"""
    try:
        # Check database connection
        db_healthy = check_database_health()
        
        if not db_healthy:
            raise HTTPException(status_code=503, detail="Database connection failed")
        
        # Get counts
        current_best_lines_count = db.query(CurrentBestLine).count()
        events_count = db.query(Event).count()
        users_count = db.query(User).count()
        
        # Get last odds update time
        last_update = db.query(func.max(CurrentBestLine.updated_at)).scalar()
        
        if last_update:
            last_odds_update = str(last_update)
        else:
            last_odds_update = None
        
        return DeepHealthResponse(
            status="healthy" if db_healthy else "unhealthy",
            timestamp=datetime.now(),
            version="0.2.0",
            database="storage/odds.db",
            database_connection=db_healthy,
            current_best_lines_count=current_best_lines_count,
            events_count=events_count,
            users_count=users_count,
            last_odds_update=last_odds_update
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Health check failed: {str(e)}"
        )
