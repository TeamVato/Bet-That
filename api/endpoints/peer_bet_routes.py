import logging
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from api.auth.dependencies import get_current_user_from_token, get_current_user_optional, CurrentUser, OptionalUser
from api.database import get_db
from api.enums.betting_enums import BetCategory, BetStatus
from api.exceptions.betting_exceptions import (
    BetCreationError,
    BetNotFoundError,
    BetValidationError,
    UnauthorizedBetActionError,
)
from api.schemas.bet_schemas import PeerBetCreateRequest, PeerBetResponse, PeerBetSummaryResponse
from api.services.peer_bet_service import PeerBetService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/bets", tags=["peer-bets"])


@router.post("/", response_model=PeerBetResponse, status_code=status.HTTP_201_CREATED)
async def create_peer_bet(
    bet_data: PeerBetCreateRequest,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> PeerBetResponse:
    """Create a new peer-to-peer bet"""
    try:
        service = PeerBetService(db)
        result = service.create_peer_bet(bet_data, int(current_user.id))
        logger.info(f"Peer bet created: {result.id} by user {current_user.id}")
        return result
    except BetCreationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except BetValidationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error creating bet: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create bet"
        )


@router.get("/{bet_id}", response_model=PeerBetResponse)
async def get_peer_bet(
    bet_id: int, 
    db: Annotated[Session, Depends(get_db)],
    current_user: OptionalUser = None
) -> PeerBetResponse:
    """Get a specific peer bet by ID"""
    try:
        service = PeerBetService(db)
        return service.get_peer_bet(bet_id, int(current_user.id) if current_user else None)
    except BetNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bet not found")
    except UnauthorizedBetActionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")


@router.get("/", response_model=List[PeerBetSummaryResponse])
async def get_public_peer_bets(
    db: Annotated[Session, Depends(get_db)],
    category: Annotated[Optional[BetCategory], Query(description="Filter by category")] = None,
    bet_status: Annotated[Optional[BetStatus], Query(description="Filter by status")] = None,
    limit: Annotated[int, Query(ge=1, le=100, description="Number of bets to return")] = 50,
    offset: Annotated[int, Query(ge=0, description="Number of bets to skip")] = 0,
) -> List[PeerBetSummaryResponse]:
    """Get public peer bets with optional filtering"""
    try:
        service = PeerBetService(db)
        return service.get_public_bets(category, bet_status, limit, offset)
    except Exception as e:
        logger.error(f"Error fetching public bets: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch bets"
        )


@router.get("/my/created", response_model=List[PeerBetSummaryResponse])
async def get_my_created_bets(
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> List[PeerBetSummaryResponse]:
    """Get bets created by the current user"""
    try:
        service = PeerBetService(db)
        return service.get_user_created_bets(int(current_user.id), limit)
    except Exception as e:
        logger.error(f"Error fetching user's created bets: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch your bets"
        )


@router.post("/{bet_id}/publish", response_model=PeerBetResponse)
async def publish_peer_bet(
    bet_id: int, 
    current_user: CurrentUser, 
    db: Annotated[Session, Depends(get_db)]
) -> PeerBetResponse:
    """Publish a draft bet to make it active"""
    try:
        service = PeerBetService(db)
        return service.publish_bet(bet_id, int(current_user.id))
    except BetNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bet not found")
    except UnauthorizedBetActionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only bet creator can publish bet"
        )
    except BetValidationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        logger.error(f"Error publishing bet: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to publish bet"
        )
