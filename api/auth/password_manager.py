"""Password security and management for Bet-That API

Provides secure password hashing, verification, and strength validation
using industry-standard bcrypt with proper salt handling.
"""

import hashlib
import logging
import re
import secrets
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from .exceptions import PasswordTooWeakError

# Try to use bcrypt, fall back to PBKDF2 if there are compatibility issues
try:
    from passlib.context import CryptContext
    from passlib.hash import bcrypt

    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False

# Import simple password functions as fallback
from .simple_password import hash_password_pbkdf2, validate_password_simple, verify_password_pbkdf2

logger = logging.getLogger(__name__)


class PasswordConfig:
    """Password security configuration"""

    # bcrypt configuration
    BCRYPT_ROUNDS = 12  # Good balance of security and performance

    # Password strength requirements
    MIN_LENGTH = 8
    MAX_LENGTH = 128
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_DIGITS = True
    REQUIRE_SPECIAL_CHARS = True

    # Common weak passwords and patterns
    FORBIDDEN_PASSWORDS = {
        "password",
        "123456",
        "123456789",
        "qwerty",
        "abc123",
        "password123",
        "admin",
        "letmein",
        "welcome",
        "monkey",
        "dragon",
        "12345678",
        "1234567890",
        "football",
        "iloveyou",
    }

    # Special characters allowed
    SPECIAL_CHARS = "!@#$%^&*()_+-=[]{}|;:,.<>?"


# Create password context with bcrypt (if available)
pwd_context = None
if BCRYPT_AVAILABLE:
    try:
        pwd_context = CryptContext(
            schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=PasswordConfig.BCRYPT_ROUNDS
        )
        # Test if bcrypt is working by attempting a simple hash
        pwd_context.hash("test")
        logger.info("Using bcrypt for password hashing")
    except Exception as e:
        logger.warning(f"bcrypt initialization failed: {e}. Falling back to PBKDF2")
        pwd_context = None
        BCRYPT_AVAILABLE = False

if not BCRYPT_AVAILABLE or pwd_context is None:
    logger.info("Using PBKDF2 for password hashing")


def generate_salt() -> str:
    """Generate cryptographically secure salt

    Returns:
        32-character hex salt string
    """
    return secrets.token_hex(16)


def hash_password(password: str, salt: Optional[str] = None) -> str:
    """Hash password using bcrypt or PBKDF2 fallback

    Args:
        password: Plain text password
        salt: Optional custom salt (auto-generated if not provided)

    Returns:
        Hashed password string

    Raises:
        PasswordTooWeakError: If password doesn't meet requirements
    """
    # Validate password strength first
    validate_password_strength(password)

    try:
        # Try bcrypt first if available
        if pwd_context is not None:
            # bcrypt handles salt internally and has a 72-byte limit
            password_to_hash = password
            if len(password_to_hash.encode("utf-8")) > 72:
                password_to_hash = password_to_hash.encode("utf-8")[:72].decode(
                    "utf-8", errors="ignore"
                )

            hashed = pwd_context.hash(password_to_hash)
            logger.debug("Password hashed successfully with bcrypt")
            return hashed
        else:
            # Fall back to PBKDF2
            hashed = hash_password_pbkdf2(password, salt)
            logger.debug("Password hashed successfully with PBKDF2")
            return hashed

    except Exception as e:
        logger.error(f"Password hashing failed: {e}")
        # Try fallback if bcrypt fails
        if pwd_context is not None:
            try:
                hashed = hash_password_pbkdf2(password, salt)
                logger.warning("bcrypt failed, used PBKDF2 fallback")
                return hashed
            except Exception as e2:
                logger.error(f"PBKDF2 fallback also failed: {e2}")
        raise PasswordTooWeakError("Failed to hash password")


