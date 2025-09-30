"""Repository for bet resolution operations"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy.orm import Session

from ..models import Bet, BetResolutionHistory, BetStatus, User


class BetRepository:
    """Repository for bet resolution data operations"""

    def __init__(self, db: Session):
        self.db = db

    def get_bet_by_id(self, bet_id: int) -> Optional[Bet]:
        """Get bet by ID"""
        return self.db.query(Bet).filter(Bet.id == bet_id).first()

    def get_bet_with_user(self, bet_id: int) -> Optional[Bet]:
        """Get bet with user relationship loaded"""
        return (
            self.db.query(Bet)
            .join(User, Bet.user_id == User.id)
            .filter(Bet.id == bet_id)
            .first()
        )

    def can_user_resolve_bet(self, bet: Bet, user_id: int) -> bool:
        """Check if user can resolve this bet (bet creator or admin)"""
        # For now, only bet creator can resolve
        # TODO: Add admin role check
        return bet.user_id == user_id

    def resolve_bet(
        self,
        bet_id: int,
        result: str,
        resolved_by: int,
        resolution_notes: Optional[str] = None,
        resolution_source: Optional[str] = None,
    ) -> Optional[Bet]:
        """Resolve a bet with result and create audit trail"""
        bet = self.get_bet_by_id(bet_id)
        if not bet:
            return None

        if bet.status != BetStatus.PENDING:
            raise ValueError("Can only resolve pending bets")

        # Store previous values for audit trail
        previous_status = bet.status
        previous_result = bet.result

        # Update bet
        bet.status = BetStatus.SETTLED
        bet.result = result
        bet.settled_at = datetime.utcnow()
        bet.graded_at = datetime.utcnow()
        bet.resolved_at = datetime.utcnow()
        bet.resolved_by = resolved_by
        bet.resolution_notes = resolution_notes
        bet.resolution_source = resolution_source

        # Calculate actual return and profit
        if result == "win":
            bet.actual_return = bet.potential_return
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

        # Create audit trail entry
        history_entry = BetResolutionHistory(
            bet_id=bet_id,
            action_type="resolve",
            previous_status=previous_status,
            new_status=bet.status,
            previous_result=previous_result,
            new_result=result,
            resolution_notes=resolution_notes,
            resolution_source=resolution_source,
            performed_by=resolved_by,
        )

        try:
            self.db.add(bet)
            self.db.add(history_entry)
            self.db.commit()
            self.db.refresh(bet)
            return bet
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Failed to resolve bet: {str(e)}")

    def dispute_bet_resolution(
        self, bet_id: int, dispute_reason: str, disputed_by: int
    ) -> Optional[Bet]:
        """Dispute a bet resolution"""
        bet = self.get_bet_by_id(bet_id)
        if not bet:
            return None

        if bet.status != BetStatus.SETTLED:
            raise ValueError("Can only dispute settled bets")

        if bet.is_disputed:
            raise ValueError("Bet is already disputed")

        # Update bet
        bet.is_disputed = True
        bet.dispute_reason = dispute_reason
        bet.dispute_created_at = datetime.utcnow()

        # Create audit trail entry
        history_entry = BetResolutionHistory(
            bet_id=bet_id,
            action_type="dispute",
            previous_status=bet.status,
            new_status=bet.status,  # Status doesn't change on dispute
            previous_result=bet.result,
            new_result=bet.result,  # Result doesn't change on dispute
            dispute_reason=dispute_reason,
            performed_by=disputed_by,
        )

        try:
            self.db.add(bet)
            self.db.add(history_entry)
            self.db.commit()
            self.db.refresh(bet)
            return bet
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Failed to dispute bet: {str(e)}")

    def resolve_dispute(
        self,
        bet_id: int,
        new_result: Optional[str] = None,
        resolved_by: int = None,
        resolution_notes: Optional[str] = None,
    ) -> Optional[Bet]:
        """Resolve a bet dispute (admin only)"""
        bet = self.get_bet_by_id(bet_id)
        if not bet:
            return None

        if not bet.is_disputed:
            raise ValueError("Bet is not disputed")

        # Store previous values for audit trail
        previous_status = bet.status
        previous_result = bet.result

        # Update bet if new result provided
        if new_result:
            bet.result = new_result
            bet.resolution_notes = resolution_notes
            bet.resolved_by = resolved_by
            bet.resolved_at = datetime.utcnow()

            # Recalculate actual return and profit
            if new_result == "win":
                bet.actual_return = bet.potential_return
                bet.net_profit = bet.actual_return - bet.stake
            elif new_result == "loss":
                bet.actual_return = Decimal("0.00")
                bet.net_profit = -bet.stake
            elif new_result == "push":
                bet.actual_return = bet.stake
                bet.net_profit = Decimal("0.00")
            elif new_result == "void":
                bet.actual_return = bet.stake
                bet.net_profit = Decimal("0.00")
                bet.status = BetStatus.VOIDED

        # Clear dispute
        bet.is_disputed = False
        bet.dispute_resolved_at = datetime.utcnow()
        bet.dispute_resolved_by = resolved_by

        # Create audit trail entry
        history_entry = BetResolutionHistory(
            bet_id=bet_id,
            action_type="dispute_resolve",
            previous_status=previous_status,
            new_status=bet.status,
            previous_result=previous_result,
            new_result=bet.result,
            resolution_notes=resolution_notes,
            performed_by=resolved_by,
        )

        try:
            self.db.add(bet)
            self.db.add(history_entry)
            self.db.commit()
            self.db.refresh(bet)
            return bet
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Failed to resolve dispute: {str(e)}")

    def get_resolution_history(
        self, bet_id: int, skip: int = 0, limit: int = 100
    ) -> List[BetResolutionHistory]:
        """Get resolution history for a bet"""
        return (
            self.db.query(BetResolutionHistory)
            .filter(BetResolutionHistory.bet_id == bet_id)
            .order_by(BetResolutionHistory.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_resolution_history_count(self, bet_id: int) -> int:
        """Get count of resolution history entries for a bet"""
        return (
            self.db.query(BetResolutionHistory)
            .filter(BetResolutionHistory.bet_id == bet_id)
            .count()
        )

    def get_disputed_bets(self, skip: int = 0, limit: int = 100) -> List[Bet]:
        """Get all disputed bets"""
        return (
            self.db.query(Bet)
            .filter(Bet.is_disputed == True)
            .order_by(Bet.dispute_created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_pending_resolution_bets(self, skip: int = 0, limit: int = 100) -> List[Bet]:
        """Get bets that are pending resolution"""
        return (
            self.db.query(Bet)
            .filter(Bet.status == BetStatus.PENDING)
            .order_by(Bet.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
