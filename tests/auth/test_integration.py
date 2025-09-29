"""Integration tests for JWT authentication system

Tests the complete authentication flow including database operations,
API endpoints, and security features working together.
"""

import asyncio
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from api.auth.exceptions import RateLimitExceededError
from api.auth.jwt_auth import JWTAuthenticator
from api.auth.password_manager import PasswordManager, hash_password
from api.auth.security_utils import SecurityManager
from api.database import Base, get_db
from api.main import app
from api.models import AuthLog, JWTTokenBlacklist, User, UserStatus

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_auth.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def test_db():
    """Create test database"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def test_user_data():
    """Test user data"""
    return {
        "email": "testuser@example.com",
        "password": "TestPassword123!",
        "name": "Test User",
        "first_name": "Test",
        "last_name": "User",
    }


@pytest.fixture
def db_session():
    """Create database session for tests"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


class TestUserRegistration:
    """Test user registration flow"""

    @patch("api.auth.endpoints.security_manager")
    def test_register_user_success(self, mock_security, client, test_db, test_user_data):
        """Test successful user registration"""
        mock_security.check_auth_rate_limit.return_value = None

        response = client.post("/auth/register", json=test_user_data)

        assert response.status_code == 200
        data = response.json()

        assert data["email"] == test_user_data["email"]
        assert data["name"] == test_user_data["name"]
        assert "id" in data
        assert "message" in data

    def test_register_user_duplicate_email(self, client, test_db, test_user_data, db_session):
        """Test registration with duplicate email"""
        # Create existing user
        existing_user = User(
            email=test_user_data["email"],
            external_id="existing_user",
            password_hash=hash_password("password123"),
        )
        db_session.add(existing_user)
        db_session.commit()

        response = client.post("/auth/register", json=test_user_data)

        assert response.status_code == 409
        assert "already exists" in response.json()["detail"]

    def test_register_user_weak_password(self, client, test_db, test_user_data):
        """Test registration with weak password"""
        weak_data = test_user_data.copy()
        weak_data["password"] = "123"

        response = client.post("/auth/register", json=weak_data)

        assert response.status_code == 400
        assert "password" in response.json()["detail"].lower()


class TestUserLogin:
    """Test user login flow"""

    @pytest.fixture
    def registered_user(self, db_session, test_user_data):
        """Create registered user for login tests"""
        user = User(
            email=test_user_data["email"],
            external_id="test_user_login",
            password_hash=hash_password(test_user_data["password"]),
            name=test_user_data["name"],
            status=UserStatus.ACTIVE,
            is_active=True,
            email_verified=True,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    @patch("api.auth.endpoints.security_manager")
    def test_login_success(self, mock_security, client, test_db, registered_user, test_user_data):
        """Test successful login"""
        mock_security.check_auth_rate_limit.return_value = None
        mock_security.record_successful_auth.return_value = None

        login_data = {"username": test_user_data["email"], "password": test_user_data["password"]}

        response = client.post("/auth/login", data=login_data)

        assert response.status_code == 200
        data = response.json()

        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
        assert "user" in data
        assert data["user"]["email"] == test_user_data["email"]

    def test_login_invalid_credentials(self, client, test_db, registered_user):
        """Test login with invalid credentials"""
        login_data = {"username": "testuser@example.com", "password": "WrongPassword123!"}

        response = client.post("/auth/login", data=login_data)

        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]

    def test_login_nonexistent_user(self, client, test_db):
        """Test login with nonexistent user"""
        login_data = {"username": "nonexistent@example.com", "password": "SomePassword123!"}

        response = client.post("/auth/login", data=login_data)

        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]

    def test_login_inactive_user(self, client, test_db, db_session, test_user_data):
        """Test login with inactive user"""
        # Create inactive user
        user = User(
            email=test_user_data["email"],
            external_id="inactive_user",
            password_hash=hash_password(test_user_data["password"]),
            status=UserStatus.SUSPENDED,
            is_active=False,
        )
        db_session.add(user)
        db_session.commit()

        login_data = {"username": test_user_data["email"], "password": test_user_data["password"]}

        response = client.post("/auth/login", data=login_data)

        assert response.status_code == 401
        assert "inactive" in response.json()["detail"].lower()


