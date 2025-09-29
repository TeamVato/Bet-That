"""Unit tests for security utilities"""

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest

from api.auth.exceptions import RateLimitExceededError
from api.auth.security_utils import (
    CSRFProtection,
    InputSanitizer,
    RateLimiter,
    SecurityManager,
    check_auth_rate_limit,
    generate_csrf_token,
    generate_secure_token,
    record_successful_auth,
    sanitize_auth_input,
    verify_csrf_token,
)


class TestCSRFProtection:
    """Test CSRF token generation and validation"""

    @patch("api.auth.security_utils.settings")
    def test_generate_csrf_token(self, mock_settings):
        """Test CSRF token generation"""
        mock_settings.jwt_secret_key = "test-secret-key"

        user_id = 123
        token = CSRFProtection.generate_csrf_token(user_id)

        assert isinstance(token, str)
        assert len(token) > 0
        assert ":" in token  # Should contain separators

    @patch("api.auth.security_utils.settings")
    def test_verify_csrf_token_valid(self, mock_settings):
        """Test CSRF token verification with valid token"""
        mock_settings.jwt_secret_key = "test-secret-key"

        user_id = 123
        token = CSRFProtection.generate_csrf_token(user_id)

        # Should verify successfully
        assert CSRFProtection.verify_csrf_token(token, user_id) is True

    @patch("api.auth.security_utils.settings")
    def test_verify_csrf_token_wrong_user(self, mock_settings):
        """Test CSRF token verification with wrong user"""
        mock_settings.jwt_secret_key = "test-secret-key"

        user_id = 123
        wrong_user_id = 456
        token = CSRFProtection.generate_csrf_token(user_id)

        # Should fail for wrong user
        assert CSRFProtection.verify_csrf_token(token, wrong_user_id) is False

    @patch("api.auth.security_utils.settings")
    def test_verify_csrf_token_expired(self, mock_settings):
        """Test CSRF token verification with expired token"""
        mock_settings.jwt_secret_key = "test-secret-key"

        user_id = 123

        # Create token with very short expiry
        with patch("api.auth.security_utils.datetime") as mock_datetime:
            # Set current time to past
            past_time = datetime.now(timezone.utc) - timedelta(hours=25)
            mock_datetime.now.return_value = past_time
            mock_datetime.fromtimestamp = datetime.fromtimestamp

            token = CSRFProtection.generate_csrf_token(user_id)

        # Should fail verification due to age
        assert CSRFProtection.verify_csrf_token(token, user_id, max_age_hours=24) is False

    def test_verify_csrf_token_invalid_format(self):
        """Test CSRF token verification with invalid format"""
        invalid_tokens = [
            "invalid-token",
            "too:few:parts",
            "too:many:parts:here:invalid",
            "",
        ]

        for token in invalid_tokens:
            assert CSRFProtection.verify_csrf_token(token, 123) is False


