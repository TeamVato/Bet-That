"""FastAPI dependencies for authentication and database access"""
from typing import Optional
from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session
from .database import get_db
from .schemas import UserRegistrationRequest

def get_current_user_external_id(x_user_id: Optional[str] = Header(None)) -> str:
    """Extract external user ID from header. Simple auth for Sprint 1."""
    if not x_user_id:
        raise HTTPException(
            status_code=401, 
            detail="X-User-Id header required"
        )
    return x_user_id

async def get_current_user(
    external_id: str = Depends(get_current_user_external_id),
    db: Session = Depends(get_db)
) -> Optional[dict]:
    """Get or create user based on external ID from Supabase."""
    from sqlalchemy.orm import Session
    
    # Check if user exists
    from .models import User
    user = db.query(User).filter(User.external_id == external_id).first()
    
    if not user:
        # For Sprint 1, we'll just return external_id
        # In production, we'd link with Supabase to get email/name
        return {
            "external_id": external_id,
            "id": None,
            "email": None,
            "name": None
        }
    
    return {
        "id": user.id,
        "external_id": user.external_id,
        "email": user.email,
        "name": user.name
    }
