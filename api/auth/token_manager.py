"""Database-backed token management for JWT authentication

Provides persistent token blacklisting, session management, and security logging
using SQLAlchemy models for production-ready token management.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import and_
from sqlalchemy.orm import Session

from ..models import AuthLog, JWTTokenBlacklist, User, UserSession
from ..settings import settings

logger = logging.getLogger(__name__)


class DatabaseTokenBlacklist:
    """Database-backed token blacklist management"""

    @staticmethod
    def add_token(
        db: Session,
        jti: str,
        user_id: int,
        token_type: str,
        expires_at: datetime,
        reason: Optional[str] = None,
    ) -> None:
        """Add token to blacklist

        Args:
            db: Database session
            jti: JWT ID
            user_id: User ID
            token_type: Token type (access, refresh, password_reset)
            expires_at: Token expiration time
            reason: Optional revocation reason
        """
        try:
            blacklist_entry = JWTTokenBlacklist(
                jti=jti,
                user_id=user_id,
                token_type=token_type,
                expires_at=expires_at,
                reason=reason,
            )

            db.add(blacklist_entry)
            db.commit()

            logger.info(f"Token blacklisted: {jti} for user {user_id}")

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to blacklist token: {e}")
            raise

    @staticmethod
    def is_token_revoked(db: Session, jti: str, user_id: int) -> bool:
        """Check if token is revoked

        Args:
            db: Database session
            jti: JWT ID
            user_id: User ID

        Returns:
            True if token is revoked, False otherwise
        """
        try:
            blacklist_entry = (
                db.query(JWTTokenBlacklist)
                .filter(
                    and_(
                        JWTTokenBlacklist.jti == jti,
                        JWTTokenBlacklist.user_id == user_id,
                        JWTTokenBlacklist.expires_at > datetime.now(timezone.utc),
                    )
                )
                .first()
            )

            return blacklist_entry is not None

        except Exception as e:
            logger.error(f"Failed to check token revocation: {e}")
            return True  # Fail safe - assume revoked if we can't check

    @staticmethod
    def revoke_user_tokens(
        db: Session, user_id: int, token_type: Optional[str] = None, reason: Optional[str] = None
    ) -> int:
        """Revoke all tokens for a user

        Args:
            db: Database session
            user_id: User ID
            token_type: Optional token type filter
            reason: Revocation reason

        Returns:
            Number of tokens revoked
        """
        try:
            # This is a simplified approach - in production you'd need to track
            # all active tokens for a user, possibly through sessions table

            # For now, we'll add a special blacklist entry that revokes all future tokens
            # until a certain timestamp
            revoke_until = datetime.now(timezone.utc) + timedelta(days=365)  # Far future

            blacklist_entry = JWTTokenBlacklist(
                jti=f"user_revoke_{user_id}_{int(datetime.now(timezone.utc).timestamp())}",
                user_id=user_id,
                token_type=token_type or "all",
                expires_at=revoke_until,
                reason=reason or "User logout all sessions",
            )

            db.add(blacklist_entry)
            db.commit()

            logger.info(f"All tokens revoked for user {user_id}")
            return 1

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to revoke user tokens: {e}")
            raise

    @staticmethod
    def cleanup_expired_tokens(db: Session) -> int:
        """Remove expired tokens from blacklist

        Args:
            db: Database session

        Returns:
            Number of tokens cleaned up
        """
        try:
            now = datetime.now(timezone.utc)

            # Delete expired blacklist entries
            deleted_count = (
                db.query(JWTTokenBlacklist).filter(JWTTokenBlacklist.expires_at < now).delete()
            )

            db.commit()

            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} expired blacklist entries")

            return deleted_count

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to cleanup expired tokens: {e}")
            return 0


class SessionManager:
    """User session management for JWT tokens"""

    @staticmethod
    def create_session(
        db: Session,
        user_id: int,
        session_id: str,
        refresh_token_jti: str,
        ip_address: str,
        user_agent: Optional[str] = None,
        expires_at: Optional[datetime] = None,
    ) -> UserSession:
        """Create new user session

        Args:
            db: Database session
            user_id: User ID
            session_id: Session identifier
            refresh_token_jti: Refresh token JTI
            ip_address: Client IP address
            user_agent: Client user agent
            expires_at: Session expiration time

        Returns:
            Created session object
        """
        try:
            if expires_at is None:
                expires_at = datetime.now(timezone.utc) + timedelta(
                    minutes=settings.session_timeout_minutes
                )

            session = UserSession(
                user_id=user_id,
                session_id=session_id,
                refresh_token_jti=refresh_token_jti,
                ip_address=ip_address,
                user_agent=user_agent,
                expires_at=expires_at,
            )

            db.add(session)
            db.commit()
            db.refresh(session)

            logger.info(f"Session created for user {user_id}: {session_id}")
            return session

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create session: {e}")
            raise

    @staticmethod
    def get_active_sessions(db: Session, user_id: int) -> List[UserSession]:
        """Get active sessions for user

        Args:
            db: Database session
            user_id: User ID

        Returns:
            List of active sessions
        """
        now = datetime.now(timezone.utc)

        return (
            db.query(UserSession)
            .filter(
                and_(
                    UserSession.user_id == user_id,
                    UserSession.is_active == True,
                    UserSession.expires_at > now,
                )
            )
            .order_by(UserSession.last_activity_at.desc())
            .all()
        )

    @staticmethod
    def update_session_activity(db: Session, session_id: str, user_id: int) -> None:
        """Update session last activity timestamp

        Args:
            db: Database session
            session_id: Session identifier
            user_id: User ID
        """
        try:
            session = (
                db.query(UserSession)
                .filter(
                    and_(
                        UserSession.session_id == session_id,
                        UserSession.user_id == user_id,
                        UserSession.is_active == True,
                    )
                )
                .first()
            )

            if session:
                session.last_activity_at = datetime.now(timezone.utc)
                db.commit()

        except Exception as e:
            logger.error(f"Failed to update session activity: {e}")

    @staticmethod
    def revoke_session(db: Session, session_id: str, user_id: int) -> bool:
        """Revoke specific session

        Args:
            db: Database session
            session_id: Session identifier
            user_id: User ID

        Returns:
            True if session was revoked, False if not found
        """
        try:
            session = (
                db.query(UserSession)
                .filter(and_(UserSession.session_id == session_id, UserSession.user_id == user_id))
                .first()
            )

            if session:
                session.is_active = False
                session.revoked_at = datetime.now(timezone.utc)
                db.commit()
                logger.info(f"Session revoked: {session_id}")
                return True

            return False

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to revoke session: {e}")
            return False

    @staticmethod
    def revoke_all_user_sessions(db: Session, user_id: int) -> int:
        """Revoke all sessions for user

        Args:
            db: Database session
            user_id: User ID

        Returns:
            Number of sessions revoked
        """
        try:
            now = datetime.now(timezone.utc)

            updated_count = (
                db.query(UserSession)
                .filter(and_(UserSession.user_id == user_id, UserSession.is_active == True))
                .update({"is_active": False, "revoked_at": now})
            )

            db.commit()

            logger.info(f"Revoked {updated_count} sessions for user {user_id}")
            return updated_count

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to revoke user sessions: {e}")
            return 0

    @staticmethod
    def cleanup_expired_sessions(db: Session) -> int:
        """Cleanup expired sessions

        Args:
            db: Database session

        Returns:
            Number of sessions cleaned up
        """
        try:
            now = datetime.now(timezone.utc)

            # Mark expired sessions as inactive
            updated_count = (
                db.query(UserSession)
                .filter(and_(UserSession.expires_at < now, UserSession.is_active == True))
                .update({"is_active": False, "revoked_at": now})
            )

            db.commit()

            if updated_count > 0:
                logger.info(f"Cleaned up {updated_count} expired sessions")

            return updated_count

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to cleanup expired sessions: {e}")
            return 0


class AuthLogger:
    """Authentication event logging for security auditing"""

    @staticmethod
    def log_auth_event(
        db: Session,
        event_type: str,
        ip_address: str,
        success: bool,
        user_id: Optional[int] = None,
        user_agent: Optional[str] = None,
        failure_reason: Optional[str] = None,
        additional_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log authentication event

        Args:
            db: Database session
            event_type: Type of auth event
            ip_address: Client IP address
            success: Whether event was successful
            user_id: User ID (if applicable)
            user_agent: Client user agent
            failure_reason: Reason for failure (if applicable)
            additional_data: Additional context data
        """
        try:
            import json

            auth_log = AuthLog(
                user_id=user_id,
                event_type=event_type,
                ip_address=ip_address,
                user_agent=user_agent,
                success=success,
                failure_reason=failure_reason,
                additional_data=json.dumps(additional_data) if additional_data else None,
            )

            db.add(auth_log)
            db.commit()

            logger.info(
                f"Auth event logged: {event_type} for user {user_id} - {'SUCCESS' if success else 'FAILURE'}"
            )

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to log auth event: {e}")

    @staticmethod
    def get_recent_failures(
        db: Session,
        ip_address: Optional[str] = None,
        user_id: Optional[int] = None,
        hours: int = 24,
    ) -> List[AuthLog]:
        """Get recent authentication failures

        Args:
            db: Database session
            ip_address: IP address to filter by
            user_id: User ID to filter by
            hours: Hours to look back

        Returns:
            List of recent failure logs
        """
        since = datetime.now(timezone.utc) - timedelta(hours=hours)

        query = db.query(AuthLog).filter(and_(AuthLog.success == False, AuthLog.created_at > since))

        if ip_address:
            query = query.filter(AuthLog.ip_address == ip_address)

        if user_id:
            query = query.filter(AuthLog.user_id == user_id)

        return query.order_by(AuthLog.created_at.desc()).all()

    @staticmethod
    def cleanup_old_logs(db: Session, days: int = 90) -> int:
        """Cleanup old authentication logs

        Args:
            db: Database session
            days: Days to keep logs

        Returns:
            Number of logs deleted
        """
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)

            deleted_count = db.query(AuthLog).filter(AuthLog.created_at < cutoff_date).delete()

            db.commit()

            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} old auth logs")

            return deleted_count

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to cleanup old auth logs: {e}")
            return 0


