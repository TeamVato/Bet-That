"""User bet tracking endpoints"""

from typing import Annotated, Any, Union

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import Bet, User
from ..schemas import (
    BetCreateRequest,
    BetListResponse,
    BetResponse,
    UserRegistrationRequest,
    UserRegistrationResponse,
)
from ..schemas.bet_schemas import (
    BetDisputeRequest,
    BetResolveRequest,
    BetResolutionHistoryListResponse,
)
from ..services.bet_service import BetService


def get_model_value(model: Union[User, Bet], field: str) -> Any:
    """Helper function to get actual values from SQLAlchemy model"""
    return getattr(model, field)


def build_bet_response(bet: Bet) -> BetResponse:
    """Helper function to build BetResponse from Bet model"""
    return BetResponse(
        id=get_model_value(bet, "id"),
        user_id=get_model_value(bet, "user_id"),
        event_id=get_model_value(bet, "event_id"),
        edge_id=get_model_value(bet, "edge_id"),
        market_type=get_model_value(bet, "market_type"),
        market_description=get_model_value(bet, "market_description"),
        selection=get_model_value(bet, "selection"),
        line=get_model_value(bet, "line"),
        side=get_model_value(bet, "side"),
        stake=get_model_value(bet, "stake"),
        odds_american=get_model_value(bet, "odds_american"),
        odds_decimal=get_model_value(bet, "odds_decimal"),
        potential_return=get_model_value(bet, "potential_return"),
        actual_return=get_model_value(bet, "actual_return"),
        net_profit=get_model_value(bet, "net_profit"),
        status=get_model_value(bet, "status"),
        result=get_model_value(bet, "result"),
        settled_at=get_model_value(bet, "settled_at"),
        sportsbook_id=get_model_value(bet, "sportsbook_id"),
        sportsbook_name=get_model_value(bet, "sportsbook_name"),
        external_bet_id=get_model_value(bet, "external_bet_id"),
        edge_percentage=get_model_value(bet, "edge_percentage"),
        kelly_fraction_used=get_model_value(bet, "kelly_fraction_used"),
        expected_value=get_model_value(bet, "expected_value"),
        clv_cents=get_model_value(bet, "clv_cents"),
        beat_close=get_model_value(bet, "beat_close"),
        closing_odds_american=get_model_value(bet, "closing_odds_american"),
        closing_odds_decimal=get_model_value(bet, "closing_odds_decimal"),
        notes=get_model_value(bet, "notes"),
        tags=get_model_value(bet, "tags"),
        source=get_model_value(bet, "source"),
        placed_at=get_model_value(bet, "placed_at"),
        created_at=get_model_value(bet, "created_at"),
        updated_at=get_model_value(bet, "updated_at"),
        # Resolution fields
        resolved_at=get_model_value(bet, "resolved_at"),
        resolved_by=get_model_value(bet, "resolved_by"),
        resolution_notes=get_model_value(bet, "resolution_notes"),
        resolution_source=get_model_value(bet, "resolution_source"),
        is_disputed=get_model_value(bet, "is_disputed"),
        dispute_reason=get_model_value(bet, "dispute_reason"),
        dispute_created_at=get_model_value(bet, "dispute_created_at"),
        dispute_resolved_at=get_model_value(bet, "dispute_resolved_at"),
        dispute_resolved_by=get_model_value(bet, "dispute_resolved_by"),
    )

router = APIRouter()