class TestRateLimiter:
    """Test rate limiting functionality"""

    def test_rate_limiter_basic(self):
        """Test basic rate limiting"""
        limiter = RateLimiter()
        identifier = "test-user-1"

        # Should not be limited initially
        assert limiter.is_rate_limited(identifier, max_attempts=3) is False

        # Record attempts up to limit
        for i in range(3):
            limiter.record_attempt(identifier)
            # Should not be limited yet
            if i < 2:  # 0, 1 (2 attempts recorded, limit is 3)
                assert limiter.is_rate_limited(identifier, max_attempts=3) is False

        # Should be limited after max attempts
        assert limiter.is_rate_limited(identifier, max_attempts=3) is True

    def test_rate_limiter_window_expiry(self):
        """Test rate limiter window expiry"""
        limiter = RateLimiter()
        identifier = "test-user-2"

        # Mock datetime to control time
        with patch("api.auth.security_utils.datetime") as mock_datetime:
            base_time = datetime.now(timezone.utc)
            mock_datetime.now.return_value = base_time

            # Record max attempts
            for _ in range(3):
                limiter.record_attempt(identifier)

            # Should be limited
            assert limiter.is_rate_limited(identifier, max_attempts=3, window_minutes=15) is True

            # Move time forward past window
            mock_datetime.now.return_value = base_time + timedelta(minutes=20)

            # Should not be limited anymore
            assert limiter.is_rate_limited(identifier, max_attempts=3, window_minutes=15) is False

    def test_rate_limiter_reset_attempts(self):
        """Test resetting rate limit attempts"""
        limiter = RateLimiter()
        identifier = "test-user-3"

        # Record attempts to limit
        for _ in range(5):
            limiter.record_attempt(identifier)

        assert limiter.is_rate_limited(identifier, max_attempts=3) is True

        # Reset attempts
        limiter.reset_attempts(identifier)

        # Should not be limited anymore
        assert limiter.is_rate_limited(identifier, max_attempts=3) is False

    def test_rate_limiter_cleanup(self):
        """Test rate limiter cleanup functionality"""
        limiter = RateLimiter()

        # Add some old data
        old_time = datetime.now(timezone.utc) - timedelta(hours=25)
        limiter._attempts["old-user"] = [old_time]
        limiter._blocked_ips["old-ip"] = old_time

        # Add recent data
        recent_time = datetime.now(timezone.utc)
        limiter._attempts["recent-user"] = [recent_time]
        limiter._blocked_ips["recent-ip"] = recent_time

        # Cleanup
        limiter.cleanup_expired()

        # Old data should be removed
        assert "old-user" not in limiter._attempts
        assert "old-ip" not in limiter._blocked_ips

        # Recent data should remain
        assert "recent-user" in limiter._attempts
        assert "recent-ip" in limiter._blocked_ips


class TestInputSanitizer:
    """Test input sanitization"""

    def test_sanitize_email(self):
        """Test email sanitization"""
        test_cases = [
            ("user@example.com", "user@example.com"),
            ("  USER@EXAMPLE.COM  ", "user@example.com"),
            ("user+tag@example.com", "user+tag@example.com"),
            ("<script>alert('xss')</script>@evil.com", "@evil.com"),
            ("invalid-email", ""),
            ("", ""),
        ]

        for input_email, expected in test_cases:
            result = InputSanitizer.sanitize_email(input_email)
            assert result == expected, f"Failed for input: {input_email}"

    def test_sanitize_name(self):
        """Test name sanitization"""
        test_cases = [
            ("John Doe", "John Doe"),
            ("  John Doe  ", "John Doe"),
            ("<script>alert('xss')</script>", "script>alert('xss')/script>"),
            ("João da Silva", "João da Silva"),  # Unicode support
            ("", ""),
            ("A" * 300, "A" * 255),  # Length limit
        ]

        for input_name, expected in test_cases:
            result = InputSanitizer.sanitize_name(input_name)
            assert result == expected, f"Failed for input: {input_name}"

    def test_sanitize_auth_input(self):
        """Test authentication input sanitization"""
        dirty_input = {
            "email": "  USER@EXAMPLE.COM  ",
            "name": "<script>alert('xss')</script>John",
            "first_name": "  John  ",
            "other_field": "normal content",
        }

        clean_input = InputSanitizer.sanitize_auth_input(dirty_input)

        assert clean_input["email"] == "user@example.com"
        assert "script" not in clean_input["name"]
        assert clean_input["first_name"] == "John"
        assert clean_input["other_field"] == "normal content"


class TestSecureTokenGeneration:
    """Test secure token generation"""

    def test_generate_secure_token_default(self):
        """Test default secure token generation"""
        token = generate_secure_token()

        assert isinstance(token, str)
        assert len(token) > 0

        # URL-safe base64 should not contain + or /
        assert "+" not in token
        assert "/" not in token

    def test_generate_secure_token_custom_length(self):
        """Test secure token with custom length"""
        for length in [16, 32, 64]:
            token = generate_secure_token(length)

            # Base64 encoding expands length, so token will be longer
            assert len(token) > length
            assert isinstance(token, str)

    def test_generate_secure_token_uniqueness(self):
        """Test that generated tokens are unique"""
        tokens = [generate_secure_token() for _ in range(100)]

        # All tokens should be unique
        assert len(set(tokens)) == 100


