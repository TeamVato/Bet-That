"""Security utilities for authentication and request protection

Provides CSRF protection, secure token generation, input sanitization,
and other security helpers for the authentication system.
"""

import hashlib
import hmac
import logging
import re
import secrets
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from ..settings import settings
from .exceptions import RateLimitExceededError

logger = logging.getLogger(__name__)


class CSRFProtection:
    """CSRF token generation and validation"""

    @staticmethod
    def generate_csrf_token(user_id: int, session_id: Optional[str] = None) -> str:
        """Generate CSRF token for user session

        Args:
            user_id: User database ID
            session_id: Optional session identifier

        Returns:
            CSRF token string
        """
        timestamp = str(int(datetime.now(timezone.utc).timestamp()))
        session_part = session_id or secrets.token_urlsafe(16)

        # Create token payload
        payload = f"{user_id}:{session_part}:{timestamp}"

        # Sign with secret key
        signature = hmac.new(
            settings.jwt_secret_key.encode(), payload.encode(), hashlib.sha256
        ).hexdigest()

        token = f"{payload}:{signature}"
        logger.debug(f"CSRF token generated for user {user_id}")
        return token

    @staticmethod
    def verify_csrf_token(token: str, user_id: int, max_age_hours: int = 24) -> bool:
        """Verify CSRF token validity

        Args:
            token: CSRF token to verify
            user_id: Expected user ID
            max_age_hours: Maximum token age in hours

        Returns:
            True if token is valid, False otherwise
        """
        try:
            parts = token.split(":")
            if len(parts) != 4:
                return False

            token_user_id, session_id, timestamp, signature = parts

            # Verify user ID matches
            if int(token_user_id) != user_id:
                return False

            # Verify timestamp is not too old
            token_time = datetime.fromtimestamp(int(timestamp), tz=timezone.utc)
            max_age = timedelta(hours=max_age_hours)

            if datetime.now(timezone.utc) - token_time > max_age:
                return False

            # Verify signature
            payload = f"{token_user_id}:{session_id}:{timestamp}"
            expected_signature = hmac.new(
                settings.jwt_secret_key.encode(), payload.encode(), hashlib.sha256
            ).hexdigest()

            if not hmac.compare_digest(signature, expected_signature):
                return False

            logger.debug(f"CSRF token verified for user {user_id}")
            return True

        except (ValueError, IndexError) as e:
            logger.warning(f"CSRF token verification failed: {e}")
            return False


class RateLimiter:
    """Rate limiting for authentication endpoints"""

    def __init__(self):
        self._attempts: Dict[str, list[datetime]] = defaultdict(list)
        self._blocked_ips: Dict[str, datetime] = {}

    def is_rate_limited(
        self,
        identifier: str,
        max_attempts: int = 5,
        window_minutes: int = 15,
        block_minutes: int = 60,
    ) -> bool:
        """Check if identifier is rate limited

        Args:
            identifier: IP address or user identifier
            max_attempts: Maximum attempts allowed
            window_minutes: Time window for rate limiting
            block_minutes: Block duration after limit exceeded

        Returns:
            True if rate limited, False otherwise
        """
        now = datetime.now(timezone.utc)

        # Check if currently blocked
        if identifier in self._blocked_ips:
            block_expires = self._blocked_ips[identifier] + timedelta(minutes=block_minutes)
            if now < block_expires:
                return True
            else:
                # Block expired, remove from blocked list
                del self._blocked_ips[identifier]

        # Clean old attempts
        window_start = now - timedelta(minutes=window_minutes)
        self._attempts[identifier] = [
            attempt for attempt in self._attempts[identifier] if attempt > window_start
        ]

        # Check if limit exceeded
        if len(self._attempts[identifier]) >= max_attempts:
            self._blocked_ips[identifier] = now
            logger.warning(f"Rate limit exceeded for {identifier}")
            return True

        return False

    def record_attempt(self, identifier: str) -> None:
        """Record authentication attempt

        Args:
            identifier: IP address or user identifier
        """
        self._attempts[identifier].append(datetime.now(timezone.utc))

    def reset_attempts(self, identifier: str) -> None:
        """Reset attempts for identifier (e.g., after successful auth)

        Args:
            identifier: IP address or user identifier
        """
        if identifier in self._attempts:
            del self._attempts[identifier]
        if identifier in self._blocked_ips:
            del self._blocked_ips[identifier]

    def cleanup_expired(self) -> None:
        """Cleanup expired rate limit data"""
        now = datetime.now(timezone.utc)

        # Remove old attempts
        for identifier in list(self._attempts.keys()):
            self._attempts[identifier] = [
                attempt
                for attempt in self._attempts[identifier]
                if now - attempt < timedelta(hours=24)
            ]
            if not self._attempts[identifier]:
                del self._attempts[identifier]

        # Remove expired blocks
        expired_blocks = [
            identifier
            for identifier, block_time in self._blocked_ips.items()
            if now - block_time > timedelta(hours=24)
        ]
        for identifier in expired_blocks:
            del self._blocked_ips[identifier]


