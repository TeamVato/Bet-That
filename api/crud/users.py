"""CRUD operations for User model"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from ..models import User, UserStatus
from ..schemas import UserRegistrationRequest, UserUpdateRequest
from .base import CRUDBase


class CRUDUser(CRUDBase[User, UserRegistrationRequest, UserUpdateRequest]):

    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        """Get user by email address"""
        return self.get_by_field(db=db, field="email", value=email.lower())

    def get_by_external_id(self, db: Session, *, external_id: str) -> Optional[User]:
        """Get user by external ID (e.g., from Supabase)"""
        return self.get_by_field(db=db, field="external_id", value=external_id)

    def get_active_users(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all active users"""
        return self.get_multi(
            db=db, skip=skip, limit=limit, filters={"is_active": True, "status": UserStatus.ACTIVE}
        )

    def get_users_by_status(
        self, db: Session, *, status: UserStatus, skip: int = 0, limit: int = 100
    ) -> List[User]:
        """Get users by status"""
        return self.get_multi(db=db, skip=skip, limit=limit, filters={"status": status})

    def get_users_by_verification_level(
        self, db: Session, *, level: str, skip: int = 0, limit: int = 100
    ) -> List[User]:
        """Get users by verification level"""
        return self.get_multi(db=db, skip=skip, limit=limit, filters={"verification_level": level})

    def search_users(
        self, db: Session, *, search_term: str, skip: int = 0, limit: int = 100
    ) -> List[User]:
        """Search users by name or email"""
        query = db.query(self.model).filter(
            and_(
                self.model.deleted_at.is_(None),
                or_(
                    self.model.name.ilike(f"%{search_term}%"),
                    self.model.email.ilike(f"%{search_term}%"),
                    self.model.first_name.ilike(f"%{search_term}%"),
                    self.model.last_name.ilike(f"%{search_term}%"),
                ),
            )
        )
        return query.offset(skip).limit(limit).all()

    def update_last_login(self, db: Session, *, user_id: int) -> Optional[User]:
        """Update user's last login timestamp"""
        user = self.get(db=db, id=user_id)
        if user:
            from datetime import datetime

            user.last_login_at = datetime.utcnow()
            user.last_activity_at = datetime.utcnow()
            db.add(user)
            db.commit()
            db.refresh(user)
        return user

    def update_activity(self, db: Session, *, user_id: int) -> Optional[User]:
        """Update user's last activity timestamp"""
        user = self.get(db=db, id=user_id)
        if user:
            from datetime import datetime

            user.last_activity_at = datetime.utcnow()
            db.add(user)
            db.commit()
            db.refresh(user)
        return user

    def verify_user(
        self, db: Session, *, user_id: int, verification_level: str = "basic"
    ) -> Optional[User]:
        """Verify a user account"""
        user = self.get(db=db, id=user_id)
        if user:
            from datetime import datetime

            user.is_verified = True
            user.email_verified = True
            user.email_verified_at = datetime.utcnow()
            user.verification_level = verification_level
            user.status = UserStatus.ACTIVE
            db.add(user)
            db.commit()
            db.refresh(user)
        return user

    def suspend_user(self, db: Session, *, user_id: int, reason: str = None) -> Optional[User]:
        """Suspend a user account"""
        user = self.get(db=db, id=user_id)
        if user:
            user.status = UserStatus.SUSPENDED
            user.is_active = False
            # Could store reason in notes or separate suspension log
            db.add(user)
            db.commit()
            db.refresh(user)
        return user

    def reactivate_user(self, db: Session, *, user_id: int) -> Optional[User]:
        """Reactivate a suspended user"""
        user = self.get(db=db, id=user_id)
        if user and user.status == UserStatus.SUSPENDED:
            user.status = UserStatus.ACTIVE
            user.is_active = True
            db.add(user)
            db.commit()
            db.refresh(user)
        return user

    def get_user_statistics(self, db: Session, *, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user betting statistics"""
        user = self.get(db=db, id=user_id)
        if not user:
            return None

        # This would typically use the user_bet_stats view we created
        # For now, we'll calculate basic stats
        from ..models import Bet, Transaction

        bet_count = db.query(Bet).filter(Bet.user_id == user_id, Bet.deleted_at.is_(None)).count()

        transaction_count = db.query(Transaction).filter(Transaction.user_id == user_id).count()

        return {
            "user_id": user_id,
            "total_bets": bet_count,
            "total_transactions": transaction_count,
            "account_age_days": (datetime.utcnow() - user.created_at).days,
            "last_activity": user.last_activity_at,
            "verification_level": user.verification_level,
            "risk_tolerance": user.risk_tolerance,
        }


user_crud = CRUDUser(User)