@router.post("/register", response_model=UserRegistrationResponse, tags=["users"])
async def register_user(
    request: UserRegistrationRequest, 
    db: Annotated[Session, Depends(get_db)]
) -> UserRegistrationResponse:
    """
    Register a new user

    Creates user entry or retrieves existing user by external_id.
    Idempotent operation.
    """
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.external_id == request.external_id).first()

        if existing_user:
            # Return existing user
            return UserRegistrationResponse(
                id=get_model_value(existing_user, "id"),
                external_id=get_model_value(existing_user, "external_id"),
                email=get_model_value(existing_user, "email"),
                name=get_model_value(existing_user, "name"),
                status=get_model_value(existing_user, "status"),
                created_at=get_model_value(existing_user, "created_at"),
                is_active=get_model_value(existing_user, "is_active"),
            )

        # Create new user
        new_user = User(external_id=request.external_id, email=request.email, name=request.name)

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return UserRegistrationResponse(
            id=get_model_value(new_user, "id"),
            external_id=get_model_value(new_user, "external_id"),
            email=get_model_value(new_user, "email"),
            name=get_model_value(new_user, "name"),
            status=get_model_value(new_user, "status"),
            created_at=get_model_value(new_user, "created_at"),
            is_active=get_model_value(new_user, "is_active"),
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to register user: {str(e)}")


@router.post("/bets", response_model=BetResponse, tags=["bets"])
async def create_user_bet(
    request: BetCreateRequest,
    user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> BetResponse:
    """
    Log a new user bet

    Creates bet entry for CLV tracking and analysis.
    """
    try:
        if not user or not user.get("external_id"):
            raise HTTPException(status_code=401, detail="User not authenticated")

        # Get or create user by external_id
        db_user = db.query(User).filter(User.external_id == user["external_id"]).first()

        if not db_user:
            raise HTTPException(status_code=404, detail="User not registered")

        # Create bet entry
        new_bet = Bet(
            user_id=db_user.id,
            external_user_id=user["external_id"],
            event_id=request.event_id,
            market_type=request.market_type,
            market_description=request.market_description,
            selection=request.selection,
            line=request.line,
            side=request.side,
            stake=request.stake,
            odds_american=request.odds_american,
            odds_decimal=request.odds_decimal,
            sportsbook_id=request.sportsbook_id,
            sportsbook_name=request.sportsbook_name,
            external_bet_id=request.external_bet_id,
            notes=request.notes,
            tags=request.tags,
        )

        db.add(new_bet)
        db.commit()
        db.refresh(new_bet)

        return build_bet_response(new_bet)

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create bet: {str(e)}")


@router.get("/bets", response_model=BetListResponse, tags=["bets"])
async def get_user_bets(
    user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    limit: int = 50,
    offset: int = 0,
) -> BetListResponse:
    """
    Get user's bet history

    Returns paginated list of user bets.
    """
    try:
        if not user or not user.get("external_id"):
            raise HTTPException(status_code=401, detail="User not authenticated")

        # Query user bets
        bets_query = (
            db.query(Bet)
            .filter(Bet.external_user_id == user["external_id"])
            .order_by(Bet.created_at.desc())
        )

        total_count = bets_query.count()
        bets = bets_query.offset(offset).limit(limit).all()

        bet_responses = [build_bet_response(bet) for bet in bets]

        return BetListResponse(bets=bet_responses, total=total_count, page=offset // limit + 1, per_page=limit)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user bets: {str(e)}")


# BET RESOLUTION ENDPOINTS

@router.post("/bets/{bet_id}/resolve", response_model=BetResponse, tags=["bets"])
async def resolve_bet(
    bet_id: int,
    request: BetResolveRequest,
    user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> BetResponse:
    """
    Resolve a bet
    
    Allows bet creator to resolve their bet with a result.
    """
    try:
        if not user or not user.get("external_id"):
            raise HTTPException(status_code=401, detail="User not authenticated")

        # Get user ID
        db_user = db.query(User).filter(User.external_id == user["external_id"]).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        # Resolve bet using service
        bet_service = BetService(db)
        resolved_bet = bet_service.resolve_bet(
            bet_id=bet_id,
            request=request,
            user_id=db_user.id,
        )

        return resolved_bet

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to resolve bet: {str(e)}")


@router.post("/bets/{bet_id}/dispute", response_model=BetResponse, tags=["bets"])
async def dispute_bet_resolution(
    bet_id: int,
    request: BetDisputeRequest,
    user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> BetResponse:
    """
    Dispute a bet resolution
    
    Allows bet creator to dispute the resolution of their bet.
    """
    try:
        if not user or not user.get("external_id"):
            raise HTTPException(status_code=401, detail="User not authenticated")

        # Get user ID
        db_user = db.query(User).filter(User.external_id == user["external_id"]).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        # Dispute bet using service
        bet_service = BetService(db)
        disputed_bet = bet_service.dispute_bet_resolution(
            bet_id=bet_id,
            request=request,
            user_id=db_user.id,
        )

        return disputed_bet

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to dispute bet: {str(e)}")


@router.get("/bets/{bet_id}/resolution-history", response_model=BetResolutionHistoryListResponse, tags=["bets"])
async def get_bet_resolution_history(
    bet_id: int,
    user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=100, description="Items per page"),
) -> BetResolutionHistoryListResponse:
    """
    Get resolution history for a bet
    
    Returns audit trail of all resolution actions for a bet.
    """
    try:
        if not user or not user.get("external_id"):
            raise HTTPException(status_code=401, detail="User not authenticated")

        # Get resolution history using service
        bet_service = BetService(db)
        history = bet_service.get_resolution_history(
            bet_id=bet_id,
            page=page,
            per_page=per_page,
        )

        return history

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get resolution history: {str(e)}")


@router.get("/bets/disputed", response_model=BetListResponse, tags=["bets"])
async def get_disputed_bets(
    user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=100, description="Items per page"),
) -> BetListResponse:
    """
    Get all disputed bets (admin only)
    
    Returns list of all bets that have been disputed.
    """
    try:
        if not user or not user.get("external_id"):
            raise HTTPException(status_code=401, detail="User not authenticated")

        # TODO: Add admin role validation
        # For now, any authenticated user can view disputed bets

        # Get disputed bets using service
        bet_service = BetService(db)
        disputed_bets = bet_service.get_disputed_bets(
            page=page,
            per_page=per_page,
        )

        return disputed_bets

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get disputed bets: {str(e)}")


@router.get("/bets/pending-resolution", response_model=BetListResponse, tags=["bets"])
async def get_pending_resolution_bets(
    user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=100, description="Items per page"),
) -> BetListResponse:
    """
    Get bets pending resolution
    
    Returns list of all bets that are pending resolution.
    """
    try:
        if not user or not user.get("external_id"):
            raise HTTPException(status_code=401, detail="User not authenticated")

        # Get pending resolution bets using service
        bet_service = BetService(db)
        pending_bets = bet_service.get_pending_resolution_bets(
            page=page,
            per_page=per_page,
        )

        return pending_bets

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get pending resolution bets: {str(e)}")


@router.put("/bets/{bet_id}/resolve-dispute", response_model=BetResponse, tags=["bets"])
async def resolve_bet_dispute(
    bet_id: int,
    user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    new_result: str = Query(..., description="New result for the bet"),
    resolution_notes: str = Query(None, description="Notes about the dispute resolution"),
) -> BetResponse:
    """
    Resolve a bet dispute (admin only)
    
    Allows admin to resolve a disputed bet with a new result.
    """
    try:
        if not user or not user.get("external_id"):
            raise HTTPException(status_code=401, detail="User not authenticated")

        # Get user ID
        db_user = db.query(User).filter(User.external_id == user["external_id"]).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        # TODO: Add admin role validation
        # For now, any authenticated user can resolve disputes

        # Resolve dispute using service
        bet_service = BetService(db)
        resolved_bet = bet_service.resolve_dispute(
            bet_id=bet_id,
            new_result=new_result,
            resolution_notes=resolution_notes,
            admin_user_id=db_user.id,
        )

        return resolved_bet

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to resolve dispute: {str(e)}")
