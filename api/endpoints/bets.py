"""User bet tracking endpoints"""

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

router = APIRouter()


@router.post("/register", response_model=UserRegistrationResponse, tags=["users"])
async def register_user(request: UserRegistrationRequest, db: Session = Depends(get_db)):
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
                id=existing_user.id,
                external_id=existing_user.external_id,
                email=existing_user.email,
                name=existing_user.name,
                created_at=existing_user.created_at,
                is_active=existing_user.is_active,
            )

        # Create new user
        new_user = User(external_id=request.external_id, email=request.email, name=request.name)

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return UserRegistrationResponse(
            id=new_user.id,
            external_id=new_user.external_id,
            email=new_user.email,
            name=new_user.name,
            created_at=new_user.created_at,
            is_active=new_user.is_active,
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to register user: {str(e)}")


@router.post("/bets", response_model=BetResponse, tags=["bets"])
async def create_user_bet(
    request: BetCreateRequest,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
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
            game_id=request.game_id,
            market=request.market,
            selection=request.selection,
            stake=request.stake,
            odds=request.odds,
            notes=request.notes,
        )

        db.add(new_bet)
        db.commit()
        db.refresh(new_bet)

        return BetResponse(
            id=new_bet.id,
            game_id=new_bet.game_id,
            market=new_bet.market,
            selection=new_bet.selection,
            stake=new_bet.stake,
            odds=new_bet.odds,
            created_at=new_bet.created_at,
            notes=new_bet.notes,
            clv_cents=new_bet.clv_cents,
            beat_close=new_bet.beat_close,
            is_settled=new_bet.is_settled,
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create bet: {str(e)}")


@router.get("/bets", response_model=BetListResponse, tags=["bets"])
async def get_user_bets(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 50,
    offset: int = 0,
):
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

        bet_responses = []
        for bet in bets:
            bet_responses.append(
                BetResponse(
                    id=bet.id,
                    game_id=bet.game_id,
                    market=bet.market,
                    selection=bet.selection,
                    stake=bet.stake,
                    odds=bet.odds,
                    created_at=bet.created_at,
                    notes=bet.notes,
                    clv_cents=bet.clv_cents,
                    beat_close=bet.beat_close,
                    is_settled=bet.is_settled,
                )
            )

        return BetListResponse(bets=bet_responses, total=total_count)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user bets: {str(e)}")
