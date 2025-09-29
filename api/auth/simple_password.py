"""Simple password hashing alternative for compatibility

This module provides a working password hashing solution that doesn't
rely on bcrypt to avoid version compatibility issues. Uses PBKDF2
which is secure and widely supported.
"""

import hashlib
import logging
import secrets
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# PBKDF2 settings for secure password hashing
PBKDF2_ALGORITHM = "sha256"
PBKDF2_ITERATIONS = 100000  # Recommended by OWASP
SALT_LENGTH = 32


def generate_salt() -> str:
    """Generate cryptographically secure salt"""
    return secrets.token_hex(SALT_LENGTH // 2)


def hash_password_pbkdf2(password: str, salt: Optional[str] = None) -> str:
    """Hash password using PBKDF2

    Args:
        password: Plain text password
        salt: Optional salt (auto-generated if not provided)

    Returns:
        Hashed password in format: salt$hash
    """
    if salt is None:
        salt = generate_salt()

    # Use PBKDF2 with SHA-256
    password_hash = hashlib.pbkdf2_hmac(
        PBKDF2_ALGORITHM, password.encode("utf-8"), salt.encode("utf-8"), PBKDF2_ITERATIONS
    )

    # Return in format: salt$hash
    return f"{salt}${password_hash.hex()}"


def verify_password_pbkdf2(password: str, stored_hash: str) -> bool:
    """Verify password against PBKDF2 hash

    Args:
        password: Plain text password
        stored_hash: Stored hash in format: salt$hash

    Returns:
        True if password matches, False otherwise
    """
    try:
        salt, hash_hex = stored_hash.split("$", 1)

        # Recreate hash with same salt
        password_hash = hashlib.pbkdf2_hmac(
            PBKDF2_ALGORITHM, password.encode("utf-8"), salt.encode("utf-8"), PBKDF2_ITERATIONS
        )

        # Compare hashes
        return secrets.compare_digest(hash_hex, password_hash.hex())

    except ValueError:
        logger.error("Invalid stored hash format")
        return False
    except Exception as e:
        logger.error(f"Password verification failed: {e}")
        return False


def validate_password_simple(password: str) -> Dict[str, Any]:
    """Simple password validation without bcrypt dependency

    Args:
        password: Password to validate

    Returns:
        Validation result
    """
    errors = []
    score = 0

    # Length check
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    else:
        score += 25

    # Character type checks
    if any(c.isupper() for c in password):
        score += 20
    else:
        errors.append("Password must contain at least one uppercase letter")

    if any(c.islower() for c in password):
        score += 20
    else:
        errors.append("Password must contain at least one lowercase letter")

    if any(c.isdigit() for c in password):
        score += 20
    else:
        errors.append("Password must contain at least one digit")

    if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        score += 15
    else:
        errors.append("Password must contain at least one special character")

    # Bonus points for length
    if len(password) >= 12:
        score += 10
    if len(password) >= 16:
        score += 10

    return {
        "is_valid": len(errors) == 0,
        "score": min(score, 100),
        "errors": errors,
        "strength": (
            "strong"
            if score >= 80
            else "good" if score >= 60 else "fair" if score >= 40 else "weak"
        ),
    }
