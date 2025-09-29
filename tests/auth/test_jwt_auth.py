"""Unit tests for JWT authentication functionality"""

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest

from api.auth.exceptions import (
    AuthenticationError,
    TokenExpiredError,
    TokenInvalidError,
    TokenRevokedError,
)
from api.auth.jwt_auth import (
    JWTAuthenticator,
    JWTConfig,
    TokenBlacklist,
    create_access_token,
    create_refresh_token,
    get_token_payload,
    is_token_expired,
    revoke_token,
    verify_token,
)


class TestJWTConfig:
    """Test JWT configuration"""

    def test_get_secret_key_development(self):
        """Test secret key retrieval in development"""
        with patch("api.auth.jwt_auth.settings") as mock_settings:
            mock_settings.jwt_secret_key = "dev-test-key"
            mock_settings.environment = "development"

            secret = JWTConfig.get_secret_key()
            assert secret == "dev-test-key"

    def test_get_secret_key_production_error(self):
        """Test secret key validation in production"""
        with patch("api.auth.jwt_auth.settings") as mock_settings:
            mock_settings.jwt_secret_key = "dev-test-key"
            mock_settings.environment = "production"

            with pytest.raises(ValueError, match="JWT secret key must be set in production"):
                JWTConfig.get_secret_key()

    def test_should_use_rs256(self):
        """Test RS256 algorithm detection"""
        with patch("api.auth.jwt_auth.settings") as mock_settings:
            mock_settings.jwt_algorithm = "RS256"
            mock_settings.jwt_private_key = "private-key"
            mock_settings.jwt_public_key = "public-key"

            assert JWTConfig.should_use_rs256() is True

            mock_settings.jwt_algorithm = "HS256"
            assert JWTConfig.should_use_rs256() is False


class TestTokenGeneration:
    """Test JWT token generation"""

    @pytest.fixture
    def mock_settings(self):
        """Mock settings for testing"""
        with patch("api.auth.jwt_auth.settings") as mock:
            mock.jwt_secret_key = "test-secret-key-for-unit-tests"
            mock.jwt_algorithm = "HS256"
            mock.jwt_access_token_expire_minutes = 15
            mock.jwt_refresh_token_expire_days = 30
            mock.jwt_issuer = "test-issuer"
            mock.jwt_audience = "test-audience"
            mock.environment = "testing"
            yield mock

    def test_create_access_token(self, mock_settings):
        """Test access token creation"""
        token = create_access_token(
            user_id=1, external_id="test_user", email="test@example.com", roles=["user"]
        )

        assert isinstance(token, str)
        assert len(token) > 0

        # Verify token structure
        payload = verify_token(token)
        assert payload["sub"] == "1"
        assert payload["external_id"] == "test_user"
        assert payload["email"] == "test@example.com"
        assert payload["roles"] == ["user"]
        assert payload["type"] == "access"
        assert "jti" in payload

    def test_create_refresh_token(self, mock_settings):
        """Test refresh token creation"""
        token = create_refresh_token(user_id=1, external_id="test_user", email="test@example.com")

        assert isinstance(token, str)
        assert len(token) > 0

        # Verify token structure
        payload = verify_token(token)
        assert payload["sub"] == "1"
        assert payload["external_id"] == "test_user"
        assert payload["email"] == "test@example.com"
        assert payload["type"] == "refresh"
        assert "roles" not in payload  # Refresh tokens don't include roles

    def test_create_token_with_custom_expiration(self, mock_settings):
        """Test token creation with custom expiration"""
        custom_expires = timedelta(minutes=30)
        token = create_access_token(
            user_id=1,
            external_id="test_user",
            email="test@example.com",
            expires_delta=custom_expires,
        )

        payload = verify_token(token)
        exp_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        iat_time = datetime.fromtimestamp(payload["iat"], tz=timezone.utc)

        # Should be approximately 30 minutes difference
        time_diff = exp_time - iat_time
        assert abs(time_diff.total_seconds() - 1800) < 60  # Within 1 minute tolerance


