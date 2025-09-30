"""Email digest subscription endpoints"""

from datetime import datetime
from typing import Annotated, List, cast

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import DigestSubscription
from ..schemas import DigestSubscriptionRequest, DigestSubscriptionResponse

router = APIRouter()


@router.post("/subscribe", response_model=DigestSubscriptionResponse, tags=["digest"])
async def subscribe_digest(
    request: DigestSubscriptionRequest, 
    db: Annotated[Session, Depends(get_db)]
) -> DigestSubscriptionResponse:
    """
    Subscribe to weekly digest emails

    Creates or updates email subscription for weekly analytics digest.
    """
    try:
        # Check if subscription already exists
        existing = (
            db.query(DigestSubscription).filter(DigestSubscription.email == request.email).first()
        )

        if existing:
            # Update existing subscription
            db.query(DigestSubscription).filter(DigestSubscription.id == existing.id).update({
                "frequency": request.frequency or "weekly",
                "is_active": True,
                "updated_at": datetime.now()
            })

            db.commit()
            db.refresh(existing)

            subscription = existing
        else:
            # Create new subscription
            new_subscription = DigestSubscription(
                email=request.email, frequency=request.frequency or "weekly"
            )

            db.add(new_subscription)
            db.commit()
            db.refresh(new_subscription)

            subscription = new_subscription

        return DigestSubscriptionResponse(
            id=cast(int, subscription.id),
            email=cast(str, subscription.email),
            frequency=cast(str, subscription.frequency),
            is_active=cast(bool, subscription.is_active),
            created_at=cast(datetime, subscription.created_at),
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to subscribe: {str(e)}")


@router.delete("/subscribe/{email}", tags=["digest"])
async def unsubscribe_digest(
    email: str, 
    db: Annotated[Session, Depends(get_db)]
) -> dict:
    """
    Unsubscribe from digest emails

    Deactivates email subscription.
    """
    try:
        subscription = (
            db.query(DigestSubscription).filter(DigestSubscription.email == email).first()
        )

        if not subscription:
            raise HTTPException(status_code=404, detail="Email not found in subscriptions")

        db.query(DigestSubscription).filter(DigestSubscription.id == subscription.id).update({
            "is_active": False,
            "updated_at": datetime.now()
        })

        db.commit()

        return {"message": f"Successfully unsubscribed {email} from digest"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to unsubscribe: {str(e)}")


@router.get("/subscriptions", response_model=List[DigestSubscriptionResponse], tags=["digest"])
async def list_subscriptions(
    db: Annotated[Session, Depends(get_db)],
    active_only: Annotated[bool, Query(description="Only return active subscriptions")] = True,
) -> List[DigestSubscriptionResponse]:
    """
    Get all email subscriptions (admin endpoint)
    """
    try:
        query = db.query(DigestSubscription)

        if active_only:
            query = query.filter(DigestSubscription.is_active.is_(True))

        subscriptions = query.all()

        results = []
        for sub in subscriptions:
            results.append(
                DigestSubscriptionResponse(
                    id=cast(int, sub.id),
                    email=cast(str, sub.email),
                    frequency=cast(str, sub.frequency),
                    is_active=cast(bool, sub.is_active),
                    created_at=cast(datetime, sub.created_at),
                )
            )

        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list subscriptions: {str(e)}")
