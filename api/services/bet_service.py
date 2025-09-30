"""Service layer for bet resolution business logic"""

from typing import List, Optional

from sqlalchemy.orm import Session

from ..models import User
from ..repositories.bet_repository import BetRepository
from ..schemas.bet_schemas import (
    BetDisputeRequest,
    BetResolveRequest,
    BetResolutionHistoryListResponse,
    BetResolutionHistoryResponse,
    BetResponse,
)
from ..schemas import BetListResponse
from ..endpoints.websocket import send_bet_status_update, send_dispute_resolution_update
from ..services.email_service import send_bet_resolution_notification, send_bet_dispute_notification


class BetService:
    """Service for bet resolution business logic"""

    def __init__(self, db: Session):
        self.db = db
        self.bet_repository = BetRepository(db)

    def resolve_bet(
        self, bet_id: int, request: BetResolveRequest, user_id: int
    ) -> BetResponse:
        """Resolve a bet with validation and business logic"""
        # Get bet with user relationship
        bet = self.bet_repository.get_bet_with_user(bet_id)
        if not bet:
            raise ValueError("Bet not found")

        # Validate user can resolve this bet
        if not self.bet_repository.can_user_resolve_bet(bet, user_id):
            raise ValueError("User not authorized to resolve this bet")

        # Store old status for WebSocket update
        old_status = bet.status
        
        # Resolve the bet
        resolved_bet = self.bet_repository.resolve_bet(
            bet_id=bet_id,
            result=request.result,
            resolved_by=user_id,
            resolution_notes=request.resolution_notes,
            resolution_source=request.resolution_source,
        )

        if not resolved_bet:
            raise ValueError("Failed to resolve bet")

        # Send WebSocket update
        try:
            import asyncio
            asyncio.create_task(send_bet_status_update(
                bet=resolved_bet,
                old_status=old_status,
                new_status=resolved_bet.status,
                result=request.result,
                resolution_notes=request.resolution_notes
            ))
        except Exception as e:
            # Log error but don't fail the resolution
            print(f"Failed to send WebSocket update: {e}")
        
        # Send email notification (optional)
        try:
            if resolved_bet.user and resolved_bet.user.email:
                send_bet_resolution_notification(
                    bet=resolved_bet,
                    user=resolved_bet.user,
                    result=request.result,
                    resolution_notes=request.resolution_notes
                )
        except Exception as e:
            # Log error but don't fail the resolution
            print(f"Failed to send email notification: {e}")

        return self._build_bet_response(resolved_bet)

    def dispute_bet_resolution(
        self, bet_id: int, request: BetDisputeRequest, user_id: int
    ) -> BetResponse:
        """Dispute a bet resolution"""
        # Get bet
        bet = self.bet_repository.get_bet_by_id(bet_id)
        if not bet:
            raise ValueError("Bet not found")

        # Validate user can dispute this bet (bet creator)
        if bet.user_id != user_id:
            raise ValueError("User not authorized to dispute this bet")

        # Dispute the bet
        disputed_bet = self.bet_repository.dispute_bet_resolution(
            bet_id=bet_id,
            dispute_reason=request.dispute_reason,
            disputed_by=user_id,
        )

        if not disputed_bet:
            raise ValueError("Failed to dispute bet")

        # Send WebSocket update
        try:
            import asyncio
            asyncio.create_task(send_dispute_resolution_update(
                bet=disputed_bet,
                dispute_reason=request.dispute_reason
            ))
        except Exception as e:
            # Log error but don't fail the dispute
            print(f"Failed to send WebSocket update: {e}")
        
        # Send email notification (optional)
        try:
            if disputed_bet.user and disputed_bet.user.email:
                send_bet_dispute_notification(
                    bet=disputed_bet,
                    user=disputed_bet.user,
                    dispute_reason=request.dispute_reason
                )
        except Exception as e:
            # Log error but don't fail the dispute
            print(f"Failed to send email notification: {e}")

        return self._build_bet_response(disputed_bet)

    def resolve_dispute(
        self,
        bet_id: int,
        new_result: Optional[str] = None,
        resolution_notes: Optional[str] = None,
        admin_user_id: int = None,
    ) -> BetResponse:
        """Resolve a bet dispute (admin only)"""
        # TODO: Add admin role validation
        # For now, any user can resolve disputes (should be restricted to admins)

        # Get bet
        bet = self.bet_repository.get_bet_by_id(bet_id)
        if not bet:
            raise ValueError("Bet not found")

        # Resolve the dispute
        resolved_bet = self.bet_repository.resolve_dispute(
            bet_id=bet_id,
            new_result=new_result,
            resolved_by=admin_user_id,
            resolution_notes=resolution_notes,
        )

        if not resolved_bet:
            raise ValueError("Failed to resolve dispute")

        return self._build_bet_response(resolved_bet)

    def get_resolution_history(
        self, bet_id: int, page: int = 1, per_page: int = 50
    ) -> BetResolutionHistoryListResponse:
        """Get resolution history for a bet"""
        # Validate bet exists
        bet = self.bet_repository.get_bet_by_id(bet_id)
        if not bet:
            raise ValueError("Bet not found")

        # Calculate pagination
        skip = (page - 1) * per_page

        # Get history
        history = self.bet_repository.get_resolution_history(
            bet_id=bet_id, skip=skip, limit=per_page
        )
        total = self.bet_repository.get_resolution_history_count(bet_id)

        # Build response
        history_responses = [
            BetResolutionHistoryResponse(
                id=h.id,
                bet_id=h.bet_id,
                action_type=h.action_type,
                previous_status=h.previous_status,
                new_status=h.new_status,
                previous_result=h.previous_result,
                new_result=h.new_result,
                resolution_notes=h.resolution_notes,
                resolution_source=h.resolution_source,
                dispute_reason=h.dispute_reason,
                performed_by=h.performed_by,
                created_at=h.created_at,
            )
            for h in history
        ]

        return BetResolutionHistoryListResponse(
            history=history_responses,
            total=total,
            page=page,
            per_page=per_page,
        )

    def get_disputed_bets(
        self, page: int = 1, per_page: int = 50
    ) -> BetListResponse:
        """Get all disputed bets (admin only)"""
        # TODO: Add admin role validation

        # Calculate pagination
        skip = (page - 1) * per_page

        # Get disputed bets
        bets = self.bet_repository.get_disputed_bets(skip=skip, limit=per_page)

        # Build response
        bet_responses = [self._build_bet_response(bet) for bet in bets]

        return BetListResponse(
            bets=bet_responses,
            total=len(bet_responses),  # TODO: Get actual total count
            page=page,
            per_page=per_page,
        )

    def get_pending_resolution_bets(
        self, page: int = 1, per_page: int = 50
    ) -> BetListResponse:
        """Get bets pending resolution"""
        # Calculate pagination
        skip = (page - 1) * per_page

        # Get pending bets
        bets = self.bet_repository.get_pending_resolution_bets(
            skip=skip, limit=per_page
        )

        # Build response
        bet_responses = [self._build_bet_response(bet) for bet in bets]

        return BetListResponse(
            bets=bet_responses,
            total=len(bet_responses),  # TODO: Get actual total count
            page=page,
            per_page=per_page,
        )

    def _build_bet_response(self, bet) -> BetResponse:
        """Build BetResponse from Bet model"""
        return BetResponse(
            id=bet.id,
            user_id=bet.user_id,
            event_id=bet.event_id,
            edge_id=bet.edge_id,
            market_type=bet.market_type,
            market_description=bet.market_description,
            selection=bet.selection,
            line=bet.line,
            side=bet.side,
            stake=bet.stake,
            odds_american=bet.odds_american,
            odds_decimal=bet.odds_decimal,
            potential_return=bet.potential_return,
            actual_return=bet.actual_return,
            net_profit=bet.net_profit,
            status=bet.status,
            result=bet.result,
            settled_at=bet.settled_at,
            sportsbook_id=bet.sportsbook_id,
            sportsbook_name=bet.sportsbook_name,
            external_bet_id=bet.external_bet_id,
            edge_percentage=bet.edge_percentage,
            kelly_fraction_used=bet.kelly_fraction_used,
            expected_value=bet.expected_value,
            clv_cents=bet.clv_cents,
            beat_close=bet.beat_close,
            closing_odds_american=bet.closing_odds_american,
            closing_odds_decimal=bet.closing_odds_decimal,
            notes=bet.notes,
            tags=bet.tags,
            source=bet.source,
            placed_at=bet.placed_at,
            created_at=bet.created_at,
            updated_at=bet.updated_at,
            # Resolution fields
            resolved_at=bet.resolved_at,
            resolved_by=bet.resolved_by,
            resolution_notes=bet.resolution_notes,
            resolution_source=bet.resolution_source,
            is_disputed=bet.is_disputed,
            dispute_reason=bet.dispute_reason,
            dispute_created_at=bet.dispute_created_at,
            dispute_resolved_at=bet.dispute_resolved_at,
            dispute_resolved_by=bet.dispute_resolved_by,
        )