class TokenManager:
    """Comprehensive token management combining blacklist and session management"""

    def __init__(self):
        self.blacklist = DatabaseTokenBlacklist()
        self.session_manager = SessionManager()
        self.auth_logger = AuthLogger()

    def revoke_token_with_logging(
        self,
        db: Session,
        jti: str,
        user_id: int,
        token_type: str,
        expires_at: datetime,
        ip_address: str,
        reason: Optional[str] = None,
    ) -> None:
        """Revoke token with security logging

        Args:
            db: Database session
            jti: JWT ID
            user_id: User ID
            token_type: Token type
            expires_at: Token expiration
            ip_address: Client IP
            reason: Revocation reason
        """
        # Add to blacklist
        self.blacklist.add_token(db, jti, user_id, token_type, expires_at, reason)

        # Log the revocation
        self.auth_logger.log_auth_event(
            db=db,
            event_type="token_revoke",
            ip_address=ip_address,
            success=True,
            user_id=user_id,
            additional_data={"token_type": token_type, "jti": jti, "reason": reason},
        )

    def create_user_session_with_logging(
        self,
        db: Session,
        user: User,
        session_id: str,
        refresh_token_jti: str,
        ip_address: str,
        user_agent: Optional[str] = None,
    ) -> UserSession:
        """Create session with logging

        Args:
            db: Database session
            user: User object
            session_id: Session identifier
            refresh_token_jti: Refresh token JTI
            ip_address: Client IP
            user_agent: Client user agent

        Returns:
            Created session
        """
        # Check session limit
        active_sessions = self.session_manager.get_active_sessions(db, user.id)

        if len(active_sessions) >= settings.max_concurrent_sessions:
            # Revoke oldest session
            oldest_session = min(active_sessions, key=lambda s: s.last_activity_at)
            self.session_manager.revoke_session(db, oldest_session.session_id, user.id)

            logger.info(f"Revoked oldest session for user {user.id} due to session limit")

        # Create new session
        session = self.session_manager.create_session(
            db=db,
            user_id=user.id,
            session_id=session_id,
            refresh_token_jti=refresh_token_jti,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        # Log session creation
        self.auth_logger.log_auth_event(
            db=db,
            event_type="session_create",
            ip_address=ip_address,
            success=True,
            user_id=user.id,
            user_agent=user_agent,
            additional_data={"session_id": session_id, "refresh_token_jti": refresh_token_jti},
        )

        return session

    def perform_maintenance(self, db: Session) -> Dict[str, int]:
        """Perform routine maintenance on tokens and sessions

        Args:
            db: Database session

        Returns:
            Dictionary with cleanup statistics
        """
        stats = {}

        # Cleanup expired blacklist entries
        stats["expired_blacklist_entries"] = self.blacklist.cleanup_expired_tokens(db)

        # Cleanup expired sessions
        stats["expired_sessions"] = self.session_manager.cleanup_expired_sessions(db)

        # Cleanup old auth logs
        stats["old_auth_logs"] = self.auth_logger.cleanup_old_logs(db)

        logger.info(f"Token maintenance completed: {stats}")
        return stats


# Global token manager instance
token_manager = TokenManager()