def verify_password(plain_password: str, hashed_password: str, salt: Optional[str] = None) -> bool:
    """Verify password against hash

    Args:
        plain_password: Plain text password to verify
        hashed_password: Stored password hash
        salt: Optional salt used during hashing (ignored for bcrypt)

    Returns:
        True if password matches, False otherwise
    """
    try:
        # Apply same truncation as during hashing for bcrypt 72-byte limit
        password_to_verify = plain_password
        if len(password_to_verify.encode("utf-8")) > 72:
            password_to_verify = password_to_verify.encode("utf-8")[:72].decode(
                "utf-8", errors="ignore"
            )

        is_valid = pwd_context.verify(password_to_verify, hashed_password)

        if is_valid:
            logger.debug("Password verification successful")
        else:
            logger.warning("Password verification failed")

        return is_valid

    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False


def validate_password_strength(password: str) -> Dict[str, Any]:
    """Validate password meets security requirements

    Args:
        password: Password to validate

    Returns:
        Dictionary with validation results and score

    Raises:
        PasswordTooWeakError: If password doesn't meet minimum requirements
    """
    # Use simple validation if bcrypt is having issues
    if not BCRYPT_AVAILABLE or pwd_context is None:
        simple_result = validate_password_simple(password)
        if not simple_result["is_valid"]:
            raise PasswordTooWeakError("; ".join(simple_result["errors"]))
        return simple_result

    errors = []
    checks = {
        "length": False,
        "uppercase": False,
        "lowercase": False,
        "digits": False,
        "special_chars": False,
        "not_common": False,
        "no_personal_info": False,
    }

    # Length check
    if len(password) < PasswordConfig.MIN_LENGTH:
        errors.append(f"Password must be at least {PasswordConfig.MIN_LENGTH} characters long")
    elif len(password) > PasswordConfig.MAX_LENGTH:
        errors.append(f"Password must be no more than {PasswordConfig.MAX_LENGTH} characters long")
    else:
        checks["length"] = True

    # Character type checks
    if PasswordConfig.REQUIRE_UPPERCASE and not re.search(r"[A-Z]", password):
        errors.append("Password must contain at least one uppercase letter")
    else:
        checks["uppercase"] = True

    if PasswordConfig.REQUIRE_LOWERCASE and not re.search(r"[a-z]", password):
        errors.append("Password must contain at least one lowercase letter")
    else:
        checks["lowercase"] = True

    if PasswordConfig.REQUIRE_DIGITS and not re.search(r"\d", password):
        errors.append("Password must contain at least one digit")
    else:
        checks["digits"] = True

    if PasswordConfig.REQUIRE_SPECIAL_CHARS and not re.search(
        f"[{re.escape(PasswordConfig.SPECIAL_CHARS)}]", password
    ):
        errors.append(
            f"Password must contain at least one special character: {PasswordConfig.SPECIAL_CHARS}"
        )
    else:
        checks["special_chars"] = True

    # Common password check
    if password.lower() in PasswordConfig.FORBIDDEN_PASSWORDS:
        errors.append("Password is too common and easily guessable")
    else:
        checks["not_common"] = True

    # Sequential characters check
    if re.search(r"(.)\1{2,}", password):  # 3+ repeated chars
        errors.append("Password cannot contain 3 or more repeated characters")
    else:
        checks["no_personal_info"] = True

    # Calculate strength score (0-100)
    score = sum(checks.values()) / len(checks) * 100

    # Additional scoring factors
    if len(password) >= 12:
        score += 10
    if len(password) >= 16:
        score += 10
    if re.search(r"[A-Z].*[A-Z]", password):  # Multiple uppercase
        score += 5
    if re.search(r"[0-9].*[0-9]", password):  # Multiple digits
        score += 5
    if (
        len(re.findall(f"[{re.escape(PasswordConfig.SPECIAL_CHARS)}]", password)) >= 2
    ):  # Multiple special chars
        score += 5

    score = min(score, 100)  # Cap at 100

    validation_result = {
        "is_valid": len(errors) == 0,
        "score": score,
        "errors": errors,
        "checks": checks,
        "strength": _get_strength_label(score),
    }

    # Raise exception if validation fails
    if errors:
        error_msg = "; ".join(errors)
        raise PasswordTooWeakError(f"Password validation failed: {error_msg}")

    return validation_result


