"""CRUD operations for Bet model"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, desc, func, or_
from sqlalchemy.orm import Session

from ..models import Bet, BetStatus, Edge, User
from ..schemas import BetCreateRequest, BetUpdateRequest
from .base import CRUDBase


class CRUDBet(CRUDBase[Bet, BetCreateRequest, BetUpdateRequest]):

    def create_with_user(self, db: Session, *, obj_in: BetCreateRequest, user_id: int) -> Bet:
        """Create bet with user association and calculate derived fields"""
        # Get user for validation
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")

        # Validate user can place this bet
        if not user.can_place_bet(float(obj_in.stake)):
            raise ValueError("Bet amount exceeds user's maximum bet size")

        # Calculate derived fields
        potential_return = float(obj_in.stake) * obj_in.odds_decimal
        net_amount = potential_return - float(obj_in.stake)

        # Create bet data
        bet_data = obj_in.dict()
        bet_data.update(
            {
                "user_id": user_id,
                "external_user_id": user.external_id,
                "potential_return": Decimal(str(potential_return)),
                "placed_at": datetime.utcnow(),
            }
        )

        # Get edge information if edge_id provided
        if obj_in.edge_id:
            edge = db.query(Edge).filter(Edge.edge_id == obj_in.edge_id).first()
            if edge:
                bet_data.update(
                    {
                        "edge_percentage": edge.edge_percentage,
                        "kelly_fraction_used": edge.kelly_fraction,
                        "expected_value": Decimal(
                            str(edge.expected_value_per_dollar * float(obj_in.stake))
                        ),
                        "model_probability": edge.model_probability,
                    }
                )

        db_obj = self.model(**bet_data)

        try:
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except Exception as e:
            db.rollback()
            raise ValueError(f"Failed to create bet: {str(e)}")

    def get_by_user(
        self,
        db: Session,
        *,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        status: Optional[BetStatus] = None,
    ) -> List[Bet]:
        """Get bets for a specific user"""
        filters = {"user_id": user_id}
        if status:
            filters["status"] = status

        return self.get_multi(db=db, skip=skip, limit=limit, filters=filters, order_by="created_at")

    def get_by_event(
        self, db: Session, *, event_id: str, skip: int = 0, limit: int = 100
    ) -> List[Bet]:
        """Get all bets for a specific event"""
        return self.get_multi(db=db, skip=skip, limit=limit, filters={"event_id": event_id})

    def get_by_sportsbook(
        self, db: Session, *, sportsbook_id: str, skip: int = 0, limit: int = 100
    ) -> List[Bet]:
        """Get bets for a specific sportsbook"""
        return self.get_multi(
            db=db, skip=skip, limit=limit, filters={"sportsbook_id": sportsbook_id}
        )

    def get_pending_bets(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Bet]:
        """Get all pending bets"""
        return self.get_multi(db=db, skip=skip, limit=limit, filters={"status": BetStatus.PENDING})

    def get_settled_bets(
        self, db: Session, *, user_id: Optional[int] = None, skip: int = 0, limit: int = 100
    ) -> List[Bet]:
        """Get settled bets, optionally filtered by user"""
        filters = {"status": BetStatus.SETTLED}
        if user_id:
            filters["user_id"] = user_id

        return self.get_multi(db=db, skip=skip, limit=limit, filters=filters)

    def get_recent_bets(
        self,
        db: Session,
        *,
        days: int = 7,
        user_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Bet]:
        """Get bets from the last N days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        query = db.query(self.model).filter(
            and_(self.model.created_at >= cutoff_date, self.model.deleted_at.is_(None))
        )

        if user_id:
            query = query.filter(self.model.user_id == user_id)

        return query.order_by(desc(self.model.created_at)).offset(skip).limit(limit).all()

    def settle_bet(
        self, db: Session, *, bet_id: int, result: str, actual_return: Optional[Decimal] = None
    ) -> Optional[Bet]:
        """Settle a bet with result"""
        bet = self.get(db=db, id=bet_id)
        if not bet:
            return None

        if bet.status != BetStatus.PENDING:
            raise ValueError("Can only settle pending bets")

        bet.status = BetStatus.SETTLED
        bet.result = result
        bet.settled_at = datetime.utcnow()
        bet.graded_at = datetime.utcnow()

        # Calculate actual return and profit
        if result == "win":
            bet.actual_return = actual_return or bet.potential_return
            bet.net_profit = bet.actual_return - bet.stake
        elif result == "loss":
            bet.actual_return = Decimal("0.00")
            bet.net_profit = -bet.stake
        elif result == "push":
            bet.actual_return = bet.stake
            bet.net_profit = Decimal("0.00")
        elif result == "void":
            bet.actual_return = bet.stake
            bet.net_profit = Decimal("0.00")
            bet.status = BetStatus.VOIDED

        db.add(bet)
        db.commit()
        db.refresh(bet)
        return bet

    def cancel_bet(self, db: Session, *, bet_id: int, reason: str = None) -> Optional[Bet]:
        """Cancel a pending bet"""
        bet = self.get(db=db, id=bet_id)
        if not bet:
            return None

        if bet.status != BetStatus.PENDING:
            raise ValueError("Can only cancel pending bets")

        bet.status = BetStatus.CANCELLED
        if reason:
            bet.notes = f"{bet.notes or ''}\nCancelled: {reason}".strip()

        db.add(bet)
        db.commit()
        db.refresh(bet)
        return bet

    def update_clv(
        self,
        db: Session,
        *,
        bet_id: int,
        closing_odds_american: int,
        closing_odds_decimal: float,
        clv_cents: float,
    ) -> Optional[Bet]:
        """Update bet with closing line value information"""
        bet = self.get(db=db, id=bet_id)
        if not bet:
            return None

        bet.closing_odds_american = closing_odds_american
        bet.closing_odds_decimal = closing_odds_decimal
        bet.clv_cents = clv_cents
        bet.beat_close = clv_cents > 0

        db.add(bet)
        db.commit()
        db.refresh(bet)
        return bet

    def get_user_bet_statistics(self, db: Session, *, user_id: int) -> Dict[str, Any]:
        """Get comprehensive betting statistics for a user"""
        query = db.query(self.model).filter(
            and_(self.model.user_id == user_id, self.model.deleted_at.is_(None))
        )

        total_bets = query.count()
        settled_bets = query.filter(self.model.status == BetStatus.SETTLED).all()

        if not settled_bets:
            return {
                "total_bets": total_bets,
                "settled_bets": 0,
                "win_rate": 0.0,
                "total_staked": 0.0,
                "total_return": 0.0,
                "net_profit": 0.0,
                "roi": 0.0,
                "avg_clv_cents": 0.0,
                "beat_close_rate": 0.0,
            }

        # Calculate statistics
        total_staked = sum(float(bet.stake) for bet in settled_bets)
        total_return = sum(float(bet.actual_return or 0) for bet in settled_bets)
        net_profit = total_return - total_staked

        winning_bets = [bet for bet in settled_bets if bet.result == "win"]
        win_rate = len(winning_bets) / len(settled_bets) if settled_bets else 0.0

        roi = (net_profit / total_staked * 100) if total_staked > 0 else 0.0

        # CLV statistics
        clv_bets = [bet for bet in settled_bets if bet.clv_cents is not None]
        avg_clv_cents = sum(bet.clv_cents for bet in clv_bets) / len(clv_bets) if clv_bets else 0.0
        beat_close_count = sum(1 for bet in clv_bets if bet.beat_close)
        beat_close_rate = beat_close_count / len(clv_bets) if clv_bets else 0.0

        return {
            "total_bets": total_bets,
            "settled_bets": len(settled_bets),
            "win_rate": round(win_rate * 100, 2),
            "total_staked": round(total_staked, 2),
            "total_return": round(total_return, 2),
            "net_profit": round(net_profit, 2),
            "roi": round(roi, 2),
            "avg_clv_cents": round(avg_clv_cents, 2),
            "beat_close_rate": round(beat_close_rate * 100, 2),
        }


bet_crud = CRUDBet(Bet)
