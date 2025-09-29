"""Enhanced edge opportunity endpoints for database-driven arbitrage detection"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..crud import edge_crud
from ..database import get_db
from ..models import EdgeStatus
from ..schemas import EdgeCreateRequest, EdgeListResponse, EdgeResponse, EdgeUpdateRequest

router = APIRouter(prefix="/enhanced-edges", tags=["Enhanced Edges"])


@router.get("/", response_model=EdgeListResponse)
def get_edges(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    sport_key: Optional[str] = Query(None, description="Filter by sport"),
    market_type: Optional[str] = Query(None, description="Filter by market type"),
    player: Optional[str] = Query(None, description="Filter by player name"),
    position: Optional[str] = Query(None, description="Filter by position"),
    min_edge: Optional[float] = Query(0.0, description="Minimum edge percentage"),
    max_edge: Optional[float] = Query(None, description="Maximum edge percentage"),
    min_kelly: Optional[float] = Query(None, description="Minimum Kelly fraction"),
    sportsbook: Optional[str] = Query(None, description="Filter by sportsbook"),
    strategy_tag: Optional[str] = Query(None, description="Filter by strategy"),
    active_only: bool = Query(True, description="Only return active edges"),
    db: Session = Depends(get_db),
):
    """Get arbitrage edges with comprehensive filtering and pagination"""

    # Build search filters
    search_filters = {}
    if sport_key:
        search_filters["sport_key"] = sport_key
    if market_type:
        search_filters["market_type"] = market_type
    if player:
        search_filters["player"] = player
    if position:
        search_filters["position"] = position
    if min_edge is not None:
        search_filters["min_edge_percentage"] = min_edge
    if max_edge is not None:
        search_filters["max_edge_percentage"] = max_edge
    if min_kelly is not None:
        search_filters["min_kelly"] = min_kelly
    if sportsbook:
        search_filters["sportsbook"] = sportsbook
    if strategy_tag:
        search_filters["strategy_tag"] = strategy_tag
    if active_only:
        search_filters["active_only"] = True

    # Get edges
    if search_filters:
        edges = edge_crud.search_edges(db=db, search_filters=search_filters, skip=skip, limit=limit)
        total = edge_crud.count(db=db, filters=search_filters)
    else:
        edges = edge_crud.get_active_edges(
            db=db, skip=skip, limit=limit, min_edge_percentage=min_edge or 0.0
        )
        total = edge_crud.count(db=db, filters={"status": EdgeStatus.ACTIVE, "is_stale": False})

    return EdgeListResponse(edges=edges, total=total, page=skip // limit + 1, per_page=limit)


@router.get("/top", response_model=List[EdgeResponse])
def get_top_edges(
    limit: int = Query(20, ge=1, le=100, description="Number of top edges to return"),
    min_kelly: float = Query(0.01, ge=0, description="Minimum Kelly fraction"),
    sport_key: Optional[str] = Query(None, description="Filter by sport"),
    db: Session = Depends(get_db),
):
    """Get top arbitrage edges by expected value"""
    edges = edge_crud.get_top_edges(db=db, limit=limit, min_kelly=min_kelly, sport_key=sport_key)
    return edges


@router.get("/statistics")
def get_edge_statistics(db: Session = Depends(get_db)):
    """Get overall edge statistics"""
    stats = edge_crud.get_edge_statistics(db=db)
    return stats


@router.get("/by-event/{event_id}", response_model=List[EdgeResponse])
def get_edges_by_event(
    event_id: str,
    active_only: bool = Query(True, description="Only return active edges"),
    db: Session = Depends(get_db),
):
    """Get all edges for a specific event"""
    edges = edge_crud.get_by_event(db=db, event_id=event_id, active_only=active_only)
    return edges


@router.get("/by-player/{player}", response_model=List[EdgeResponse])
def get_edges_by_player(
    player: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = Query(True, description="Only return active edges"),
    db: Session = Depends(get_db),
):
    """Get edges for a specific player"""
    edges = edge_crud.get_by_player(
        db=db, player=player, skip=skip, limit=limit, active_only=active_only
    )
    return edges


@router.get("/by-sport/{sport_key}/{season}/{week}", response_model=List[EdgeResponse])
def get_edges_by_sport_week(
    sport_key: str,
    season: int,
    week: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """Get edges for a specific sport, season, and week"""
    edges = edge_crud.get_by_sport_and_week(
        db=db, sport_key=sport_key, season=season, week=week, skip=skip, limit=limit
    )
    return edges


@router.post("/", response_model=EdgeResponse)
def create_edge(edge_in: EdgeCreateRequest, db: Session = Depends(get_db)):
    """Create a new arbitrage edge"""
    edge = edge_crud.create(db=db, obj_in=edge_in)
    return edge


@router.put("/{edge_id}", response_model=EdgeResponse)
def update_edge(edge_id: int, edge_update: EdgeUpdateRequest, db: Session = Depends(get_db)):
    """Update an existing edge"""
    edge = edge_crud.get(db=db, id=edge_id)
    if not edge:
        raise HTTPException(status_code=404, detail="Edge not found")

    updated_edge = edge_crud.update(db=db, db_obj=edge, obj_in=edge_update)
    return updated_edge


@router.post("/{edge_id}/mark-stale", response_model=EdgeResponse)
def mark_edge_stale(edge_id: int, db: Session = Depends(get_db)):
    """Mark an edge as stale"""
    edge = edge_crud.mark_stale(db=db, edge_id=edge_id)
    if not edge:
        raise HTTPException(status_code=404, detail="Edge not found")
    return edge


@router.post("/{edge_id}/mark-expired", response_model=EdgeResponse)
def mark_edge_expired(edge_id: int, db: Session = Depends(get_db)):
    """Mark an edge as expired"""
    edge = edge_crud.mark_expired(db=db, edge_id=edge_id)
    if not edge:
        raise HTTPException(status_code=404, detail="Edge not found")
    return edge


@router.post("/cleanup-expired")
def cleanup_expired_edges(db: Session = Depends(get_db)):
    """Mark expired edges as stale"""
    updated_count = edge_crud.cleanup_expired_edges(db=db)
    return {"message": f"Marked {updated_count} expired edges as stale"}


@router.get("/{edge_id}", response_model=EdgeResponse)
def get_edge(edge_id: int, db: Session = Depends(get_db)):
    """Get edge by ID"""
    edge = edge_crud.get(db=db, id=edge_id)
    if not edge:
        raise HTTPException(status_code=404, detail="Edge not found")
    return edge


@router.delete("/{edge_id}")
def delete_edge(edge_id: int, db: Session = Depends(get_db)):
    """Soft delete an edge"""
    edge = edge_crud.remove(db=db, id=edge_id)
    if not edge:
        raise HTTPException(status_code=404, detail="Edge not found")
    return {"message": "Edge deleted successfully"}
