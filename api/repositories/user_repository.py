"""User repository for database operations

Provides database access layer for user management operations including
creation, authentication, and profile management.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Optional, Any

from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..auth.simple_password import hash_password_pbkdf2
from ..auth_schemas import UserRegistrationRequest
from ..models import User

logger = logging.getLogger(__name__)


class UserRepository:
    """Repository for user database operations"""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email address"""
        try:
            return self.db.query(User).filter(User.email == email.lower()).first()
        except Exception as e:
            logger.error(f"Failed to get user by email: {e}")
            return None

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        try:
            return self.db.query(User).filter(User.username == username.lower()).first()
        except Exception as e:
            logger.error(f"Failed to get user by username: {e}")
            return None

    def get_user_by_email_or_username(self, identifier: str) -> Optional[User]:
        """Get user by email or username"""
        try:
            identifier_lower = identifier.lower()
            return (
                self.db.query(User)
                .filter(or_(User.email == identifier_lower, User.username == identifier_lower))
                .first()
            )
        except Exception as e:
            logger.error(f"Failed to get user by email or username: {e}")
            return None

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        try:
            return self.db.query(User).filter(User.id == user_id).first()
        except Exception as e:
            logger.error(f"Failed to get user by ID: {e}")
            return None

    def email_exists(self, email: str) -> bool:
        """Check if email already exists"""
        try:
            return self.db.query(User).filter(User.email == email.lower()).first() is not None
        except Exception as e:
            logger.error(f"Failed to check email exists: {e}")
            return True  # Fail safe - assume exists if we can't check

    def username_exists(self, username: str) -> bool:
        """Check if username already exists"""
        try:
            return self.db.query(User).filter(User.username == username.lower()).first() is not None
        except Exception as e:
            logger.error(f"Failed to check username exists: {e}")
            return True  # Fail safe - assume exists if we can't check

    def create_user(self, user_data: UserRegistrationRequest) -> User:
        """Create new user from registration data"""
        try:
            # Hash password using PBKDF2
            password_hash = hash_password_pbkdf2(user_data.password)

            # Create user object
            db_user = User(
                email=user_data.email.lower(),
                username=user_data.username.lower(),
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                name=f"{user_data.first_name} {user_data.last_name}",
                date_of_birth=user_data.date_of_birth,
                phone_number=user_data.phone_number,
                phone=user_data.phone_number,  # For compatibility
                password_hash=password_hash,
                is_active=True,
                is_verified=False,
                email_verified=False,
                created_at=datetime.now(timezone.utc),
                external_id=f"local_{user_data.username}_{int(datetime.now(timezone.utc).timestamp())}",
                timezone=user_data.timezone or "UTC",
            )

            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)

            logger.info(f"User created successfully: {db_user.id} ({db_user.email})")
            return db_user

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create user: {e}")
            raise

    def update_last_login(self, user_id: int) -> None:
        """Update user's last login timestamp"""
        try:
            now = datetime.now(timezone.utc)
            self.db.query(User).filter(User.id == user_id).update(
                {"last_login_at": now, "last_activity_at": now}
            )
            self.db.commit()
            logger.debug(f"Updated last login for user {user_id}")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update last login: {e}")
            raise

    def verify_user_email(self, user_id: int) -> None:
        """Mark user email as verified"""
        try:
            now = datetime.now(timezone.utc)
            self.db.query(User).filter(User.id == user_id).update(
                {
                    "is_verified": True,
                    "email_verified": True,
                    "email_verified_at": now,
                    "updated_at": now,
                }
            )
            self.db.commit()
            logger.info(f"Email verified for user {user_id}")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to verify user email: {e}")
            raise

    def update_user_profile(self, user_id: int, profile_data: Dict[str, Any]) -> Optional[User]:
        """Update user profile information"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return None

            # Update fields that are provided
            for field, value in profile_data.items():
                if hasattr(user, field) and value is not None:
                    setattr(user, field, value)

            # Note: updated_at is handled by SQLAlchemy automatically
            self.db.commit()
            self.db.refresh(user)

            logger.info(f"Profile updated for user {user_id}")
            return user

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update user profile: {e}")
            raise

    def deactivate_user(self, user_id: int, reason: Optional[str] = None) -> bool:
        """Deactivate user account"""
        try:
            updated_count = (
                self.db.query(User)
                .filter(User.id == user_id)
                .update({"is_active": False, "updated_at": datetime.now(timezone.utc)})
            )
            self.db.commit()

            if updated_count > 0:
                logger.info(f"User deactivated: {user_id} - {reason}")
                return True
            return False

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to deactivate user: {e}")
            raise