def _get_strength_label(score: float) -> str:
    """Get password strength label from score"""
    if score >= 90:
        return "very_strong"
    elif score >= 80:
        return "strong"
    elif score >= 70:
        return "good"
    elif score >= 60:
        return "fair"
    else:
        return "weak"


def needs_rehash(hashed_password: str) -> bool:
    """Check if password hash needs to be updated

    Args:
        hashed_password: Stored password hash

    Returns:
        True if hash should be updated, False otherwise
    """
    try:
        return pwd_context.needs_update(hashed_password)
    except Exception:
        return True  # If we can't determine, assume it needs updating


def generate_secure_password(length: int = 16) -> str:
    """Generate cryptographically secure password

    Args:
        length: Password length (minimum 12)

    Returns:
        Secure random password
    """
    if length < 12:
        length = 12

    # Ensure we have at least one of each required character type
    uppercase = secrets.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    lowercase = secrets.choice("abcdefghijklmnopqrstuvwxyz")
    digit = secrets.choice("0123456789")
    special = secrets.choice(PasswordConfig.SPECIAL_CHARS)

    # Fill remaining length with random characters
    all_chars = (
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        + PasswordConfig.SPECIAL_CHARS
    )
    remaining = "".join(secrets.choice(all_chars) for _ in range(length - 4))

    # Combine and shuffle
    password_chars = list(uppercase + lowercase + digit + special + remaining)
    secrets.SystemRandom().shuffle(password_chars)

    return "".join(password_chars)


class PasswordManager:
    """High-level password management class"""

    def __init__(self):
        self.config = PasswordConfig()

    def hash_password_secure(self, password: str) -> Dict[str, str]:
        """Hash password and return hash with metadata

        Args:
            password: Plain text password

        Returns:
            Dictionary with hash, salt, and metadata
        """
        salt = generate_salt()
        password_hash = hash_password(password, salt)

        return {
            "hash": password_hash,
            "salt": salt,
            "algorithm": "bcrypt",
            "rounds": PasswordConfig.BCRYPT_ROUNDS,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

    def verify_and_upgrade(
        self, password: str, current_hash: str, salt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Verify password and check if hash needs upgrading

        Args:
            password: Plain text password
            current_hash: Current stored hash
            salt: Salt used for hashing

        Returns:
            Dictionary with verification result and upgrade info
        """
        is_valid = verify_password(password, current_hash, salt)
        needs_upgrade = needs_rehash(current_hash) if is_valid else False

        result = {
            "is_valid": is_valid,
            "needs_upgrade": needs_upgrade,
            "new_hash": None,
            "new_salt": None,
        }

        if is_valid and needs_upgrade:
            # Generate new hash with current security standards
            new_salt = generate_salt()
            new_hash = hash_password(password, new_salt)
            result.update({"new_hash": new_hash, "new_salt": new_salt})

        return result

    def check_password_policy(
        self, password: str, user_email: Optional[str] = None
    ) -> Dict[str, Any]:
        """Check password against security policy

        Args:
            password: Password to check
            user_email: User's email for additional validation

        Returns:
            Policy check results
        """
        try:
            validation = validate_password_strength(password)

            # Additional checks with user context
            if user_email:
                email_local = user_email.split("@")[0].lower()
                if email_local in password.lower():
                    validation["errors"].append("Password cannot contain email address")
                    validation["is_valid"] = False

            return validation

        except PasswordTooWeakError as e:
            return {"is_valid": False, "score": 0, "errors": [str(e)], "strength": "weak"}


# Global password manager instance
password_manager = PasswordManager()
