"""Email digest subscription endpoints"""
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import DigestSubscription
from ..schemas import DigestSubscriptionRequest, DigestSubscriptionResponse

router = APIRouter()

@router.post("/subscribe", response_model=DigestSubscriptionResponse, tags=["digest"])
async def subscribe_digest(
    request: DigestSubscriptionRequest,
    db: Session = Depends(get_db)
):
    """
    Subscribe to weekly digest emails
    
    Creates or updates email subscription for weekly analytics digest.
    """
    try:
        # Check if subscription already exists
        existing = db.query(DigestSubscription).filter(
            DigestSubscription.email == request.email
        ).first()
        
        if existing:
            # Update existing subscription
            existing.frequency = request.frequency or "weekly"
            existing.is_active = True
            existing.updated_at = datetime.now()
            
            db.commit()
            db.refresh(existing)
            
            subscription = existing
        else:
            # Create new subscription
            new_subscription = DigestSubscription(
                email=request.email,
                frequency=request.frequency or "weekly"
            )
            
            db.add(new_subscription)
            db.commit()
            db.refresh(new_subscription)
            
            subscription = new_subscription
        
        return DigestSubscriptionResponse(
            id=subscription.id,
            email=subscription.email,
            frequency=subscription.frequency,
            is_active=subscription.is_active,
            created_at=subscription.created_at
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to subscribe: {str(e)}"
        )

@router.delete("/subscribe/{email}", tags=["digest"])
async def unsubscribe_digest(
    email: str,
    db: Session = Depends(get_db)
):
    """
    Unsubscribe from digest emails
    
    Deactivates email subscription.
    """
    try:
        subscription = db.query(DigestSubscription).filter(
            DigestSubscription.email == email
        ).first()
        
        if not subscription:
            raise HTTPException(status_code=404, detail="Email not found in subscriptions")
        
        subscription.is_active = False
        subscription.updated_at = datetime.now()
        
        db.commit()
        
        return {"message": f"Successfully unsubscribed {email} from digest"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to unsubscribe: {str(e)}"
        )

@router.get("/subscriptions", response_model=List[DigestSubscriptionResponse], tags=["digest"])
async def list_subscriptions(
    active_only: bool = Query(True, description="Only return active subscriptions"),
    db: Session = Depends(get_db)
):
    """
    Get all email subscriptions (admin endpoint)
    """
    try:
        query = db.query(DigestSubscription)
        
        if active_only:
            query = query.filter(DigestSubscription.is_active == True)
        
        subscriptions = query.all()
        
        results = []
        for sub in subscriptions:
            results.append(DigestSubscriptionResponse(
                id=sub.id,
                email=sub.email,
                frequency=sub.frequency,
                is_active=sub.is_active,
                created_at=sub.created_at
            ))
        
        return results
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list subscriptions: {str(e)}"
        )