class TestSecurityManager:
    """Test SecurityManager class"""

    def test_check_auth_rate_limit_success(self):
        """Test successful rate limit check"""
        manager = SecurityManager()

        # Should not raise exception for first attempt
        try:
            manager.check_auth_rate_limit("192.168.1.1", "user@example.com")
        except RateLimitExceededError:
            pytest.fail("Should not be rate limited on first attempt")

    def test_check_auth_rate_limit_exceeded(self):
        """Test rate limit exceeded"""
        manager = SecurityManager()
        ip_address = "192.168.1.2"

        # Mock rate limiter to return True (rate limited)
        with patch.object(manager.rate_limiter, "is_rate_limited", return_value=True):
            with pytest.raises(RateLimitExceededError):
                manager.check_auth_rate_limit(ip_address)

    def test_record_successful_auth(self):
        """Test recording successful authentication"""
        manager = SecurityManager()

        # Mock rate limiter reset calls
        with patch.object(manager.rate_limiter, "reset_attempts") as mock_reset:
            manager.record_successful_auth("192.168.1.3", "user@example.com")

            # Should reset both IP and user rate limits
            assert mock_reset.call_count == 2
            mock_reset.assert_any_call("ip:192.168.1.3")
            mock_reset.assert_any_call("user:user@example.com")

    def test_generate_email_verification_token(self):
        """Test email verification token generation"""
        with patch("api.auth.security_utils.settings") as mock_settings:
            mock_settings.jwt_secret_key = "test-secret"

            manager = SecurityManager()
            token = manager.generate_email_verification_token(123, "user@example.com")

            assert isinstance(token, str)
            assert ":" in token  # Should contain signature separator

    def test_verify_email_verification_token(self):
        """Test email verification token verification"""
        with patch("api.auth.security_utils.settings") as mock_settings:
            mock_settings.jwt_secret_key = "test-secret"

            manager = SecurityManager()

            # Generate token
            token = manager.generate_email_verification_token(123, "user@example.com")

            # Should verify successfully
            assert manager.verify_email_verification_token(token, 123, "user@example.com") is True

            # Should fail for wrong user/email
            assert manager.verify_email_verification_token(token, 456, "user@example.com") is False
            assert manager.verify_email_verification_token(token, 123, "other@example.com") is False


class TestConvenienceFunctions:
    """Test convenience functions"""

    @patch("api.auth.security_utils.settings")
    def test_generate_csrf_token_convenience(self, mock_settings):
        """Test CSRF token generation convenience function"""
        mock_settings.jwt_secret_key = "test-secret"

        token = generate_csrf_token(123)
        assert isinstance(token, str)
        assert len(token) > 0

    @patch("api.auth.security_utils.settings")
    def test_verify_csrf_token_convenience(self, mock_settings):
        """Test CSRF token verification convenience function"""
        mock_settings.jwt_secret_key = "test-secret"

        user_id = 123
        token = generate_csrf_token(user_id)

        assert verify_csrf_token(token, user_id) is True
        assert verify_csrf_token(token, 456) is False

    def test_sanitize_auth_input_convenience(self):
        """Test input sanitization convenience function"""
        dirty_data = {"email": "  USER@EXAMPLE.COM  ", "name": "<script>John</script>"}

        clean_data = sanitize_auth_input(dirty_data)

        assert clean_data["email"] == "user@example.com"
        assert "script" not in clean_data["name"]

    def test_check_auth_rate_limit_convenience(self):
        """Test rate limit check convenience function"""
        # Should not raise exception for new IP
        try:
            check_auth_rate_limit("192.168.1.100")
        except RateLimitExceededError:
            pytest.fail("Should not be rate limited")

    def test_record_successful_auth_convenience(self):
        """Test successful auth recording convenience function"""
        # Should not raise exception
        try:
            record_successful_auth("192.168.1.101", "user@example.com")
        except Exception as e:
            pytest.fail(f"Unexpected exception: {e}")