class TestTokenRefresh:
    """Test token refresh functionality"""

    @pytest.fixture
    def logged_in_user_tokens(self, client, test_db, registered_user, test_user_data):
        """Get tokens from logged in user"""
        with patch("api.auth.endpoints.security_manager") as mock_security:
            mock_security.check_auth_rate_limit.return_value = None
            mock_security.record_successful_auth.return_value = None

            login_data = {
                "username": test_user_data["email"],
                "password": test_user_data["password"],
            }

            response = client.post("/auth/login", data=login_data)
            return response.json()

    def test_refresh_token_success(self, client, test_db, logged_in_user_tokens):
        """Test successful token refresh"""
        refresh_data = {
            "refresh_token": logged_in_user_tokens["refresh_token"],
            "rotate_refresh_token": False,
        }

        response = client.post("/auth/refresh", json=refresh_data)

        assert response.status_code == 200
        data = response.json()

        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["access_token"] != logged_in_user_tokens["access_token"]

    def test_refresh_token_with_rotation(self, client, test_db, logged_in_user_tokens):
        """Test token refresh with rotation"""
        refresh_data = {
            "refresh_token": logged_in_user_tokens["refresh_token"],
            "rotate_refresh_token": True,
        }

        response = client.post("/auth/refresh", json=refresh_data)

        assert response.status_code == 200
        data = response.json()

        # Both tokens should be different
        assert data["access_token"] != logged_in_user_tokens["access_token"]
        assert data["refresh_token"] != logged_in_user_tokens["refresh_token"]

    def test_refresh_invalid_token(self, client, test_db):
        """Test refresh with invalid token"""
        refresh_data = {"refresh_token": "invalid.jwt.token", "rotate_refresh_token": False}

        response = client.post("/auth/refresh", json=refresh_data)

        assert response.status_code == 401
        assert "Invalid refresh token" in response.json()["detail"]


class TestProtectedEndpoints:
    """Test protected endpoint access"""

    @pytest.fixture
    def auth_headers(self, logged_in_user_tokens):
        """Create authorization headers"""
        return {"Authorization": f"Bearer {logged_in_user_tokens['access_token']}"}

    def test_protected_endpoint_with_valid_token(self, client, test_db, auth_headers):
        """Test accessing protected endpoint with valid token"""
        response = client.get("/auth/me", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert "id" in data
        assert "email" in data
        assert "status" in data

    def test_protected_endpoint_without_token(self, client, test_db):
        """Test accessing protected endpoint without token"""
        response = client.get("/auth/me")

        assert response.status_code == 401
        assert "Authorization header missing" in response.json()["detail"]

    def test_protected_endpoint_with_invalid_token(self, client, test_db):
        """Test accessing protected endpoint with invalid token"""
        headers = {"Authorization": "Bearer invalid.jwt.token"}

        response = client.get("/auth/me", headers=headers)

        assert response.status_code == 401


class TestPasswordOperations:
    """Test password change and reset operations"""

    def test_password_change_success(self, client, test_db, auth_headers, test_user_data):
        """Test successful password change"""
        change_data = {
            "current_password": test_user_data["password"],
            "new_password": "NewSecurePassword123!",
            "logout_other_sessions": False,
        }

        response = client.post("/auth/password/change", json=change_data, headers=auth_headers)

        assert response.status_code == 200
        assert "successful" in response.json()["message"]

    def test_password_change_wrong_current(self, client, test_db, auth_headers):
        """Test password change with wrong current password"""
        change_data = {
            "current_password": "WrongCurrentPassword",
            "new_password": "NewSecurePassword123!",
            "logout_other_sessions": False,
        }

        response = client.post("/auth/password/change", json=change_data, headers=auth_headers)

        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

    def test_password_reset_request(self, client, test_db, test_user_data):
        """Test password reset request"""
        reset_data = {"email": test_user_data["email"]}

        response = client.post("/auth/password/reset", json=reset_data)

        # Should always return success to prevent email enumeration
        assert response.status_code == 200
        assert "instructions" in response.json()["message"]


class TestLegacyCompatibility:
    """Test backward compatibility with legacy authentication"""

    def test_legacy_login(self, client, test_db, db_session):
        """Test legacy login endpoint"""
        legacy_data = {
            "external_id": "legacy_user_123",
            "email": "legacy@example.com",
            "name": "Legacy User",
        }

        response = client.post("/auth/legacy/login", json=legacy_data)

        assert response.status_code == 200
        data = response.json()

        assert "access_token" in data
        assert "refresh_token" in data
        assert data["user"]["external_id"] == legacy_data["external_id"]

    def test_dual_auth_support(self, client, test_db, registered_user):
        """Test that endpoints support both JWT and legacy auth"""
        # This would require testing existing endpoints with both auth methods
        # For now, just verify the dependency structure exists

        from api.deps import get_current_user, require_authentication

        assert callable(get_current_user)
        assert callable(require_authentication)


class TestSecurityLogging:
    """Test security event logging"""

    def test_auth_event_logging(self, db_session):
        """Test authentication event logging"""
        from api.auth.token_manager import AuthLogger

        logger = AuthLogger()

        # Log successful login
        logger.log_auth_event(
            db=db_session,
            event_type="login",
            ip_address="192.168.1.1",
            success=True,
            user_id=123,
            user_agent="TestAgent/1.0",
        )

        # Verify log entry
        log_entry = db_session.query(AuthLog).first()

        assert log_entry is not None
        assert log_entry.event_type == "login"
        assert log_entry.ip_address == "192.168.1.1"
        assert log_entry.success is True
        assert log_entry.user_id == 123

    def test_failed_login_logging(self, db_session):
        """Test failed login logging"""
        from api.auth.token_manager import AuthLogger

        logger = AuthLogger()

        # Log failed login
        logger.log_auth_event(
            db=db_session,
            event_type="login",
            ip_address="192.168.1.2",
            success=False,
            failure_reason="Invalid credentials",
        )

        # Verify log entry
        log_entry = db_session.query(AuthLog).first()

        assert log_entry is not None
        assert log_entry.success is False
        assert log_entry.failure_reason == "Invalid credentials"


class TestTokenBlacklisting:
    """Test database-backed token blacklisting"""

    def test_database_token_blacklist(self, db_session):
        """Test database token blacklisting"""
        from api.auth.token_manager import DatabaseTokenBlacklist

        blacklist = DatabaseTokenBlacklist()

        # Add token to blacklist
        jti = "test-jti-123"
        user_id = 456
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

        blacklist.add_token(
            db=db_session,
            jti=jti,
            user_id=user_id,
            token_type="access",
            expires_at=expires_at,
            reason="Test revocation",
        )

        # Verify token is blacklisted
        is_revoked = blacklist.is_token_revoked(db_session, jti, user_id)
        assert is_revoked is True

        # Check blacklist entry in database
        blacklist_entry = (
            db_session.query(JWTTokenBlacklist).filter(JWTTokenBlacklist.jti == jti).first()
        )

        assert blacklist_entry is not None
        assert blacklist_entry.user_id == user_id
        assert blacklist_entry.token_type == "access"
        assert blacklist_entry.reason == "Test revocation"


class TestCompleteAuthFlow:
    """Test complete authentication flow end-to-end"""

    @patch("api.auth.endpoints.security_manager")
    def test_complete_flow(self, mock_security, client, test_db, test_user_data):
        """Test complete authentication flow"""
        mock_security.check_auth_rate_limit.return_value = None
        mock_security.record_successful_auth.return_value = None

        # 1. Register user
        register_response = client.post("/auth/register", json=test_user_data)
        assert register_response.status_code == 200

        user_data = register_response.json()

        # 2. Login user
        login_data = {"username": test_user_data["email"], "password": test_user_data["password"]}

        login_response = client.post("/auth/login", data=login_data)
        assert login_response.status_code == 200

        tokens = login_response.json()

        # 3. Access protected resource
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}

        me_response = client.get("/auth/me", headers=headers)
        assert me_response.status_code == 200

        user_info = me_response.json()
        assert user_info["email"] == test_user_data["email"]

        # 4. Refresh token
        refresh_data = {"refresh_token": tokens["refresh_token"], "rotate_refresh_token": False}

        refresh_response = client.post("/auth/refresh", json=refresh_data)
        assert refresh_response.status_code == 200

        new_tokens = refresh_response.json()
        assert new_tokens["access_token"] != tokens["access_token"]

        # 5. Validate new token
        new_headers = {"Authorization": f"Bearer {new_tokens['access_token']}"}

        validate_response = client.post("/auth/tokens/validate", headers=new_headers)
        assert validate_response.status_code == 200

        validation_data = validate_response.json()
        assert validation_data["valid"] is True
        assert validation_data["email"] == test_user_data["email"]


