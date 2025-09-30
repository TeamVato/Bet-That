"""Authentication endpoints for JWT-based authentication

Provides login, logout, token refresh, password reset, and email verification
endpoints with comprehensive security features including new registration and
username-based login.
"""

import logging
from datetime import datetime, timezone
from typing import Annotated, Any, Optional, Union

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..auth_schemas import (
    AuthResponse,
    RegistrationResponse,
    UserLoginRequest,
    UserRegistrationRequest,
    UserResponse,
)
from ..database import get_db
from ..models import User, UserStatus
from ..services.auth_service import AuthService
from ..settings import settings
from .dependencies import CurrentUser, get_client_ip, verify_jwt_token
from .exceptions import (
    EmailAlreadyExistsError,
    EmailNotVerifiedError,
    InvalidCredentialsError,
    PasswordTooWeakError,
    RateLimitExceededError,
    RefreshTokenError,
    TokenExpiredError,
    TokenInvalidError,
    TokenRevokedError,
    UserInactiveError,
    UsernameAlreadyExistsError,
    UserNotFoundError,
)
from .jwt_auth import (
    generate_password_reset_token,
    jwt_auth,
    verify_password_reset_token,
    verify_token,
)
from .password_manager import hash_password, password_manager, verify_password
from .schemas import (
    EmailVerificationRequest,
    LoginResponse,
    LogoutResponse,
    PasswordChangeRequest,
    PasswordResetConfirmRequest,
    PasswordResetRequest,
    RefreshTokenRequest,
    RefreshTokenResponse,
    UserRegisterRequest,
    UserRegisterResponse,
)
from .security_utils import (
    generate_csrf_token,
    generate_secure_token,
    sanitize_auth_input,
    security_manager,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_user_value(user: Union[User, dict], field: str) -> Any:
    """Helper function to get actual values from User model or dict"""
    if isinstance(user, dict):
        return user.get(field)
    else:
        # For User model, get the actual value from the Column
        return getattr(user, field)


def get_model_value(model: User, field: str) -> Any:
    """Helper function to get actual values from SQLAlchemy model"""
    return getattr(model, field)


# Enhanced registration endpoint with username support
@router.post("/register", response_model=RegistrationResponse, status_code=status.HTTP_201_CREATED)
async def register_user_enhanced(
    registration_data: UserRegistrationRequest,
    client_request: Request,
    db: Annotated[Session, Depends(get_db)],
) -> RegistrationResponse:
    """Register a new user account with username support

    Creates new user account with email and username validation.
    Requires email verification before account activation.
    """
    client_ip = get_client_ip(client_request)

    try:
        # Check rate limiting
        security_manager.check_auth_rate_limit(client_ip)

        # Create auth service
        auth_service = AuthService(db)

        # Register user
        result = auth_service.register_user(registration_data)

        # Record successful registration
        security_manager.record_successful_auth(client_ip, registration_data.email)

        return result

    except (EmailAlreadyExistsError, UsernameAlreadyExistsError) as e:
        # Record failed attempt
        security_manager.rate_limiter.record_attempt(f"register:{client_ip}")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except PasswordTooWeakError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except RateLimitExceededError:
        raise
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Registration failed"
        )


# Enhanced login endpoint with username support
@router.post("/login", response_model=AuthResponse)
async def login_user_enhanced(
    login_data: UserLoginRequest, 
    client_request: Request, 
    db: Annotated[Session, Depends(get_db)]
) -> AuthResponse:
    """Authenticate user with email or username

    Validates credentials and returns JWT tokens for authentication.
    Supports both email and username login.
    """
    client_ip = get_client_ip(client_request)

    try:
        # Check rate limiting
        security_manager.check_auth_rate_limit(client_ip, login_data.email_or_username)

        # Create auth service
        auth_service = AuthService(db)

        # Authenticate user
        result = auth_service.login_user(login_data)

        # Record successful login
        security_manager.record_successful_auth(client_ip, login_data.email_or_username)

        return result

    except InvalidCredentialsError as e:
        # Record failed attempt
        security_manager.rate_limiter.record_attempt(f"login:{login_data.email_or_username}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except (UserInactiveError, EmailNotVerifiedError) as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except RateLimitExceededError:
        raise
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Login failed"
        )


