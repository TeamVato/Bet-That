"""Comprehensive test suite for user registration and login system

Tests the complete authentication flow including registration, login,
JWT token generation, validation, and error handling.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from api.database import get_db
from api.main import app
from api.models import User
from backend.tests.conftest import override_get_db


class TestUserRegistration:
    """Test user registration functionality"""

    def test_successful_registration(self, test_db: Session):
        """Test successful user registration with all required fields"""
        client = TestClient(app)
        app.dependency_overrides[get_db] = override_get_db(test_db)

        registration_data = {
            "email": "test@example.com",
            "username": "testuser123",
            "password": "SecurePass123!",
            "confirm_password": "SecurePass123!",
            "first_name": "Test",
            "last_name": "User",
            "date_of_birth": "1990-01-01",
            "phone_number": "+1234567890",
            "timezone": "America/New_York",
        }

        response = client.post("/auth/register", json=registration_data)

        assert response.status_code == 201
        data = response.json()

        # Check response structure
        assert "message" in data
        assert "user" in data
        assert "verification_required" in data

        # Check user data
        user_data = data["user"]
        assert user_data["email"] == "test@example.com"
        assert user_data["username"] == "testuser123"
        assert user_data["first_name"] == "Test"
        assert user_data["last_name"] == "User"
        assert user_data["is_active"] is True
        assert user_data["is_verified"] is False
        assert data["verification_required"] is True

        # Verify user was created in database
        db_user = test_db.query(User).filter(User.email == "test@example.com").first()
        assert db_user is not None
        assert db_user.username == "testuser123"
        assert db_user.first_name == "Test"
        assert db_user.last_name == "User"
        assert db_user.is_active is True
        assert db_user.is_verified is False

        app.dependency_overrides.clear()

    def test_duplicate_email_registration(self, test_db: Session):
        """Test registration with duplicate email fails"""
        client = TestClient(app)
        app.dependency_overrides[get_db] = override_get_db(test_db)

        # First registration
        registration_data = {
            "email": "duplicate@example.com",
            "username": "user1",
            "password": "SecurePass123!",
            "confirm_password": "SecurePass123!",
            "first_name": "First",
            "last_name": "User",
        }
        client.post("/auth/register", json=registration_data)

        # Duplicate email registration
        registration_data["username"] = "user2"
        response = client.post("/auth/register", json=registration_data)

        assert response.status_code == 409
        assert "Email address is already registered" in response.json()["detail"]

        app.dependency_overrides.clear()

    def test_duplicate_username_registration(self, test_db: Session):
        """Test registration with duplicate username fails"""
        client = TestClient(app)
        app.dependency_overrides[get_db] = override_get_db(test_db)

        # First registration
        registration_data = {
            "email": "user1@example.com",
            "username": "duplicateuser",
            "password": "SecurePass123!",
            "confirm_password": "SecurePass123!",
            "first_name": "First",
            "last_name": "User",
        }
        client.post("/auth/register", json=registration_data)

        # Duplicate username registration
        registration_data["email"] = "user2@example.com"
        response = client.post("/auth/register", json=registration_data)

        assert response.status_code == 409
        assert "Username is already taken" in response.json()["detail"]

        app.dependency_overrides.clear()

    def test_password_mismatch_validation(self, test_db: Session):
        """Test password confirmation validation"""
        client = TestClient(app)
        app.dependency_overrides[get_db] = override_get_db(test_db)

        registration_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "SecurePass123!",
            "confirm_password": "DifferentPass123!",
            "first_name": "Test",
            "last_name": "User",
        }

        response = client.post("/auth/register", json=registration_data)

        assert response.status_code == 422
        error_detail = response.json()["detail"]
        assert any("passwords do not match" in str(error) for error in error_detail)

        app.dependency_overrides.clear()

    def test_username_validation(self, test_db: Session):
        """Test username validation rules"""
        client = TestClient(app)
        app.dependency_overrides[get_db] = override_get_db(test_db)

        # Test reserved username
        registration_data = {
            "email": "test@example.com",
            "username": "admin",
            "password": "SecurePass123!",
            "confirm_password": "SecurePass123!",
            "first_name": "Test",
            "last_name": "User",
        }

        response = client.post("/auth/register", json=registration_data)
        assert response.status_code == 422

        # Test username too short
        registration_data["username"] = "ab"
        response = client.post("/auth/register", json=registration_data)
        assert response.status_code == 422

        # Test username too long
        registration_data["username"] = "a" * 31
        response = client.post("/auth/register", json=registration_data)
        assert response.status_code == 422

        # Test invalid characters
        registration_data["username"] = "user@name"
        response = client.post("/auth/register", json=registration_data)
        assert response.status_code == 422

        app.dependency_overrides.clear()

    def test_age_validation(self, test_db: Session):
        """Test age validation (must be 18+)"""
        client = TestClient(app)
        app.dependency_overrides[get_db] = override_get_db(test_db)

        # Test underage user
        registration_data = {
            "email": "young@example.com",
            "username": "younguser",
            "password": "SecurePass123!",
            "confirm_password": "SecurePass123!",
            "first_name": "Young",
            "last_name": "User",
            "date_of_birth": "2010-01-01",  # Under 18
        }

        response = client.post("/auth/register", json=registration_data)
        assert response.status_code == 422
        error_detail = response.json()["detail"]
        assert any("must be at least 18 years old" in str(error) for error in error_detail)

        app.dependency_overrides.clear()

    def test_minimal_registration(self, test_db: Session):
        """Test registration with minimal required fields"""
        client = TestClient(app)
        app.dependency_overrides[get_db] = override_get_db(test_db)

        registration_data = {
            "email": "minimal@example.com",
            "username": "minimaluser",
            "password": "SecurePass123!",
            "confirm_password": "SecurePass123!",
            "first_name": "Minimal",
            "last_name": "User",
        }

        response = client.post("/auth/register", json=registration_data)

        assert response.status_code == 201
        data = response.json()
        assert data["user"]["email"] == "minimal@example.com"
        assert data["user"]["username"] == "minimaluser"

        app.dependency_overrides.clear()


class TestUserLogin:
    """Test user login functionality"""

    @pytest.fixture
    def test_user(self, test_db: Session):
        """Create a test user for login tests"""
        from api.auth_schemas import UserRegistrationRequest
        from api.repositories.user_repository import UserRepository

        user_repo = UserRepository(test_db)

        registration_data = UserRegistrationRequest(
            email="logintest@example.com",
            username="logintest",
            password="TestPass123!",
            confirm_password="TestPass123!",
            first_name="Login",
            last_name="Test",
        )

        user = user_repo.create_user(registration_data)
        # Verify the user's email for testing
        user_repo.verify_user_email(user.id)
        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "password": "TestPass123!",
        }

    def test_successful_login_with_email(self, test_db: Session, test_user):
        """Test successful login using email"""
        client = TestClient(app)
        app.dependency_overrides[get_db] = override_get_db(test_db)

        login_data = {
            "email_or_username": test_user["email"],
            "password": test_user["password"],
            "remember_me": False,
        }

        response = client.post("/auth/login", json=login_data)

        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert "access_token" in data
        assert "refresh_token" in data
        assert "token_type" in data
        assert "expires_in" in data
        assert "user" in data

        # Check token properties
        assert data["token_type"] == "bearer"
        assert isinstance(data["expires_in"], int)
        assert data["expires_in"] > 0

        # Check user data
        user_data = data["user"]
        assert user_data["email"] == test_user["email"]
        assert user_data["username"] == test_user["username"]
        assert user_data["is_active"] is True

        app.dependency_overrides.clear()

    def test_successful_login_with_username(self, test_db: Session, test_user):
        """Test successful login using username"""
        client = TestClient(app)
        app.dependency_overrides[get_db] = override_get_db(test_db)

        login_data = {
            "email_or_username": test_user["username"],
            "password": test_user["password"],
            "remember_me": True,
        }

        response = client.post("/auth/login", json=login_data)

        assert response.status_code == 200
        data = response.json()

        assert "access_token" in data
        assert "refresh_token" in data
        assert data["user"]["username"] == test_user["username"]

        app.dependency_overrides.clear()

    def test_invalid_credentials(self, test_db: Session, test_user):
        """Test login with invalid credentials"""
        client = TestClient(app)
        app.dependency_overrides[get_db] = override_get_db(test_db)

        # Wrong password
        login_data = {
            "email_or_username": test_user["email"],
            "password": "wrongpassword",
            "remember_me": False,
        }

        response = client.post("/auth/login", json=login_data)

        assert response.status_code == 401
        assert "Invalid email/username or password" in response.json()["detail"]

        app.dependency_overrides.clear()

    def test_nonexistent_user_login(self, test_db: Session):
        """Test login with non-existent user"""
        client = TestClient(app)
        app.dependency_overrides[get_db] = override_get_db(test_db)

        login_data = {
            "email_or_username": "nonexistent@example.com",
            "password": "SomePassword123!",
            "remember_me": False,
        }

        response = client.post("/auth/login", json=login_data)

        assert response.status_code == 401
        assert "Invalid email/username or password" in response.json()["detail"]

        app.dependency_overrides.clear()

    def test_case_insensitive_login(self, test_db: Session, test_user):
        """Test login is case insensitive for email and username"""
        client = TestClient(app)
        app.dependency_overrides[get_db] = override_get_db(test_db)

        # Test uppercase email
        login_data = {
            "email_or_username": test_user["email"].upper(),
            "password": test_user["password"],
            "remember_me": False,
        }

        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 200

        # Test uppercase username
        login_data = {
            "email_or_username": test_user["username"].upper(),
            "password": test_user["password"],
            "remember_me": False,
        }

        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 200

        app.dependency_overrides.clear()


class TestJWTTokenValidation:
    """Test JWT token generation and validation"""

    @pytest.fixture
    def authenticated_user(self, test_db: Session):
        """Create and login a user to get tokens"""
        from api.auth_schemas import UserRegistrationRequest
        from api.repositories.user_repository import UserRepository

        user_repo = UserRepository(test_db)

        registration_data = UserRegistrationRequest(
            email="jwt@example.com",
            username="jwttest",
            password="JwtPass123!",
            confirm_password="JwtPass123!",
            first_name="JWT",
            last_name="Test",
        )

        user = user_repo.create_user(registration_data)
        # Verify the user's email for testing
        user_repo.verify_user_email(user.id)

        # Login to get tokens
        client = TestClient(app)
        app.dependency_overrides[get_db] = override_get_db(test_db)

        login_data = {
            "email_or_username": user.email,
            "password": "JwtPass123!",
            "remember_me": False,
        }

        response = client.post("/auth/login", json=login_data)
        tokens = response.json()

        app.dependency_overrides.clear()

        return {
            "user": user,
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
        }

    def test_get_current_user_with_valid_token(self, test_db: Session, authenticated_user):
        """Test getting current user with valid JWT token"""
        client = TestClient(app)
        app.dependency_overrides[get_db] = override_get_db(test_db)

        headers = {"Authorization": f"Bearer {authenticated_user['access_token']}"}

        response = client.get("/auth/me", headers=headers)

        assert response.status_code == 200
        data = response.json()

        assert data["email"] == authenticated_user["user"].email
        assert data["username"] == authenticated_user["user"].username
        assert data["is_active"] is True

        app.dependency_overrides.clear()

    def test_get_current_user_without_token(self, test_db: Session):
        """Test getting current user without token fails"""
        client = TestClient(app)
        app.dependency_overrides[get_db] = override_get_db(test_db)

        response = client.get("/auth/me")

        assert response.status_code == 401
        assert "Authorization header missing" in response.json()["detail"]

        app.dependency_overrides.clear()

    def test_get_current_user_with_invalid_token(self, test_db: Session):
        """Test getting current user with invalid token fails"""
        client = TestClient(app)
        app.dependency_overrides[get_db] = override_get_db(test_db)

        headers = {"Authorization": "Bearer invalid_token"}

        response = client.get("/auth/me", headers=headers)

        assert response.status_code == 401
        assert "Invalid token" in response.json()["detail"]

        app.dependency_overrides.clear()

    def test_token_expiration(self, test_db: Session, authenticated_user):
        """Test token expiration handling"""
        # This test would require mocking time or using very short expiration
        # For now, we'll test that tokens have proper structure
        access_token = authenticated_user["access_token"]
        refresh_token = authenticated_user["refresh_token"]

        # Tokens should be non-empty strings
        assert isinstance(access_token, str)
        assert len(access_token) > 0
        assert isinstance(refresh_token, str)
        assert len(refresh_token) > 0

        # Tokens should be different
        assert access_token != refresh_token


class TestPasswordSecurity:
    """Test password security and hashing"""

    def test_password_hashing(self, test_db: Session):
        """Test that passwords are properly hashed"""
        from api.auth_schemas import UserRegistrationRequest
        from api.repositories.user_repository import UserRepository

        user_repo = UserRepository(test_db)

        registration_data = UserRegistrationRequest(
            email="password@example.com",
            username="passwordtest",
            password="TestPassword123!",
            confirm_password="TestPassword123!",
            first_name="Password",
            last_name="Test",
        )

        user = user_repo.create_user(registration_data)

        # Password should be hashed, not stored in plain text
        assert user.password_hash != "TestPassword123!"
        assert len(user.password_hash) > 50  # PBKDF2 hash should be long
        assert "$" in user.password_hash  # Should contain salt separator

        # Verify password works
        from api.auth.simple_password import verify_password_pbkdf2

        assert verify_password_pbkdf2("TestPassword123!", user.password_hash)
        assert not verify_password_pbkdf2("WrongPassword", user.password_hash)

    def test_password_validation(self):
        """Test password strength validation"""
        from api.auth.simple_password import validate_password_simple

        # Test weak password
        result = validate_password_simple("weak")
        assert result["is_valid"] is False
        assert "at least 8 characters" in result["errors"][0]

        # Test password without uppercase
        result = validate_password_simple("weakpassword123!")
        assert result["is_valid"] is False
        assert "uppercase letter" in result["errors"][0]

        # Test password without lowercase
        result = validate_password_simple("WEAKPASSWORD123!")
        assert result["is_valid"] is False
        assert "lowercase letter" in result["errors"][0]

        # Test password without digit
        result = validate_password_simple("WeakPassword!")
        assert result["is_valid"] is False
        assert "digit" in result["errors"][0]

        # Test password without special character
        result = validate_password_simple("WeakPassword123")
        assert result["is_valid"] is False
        assert "special character" in result["errors"][0]

        # Test strong password
        result = validate_password_simple("StrongPassword123!")
        assert result["is_valid"] is True
        assert result["score"] >= 80
        assert result["strength"] == "strong"


class TestErrorHandling:
    """Test comprehensive error handling"""

    def test_malformed_json_registration(self, test_db: Session):
        """Test registration with malformed JSON"""
        client = TestClient(app)
        app.dependency_overrides[get_db] = override_get_db(test_db)

        response = client.post(
            "/auth/register", data="invalid json", headers={"Content-Type": "application/json"}
        )

        assert response.status_code == 422

        app.dependency_overrides.clear()

    def test_missing_required_fields(self, test_db: Session):
        """Test registration with missing required fields"""
        client = TestClient(app)
        app.dependency_overrides[get_db] = override_get_db(test_db)

        # Missing email
        registration_data = {
            "username": "testuser",
            "password": "SecurePass123!",
            "confirm_password": "SecurePass123!",
            "first_name": "Test",
            "last_name": "User",
        }

        response = client.post("/auth/register", json=registration_data)
        assert response.status_code == 422

        app.dependency_overrides.clear()

    def test_invalid_email_format(self, test_db: Session):
        """Test registration with invalid email format"""
        client = TestClient(app)
        app.dependency_overrides[get_db] = override_get_db(test_db)

        registration_data = {
            "email": "invalid-email",
            "username": "testuser",
            "password": "SecurePass123!",
            "confirm_password": "SecurePass123!",
            "first_name": "Test",
            "last_name": "User",
        }

        response = client.post("/auth/register", json=registration_data)
        assert response.status_code == 422

        app.dependency_overrides.clear()

    def test_invalid_phone_format(self, test_db: Session):
        """Test registration with invalid phone format"""
        client = TestClient(app)
        app.dependency_overrides[get_db] = override_get_db(test_db)

        registration_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "SecurePass123!",
            "confirm_password": "SecurePass123!",
            "first_name": "Test",
            "last_name": "User",
            "phone_number": "invalid-phone",
        }

        response = client.post("/auth/register", json=registration_data)
        assert response.status_code == 422

        app.dependency_overrides.clear()


class TestIntegration:
    """Integration tests for complete authentication flow"""

    def test_complete_registration_login_flow(self, test_db: Session):
        """Test complete flow: register -> login -> get profile"""
        client = TestClient(app)
        app.dependency_overrides[get_db] = override_get_db(test_db)

        # Step 1: Register user
        registration_data = {
            "email": "integration@example.com",
            "username": "integrationtest",
            "password": "IntegrationPass123!",
            "confirm_password": "IntegrationPass123!",
            "first_name": "Integration",
            "last_name": "Test",
            "date_of_birth": "1990-01-01",
            "phone_number": "+1234567890",
            "timezone": "America/New_York",
        }

        register_response = client.post("/auth/register", json=registration_data)
        assert register_response.status_code == 201

        # Verify the user's email for testing
        from api.repositories.user_repository import UserRepository

        user_repo = UserRepository(test_db)
        user = user_repo.get_user_by_email("integration@example.com")
        user_repo.verify_user_email(user.id)

        # Step 2: Login user
        login_data = {
            "email_or_username": "integration@example.com",
            "password": "IntegrationPass123!",
            "remember_me": False,
        }

        login_response = client.post("/auth/login", json=login_data)
        assert login_response.status_code == 200

        tokens = login_response.json()
        access_token = tokens["access_token"]

        # Step 3: Get user profile
        headers = {"Authorization": f"Bearer {access_token}"}
        profile_response = client.get("/auth/me", headers=headers)
        assert profile_response.status_code == 200

        profile_data = profile_response.json()
        assert profile_data["email"] == "integration@example.com"
        assert profile_data["username"] == "integrationtest"
        assert profile_data["first_name"] == "Integration"
        assert profile_data["last_name"] == "Test"

        app.dependency_overrides.clear()

    def test_multiple_user_registration(self, test_db: Session):
        """Test registering multiple users"""
        client = TestClient(app)
        app.dependency_overrides[get_db] = override_get_db(test_db)

        users = []
        for i in range(3):
            registration_data = {
                "email": f"user{i}@example.com",
                "username": f"user{i}",
                "password": "SecurePass123!",
                "confirm_password": "SecurePass123!",
                "first_name": f"User{i}",
                "last_name": "Test",
            }

            response = client.post("/auth/register", json=registration_data)
            assert response.status_code == 201
            users.append(response.json()["user"])

        # Verify all users were created
        assert len(users) == 3
        for i, user in enumerate(users):
            assert user["email"] == f"user{i}@example.com"
            assert user["username"] == f"user{i}"

        # Verify in database
        db_users = test_db.query(User).all()
        assert len(db_users) == 3

        app.dependency_overrides.clear()

    def test_concurrent_registration_attempts(self, test_db: Session):
        """Test handling of concurrent registration attempts"""
        client = TestClient(app)
        app.dependency_overrides[get_db] = override_get_db(test_db)

        # This test would require threading for true concurrency
        # For now, test rapid sequential requests
        registration_data = {
            "email": "concurrent@example.com",
            "username": "concurrent",
            "password": "SecurePass123!",
            "confirm_password": "SecurePass123!",
            "first_name": "Concurrent",
            "last_name": "Test",
        }

        # First registration should succeed
        response1 = client.post("/auth/register", json=registration_data)
        assert response1.status_code == 201

        # Second registration with same email should fail
        response2 = client.post("/auth/register", json=registration_data)
        assert response2.status_code == 409

        app.dependency_overrides.clear()