class TestErrorScenarios:
    """Test various error scenarios"""

    def test_malformed_requests(self, client, test_db):
        """Test API behavior with malformed requests"""
        malformed_requests = [
            ("/auth/register", {}),  # Empty registration
            ("/auth/login", {"username": "test"}),  # Missing password
            ("/auth/refresh", {"invalid": "data"}),  # Invalid refresh data
        ]

        for endpoint, data in malformed_requests:
            if endpoint == "/auth/login":
                response = client.post(endpoint, data=data)
            else:
                response = client.post(endpoint, json=data)

            # Should return 4xx status code
            assert 400 <= response.status_code < 500

    def test_rate_limiting_integration(self, client, test_db):
        """Test rate limiting integration"""
        with patch("api.auth.endpoints.security_manager") as mock_security:
            mock_security.check_auth_rate_limit.side_effect = RateLimitExceededError()

            response = client.post(
                "/auth/register", json={"email": "test@example.com", "password": "Test123!"}
            )

            assert response.status_code == 429


@pytest.mark.asyncio
async def test_async_operations():
    """Test asynchronous authentication operations"""

    # Test async JWT operations
    authenticator = JWTAuthenticator()

    tokens = authenticator.create_user_tokens(
        user_id=999, external_id="async_user", email="async@example.com"
    )

    assert "access_token" in tokens
    assert "refresh_token" in tokens

    # Test async token verification
    from api.auth.jwt_auth import verify_token

    payload = verify_token(tokens["access_token"])
    assert payload["sub"] == "999"
    assert payload["email"] == "async@example.com"


if __name__ == "__main__":
    # Run integration tests
    pytest.main([__file__, "-v", "--tb=short"])
