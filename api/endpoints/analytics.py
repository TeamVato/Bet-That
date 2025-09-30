"""Analytics endpoints for bet resolution data"""

from typing import Annotated, Optional
from datetime import datetime, timedelta
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from ..database import get_db
from ..deps import get_current_user
from ..models import Bet, User, BetResolutionHistory
from ..schemas.bet_schemas import (
    ResolutionAnalytics,
    ResolutionHistoryFilters,
    ResolutionHistoryItem,
    ResolutionHistoryResponse,
)

router = APIRouter()


@router.get("/resolution", response_model=ResolutionAnalytics, tags=["analytics"])
async def get_resolution_analytics(
    user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> ResolutionAnalytics:
    """
    Get comprehensive resolution analytics
    
    Returns key metrics about bet resolution performance including:
    - Total resolutions and average resolution time
    - Resolution accuracy and dispute rates
    - Outcome distribution and most active resolvers
    - Resolution trends over time
    """
    try:
        if not user or not user.get("external_id"):
            raise HTTPException(status_code=401, detail="User not authenticated")

        # Get user ID
        db_user = db.query(User).filter(User.external_id == user["external_id"]).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        # Calculate total resolutions
        total_resolutions = db.query(Bet).filter(
            and_(
                Bet.resolved_at.isnot(None),
                Bet.external_user_id == user["external_id"]
            )
        ).count()

        if total_resolutions == 0:
            return ResolutionAnalytics(
                total_resolutions=0,
                average_resolution_time_hours=0.0,
                resolution_accuracy_percentage=0.0,
                outcome_distribution={"win": 0, "loss": 0, "push": 0, "void": 0},
                most_active_resolvers=[],
                resolution_trends=[],
                dispute_rate=0.0,
                average_dispute_resolution_time_hours=0.0,
            )

        # Calculate average resolution time
        resolution_times = db.query(
            func.extract('epoch', Bet.resolved_at - Bet.created_at) / 3600
        ).filter(
            and_(
                Bet.resolved_at.isnot(None),
                Bet.external_user_id == user["external_id"]
            )
        ).all()

        avg_resolution_time = sum([t[0] for t in resolution_times]) / len(resolution_times) if resolution_times else 0.0

        # Calculate outcome distribution
        outcome_counts = db.query(
            Bet.result,
            func.count(Bet.id)
        ).filter(
            and_(
                Bet.resolved_at.isnot(None),
                Bet.external_user_id == user["external_id"]
            )
        ).group_by(Bet.result).all()

        outcome_distribution = {"win": 0, "loss": 0, "push": 0, "void": 0}
        for result, count in outcome_counts:
            if result in outcome_distribution:
                outcome_distribution[result] = count

        # Calculate dispute rate
        disputed_count = db.query(Bet).filter(
            and_(
                Bet.is_disputed == True,
                Bet.external_user_id == user["external_id"]
            )
        ).count()

        dispute_rate = (disputed_count / total_resolutions) * 100 if total_resolutions > 0 else 0.0

        # Calculate average dispute resolution time
        dispute_resolution_times = db.query(
            func.extract('epoch', Bet.dispute_resolved_at - Bet.dispute_created_at) / 3600
        ).filter(
            and_(
                Bet.dispute_resolved_at.isnot(None),
                Bet.external_user_id == user["external_id"]
            )
        ).all()

        avg_dispute_resolution_time = sum([t[0] for t in dispute_resolution_times]) / len(dispute_resolution_times) if dispute_resolution_times else 0.0

        # Get most active resolvers (for now, just the current user)
        most_active_resolvers = [{
            "user_id": db_user.id,
            "user_name": db_user.name or "Unknown",
            "resolution_count": total_resolutions
        }]

        # Calculate resolution trends (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        trends_data = db.query(
            func.date(Bet.resolved_at).label('date'),
            func.count(Bet.id).label('count'),
            func.avg(func.extract('epoch', Bet.resolved_at - Bet.created_at) / 3600).label('avg_time')
        ).filter(
            and_(
                Bet.resolved_at.isnot(None),
                Bet.resolved_at >= thirty_days_ago,
                Bet.external_user_id == user["external_id"]
            )
        ).group_by(func.date(Bet.resolved_at)).order_by('date').all()

        resolution_trends = [
            {
                "date": trend.date.isoformat(),
                "resolutions_count": trend.count,
                "average_time_hours": float(trend.avg_time) if trend.avg_time else 0.0
            }
            for trend in trends_data
        ]

        # Calculate resolution accuracy (for now, assume 95% if no disputes)
        resolution_accuracy = 95.0 if dispute_rate < 5.0 else max(80.0, 95.0 - dispute_rate)

        return ResolutionAnalytics(
            total_resolutions=total_resolutions,
            average_resolution_time_hours=round(avg_resolution_time, 2),
            resolution_accuracy_percentage=round(resolution_accuracy, 2),
            outcome_distribution=outcome_distribution,
            most_active_resolvers=most_active_resolvers,
            resolution_trends=resolution_trends,
            dispute_rate=round(dispute_rate, 2),
            average_dispute_resolution_time_hours=round(avg_dispute_resolution_time, 2),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get resolution analytics: {str(e)}")


@router.get("/resolution-history", response_model=ResolutionHistoryResponse, tags=["analytics"])
async def get_resolution_history(
    user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    start_date: Optional[str] = Query(None, description="Start date filter (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date filter (YYYY-MM-DD)"),
    result: Optional[str] = Query(None, description="Result filter (win, loss, push, void)"),
    resolver_id: Optional[int] = Query(None, description="Resolver ID filter"),
    has_dispute: Optional[bool] = Query(None, description="Filter by dispute status"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
) -> ResolutionHistoryResponse:
    """
    Get detailed resolution history with filtering
    
    Returns paginated list of resolved bets with comprehensive filtering options.
    """
    try:
        if not user or not user.get("external_id"):
            raise HTTPException(status_code=401, detail="User not authenticated")

        # Get user ID
        db_user = db.query(User).filter(User.external_id == user["external_id"]).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        # Build query
        query = db.query(Bet).filter(
            and_(
                Bet.resolved_at.isnot(None),
                Bet.external_user_id == user["external_id"]
            )
        )

        # Apply filters
        if start_date:
            try:
                start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                query = query.filter(Bet.resolved_at >= start_dt)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD")

        if end_date:
            try:
                end_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
                query = query.filter(Bet.resolved_at < end_dt)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD")

        if result:
            query = query.filter(Bet.result == result)

        if resolver_id:
            query = query.filter(Bet.resolved_by == resolver_id)

        if has_dispute is not None:
            query = query.filter(Bet.is_disputed == has_dispute)

        # Get total count
        total = query.count()

        # Apply pagination
        offset = (page - 1) * per_page
        bets = query.order_by(Bet.resolved_at.desc()).offset(offset).limit(per_page).all()

        # Convert to response format
        history_items = []
        for bet in bets:
            # Calculate resolution time
            resolution_time_hours = 0.0
            if bet.resolved_at and bet.created_at:
                delta = bet.resolved_at - bet.created_at
                resolution_time_hours = delta.total_seconds() / 3600

            # Get resolver name
            resolver_name = "Unknown"
            if bet.resolved_by:
                resolver = db.query(User).filter(User.id == bet.resolved_by).first()
                if resolver:
                    resolver_name = resolver.name or "Unknown"

            history_items.append(ResolutionHistoryItem(
                id=bet.id,
                bet_id=bet.id,
                game_name=bet.market_description or "Unknown Game",
                market=bet.market_type or "Unknown Market",
                selection=bet.selection or "Unknown Selection",
                result=bet.result or "Unknown",
                resolved_at=bet.resolved_at.isoformat() if bet.resolved_at else "",
                resolved_by=bet.resolved_by or 0,
                resolver_name=resolver_name,
                resolution_notes=bet.resolution_notes,
                is_disputed=bet.is_disputed or False,
                dispute_reason=bet.dispute_reason,
                dispute_resolved_at=bet.dispute_resolved_at.isoformat() if bet.dispute_resolved_at else None,
                resolution_time_hours=round(resolution_time_hours, 2),
            ))

        return ResolutionHistoryResponse(
            history=history_items,
            total=total,
            page=page,
            per_page=per_page,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get resolution history: {str(e)}")


@router.get("/export-resolution-data", tags=["analytics"])
async def export_resolution_data(
    user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    start_date: Optional[str] = Query(None, description="Start date filter (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date filter (YYYY-MM-DD)"),
    result: Optional[str] = Query(None, description="Result filter (win, loss, push, void)"),
    resolver_id: Optional[int] = Query(None, description="Resolver ID filter"),
    has_dispute: Optional[bool] = Query(None, description="Filter by dispute status"),
    format: str = Query("csv", description="Export format (csv, json)"),
):
    """
    Export resolution data in CSV or JSON format
    
    Returns downloadable file with filtered resolution data.
    """
    try:
        if not user or not user.get("external_id"):
            raise HTTPException(status_code=401, detail="User not authenticated")

        # Get user ID
        db_user = db.query(User).filter(User.external_id == user["external_id"]).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        # Build query (same as resolution history)
        query = db.query(Bet).filter(
            and_(
                Bet.resolved_at.isnot(None),
                Bet.external_user_id == user["external_id"]
            )
        )

        # Apply filters (same logic as resolution history)
        if start_date:
            try:
                start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                query = query.filter(Bet.resolved_at >= start_dt)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD")

        if end_date:
            try:
                end_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
                query = query.filter(Bet.resolved_at < end_dt)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD")

        if result:
            query = query.filter(Bet.result == result)

        if resolver_id:
            query = query.filter(Bet.resolved_by == resolver_id)

        if has_dispute is not None:
            query = query.filter(Bet.is_disputed == has_dispute)

        # Get all matching bets
        bets = query.order_by(Bet.resolved_at.desc()).all()

        # Convert to export format
        export_data = []
        for bet in bets:
            # Calculate resolution time
            resolution_time_hours = 0.0
            if bet.resolved_at and bet.created_at:
                delta = bet.resolved_at - bet.created_at
                resolution_time_hours = delta.total_seconds() / 3600

            # Get resolver name
            resolver_name = "Unknown"
            if bet.resolved_by:
                resolver = db.query(User).filter(User.id == bet.resolved_by).first()
                if resolver:
                    resolver_name = resolver.name or "Unknown"

            export_data.append({
                "id": bet.id,
                "bet_id": bet.id,
                "game_name": bet.market_description or "Unknown Game",
                "market": bet.market_type or "Unknown Market",
                "selection": bet.selection or "Unknown Selection",
                "result": bet.result or "Unknown",
                "resolved_at": bet.resolved_at.isoformat() if bet.resolved_at else "",
                "resolved_by": bet.resolved_by or 0,
                "resolver_name": resolver_name,
                "resolution_notes": bet.resolution_notes,
                "is_disputed": bet.is_disputed or False,
                "dispute_reason": bet.dispute_reason,
                "dispute_resolved_at": bet.dispute_resolved_at.isoformat() if bet.dispute_resolved_at else None,
                "resolution_time_hours": round(resolution_time_hours, 2),
                "stake": float(bet.stake) if bet.stake else 0.0,
                "odds_american": bet.odds_american,
                "potential_return": float(bet.potential_return) if bet.potential_return else 0.0,
                "actual_return": float(bet.actual_return) if bet.actual_return else 0.0,
                "net_profit": float(bet.net_profit) if bet.net_profit else 0.0,
            })

        if format.lower() == "csv":
            import csv
            import io
            
            output = io.StringIO()
            if export_data:
                writer = csv.DictWriter(output, fieldnames=export_data[0].keys())
                writer.writeheader()
                writer.writerows(export_data)
            
            from fastapi.responses import Response
            return Response(
                content=output.getvalue(),
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=resolution-data.csv"}
            )
        else:
            from fastapi.responses import JSONResponse
            return JSONResponse(
                content=export_data,
                headers={"Content-Disposition": "attachment; filename=resolution-data.json"}
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export resolution data: {str(e)}")