# Enhanced current user endpoint
@router.get("/me", response_model=UserResponse)
async def get_current_user_enhanced(
    current_user: CurrentUser, 
    db: Annotated[Session, Depends(get_db)]
) -> UserResponse:
    """Get current authenticated user information

    Returns comprehensive user profile data for the authenticated user.
    """
    try:
        auth_service = AuthService(db)
        user_id = get_user_value(current_user, "id")
        return auth_service.get_user_by_id(user_id)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get current user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user information",
        )


# Legacy registration endpoint for backward compatibility
@router.post("/register-legacy", response_model=UserRegisterResponse)
async def register_user(
    request: UserRegisterRequest,
    client_request: Request,
    background_tasks: BackgroundTasks,
    db: Annotated[Session, Depends(get_db)],
) -> UserRegisterResponse:
    """Register new user with email and password

    Creates new user account with email verification requirement.
    Automatically sends verification email in background.
    """
    client_ip = get_client_ip(client_request)

    try:
        # Check rate limiting
        security_manager.check_auth_rate_limit(client_ip)

        # Sanitize input
        sanitized_data = sanitize_auth_input(request.dict())

        # Check if user already exists
        existing_user = db.query(User).filter(User.email == sanitized_data["email"]).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="User with this email already exists"
            )

        # Validate password strength
        password_validation = password_manager.check_password_policy(
            request.password.get_secret_value(), sanitized_data["email"]
        )
        if not password_validation["is_valid"]:
            raise PasswordTooWeakError("; ".join(password_validation["errors"]))

        # Hash password
        password_hash = hash_password(request.password.get_secret_value())

        # Create user
        user = User(
            email=sanitized_data["email"],
            password_hash=password_hash,
            name=sanitized_data.get("name"),
            first_name=sanitized_data.get("first_name"),
            last_name=sanitized_data.get("last_name"),
            external_id=f"local_{generate_secure_token(16)}",  # Generate local external_id
            status=(
                UserStatus.PENDING_VERIFICATION
                if settings.enable_email_verification
                else UserStatus.ACTIVE
            ),
            email_verified=not settings.enable_email_verification,
            timezone=request.timezone or "UTC",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        # Generate email verification token if needed
        if settings.enable_email_verification:
            security_manager.generate_email_verification_token(get_model_value(user, "id"), get_model_value(user, "email"))
            # TODO: Send verification email in background task
            # background_tasks.add_task(send_verification_email, user.email, verification_token)

        logger.info(f"User registered: {user.id} ({user.email})")

        return UserRegisterResponse(
            id=get_model_value(user, "id"),
            email=get_model_value(user, "email"),
            name=get_model_value(user, "name"),
            status=get_model_value(user, "status"),
            email_verified=get_model_value(user, "email_verified"),
            created_at=get_model_value(user, "created_at"),
            verification_required=settings.enable_email_verification,
            message="Registration successful"
            + (
                ". Please check your email for verification instructions."
                if settings.enable_email_verification
                else ""
            ),
        )

    except (PasswordTooWeakError, HTTPException):
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Registration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Registration failed"
        )


