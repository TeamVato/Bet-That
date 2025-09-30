"""User bet tracking endpoints"""

from typing import Annotated, Any, Union

from fastapi import APIRouter, Depends, HTTPException
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
