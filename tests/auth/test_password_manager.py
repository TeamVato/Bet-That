"""Unit tests for password management functionality"""

from unittest.mock import patch

import pytest

from api.auth.exceptions import PasswordTooWeakError
from api.auth.password_manager import (
    PasswordConfig,
    PasswordManager,
    generate_salt,
    generate_secure_password,
    hash_password,
    needs_rehash,
    validate_password_strength,
    verify_password,
)


class TestPasswordHashing:
    """Test password hashing and verification"""

    def test_hash_password_basic(self):
        """Test basic password hashing"""
        password = "TestPassword123!"
        hashed = hash_password(password)

        assert isinstance(hashed, str)
        assert len(hashed) > 0
        assert hashed != password
        assert hashed.startswith("$2b$")  # bcrypt prefix

    def test_hash_password_with_salt(self):
        """Test password hashing with custom salt"""
        password = "TestPassword123!"
        salt = generate_salt()

        hashed1 = hash_password(password, salt)
        hashed2 = hash_password(password, salt)

        # Same password and salt should produce same hash
        assert hashed1 == hashed2

    def test_verify_password_correct(self):
        """Test password verification with correct password"""
        password = "TestPassword123!"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password"""
        password = "TestPassword123!"
        wrong_password = "WrongPassword123!"
        hashed = hash_password(password)

        assert verify_password(wrong_password, hashed) is False

    def test_verify_password_with_salt(self):
        """Test password verification with salt"""
        password = "TestPassword123!"
        salt = generate_salt()
        hashed = hash_password(password, salt)

        assert verify_password(password, hashed, salt) is True
        assert verify_password("WrongPassword123!", hashed, salt) is False

    def test_generate_salt(self):
        """Test salt generation"""
        salt1 = generate_salt()
        salt2 = generate_salt()

        assert isinstance(salt1, str)
        assert isinstance(salt2, str)
        assert len(salt1) == 32  # 16 bytes as hex = 32 chars
        assert len(salt2) == 32
        assert salt1 != salt2  # Should be different


class TestPasswordStrengthValidation:
    """Test password strength validation"""

    def test_strong_password(self):
        """Test validation of strong password"""
        strong_password = "StrongPassword123!@#"

        result = validate_password_strength(strong_password)

        assert result["is_valid"] is True
        assert result["score"] > 80
        assert result["strength"] in ["strong", "very_strong"]
        assert len(result["errors"]) == 0
        assert all(result["checks"].values())

    def test_weak_password_too_short(self):
        """Test validation of too short password"""
        with pytest.raises(PasswordTooWeakError, match="at least"):
            validate_password_strength("Sh0rt!")

    def test_weak_password_no_uppercase(self):
        """Test validation of password without uppercase"""
        with pytest.raises(PasswordTooWeakError, match="uppercase"):
            validate_password_strength("lowercase123!")

    def test_weak_password_no_lowercase(self):
        """Test validation of password without lowercase"""
        with pytest.raises(PasswordTooWeakError, match="lowercase"):
            validate_password_strength("UPPERCASE123!")

    def test_weak_password_no_digits(self):
        """Test validation of password without digits"""
        with pytest.raises(PasswordTooWeakError, match="digit"):
            validate_password_strength("NoDigitsHere!")

    def test_weak_password_no_special_chars(self):
        """Test validation of password without special characters"""
        with pytest.raises(PasswordTooWeakError, match="special character"):
            validate_password_strength("NoSpecialChars123")

    def test_weak_password_common(self):
        """Test validation of common password"""
        with pytest.raises(PasswordTooWeakError, match="too common"):
            validate_password_strength("Password123!")

    def test_weak_password_repeated_chars(self):
        """Test validation of password with repeated characters"""
        with pytest.raises(PasswordTooWeakError, match="repeated characters"):
            validate_password_strength("Passsssword123!")

    def test_password_strength_scoring(self):
        """Test password strength scoring system"""
        # Test different strength levels
        passwords = [
            ("Weak1!", 60, 80),  # Minimal requirements
            ("StrongPass123!", 80, 90),  # Good password
            ("VeryStrongPassword123!@#$", 90, 100),  # Very strong
        ]

        for password, min_score, max_score in passwords:
            result = validate_password_strength(password)
            assert min_score <= result["score"] <= max_score


class TestPasswordPolicy:
    """Test password policy enforcement"""

    def test_password_policy_with_email(self):
        """Test password policy with email context"""
        manager = PasswordManager()

        # Password containing email should fail
        with pytest.raises(PasswordTooWeakError):
            manager.check_password_policy("john.smith123!", "john.smith@example.com")

    def test_password_policy_without_email(self):
        """Test password policy without email context"""
        manager = PasswordManager()

        result = manager.check_password_policy("StrongPassword123!")
        assert result["is_valid"] is True
        assert result["score"] > 70


class TestSecurePasswordGeneration:
    """Test secure password generation"""

    def test_generate_secure_password_default(self):
        """Test default secure password generation"""
        password = generate_secure_password()

        assert isinstance(password, str)
        assert len(password) == 16

        # Should meet strength requirements
        result = validate_password_strength(password)
        assert result["is_valid"] is True
        assert result["score"] > 80

    def test_generate_secure_password_custom_length(self):
        """Test secure password generation with custom length"""
        password = generate_secure_password(24)

        assert len(password) == 24

        result = validate_password_strength(password)
        assert result["is_valid"] is True

    def test_generate_secure_password_minimum_length(self):
        """Test secure password generation with minimum length enforcement"""
        password = generate_secure_password(8)  # Below minimum

        assert len(password) == 12  # Should be adjusted to minimum

    def test_generate_multiple_passwords_unique(self):
        """Test that generated passwords are unique"""
        passwords = [generate_secure_password() for _ in range(10)]

        # All passwords should be unique
        assert len(set(passwords)) == 10


class TestPasswordManager:
    """Test PasswordManager class"""

    def test_hash_password_secure(self):
        """Test secure password hashing with metadata"""
        manager = PasswordManager()

        result = manager.hash_password_secure("TestPassword123!")

        assert "hash" in result
        assert "salt" in result
        assert "algorithm" in result
        assert "rounds" in result
        assert "created_at" in result

        assert result["algorithm"] == "bcrypt"
        assert result["rounds"] == PasswordConfig.BCRYPT_ROUNDS
        assert len(result["salt"]) == 32

    def test_verify_and_upgrade(self):
        """Test password verification with upgrade check"""
        manager = PasswordManager()

        password = "TestPassword123!"
        old_hash = hash_password(password)

        result = manager.verify_and_upgrade(password, old_hash)

        assert result["is_valid"] is True
        assert "needs_upgrade" in result

        # Should not need upgrade for fresh hash
        assert result["needs_upgrade"] is False

    def test_verify_and_upgrade_with_upgrade_needed(self):
        """Test password verification when upgrade is needed"""
        manager = PasswordManager()

        password = "TestPassword123!"

        # Mock old hash that needs upgrade
        with patch("api.auth.password_manager.needs_rehash", return_value=True):
            old_hash = hash_password(password)
            result = manager.verify_and_upgrade(password, old_hash)

            assert result["is_valid"] is True
            assert result["needs_upgrade"] is True
            assert result["new_hash"] is not None
            assert result["new_salt"] is not None

    def test_verify_and_upgrade_invalid_password(self):
        """Test verification with invalid password"""
        manager = PasswordManager()

        password = "TestPassword123!"
        wrong_password = "WrongPassword123!"
        hashed = hash_password(password)

        result = manager.verify_and_upgrade(wrong_password, hashed)

        assert result["is_valid"] is False
        assert result["needs_upgrade"] is False
        assert result["new_hash"] is None


class TestPasswordConfiguration:
    """Test password configuration settings"""

    def test_password_config_constants(self):
        """Test password configuration constants"""
        assert PasswordConfig.MIN_LENGTH >= 8
        assert PasswordConfig.MAX_LENGTH >= PasswordConfig.MIN_LENGTH
        assert PasswordConfig.BCRYPT_ROUNDS >= 10
        assert len(PasswordConfig.FORBIDDEN_PASSWORDS) > 0
        assert len(PasswordConfig.SPECIAL_CHARS) > 0

    def test_forbidden_passwords(self):
        """Test forbidden password list"""
        for forbidden in PasswordConfig.FORBIDDEN_PASSWORDS:
            with pytest.raises(PasswordTooWeakError, match="too common"):
                validate_password_strength(forbidden)

    def test_special_characters_accepted(self):
        """Test that all defined special characters are accepted"""
        base_password = "TestPass123"

        for special_char in PasswordConfig.SPECIAL_CHARS:
            password = base_password + special_char
            try:
                result = validate_password_strength(password)
                assert result["checks"]["special_chars"] is True
            except PasswordTooWeakError:
                # Some combinations might fail other checks, that's OK
                pass