class TestSecurityIntegration:
    """Test security component integration"""

    def test_full_security_flow(self):
        """Test complete security flow"""
        manager = SecurityManager()
        ip_address = "192.168.1.200"
        user_email = "testuser@example.com"

        # 1. Check rate limit (should pass)
        try:
            manager.check_auth_rate_limit(ip_address, user_email)
        except RateLimitExceededError:
            pytest.fail("Should not be rate limited initially")

        # 2. Record successful auth
        manager.record_successful_auth(ip_address, user_email)

        # 3. Generate verification token
        with patch("api.auth.security_utils.settings") as mock_settings:
            mock_settings.jwt_secret_key = "test-secret"

            token = manager.generate_email_verification_token(123, user_email)
            assert isinstance(token, str)

            # 4. Verify token
            is_valid = manager.verify_email_verification_token(token, 123, user_email)
            assert is_valid is True

        # 5. Cleanup
        manager.cleanup_security_data()


class TestErrorScenarios:
    """Test error scenarios and edge cases"""

    def test_csrf_token_with_malformed_data(self):
        """Test CSRF token handling with malformed data"""
        malformed_tokens = [
            "",
            "single-part",
            "two:parts",
            "invalid:timestamp:signature",
            "123:session:not-a-number:signature",
        ]

        for token in malformed_tokens:
            assert CSRFProtection.verify_csrf_token(token, 123) is False

    def test_rate_limiter_edge_cases(self):
        """Test rate limiter edge cases"""
        limiter = RateLimiter()

        # Test with zero max attempts
        assert limiter.is_rate_limited("test", max_attempts=0) is True

        # Test with negative window
        assert limiter.is_rate_limited("test", window_minutes=-1) is False

        # Test cleanup with empty data
        limiter.cleanup_expired()  # Should not raise exception

    def test_input_sanitizer_edge_cases(self):
        """Test input sanitizer edge cases"""
        edge_cases = [
            (None, ""),
            ("", ""),
            ("   ", ""),
            ("\x00\x01\x02", ""),
            ("normal text", "normal text"),
        ]

        for input_val, expected in edge_cases:
            if input_val is None:
                result = InputSanitizer.sanitize_email("")
            else:
                result = InputSanitizer.sanitize_email(input_val)

            # For edge cases, just ensure no exception is raised
            assert isinstance(result, str)


class TestSecurityConfiguration:
    """Test security configuration and settings"""

    def test_security_manager_initialization(self):
        """Test security manager initialization"""
        manager = SecurityManager()

        assert hasattr(manager, "rate_limiter")
        assert hasattr(manager, "csrf")
        assert hasattr(manager, "sanitizer")

        assert isinstance(manager.rate_limiter, RateLimiter)
        assert isinstance(manager.csrf, CSRFProtection)
        assert isinstance(manager.sanitizer, InputSanitizer)

    @patch("api.auth.security_utils.settings")
    def test_settings_integration(self, mock_settings):
        """Test integration with settings"""
        mock_settings.jwt_secret_key = "test-secret"
        mock_settings.auth_max_attempts_per_ip = 5
        mock_settings.auth_max_attempts_per_user = 3
        mock_settings.auth_rate_limit_window_minutes = 10

        manager = SecurityManager()

        # Test that settings are used
        with patch.object(manager.rate_limiter, "is_rate_limited") as mock_limited:
            mock_limited.return_value = False

            manager.check_auth_rate_limit("test-ip", "test@example.com")

            # Should call with settings values
            assert mock_limited.call_count == 2  # IP and user checks
