"""Authentication service layer for user management

Provides business logic for user registration, login, and profile management
with comprehensive validation and error handling.
"""

import logging
from datetime import datetime
from typing import Optional, cast

from sqlalchemy.orm import Session

from ..auth.exceptions import (
    EmailAlreadyExistsError,
    EmailNotVerifiedError,
    InvalidCredentialsError,
    UserInactiveError,
    UsernameAlreadyExistsError,
    UserNotFoundError,
)
from ..auth.jwt_auth import jwt_auth
from ..auth.simple_password import verify_password_pbkdf2
from ..auth_schemas import (
    AuthResponse,
    RegistrationResponse,
    UserLoginRequest,
    UserRegistrationRequest,
    UserResponse,
)
from ..models import User, UserStatus
from ..repositories.user_repository import UserRepository
from ..settings import settings

logger = logging.getLogger(__name__)


class AuthService:
    """Service class for authentication operations"""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.user_repo = UserRepository(db)

    def register_user(self, registration_data: UserRegistrationRequest) -> RegistrationResponse:
        """Register a new user account

        Args:
            registration_data: User registration information

        Returns:
            Registration response with user data

        Raises:
            EmailAlreadyExistsError: If email is already registered
            UsernameAlreadyExistsError: If username is already taken
        """
        try:
            # Check if email already exists
            if self.user_repo.email_exists(registration_data.email):
                raise EmailAlreadyExistsError("Email address is already registered")

            # Check if username already exists
            if self.user_repo.username_exists(registration_data.username):
                raise UsernameAlreadyExistsError("Username is already taken")

            # Create user
            user = self.user_repo.create_user(registration_data)

            logger.info(f"User registered successfully: {user.email} ({user.username})")

            # TODO: Send verification email

            return RegistrationResponse(
                message="Registration successful. Please check your email to verify your account.",
                user=self._create_user_response(user),
                verification_required=(
                    settings.enable_email_verification
                    if hasattr(settings, "enable_email_verification")
                    else True
                ),
            )

        except (EmailAlreadyExistsError, UsernameAlreadyExistsError):
            raise
        except Exception as e:
            logger.error(f"Registration failed for {registration_data.email}: {str(e)}")
            self.db.rollback()
            raise

    def login_user(self, login_data: UserLoginRequest) -> AuthResponse:
        """Authenticate user and return tokens

        Args:
            login_data: User login information

        Returns:
            Authentication response with tokens and user data

        Raises:
            InvalidCredentialsError: If credentials are invalid
            UserInactiveError: If user account is deactivated
            EmailNotVerifiedError: If email is not verified (when required)
        """
        try:
            # Find user by email or username
            user = self.user_repo.get_user_by_email_or_username(login_data.email_or_username)

            if not user:
                logger.warning(
                    f"Login attempt with non-existent user: {login_data.email_or_username}"
                )
                raise InvalidCredentialsError("Invalid email/username or password")

            # Verify password
            if not user.password_hash or not verify_password_pbkdf2(
                login_data.password, cast(str, user.password_hash)
            ):
                logger.warning(f"Invalid password for user: {user.email}")
                raise InvalidCredentialsError("Invalid email/username or password")

            # Check if user is active
            if not user.is_active:
                logger.warning(f"Login attempt for inactive user: {user.email}")
                raise UserInactiveError("Account is deactivated")

            # Check account status
            if user.status in [UserStatus.SUSPENDED, UserStatus.BANNED]:
                logger.warning(f"Login attempt for suspended/banned user: {user.email}")
                raise UserInactiveError("Account is suspended or banned")

            # Check email verification if required
            enable_email_verification = getattr(settings, "enable_email_verification", True)
            if enable_email_verification and not user.email_verified:
                logger.warning(f"Login attempt for unverified user: {user.email}")
                raise EmailNotVerifiedError("Email address not verified")

            # Generate tokens
            tokens = jwt_auth.create_user_tokens(
                user_id=cast(int, user.id),
                external_id=cast(str, user.external_id),
                email=cast(str, user.email),
                roles=["user"],  # TODO: Implement role system
            )

            # Update last login
            self.user_repo.update_last_login(cast(int, user.id))

            logger.info(f"User logged in successfully: {user.email} ({user.username})")

            # Calculate token expiration
            access_token_expire_minutes = getattr(settings, "jwt_access_token_expire_minutes", 15)

            return AuthResponse(
                access_token=tokens["access_token"],
                refresh_token=tokens["refresh_token"],
                token_type="bearer",
                expires_in=access_token_expire_minutes * 60,
                user=self._create_user_response(user),
            )

        except (InvalidCredentialsError, UserInactiveError, EmailNotVerifiedError):
            raise
        except Exception as e:
            logger.error(f"Login failed for {login_data.email_or_username}: {str(e)}")
            raise InvalidCredentialsError("Login failed")

    def get_user_by_id(self, user_id: int) -> UserResponse:
        """Get user by ID and return response model

        Args:
            user_id: User database ID

        Returns:
            User response model

        Raises:
            UserNotFoundError: If user doesn't exist
        """
        user = self.user_repo.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError("User not found")

        return self._create_user_response(user)

    def verify_user_email(self, user_id: int) -> UserResponse:
        """Verify user email and return updated user data

        Args:
            user_id: User database ID

        Returns:
            Updated user response

        Raises:
            UserNotFoundError: If user doesn't exist
        """
        try:
            self.user_repo.verify_user_email(user_id)
            user = self.user_repo.get_user_by_id(user_id)

            if not user:
                raise UserNotFoundError("User not found")

            logger.info(f"Email verified for user: {user.email}")
            return self._create_user_response(user)

        except UserNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Email verification failed for user {user_id}: {e}")
            raise

    def _create_user_response(self, user: User) -> UserResponse:
        """Create UserResponse from User model

        Args:
            user: User database model

        Returns:
            UserResponse Pydantic model
        """
        return UserResponse(
            id=cast(int, user.id),
            email=cast(str, user.email),
            username=cast(Optional[str], user.username),
            first_name=cast(Optional[str], user.first_name),
            last_name=cast(Optional[str], user.last_name),
            name=cast(Optional[str], user.name),
            is_active=cast(bool, user.is_active),
            is_verified=cast(bool, user.is_verified),
            email_verified=cast(bool, user.email_verified),
            status=cast(str, user.status),
            timezone=cast(str, user.timezone),
            created_at=cast(datetime, user.created_at),
            last_login_at=cast(Optional[datetime], user.last_login_at),
            verification_level=cast(str, user.verification_level),
        )
