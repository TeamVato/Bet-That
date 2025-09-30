import json
import logging
from datetime import datetime
from typing import List, Optional, Tuple, cast

from sqlalchemy import and_, asc, desc, or_
from sqlalchemy.orm import Session

from api.enums.betting_enums import BetStatus, BetType, OutcomeStatus
from api.models import PeerBet, PeerBetOutcome, PeerBetParticipant, User
from api.schemas.bet_schemas import PeerBetCreateRequest

logger = logging.getLogger(__name__)


class PeerBetRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_peer_bet(self, bet_data: PeerBetCreateRequest, creator_id: int) -> PeerBet:
        """Create a new peer bet with outcomes"""
        try:
            # Prepare possible outcomes as JSON
            possible_outcomes = [outcome.dict() for outcome in bet_data.possible_outcomes]

            # Create the peer bet
            peer_bet = PeerBet(
                title=bet_data.title,
                description=bet_data.description,
                category=bet_data.category,
                bet_type=bet_data.bet_type,
                creator_id=creator_id,
                minimum_stake=bet_data.minimum_stake,
                maximum_stake=bet_data.maximum_stake,
                participant_limit=bet_data.participant_limit,
                starts_at=bet_data.starts_at,
                locks_at=bet_data.locks_at,
                resolves_at=bet_data.resolves_at,
                is_public=bet_data.is_public,
                requires_approval=bet_data.requires_approval,
                possible_outcomes=json.dumps(possible_outcomes),
                tags=json.dumps(bet_data.tags) if bet_data.tags else None,
                status=BetStatus.DRAFT,
                created_at=datetime.utcnow(),
            )

            self.db.add(peer_bet)
            self.db.flush()  # Get the ID

            # Create bet outcomes
            for i, outcome_data in enumerate(bet_data.possible_outcomes):
                outcome = PeerBetOutcome(
                    bet_id=peer_bet.id,
                    name=outcome_data.name,
                    description=outcome_data.description,
                    odds=outcome_data.odds,
                    order_index=i,
                    status=OutcomeStatus.PENDING,
                    created_at=datetime.utcnow(),
                )
                self.db.add(outcome)

            self.db.commit()
            self.db.refresh(peer_bet)

            logger.info(f"Created peer bet: {peer_bet.id} by user {creator_id}")
            return peer_bet

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create peer bet: {str(e)}")
            raise

    def get_peer_bet_by_id(self, bet_id: int) -> Optional[PeerBet]:
        """Get peer bet by ID with all relationships"""
        return self.db.query(PeerBet).filter(PeerBet.id == bet_id).first()

    def get_peer_bets_by_creator(self, creator_id: int, limit: int = 50) -> List[PeerBet]:
        """Get peer bets created by a specific user"""
        return (
            self.db.query(PeerBet)
            .filter(PeerBet.creator_id == creator_id)
            .order_by(desc(PeerBet.created_at))
            .limit(limit)
            .all()
        )

    def get_public_peer_bets(
        self,
        category: Optional[str] = None,
        status: Optional[BetStatus] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[PeerBet]:
        """Get public peer bets with optional filtering"""
        query = self.db.query(PeerBet).filter(PeerBet.is_public.is_(True))

        if category:
            query = query.filter(PeerBet.category == category)

        if status:
            query = query.filter(PeerBet.status == status)

        return query.order_by(desc(PeerBet.created_at)).offset(offset).limit(limit).all()

    def update_peer_bet_status(self, bet_id: int, status: BetStatus) -> bool:
        """Update peer bet status"""
        try:
            updated = (
                self.db.query(PeerBet)
                .filter(PeerBet.id == bet_id)
                .update({"status": status, "updated_at": datetime.utcnow()})
            )
            self.db.commit()
            return updated > 0
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update peer bet status: {str(e)}")
            return False

    def get_bet_outcomes(self, bet_id: int) -> List[PeerBetOutcome]:
        """Get all outcomes for a peer bet"""
        return (
            self.db.query(PeerBetOutcome)
            .filter(PeerBetOutcome.bet_id == bet_id)
            .order_by(asc(PeerBetOutcome.order_index))
            .all()
        )

    def can_user_create_bet(self, user_id: int) -> Tuple[bool, str]:
        """Check if user can create a new bet (rate limiting, etc.)"""
        # Check if user exists and is active
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user or not cast(bool, user.is_active):
            return False, "User not found or inactive"

        # Check daily creation limit (example: 10 bets per day)
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_count = (
            self.db.query(PeerBet)
            .filter(and_(PeerBet.creator_id == user_id, PeerBet.created_at >= today_start))
            .count()
        )

        if today_count >= 10:
            return False, "Daily bet creation limit exceeded (10 bets per day)"

        return True, "OK"