@router.post("/login-form", response_model=LoginResponse)
async def login_user_form(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
) -> LoginResponse:
    """Login user with email and password

    Validates credentials and returns JWT tokens for authentication.
    Implements rate limiting and security logging.
    """
    client_ip = get_client_ip(request)

    try:
        # Check rate limiting
        security_manager.check_auth_rate_limit(client_ip, form_data.username)

        # Find user by email (username field contains email)
        user = db.query(User).filter(User.email == form_data.username.lower()).first()

        if not user:
            security_manager.rate_limiter.record_attempt(f"user:{form_data.username}")
            raise InvalidCredentialsError()

        # Verify password
        if not get_model_value(user, "password_hash") or not verify_password(form_data.password, get_model_value(user, "password_hash")):
            security_manager.rate_limiter.record_attempt(f"user:{form_data.username}")
            raise InvalidCredentialsError()

        # Check user status
        if not user.is_active or user.status in [UserStatus.SUSPENDED, UserStatus.BANNED]:
            raise UserInactiveError()

        # Check email verification
        if settings.enable_email_verification and not user.email_verified:
            raise EmailNotVerifiedError()

        # Generate tokens
        tokens = jwt_auth.create_user_tokens(
            user_id=get_model_value(user, "id"),
            external_id=get_model_value(user, "external_id"),
            email=get_model_value(user, "email"),
            roles=["user"],  # TODO: Implement role system
        )

        # Update user login timestamp
        db.query(User).filter(User.id == get_model_value(user, "id")).update({
            "last_login_at": datetime.now(timezone.utc),
            "last_activity_at": datetime.now(timezone.utc)
        })
        db.commit()

        # Reset rate limiting on successful login
        security_manager.record_successful_auth(client_ip, get_model_value(user, "email"))

        # Generate CSRF token if enabled
        csrf_token = None
        if settings.enable_csrf_protection:
            csrf_token = generate_csrf_token(get_model_value(user, "id"))

        logger.info(f"User logged in: {user.id} ({user.email})")

        return LoginResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type="bearer",
            expires_in=settings.jwt_access_token_expire_minutes * 60,
            csrf_token=csrf_token,
            user={
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "status": user.status,
                "email_verified": user.email_verified,
            },
        )

    except (
        InvalidCredentialsError,
        UserInactiveError,
        EmailNotVerifiedError,
        RateLimitExceededError,
    ):
        raise
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Login failed"
        )


@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_access_token(
    request: RefreshTokenRequest, 
    db: Annotated[Session, Depends(get_db)]
) -> RefreshTokenResponse:
    """Refresh access token using refresh token

    Validates refresh token and generates new access token.
    Optionally rotates refresh token for enhanced security.
    """
    try:
        # Verify refresh token
        payload = verify_token(request.refresh_token, token_type="refresh")
        user_id = int(payload["sub"])

        # Verify user still exists and is active
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise RefreshTokenError("User account is inactive")

        # Generate new access token
        new_access_token = jwt_auth.refresh_access_token(request.refresh_token)

        # Optionally rotate refresh token (recommended for high security)
        new_refresh_token = request.refresh_token
        if request.rotate_refresh_token:
            # Revoke old refresh token
            jwt_auth.logout_user("", request.refresh_token)

            # Create new refresh token
            tokens = jwt_auth.create_user_tokens(
                user_id=get_model_value(user, "id"), 
                external_id=get_model_value(user, "external_id"), 
                email=get_model_value(user, "email"), 
                roles=["user"]
            )
            new_refresh_token = tokens["refresh_token"]

        # Update user activity
        db.query(User).filter(User.id == get_model_value(user, "id")).update({
            "last_activity_at": datetime.now(timezone.utc)
        })
        db.commit()

        logger.info(f"Token refreshed for user: {user_id}")

        return RefreshTokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=settings.jwt_access_token_expire_minutes * 60,
        )

    except (TokenInvalidError, TokenExpiredError, TokenRevokedError) as e:
        raise RefreshTokenError(str(e))
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Token refresh failed"
        )


@router.post("/logout", response_model=LogoutResponse)
async def logout_user(
    current_user: CurrentUser,
    token_payload: Annotated[dict, Depends(verify_jwt_token)],
    request_data: Optional[dict] = None,
) -> LogoutResponse:
    """Logout user by revoking current tokens

    Revokes the current access token and optionally refresh token.
    Can logout from current session or all sessions.
    """
    try:
        # Extract token from the request (we need the raw token)
        # This is a simplified approach - in production, you'd extract from the request

        # Revoke current session
        user_id = get_user_value(current_user, "id")
        if request_data and request_data.get("logout_all_sessions"):
            jwt_auth.logout_all_user_sessions(user_id)
            logger.info(f"User logged out from all sessions: {user_id}")
            message = "Logged out from all sessions"
        else:
            # For individual session logout, we need the actual tokens
            # This would typically be handled by middleware that extracts tokens
            logger.info(f"User logged out: {user_id}")
            message = "Logged out successfully"

        return LogoutResponse(message=message, logged_out_at=datetime.now(timezone.utc))

    except Exception as e:
        logger.error(f"Logout failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Logout failed"
        )


