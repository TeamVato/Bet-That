import logging
from datetime import datetime, timedelta
from typing import List, Optional, cast

from sqlalchemy.orm import Session

from api.enums.betting_enums import BetStatus, BetType, BetCategory
from api.exceptions.betting_exceptions import (
    BetCreationError,
    BetNotFoundError,
    BetValidationError,
    UnauthorizedBetActionError,
)
from api.repositories.peer_bet_repository import PeerBetRepository
from api.schemas.bet_schemas import (
    PeerBetCreateRequest,
    PeerBetOutcomeResponse,
    PeerBetResponse,
    PeerBetSummaryResponse,
)

logger = logging.getLogger(__name__)


class PeerBetService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = PeerBetRepository(db)

    def create_peer_bet(self, bet_data: PeerBetCreateRequest, creator_id: int) -> PeerBetResponse:
        """Create a new peer bet with comprehensive validation"""
        # Validate user can create bet
        can_create, reason = self.repository.can_user_create_bet(creator_id)
        if not can_create:
            raise BetCreationError(reason)

        # Validate bet data
        self._validate_bet_creation_data(bet_data)

        try:
            # Create the bet
            peer_bet = self.repository.create_peer_bet(bet_data, creator_id)

            # If starts_at is not set and is_public is True, activate immediately
            if bet_data.is_public and bet_data.starts_at is None:
                self.repository.update_peer_bet_status(cast(int, peer_bet.id), BetStatus.ACTIVE)
                # Refresh the peer_bet to get updated status from database
                self.db.refresh(peer_bet)

            logger.info(f"Peer bet created successfully: {peer_bet.id}")
            return self._convert_to_response(peer_bet)

        except Exception as e:
            logger.error(f"Failed to create peer bet: {str(e)}")
            raise BetCreationError(f"Failed to create bet: {str(e)}")

    def get_peer_bet(
        self, bet_id: int, requesting_user_id: Optional[int] = None
    ) -> PeerBetResponse:
        """Get a peer bet by ID with access control"""
        peer_bet = self.repository.get_peer_bet_by_id(bet_id)

        if not peer_bet:
            raise BetNotFoundError("Bet not found")

        # Check access permissions
        if not cast(bool, peer_bet.is_public) and cast(int, peer_bet.creator_id) != requesting_user_id:
            raise UnauthorizedBetActionError("Access denied to private bet")

        return self._convert_to_response(peer_bet)

    def get_user_created_bets(
        self, creator_id: int, limit: int = 50
    ) -> List[PeerBetSummaryResponse]:
        """Get bets created by a user"""
        peer_bets = self.repository.get_peer_bets_by_creator(creator_id, limit)
        return [self._convert_to_summary(bet) for bet in peer_bets]

    def get_public_bets(
        self,
        category: Optional[str] = None,
        status: Optional[BetStatus] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[PeerBetSummaryResponse]:
        """Get public bets with filtering"""
        peer_bets = self.repository.get_public_peer_bets(category, status, limit, offset)
        return [self._convert_to_summary(bet) for bet in peer_bets]

    def publish_bet(self, bet_id: int, creator_id: int) -> PeerBetResponse:
        """Publish a draft bet to make it active"""
        peer_bet = self.repository.get_peer_bet_by_id(bet_id)

        if not peer_bet:
            raise BetNotFoundError("Bet not found")

        if cast(int, peer_bet.creator_id) != creator_id:
            raise UnauthorizedBetActionError("Only bet creator can publish bet")

        if cast(str, peer_bet.status) != BetStatus.DRAFT:
            raise BetValidationError("Only draft bets can be published")

        # Validate bet is ready for publishing
        self._validate_bet_for_publishing(peer_bet)

        # Update status to active
        success = self.repository.update_peer_bet_status(bet_id, BetStatus.ACTIVE)
        if not success:
            raise BetCreationError("Failed to publish bet")

        # Refresh the peer_bet to get updated status from database
        self.db.refresh(peer_bet)
        logger.info(f"Peer bet published: {bet_id}")

        return self._convert_to_response(peer_bet)

    def _validate_bet_creation_data(self, bet_data: PeerBetCreateRequest) -> None:
        """Validate bet creation data"""
        # Validate timing
        now = datetime.utcnow()

        if bet_data.starts_at and bet_data.starts_at < now:
            raise BetValidationError("Start time cannot be in the past")

        if bet_data.locks_at and bet_data.starts_at and bet_data.locks_at <= bet_data.starts_at:
            raise BetValidationError("Lock time must be after start time")

        if bet_data.resolves_at and bet_data.locks_at and bet_data.resolves_at <= bet_data.locks_at:
            raise BetValidationError("Resolution time must be after lock time")

        # Validate outcomes
        if len(bet_data.possible_outcomes) < 2:
            raise BetValidationError("Bet must have at least 2 possible outcomes")

        # Validate bet type specific rules
        if bet_data.bet_type == BetType.BINARY and len(bet_data.possible_outcomes) != 2:
            raise BetValidationError("Binary bets must have exactly 2 outcomes")

        # Validate stake amounts
        if bet_data.maximum_stake and bet_data.maximum_stake <= bet_data.minimum_stake:
            raise BetValidationError("Maximum stake must be greater than minimum stake")

        if bet_data.minimum_stake <= 0:
            raise BetValidationError("Minimum stake must be positive")

    def _validate_bet_for_publishing(self, peer_bet) -> None:
        """Validate bet is ready for publishing"""
        if not peer_bet.possible_outcomes:
            raise BetValidationError("Bet must have outcomes defined")

        if peer_bet.locks_at and cast(datetime, peer_bet.locks_at) <= datetime.utcnow():
            raise BetValidationError("Cannot publish bet that has already locked")

    def _convert_to_response(self, peer_bet) -> PeerBetResponse:
        """Convert PeerBet model to response schema"""
        return PeerBetResponse(
            id=cast(int, peer_bet.id),
            title=cast(str, peer_bet.title),
            description=cast(str, peer_bet.description),
            category=cast(BetCategory, peer_bet.category),
            bet_type=cast(BetType, peer_bet.bet_type),
            status=cast(BetStatus, peer_bet.status),
            creator_id=cast(int, peer_bet.creator_id),
            minimum_stake=peer_bet.minimum_stake,
            maximum_stake=peer_bet.maximum_stake,
            total_stake_pool=peer_bet.total_stake_pool,
            current_participants=cast(int, peer_bet.current_participants),
            participant_limit=peer_bet.participant_limit,
            created_at=cast(datetime, peer_bet.created_at),
            starts_at=peer_bet.starts_at,
            locks_at=peer_bet.locks_at,
            resolves_at=peer_bet.resolves_at,
            resolved_at=peer_bet.resolved_at,
            is_public=cast(bool, peer_bet.is_public),
            requires_approval=cast(bool, peer_bet.requires_approval),
            auto_resolve=cast(bool, peer_bet.auto_resolve),
            possible_outcomes=peer_bet.possible_outcomes,
            winning_outcome=peer_bet.winning_outcome,
            outcome_source=peer_bet.outcome_source,
            platform_fee_percentage=peer_bet.platform_fee_percentage,
            creator_fee_percentage=peer_bet.creator_fee_percentage,
            tags=peer_bet.tags,
            external_reference=peer_bet.external_reference,
            notes=peer_bet.notes,
            updated_at=cast(datetime, peer_bet.updated_at),
            is_active=peer_bet.is_active,
            is_locked=peer_bet.is_locked,
            can_be_resolved=peer_bet.can_be_resolved,
        )

    def _convert_to_summary(self, peer_bet) -> PeerBetSummaryResponse:
        """Convert PeerBet model to summary response schema"""
        return PeerBetSummaryResponse(
            id=cast(int, peer_bet.id),
            title=cast(str, peer_bet.title),
            category=cast(BetCategory, peer_bet.category),
            status=cast(BetStatus, peer_bet.status),
            total_stake_pool=peer_bet.total_stake_pool,
            current_participants=cast(int, peer_bet.current_participants),
            participant_limit=peer_bet.participant_limit,
            created_at=cast(datetime, peer_bet.created_at),
            locks_at=peer_bet.locks_at,
            is_public=cast(bool, peer_bet.is_public),
            is_active=peer_bet.is_active,
            is_locked=peer_bet.is_locked,
        )
