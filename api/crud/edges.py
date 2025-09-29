"""CRUD operations for Edge model"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, desc, func, or_
from sqlalchemy.orm import Session, joinedload

from ..models import Edge, EdgeStatus
from ..schemas import EdgeCreateRequest, EdgeUpdateRequest
from .base import CRUDBase


class CRUDEdge(CRUDBase[Edge, EdgeCreateRequest, EdgeUpdateRequest]):

    def get_active_edges(
        self, db: Session, *, skip: int = 0, limit: int = 100, min_edge_percentage: float = 0.0
    ) -> List[Edge]:
        """Get active, non-stale edges with minimum edge percentage"""
        query = (
            db.query(self.model)
            .filter(
                and_(
                    self.model.status == EdgeStatus.ACTIVE,
                    self.model.is_stale.is_(False),
                    self.model.deleted_at.is_(None),
                    self.model.edge_percentage >= min_edge_percentage,
                    or_(self.model.expires_at.is_(None), self.model.expires_at > datetime.utcnow()),
                )
            )
            .order_by(desc(self.model.edge_percentage))
        )

        return query.offset(skip).limit(limit).all()

    def get_by_event(
        self,
        db: Session,
        *,
        event_id: str,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = True,
    ) -> List[Edge]:
        """Get edges for a specific event"""
        filters = {"event_id": event_id}
        if active_only:
            filters.update({"status": EdgeStatus.ACTIVE, "is_stale": False})

        return self.get_multi(
            db=db, skip=skip, limit=limit, filters=filters, order_by="edge_percentage"
        )

    def get_by_player(
        self, db: Session, *, player: str, skip: int = 0, limit: int = 100, active_only: bool = True
    ) -> List[Edge]:
        """Get edges for a specific player"""
        filters = {"player": player}
        if active_only:
            filters.update({"status": EdgeStatus.ACTIVE, "is_stale": False})

        return self.get_multi(
            db=db, skip=skip, limit=limit, filters=filters, order_by="edge_percentage"
        )

    def get_by_sport_and_week(
        self,
        db: Session,
        *,
        sport_key: str,
        season: int,
        week: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Edge]:
        """Get edges for a specific sport, season, and week"""
        return self.get_multi(
            db=db,
            skip=skip,
            limit=limit,
            filters={
                "sport_key": sport_key,
                "season": season,
                "week": week,
                "status": EdgeStatus.ACTIVE,
                "is_stale": False,
            },
            order_by="edge_percentage",
        )

    def get_by_sportsbook(
        self, db: Session, *, sportsbook: str, skip: int = 0, limit: int = 100
    ) -> List[Edge]:
        """Get edges for a specific sportsbook"""
        return self.get_multi(
            db=db,
            skip=skip,
            limit=limit,
            filters={"best_sportsbook": sportsbook},
            order_by="edge_percentage",
        )

    def get_top_edges(
        self,
        db: Session,
        *,
        limit: int = 50,
        min_kelly: float = 0.01,
        sport_key: Optional[str] = None,
    ) -> List[Edge]:
        """Get top edges by expected value"""
        query = db.query(self.model).filter(
            and_(
                self.model.status == EdgeStatus.ACTIVE,
                self.model.is_stale.is_(False),
                self.model.deleted_at.is_(None),
                self.model.kelly_fraction >= min_kelly,
                or_(self.model.expires_at.is_(None), self.model.expires_at > datetime.utcnow()),
            )
        )

        if sport_key:
            query = query.filter(self.model.sport_key == sport_key)

        return query.order_by(desc(self.model.expected_value_per_dollar)).limit(limit).all()

    def search_edges(
        self, db: Session, *, search_filters: Dict[str, Any], skip: int = 0, limit: int = 100
    ) -> List[Edge]:
        """Search edges with multiple filters"""
        query = db.query(self.model).filter(self.model.deleted_at.is_(None))

        # Apply search filters
        if "sport_key" in search_filters:
            query = query.filter(self.model.sport_key == search_filters["sport_key"])

        if "market_type" in search_filters:
            query = query.filter(self.model.market_type == search_filters["market_type"])

        if "player" in search_filters:
            query = query.filter(self.model.player.ilike(f"%{search_filters['player']}%"))

        if "position" in search_filters:
            query = query.filter(self.model.position == search_filters["position"])

        if "min_edge_percentage" in search_filters:
            query = query.filter(
                self.model.edge_percentage >= search_filters["min_edge_percentage"]
            )

        if "max_edge_percentage" in search_filters:
            query = query.filter(
                self.model.edge_percentage <= search_filters["max_edge_percentage"]
            )

        if "min_kelly" in search_filters:
            query = query.filter(self.model.kelly_fraction >= search_filters["min_kelly"])

        if "sportsbook" in search_filters:
            query = query.filter(self.model.best_sportsbook == search_filters["sportsbook"])

        if "strategy_tag" in search_filters:
            query = query.filter(self.model.strategy_tag == search_filters["strategy_tag"])

        if "active_only" in search_filters and search_filters["active_only"]:
            query = query.filter(
                and_(self.model.status == EdgeStatus.ACTIVE, self.model.is_stale.is_(False))
            )

        return query.order_by(desc(self.model.edge_percentage)).offset(skip).limit(limit).all()

    def mark_stale(self, db: Session, *, edge_id: int) -> Optional[Edge]:
        """Mark an edge as stale"""
        edge = self.get(db=db, id=edge_id)
        if edge:
            edge.is_stale = True
            edge.status = EdgeStatus.STALE
            db.add(edge)
            db.commit()
            db.refresh(edge)
        return edge

    def mark_expired(self, db: Session, *, edge_id: int) -> Optional[Edge]:
        """Mark an edge as expired"""
        edge = self.get(db=db, id=edge_id)
        if edge:
            edge.status = EdgeStatus.EXPIRED
            edge.expires_at = datetime.utcnow()
            db.add(edge)
            db.commit()
            db.refresh(edge)
        return edge

    def cleanup_expired_edges(self, db: Session) -> int:
        """Mark expired edges as stale"""
        current_time = datetime.utcnow()

        updated_count = (
            db.query(self.model)
            .filter(
                and_(self.model.expires_at < current_time, self.model.status == EdgeStatus.ACTIVE)
            )
            .update({"status": EdgeStatus.EXPIRED, "is_stale": True}, synchronize_session=False)
        )

        db.commit()
        return updated_count

    def get_edge_statistics(self, db: Session) -> Dict[str, Any]:
        """Get overall edge statistics"""
        total_edges = db.query(self.model).filter(self.model.deleted_at.is_(None)).count()

        active_edges = (
            db.query(self.model)
            .filter(
                and_(
                    self.model.status == EdgeStatus.ACTIVE,
                    self.model.is_stale.is_(False),
                    self.model.deleted_at.is_(None),
                )
            )
            .count()
        )

        # Get averages for active edges
        avg_stats = (
            db.query(
                func.avg(self.model.edge_percentage).label("avg_edge"),
                func.avg(self.model.expected_value_per_dollar).label("avg_ev"),
                func.avg(self.model.kelly_fraction).label("avg_kelly"),
                func.max(self.model.edge_percentage).label("max_edge"),
                func.count(func.distinct(self.model.event_id)).label("unique_events"),
                func.count(func.distinct(self.model.player)).label("unique_players"),
            )
            .filter(
                and_(
                    self.model.status == EdgeStatus.ACTIVE,
                    self.model.is_stale.is_(False),
                    self.model.deleted_at.is_(None),
                )
            )
            .first()
        )

        return {
            "total_edges": total_edges,
            "active_edges": active_edges,
            "avg_edge_percentage": round(avg_stats.avg_edge or 0, 4),
            "avg_expected_value": round(avg_stats.avg_ev or 0, 4),
            "avg_kelly_fraction": round(avg_stats.avg_kelly or 0, 4),
            "max_edge_percentage": round(avg_stats.max_edge or 0, 4),
            "unique_events": avg_stats.unique_events or 0,
            "unique_players": avg_stats.unique_players or 0,
        }

    def get_edges_with_event_data(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Edge]:
        """Get edges with joined event data for efficiency"""
        query = db.query(self.model).options(joinedload(self.model.event))

        # Add soft delete check
        query = query.filter(self.model.deleted_at.is_(None))

        # Apply filters
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.filter(getattr(self.model, field) == value)

        return query.order_by(desc(self.model.edge_percentage)).offset(skip).limit(limit).all()


edge_crud = CRUDEdge(Edge)