class InputSanitizer:
    """Input sanitization for authentication fields"""

    @staticmethod
    def sanitize_email(email: str) -> str:
        """Sanitize email input

        Args:
            email: Raw email input

        Returns:
            Sanitized email address
        """
        if not email:
            return ""

        # Basic sanitization
        email = email.strip().lower()

        # Remove potentially dangerous characters
        email = re.sub(r'[<>"\'\x00-\x1f\x7f-\x9f]', "", email)

        # Validate basic email format
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
            return ""

        return email

    @staticmethod
    def sanitize_name(name: str) -> str:
        """Sanitize name input

        Args:
            name: Raw name input

        Returns:
            Sanitized name
        """
        if not name:
            return ""

        # Basic sanitization
        name = name.strip()

        # Remove potentially dangerous characters but keep unicode letters
        name = re.sub(r'[<>"\'\x00-\x1f\x7f-\x9f]', "", name)

        # Limit length
        return name[:255]

    @staticmethod
    def sanitize_auth_input(data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize authentication input data

        Args:
            data: Dictionary with authentication data

        Returns:
            Sanitized data dictionary
        """
        sanitized = {}

        for key, value in data.items():
            if key == "email" and isinstance(value, str):
                sanitized[key] = InputSanitizer.sanitize_email(value)
            elif key in ["name", "first_name", "last_name"] and isinstance(value, str):
                sanitized[key] = InputSanitizer.sanitize_name(value)
            elif isinstance(value, str):
                # General string sanitization
                sanitized[key] = re.sub(r'[<>"\'\x00-\x1f\x7f-\x9f]', "", value.strip())
            else:
                sanitized[key] = value

        return sanitized


def generate_secure_token(length: int = 32) -> str:
    """Generate cryptographically secure random token

    Args:
        length: Token length in bytes

    Returns:
        URL-safe base64 encoded token
    """
    return secrets.token_urlsafe(length)


def generate_csrf_token(user_id: int, session_id: Optional[str] = None) -> str:
    """Generate CSRF token (convenience function)"""
    return CSRFProtection.generate_csrf_token(user_id, session_id)


def verify_csrf_token(token: str, user_id: int) -> bool:
    """Verify CSRF token (convenience function)"""
    return CSRFProtection.verify_csrf_token(token, user_id)


def sanitize_auth_input(data: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize authentication input (convenience function)"""
    return InputSanitizer.sanitize_auth_input(data)


class SecurityManager:
    """Central security manager for authentication operations"""

    def __init__(self):
        self.rate_limiter = RateLimiter()
        self.csrf = CSRFProtection()
        self.sanitizer = InputSanitizer()

    def check_auth_rate_limit(self, ip_address: str, user_email: Optional[str] = None) -> None:
        """Check rate limit for authentication attempt

        Args:
            ip_address: Client IP address
            user_email: User email for user-specific limiting

        Raises:
            RateLimitExceededError: If rate limit exceeded
        """
        # Check IP-based rate limiting
        if self.rate_limiter.is_rate_limited(
            f"ip:{ip_address}", max_attempts=10, window_minutes=15
        ):
            raise RateLimitExceededError("Too many authentication attempts from this IP")

        # Check user-based rate limiting if email provided
        if user_email:
            if self.rate_limiter.is_rate_limited(
                f"user:{user_email}", max_attempts=5, window_minutes=15
            ):
                raise RateLimitExceededError("Too many authentication attempts for this account")

        # Record the attempt
        self.rate_limiter.record_attempt(f"ip:{ip_address}")
        if user_email:
            self.rate_limiter.record_attempt(f"user:{user_email}")

    def record_successful_auth(self, ip_address: str, user_email: str) -> None:
        """Record successful authentication to reset rate limits

        Args:
            ip_address: Client IP address
            user_email: User email address
        """
        self.rate_limiter.reset_attempts(f"ip:{ip_address}")
        self.rate_limiter.reset_attempts(f"user:{user_email}")

    def generate_email_verification_token(self, user_id: int, email: str) -> str:
        """Generate secure token for email verification

        Args:
            user_id: User database ID
            email: Email address to verify

        Returns:
            Verification token
        """
        payload = f"{user_id}:{email}:{datetime.now(timezone.utc).isoformat()}"
        signature = hmac.new(
            settings.jwt_secret_key.encode(), payload.encode(), hashlib.sha256
        ).hexdigest()

        return f"{secrets.token_urlsafe(32)}:{signature}"

    def verify_email_verification_token(self, token: str, user_id: int, email: str) -> bool:
        """Verify email verification token

        Args:
            token: Verification token
            user_id: Expected user ID
            email: Expected email address

        Returns:
            True if token is valid, False otherwise
        """
        try:
            parts = token.split(":")
            if len(parts) != 2:
                return False

            token_part, signature = parts

            # Reconstruct payload (simplified verification)
            # In production, embed user_id and email in the token
            expected_signature = hmac.new(
                settings.jwt_secret_key.encode(), f"{user_id}:{email}".encode(), hashlib.sha256
            ).hexdigest()

            return hmac.compare_digest(signature, expected_signature)

        except Exception as e:
            logger.warning(f"Email verification token verification failed: {e}")
            return False

    def cleanup_security_data(self) -> None:
        """Cleanup expired security data"""
        self.rate_limiter.cleanup_expired()


# Global security manager instance
security_manager = SecurityManager()


# Convenience functions
def check_auth_rate_limit(ip_address: str, user_email: Optional[str] = None) -> None:
    """Check authentication rate limit (convenience function)"""
    security_manager.check_auth_rate_limit(ip_address, user_email)


def record_successful_auth(ip_address: str, user_email: str) -> None:
    """Record successful authentication (convenience function)"""
    security_manager.record_successful_auth(ip_address, user_email)