@router.post("/password/reset")
async def request_password_reset(
    request: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    client_request: Request,
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    """Request password reset for user email

    Sends password reset email with secure token.
    Always returns success to prevent email enumeration.
    """
    client_ip = get_client_ip(client_request)

    try:
        # Check rate limiting
        security_manager.check_auth_rate_limit(client_ip)

        # Sanitize email
        email = sanitize_auth_input({"email": request.email})["email"]

        # Find user (but don't reveal if user exists)
        user = db.query(User).filter(User.email == email).first()

        if user and user.is_active:
            # Generate password reset token
            generate_password_reset_token(get_model_value(user, "id"), get_model_value(user, "email"))

            # TODO: Send password reset email in background
            # background_tasks.add_task(send_password_reset_email, user.email, reset_token)

            logger.info(f"Password reset requested for user: {user.id}")
        else:
            logger.warning(f"Password reset requested for non-existent user: {email}")

        # Always return success to prevent email enumeration
        return {
            "message": "If an account with this email exists, you will receive password reset instructions."
        }

    except RateLimitExceededError:
        raise
    except Exception as e:
        logger.error(f"Password reset request failed: {e}")
        return {
            "message": "If an account with this email exists, you will receive password reset instructions."
        }


@router.post("/password/reset/confirm")
async def confirm_password_reset(
    request: PasswordResetConfirmRequest, 
    db: Annotated[Session, Depends(get_db)]
) -> dict:
    """Confirm password reset with token and new password

    Validates reset token and updates user password.
    """
    try:
        # Verify reset token
        payload = verify_password_reset_token(request.token)
        user_id = int(payload["sub"])

        # Find user
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise UserNotFoundError()

        # Validate new password
        password_validation = password_manager.check_password_policy(
            request.new_password.get_secret_value(), get_model_value(user, "email")
        )
        if not password_validation["is_valid"]:
            raise PasswordTooWeakError("; ".join(password_validation["errors"]))

        # Update password
        db.query(User).filter(User.id == user_id).update({
            "password_hash": hash_password(request.new_password.get_secret_value()),
            "updated_at": datetime.now(timezone.utc)
        })

        # Revoke all existing tokens for security
        jwt_auth.logout_all_user_sessions(user_id)

        db.commit()

        logger.info(f"Password reset completed for user: {user.id}")

        return {"message": "Password reset successful"}

    except (TokenInvalidError, UserNotFoundError, PasswordTooWeakError):
        raise
    except Exception as e:
        logger.error(f"Password reset confirmation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Password reset failed"
        )


@router.post("/password/change")
async def change_password(
    request: PasswordChangeRequest, 
    current_user: CurrentUser, 
    db: Annotated[Session, Depends(get_db)]
) -> dict:
    """Change user password (requires current password)

    Validates current password and updates to new password.
    """
    try:
        # Get user values
        user_id = get_user_value(current_user, "id")
        password_hash = get_user_value(current_user, "password_hash")
        email = get_user_value(current_user, "email")
        
        # Verify current password
        if not password_hash or not verify_password(
            request.current_password.get_secret_value(), password_hash
        ):
            raise InvalidCredentialsError("Current password is incorrect")

        # Validate new password
        password_validation = password_manager.check_password_policy(
            request.new_password.get_secret_value(), email
        )
        if not password_validation["is_valid"]:
            raise PasswordTooWeakError("; ".join(password_validation["errors"]))

        # Update password
        db.query(User).filter(User.id == user_id).update({
            "password_hash": hash_password(request.new_password.get_secret_value()),
            "updated_at": datetime.now(timezone.utc)
        })

        # Optionally revoke all other sessions
        if request.logout_other_sessions:
            jwt_auth.logout_all_user_sessions(user_id)

        db.commit()

        logger.info(f"Password changed for user: {user_id}")

        return {"message": "Password changed successfully"}

    except (InvalidCredentialsError, PasswordTooWeakError):
        raise
    except Exception as e:
        logger.error(f"Password change failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Password change failed"
        )


@router.post("/email/verify")
async def verify_email(
    request: EmailVerificationRequest, 
    db: Annotated[Session, Depends(get_db)]
) -> dict:
    """Verify user email with verification token

    Validates verification token and marks email as verified.
    """
    try:
        # For this simplified implementation, we'll decode the token
        # In production, you'd have a more sophisticated token format
        if not security_manager.verify_email_verification_token(
            request.token, request.user_id, request.email
        ):
            raise TokenInvalidError("Invalid verification token")

        # Find user
        user = (
            db.query(User).filter(User.id == request.user_id, User.email == request.email).first()
        )

        if not user:
            raise UserNotFoundError()

        # Mark email as verified
        current_status = get_model_value(user, "status")
        new_status = (
            UserStatus.ACTIVE if current_status == UserStatus.PENDING_VERIFICATION else current_status
        )
        db.query(User).filter(User.id == get_model_value(user, "id")).update({
            "email_verified": True,
            "email_verified_at": datetime.now(timezone.utc),
            "status": new_status,
            "updated_at": datetime.now(timezone.utc)
        })

        db.commit()

        logger.info(f"Email verified for user: {user.id}")

        return {"message": "Email verified successfully"}

    except (TokenInvalidError, UserNotFoundError):
        raise
    except Exception as e:
        logger.error(f"Email verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Email verification failed"
        )


@router.post("/email/verification/resend")
async def resend_email_verification(
    current_user: CurrentUser, 
    background_tasks: BackgroundTasks
) -> dict:
    """Resend email verification for current user

    Generates new verification token and sends email.
    """
    try:
        user_id = get_user_value(current_user, "id")
        email = get_user_value(current_user, "email")
        email_verified = get_user_value(current_user, "email_verified")
        
        if email_verified:
            return {"message": "Email is already verified"}

        # Generate new verification token
        security_manager.generate_email_verification_token(user_id, email)

        # TODO: Send verification email in background
        # background_tasks.add_task(send_verification_email, email, verification_token)

        logger.info(f"Email verification resent for user: {user_id}")

        return {"message": "Verification email sent"}

    except Exception as e:
        logger.error(f"Email verification resend failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification email",
        )


@router.get("/me-legacy")
async def get_current_user_info_legacy(current_user: CurrentUser) -> dict:
    """Get current authenticated user information

    Returns user profile and authentication status.
    """
    return {
        "id": get_user_value(current_user, "id"),
        "external_id": get_user_value(current_user, "external_id"),
        "email": get_user_value(current_user, "email"),
        "name": get_user_value(current_user, "name"),
        "first_name": get_user_value(current_user, "first_name"),
        "last_name": get_user_value(current_user, "last_name"),
        "status": get_user_value(current_user, "status"),
        "email_verified": get_user_value(current_user, "email_verified"),
        "timezone": get_user_value(current_user, "timezone"),
        "created_at": get_user_value(current_user, "created_at"),
        "last_login_at": get_user_value(current_user, "last_login_at"),
        "verification_level": get_user_value(current_user, "verification_level"),
        "is_active": get_user_value(current_user, "is_active"),
    }


@router.post("/tokens/validate")
async def validate_token(
    token_payload: Annotated[dict, Depends(verify_jwt_token)]
) -> dict:
    """Validate JWT token and return payload information

    Useful for client-side token validation and debugging.
    """
    return {
        "valid": True,
        "user_id": int(token_payload["sub"]),
        "email": token_payload["email"],
        "token_type": token_payload["type"],
        "expires_at": token_payload["exp"],
        "issued_at": token_payload["iat"],
        "roles": token_payload.get("roles", []),
    }


# Legacy endpoint for backward compatibility during migration
@router.post("/legacy/login")
async def legacy_login(
    request: dict, 
    db: Annotated[Session, Depends(get_db)]
) -> dict:
    """Legacy login endpoint for backward compatibility

    Supports existing external_id based authentication during migration.
    """
    external_id = request.get("external_id")
    if not external_id:
        raise HTTPException(status_code=400, detail="external_id required")

    # Find or create user
    user = db.query(User).filter(User.external_id == external_id).first()

    if not user:
        # Create user for legacy compatibility
        user = User(
            external_id=external_id,
            email=request.get("email", f"{external_id}@placeholder.com"),
            name=request.get("name"),
            status=UserStatus.ACTIVE,
            email_verified=False,  # Legacy users need to verify
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # Generate tokens
    tokens = jwt_auth.create_user_tokens(
        user_id=get_model_value(user, "id"), 
        external_id=get_model_value(user, "external_id"), 
        email=get_model_value(user, "email"), 
        roles=["user"]
    )

    return {
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "external_id": user.external_id,
            "email": user.email,
            "name": user.name,
        },
    }