class TestTokenVerification:
    """Test JWT token verification"""

    @pytest.fixture
    def mock_settings(self):
        """Mock settings for testing"""
        with patch("api.auth.jwt_auth.settings") as mock:
            mock.jwt_secret_key = "test-secret-key-for-unit-tests"
            mock.jwt_algorithm = "HS256"
            mock.jwt_issuer = "test-issuer"
            mock.jwt_audience = "test-audience"
            mock.environment = "testing"
            yield mock

    @pytest.fixture
    def valid_token(self, mock_settings):
        """Create valid token for testing"""
        return create_access_token(
            user_id=1, external_id="test_user", email="test@example.com", roles=["user"]
        )

    def test_verify_valid_token(self, mock_settings, valid_token):
        """Test verification of valid token"""
        payload = verify_token(valid_token)

        assert payload["sub"] == "1"
        assert payload["email"] == "test@example.com"
        assert payload["type"] == "access"

    def test_verify_token_with_type_check(self, mock_settings, valid_token):
        """Test token verification with type checking"""
        # Should succeed for correct type
        payload = verify_token(valid_token, token_type="access")
        assert payload["type"] == "access"

        # Should fail for wrong type
        with pytest.raises(TokenInvalidError, match="Expected refresh token"):
            verify_token(valid_token, token_type="refresh")

    def test_verify_expired_token(self, mock_settings):
        """Test verification of expired token"""
        # Create token that expires immediately
        expired_token = create_access_token(
            user_id=1,
            external_id="test_user",
            email="test@example.com",
            expires_delta=timedelta(seconds=-1),  # Already expired
        )

        with pytest.raises(TokenExpiredError):
            verify_token(expired_token)

    def test_verify_invalid_token(self, mock_settings):
        """Test verification of malformed token"""
        with pytest.raises(TokenInvalidError):
            verify_token("invalid.token.here")

    def test_verify_token_wrong_secret(self, mock_settings):
        """Test verification with wrong secret key"""
        token = create_access_token(1, "test_user", "test@example.com")

        # Change secret key
        mock_settings.jwt_secret_key = "different-secret-key"

        with pytest.raises(TokenInvalidError):
            verify_token(token)


class TestTokenRevocation:
    """Test token revocation and blacklisting"""

    @pytest.fixture
    def mock_settings(self):
        """Mock settings for testing"""
        with patch("api.auth.jwt_auth.settings") as mock:
            mock.jwt_secret_key = "test-secret-key-for-unit-tests"
            mock.jwt_algorithm = "HS256"
            mock.jwt_issuer = "test-issuer"
            mock.jwt_audience = "test-audience"
            mock.environment = "testing"
            yield mock

    def test_token_blacklist_operations(self):
        """Test token blacklist add/check operations"""
        # Clear blacklist
        TokenBlacklist._blacklisted_tokens = set()
        TokenBlacklist._blacklisted_users = set()

        # Test adding token
        TokenBlacklist.add_token("test-jti-123")
        assert TokenBlacklist.is_token_revoked("test-jti-123", 1) is True
        assert TokenBlacklist.is_token_revoked("other-jti", 1) is False

        # Test adding user tokens
        TokenBlacklist.add_user_tokens(2)
        assert TokenBlacklist.is_token_revoked("any-jti", 2) is True
        assert TokenBlacklist.is_token_revoked("any-jti", 3) is False

    def test_revoke_token(self, mock_settings):
        """Test token revocation"""
        # Clear blacklist
        TokenBlacklist._blacklisted_tokens = set()

        token = create_access_token(1, "test_user", "test@example.com")

        # Token should be valid initially
        payload = verify_token(token)
        assert payload["sub"] == "1"

        # Revoke token
        revoke_token(token)

        # Token should now be revoked
        with pytest.raises(TokenRevokedError):
            verify_token(token)

    def test_revoke_expired_token(self, mock_settings):
        """Test revoking already expired token"""
        expired_token = create_access_token(
            user_id=1,
            external_id="test_user",
            email="test@example.com",
            expires_delta=timedelta(seconds=-1),
        )

        # Should not raise exception when revoking expired token
        revoke_token(expired_token)


