"""User management endpoints"""

from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..crud import bet_crud, transaction_crud, user_crud
from ..database import get_db
from ..models import UserStatus
from ..schemas import (
    BetListResponse,
    TransactionListResponse,
    UserRegistrationRequest,
    UserRegistrationResponse,
    UserResponse,
    UserUpdateRequest,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserRegistrationResponse)
def create_user(
    user_in: UserRegistrationRequest, 
    db: Annotated[Session, Depends(get_db)]
) -> UserRegistrationResponse:
    """Create a new user account"""
    # Check if user already exists
    existing_user = user_crud.get_by_email(db=db, email=user_in.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    existing_external = user_crud.get_by_external_id(db=db, external_id=user_in.external_id)
    if existing_external:
        raise HTTPException(status_code=400, detail="External ID already registered")

    # Create user
    user = user_crud.create(db=db, obj_in=user_in)
    return user


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int, 
    db: Annotated[Session, Depends(get_db)]
) -> UserResponse:
    """Get user by ID"""
    user = user_crud.get(db=db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/external/{external_id}", response_model=UserResponse)
def get_user_by_external_id(
    external_id: str, 
    db: Annotated[Session, Depends(get_db)]
) -> UserResponse:
    """Get user by external ID"""
    user = user_crud.get_by_external_id(db=db, external_id=external_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int, 
    user_update: UserUpdateRequest, 
    db: Annotated[Session, Depends(get_db)]
) -> UserResponse:
    """Update user information"""
    user = user_crud.get(db=db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    updated_user = user_crud.update(db=db, db_obj=user, obj_in=user_update)
    return updated_user


@router.delete("/{user_id}")
def delete_user(
    user_id: int, 
    db: Annotated[Session, Depends(get_db)]
) -> dict:
    """Soft delete a user account"""
    user = user_crud.remove(db=db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}


@router.post("/{user_id}/verify", response_model=UserResponse)
def verify_user(
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
    verification_level: Annotated[str, Query(regex="^(basic|enhanced|premium)$")] = "basic",
) -> UserResponse:
    """Verify a user account"""
    user = user_crud.verify_user(db=db, user_id=user_id, verification_level=verification_level)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/{user_id}/suspend", response_model=UserResponse)
def suspend_user(
    user_id: int, 
    db: Annotated[Session, Depends(get_db)]
) -> UserResponse:
    """Suspend a user account"""
    user = user_crud.suspend_user(db=db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/{user_id}/reactivate", response_model=UserResponse)
def reactivate_user(
    user_id: int, 
    db: Annotated[Session, Depends(get_db)]
) -> UserResponse:
    """Reactivate a suspended user account"""
    user = user_crud.reactivate_user(db=db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/{user_id}/bets", response_model=BetListResponse)
def get_user_bets(
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
    status: Annotated[Optional[str], Query()] = None,
) -> BetListResponse:
    """Get bets for a specific user"""
    user = user_crud.get(db=db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    from ..models import BetStatus

    bet_status = BetStatus(status) if status else None

    bets = bet_crud.get_by_user(db=db, user_id=user_id, skip=skip, limit=limit, status=bet_status)
    total = bet_crud.count(db=db, filters={"user_id": user_id})

    from ..schemas.bet_schemas import BetResponse
    bet_responses = [BetResponse.model_validate(bet) for bet in bets]
    return BetListResponse(bets=bet_responses, total=total, page=skip // limit + 1, per_page=limit)


@router.get("/{user_id}/transactions", response_model=TransactionListResponse)
def get_user_transactions(
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
    transaction_type: Annotated[Optional[str], Query()] = None,
) -> TransactionListResponse:
    """Get transactions for a specific user"""
    user = user_crud.get(db=db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    from ..models import TransactionType

    trans_type = TransactionType(transaction_type) if transaction_type else None

    transactions = transaction_crud.get_by_user(
        db=db, user_id=user_id, skip=skip, limit=limit, transaction_type=trans_type
    )
    total = transaction_crud.count(db=db, filters={"user_id": user_id})

    from ..schemas.common_schemas import TransactionResponse
    transaction_responses = [TransactionResponse.model_validate(transaction) for transaction in transactions]
    return TransactionListResponse(
        transactions=transaction_responses, total=total, page=skip // limit + 1, per_page=limit
    )


@router.get("/{user_id}/statistics")
def get_user_statistics(
    user_id: int, 
    db: Annotated[Session, Depends(get_db)]
) -> dict:
    """Get comprehensive user statistics"""
    user = user_crud.get(db=db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get user statistics
    user_stats = user_crud.get_user_statistics(db=db, user_id=user_id)
    bet_stats = bet_crud.get_user_bet_statistics(db=db, user_id=user_id)
    transaction_stats = transaction_crud.get_user_transaction_summary(db=db, user_id=user_id)

    return {"user": user_stats, "betting": bet_stats, "financial": transaction_stats}


@router.get("/", response_model=List[UserResponse])
def list_users(
    db: Annotated[Session, Depends(get_db)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
    status: Annotated[Optional[str], Query()] = None,
    search: Annotated[Optional[str], Query()] = None,
) -> List[UserResponse]:
    """List users with optional filtering"""
    if search:
        users = user_crud.search_users(db=db, search_term=search, skip=skip, limit=limit)
    elif status:
        user_status = UserStatus(status)
        users = user_crud.get_users_by_status(db=db, status=user_status, skip=skip, limit=limit)
    else:
        users = user_crud.get_multi(db=db, skip=skip, limit=limit)

    from ..schemas.user_schemas import UserResponse
    user_responses = [UserResponse.model_validate(user) for user in users]
    return user_responses