class TestTokenPayload:
    """Test token payload extraction"""

    @pytest.fixture
    def mock_settings(self):
        """Mock settings for testing"""
        with patch("api.auth.jwt_auth.settings") as mock:
            mock.jwt_secret_key = "test-secret-key-for-unit-tests"
            mock.jwt_algorithm = "HS256"
            mock.jwt_issuer = "test-issuer"
            mock.jwt_audience = "test-audience"
            mock.environment = "testing"
            yield mock

    def test_get_token_payload(self, mock_settings):
        """Test extracting token payload"""
        token = create_access_token(
            user_id=123,
            external_id="test_user_123",
            email="test@example.com",
            roles=["user", "premium"],
        )

        payload = get_token_payload(token)

        assert payload.user_id == 123
        assert payload.external_id == "test_user_123"
        assert payload.email == "test@example.com"
        assert payload.roles == ["user", "premium"]
        assert payload.token_type == "access"
        assert isinstance(payload.issued_at, datetime)
        assert isinstance(payload.expires_at, datetime)
        assert len(payload.jti) > 0


class TestJWTAuthenticator:
    """Test JWTAuthenticator class"""

    @pytest.fixture
    def mock_settings(self):
        """Mock settings for testing"""
        with patch("api.auth.jwt_auth.settings") as mock:
            mock.jwt_secret_key = "test-secret-key-for-unit-tests"
            mock.jwt_algorithm = "HS256"
            mock.jwt_access_token_expire_minutes = 15
            mock.jwt_refresh_token_expire_days = 30
            mock.jwt_issuer = "test-issuer"
            mock.jwt_audience = "test-audience"
            mock.environment = "testing"
            yield mock

    def test_create_user_tokens(self, mock_settings):
        """Test creating token pair for user"""
        authenticator = JWTAuthenticator()

        tokens = authenticator.create_user_tokens(
            user_id=1, external_id="test_user", email="test@example.com", roles=["user"]
        )

        assert "access_token" in tokens
        assert "refresh_token" in tokens
        assert "token_type" in tokens
        assert tokens["token_type"] == "bearer"

        # Verify both tokens are valid
        access_payload = verify_token(tokens["access_token"], "access")
        refresh_payload = verify_token(tokens["refresh_token"], "refresh")

        assert access_payload["sub"] == refresh_payload["sub"]
        assert access_payload["email"] == refresh_payload["email"]

    def test_refresh_access_token(self, mock_settings):
        """Test refreshing access token"""
        authenticator = JWTAuthenticator()

        # Create initial tokens
        tokens = authenticator.create_user_tokens(1, "test_user", "test@example.com")

        # Refresh access token
        new_access_token = authenticator.refresh_access_token(tokens["refresh_token"])

        # Verify new token is valid and different
        assert new_access_token != tokens["access_token"]

        new_payload = verify_token(new_access_token, "access")
        assert new_payload["sub"] == "1"
        assert new_payload["email"] == "test@example.com"

    def test_logout_user(self, mock_settings):
        """Test user logout functionality"""
        # Clear blacklist
        TokenBlacklist._blacklisted_tokens = set()

        authenticator = JWTAuthenticator()
        tokens = authenticator.create_user_tokens(1, "test_user", "test@example.com")

        # Tokens should be valid initially
        verify_token(tokens["access_token"])
        verify_token(tokens["refresh_token"])

        # Logout user
        authenticator.logout_user(tokens["access_token"], tokens["refresh_token"])

        # Tokens should be revoked
        with pytest.raises(TokenRevokedError):
            verify_token(tokens["access_token"])
        with pytest.raises(TokenRevokedError):
            verify_token(tokens["refresh_token"])


class TestTokenUtilities:
    """Test token utility functions"""

    @pytest.fixture
    def mock_settings(self):
        """Mock settings for testing"""
        with patch("api.auth.jwt_auth.settings") as mock:
            mock.jwt_secret_key = "test-secret-key-for-unit-tests"
            mock.jwt_algorithm = "HS256"
            mock.jwt_issuer = "test-issuer"
            mock.jwt_audience = "test-audience"
            mock.environment = "testing"
            yield mock

    def test_is_token_expired_valid(self, mock_settings):
        """Test expired check for valid token"""
        token = create_access_token(1, "test_user", "test@example.com")
        assert is_token_expired(token) is False

    def test_is_token_expired_expired(self, mock_settings):
        """Test expired check for expired token"""
        expired_token = create_access_token(
            user_id=1,
            external_id="test_user",
            email="test@example.com",
            expires_delta=timedelta(seconds=-1),
        )
        assert is_token_expired(expired_token) is True

    def test_is_token_expired_invalid(self, mock_settings):
        """Test expired check for invalid token"""
        assert is_token_expired("invalid.token.here") is True


class TestPasswordResetTokens:
    """Test password reset token functionality"""

    @pytest.fixture
    def mock_settings(self):
        """Mock settings for testing"""
        with patch("api.auth.jwt_auth.settings") as mock:
            mock.jwt_secret_key = "test-secret-key-for-unit-tests"
            mock.jwt_algorithm = "HS256"
            mock.jwt_issuer = "test-issuer"
            mock.jwt_audience = "test-audience"
            mock.environment = "testing"
            yield mock

    def test_generate_password_reset_token(self, mock_settings):
        """Test password reset token generation"""
        from api.auth.jwt_auth import generate_password_reset_token

        token = generate_password_reset_token(1, "test@example.com")

        assert isinstance(token, str)
        assert len(token) > 0

        # Verify token structure
        payload = verify_token(token, "password_reset")
        assert payload["sub"] == "1"
        assert payload["email"] == "test@example.com"
        assert payload["type"] == "password_reset"

    def test_verify_password_reset_token(self, mock_settings):
        """Test password reset token verification"""
        from api.auth.jwt_auth import generate_password_reset_token, verify_password_reset_token

        token = generate_password_reset_token(1, "test@example.com")
        payload = verify_password_reset_token(token)

        assert payload["sub"] == "1"
        assert payload["email"] == "test@example.com"
        assert payload["type"] == "password_reset"


class TestErrorHandling:
    """Test error handling in JWT operations"""

    def test_create_token_invalid_input(self):
        """Test token creation with invalid input"""
        with pytest.raises(AuthenticationError):
            create_access_token(user_id=0, external_id="", email="invalid-email")  # Invalid user ID

    def test_verify_token_missing_claims(self):
        """Test verification of token with missing claims"""
        with patch("api.auth.jwt_auth.jwt.decode") as mock_decode:
            mock_decode.return_value = {"sub": "1"}  # Missing required claims

            with pytest.raises(TokenInvalidError):
                verify_token("fake-token")

    def test_verify_token_invalid_user_id(self):
        """Test verification with invalid user ID format"""
        with patch("api.auth.jwt_auth.jwt.decode") as mock_decode:
            mock_decode.return_value = {
                "sub": "invalid-user-id",  # Non-numeric user ID
                "email": "test@example.com",
                "exp": int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp()),
                "iat": int(datetime.now(timezone.utc).timestamp()),
                "jti": "test-jti",
                "iss": "test-issuer",
                "aud": "test-audience",
            }

            with pytest.raises(TokenInvalidError):
                verify_token("fake-token")


class TestTokenBlacklist:
    """Test token blacklist functionality"""

    def setUp(self):
        """Clear blacklist before each test"""
        TokenBlacklist._blacklisted_tokens = set()
        TokenBlacklist._blacklisted_users = set()

    def test_blacklist_token(self):
        """Test adding token to blacklist"""
        self.setUp()

        jti = "test-jti-123"
        user_id = 1

        # Token should not be revoked initially
        assert TokenBlacklist.is_token_revoked(jti, user_id) is False

        # Add to blacklist
        TokenBlacklist.add_token(jti)

        # Token should now be revoked
        assert TokenBlacklist.is_token_revoked(jti, user_id) is True

    def test_blacklist_user_tokens(self):
        """Test blacklisting all tokens for a user"""
        self.setUp()

        user_id = 1

        # User tokens should not be revoked initially
        assert TokenBlacklist.is_token_revoked("any-jti", user_id) is False

        # Blacklist all user tokens
        TokenBlacklist.add_user_tokens(user_id)

        # All tokens for user should now be revoked
        assert TokenBlacklist.is_token_revoked("any-jti", user_id) is True
        assert TokenBlacklist.is_token_revoked("other-jti", user_id) is True

        # Other users should not be affected
        assert TokenBlacklist.is_token_revoked("any-jti", 2) is False

    def test_remove_user_from_blacklist(self):
        """Test removing user from blacklist"""
        self.setUp()

        user_id = 1

        # Blacklist user
        TokenBlacklist.add_user_tokens(user_id)
        assert TokenBlacklist.is_token_revoked("test-jti", user_id) is True

        # Remove from blacklist
        TokenBlacklist.remove_user_from_blacklist(user_id)
        assert TokenBlacklist.is_token_revoked("test-jti", user_id) is False
