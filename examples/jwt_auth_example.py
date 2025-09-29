"""
JWT Authentication System Example

Demonstrates how to use the comprehensive JWT authentication system
for the Bet-That sports betting arbitrage platform.
"""

import asyncio
import os
import sys
from datetime import datetime, timezone

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.auth.exceptions import PasswordTooWeakError, TokenExpiredError, TokenInvalidError
from api.auth.jwt_auth import (
    JWTAuthenticator,
    create_access_token,
    create_refresh_token,
    get_token_payload,
    revoke_token,
    verify_token,
)
from api.auth.password_manager import (
    PasswordManager,
    generate_secure_password,
    hash_password,
    validate_password_strength,
    verify_password,
)
from api.auth.security_utils import (
    generate_csrf_token,
    generate_secure_token,
    sanitize_auth_input,
    verify_csrf_token,
)


def demonstrate_password_security():
    """Demonstrate password hashing and validation"""
    print("\n=== Password Security Demo ===")

    # 1. Password strength validation
    print("\n1. Password Strength Validation:")

    weak_passwords = ["123456", "password", "abc123"]
    strong_passwords = ["MySecureP@ssw0rd!", "C0mpl3x_P@ssw0rd_2024"]

    for password in weak_passwords:
        try:
            validate_password_strength(password)
            print(f"  ❌ '{password}' - Should have failed validation")
        except PasswordTooWeakError as e:
            print(f"  ✅ '{password}' - Correctly rejected: {e}")

    for password in strong_passwords:
        try:
            result = validate_password_strength(password)
            print(f"  ✅ '{password}' - Score: {result['score']}, Strength: {result['strength']}")
        except PasswordTooWeakError as e:
            print(f"  ❌ '{password}' - Unexpected failure: {e}")

    # 2. Password hashing and verification
    print("\n2. Password Hashing:")

    password = "MySecureP@ssw0rd!"
    hashed = hash_password(password)

    print(f"  Original: {password}")
    print(f"  Hashed: {hashed[:50]}...")
    print(f"  Verification: {verify_password(password, hashed)}")
    print(f"  Wrong password: {verify_password('WrongPassword', hashed)}")

    # 3. Secure password generation
    print("\n3. Secure Password Generation:")

    for length in [12, 16, 20]:
        secure_pass = generate_secure_password(length)
        strength = validate_password_strength(secure_pass)
        print(f"  Length {length}: {secure_pass} (Score: {strength['score']})")


def demonstrate_jwt_tokens():
    """Demonstrate JWT token operations"""
    print("\n=== JWT Token Demo ===")

    # 1. Create tokens
    print("\n1. Token Creation:")

    user_id = 123
    external_id = "user_123_external"
    email = "user@example.com"
    roles = ["user", "premium"]

    access_token = create_access_token(
        user_id=user_id, external_id=external_id, email=email, roles=roles
    )

    refresh_token = create_refresh_token(user_id=user_id, external_id=external_id, email=email)

    print(f"  Access Token: {access_token[:50]}...")
    print(f"  Refresh Token: {refresh_token[:50]}...")

    # 2. Token verification
    print("\n2. Token Verification:")

    try:
        access_payload = verify_token(access_token, "access")
        print(f"  ✅ Access token valid - User ID: {access_payload['sub']}")

        refresh_payload = verify_token(refresh_token, "refresh")
        print(f"  ✅ Refresh token valid - User ID: {refresh_payload['sub']}")

    except (TokenExpiredError, TokenInvalidError) as e:
        print(f"  ❌ Token verification failed: {e}")

    # 3. Token payload extraction
    print("\n3. Token Payload Extraction:")

    token_payload = get_token_payload(access_token)
    print(f"  User ID: {token_payload.user_id}")
    print(f"  Email: {token_payload.email}")
    print(f"  Roles: {token_payload.roles}")
    print(f"  Expires: {token_payload.expires_at}")
    print(f"  Token Type: {token_payload.token_type}")

    # 4. Token revocation
    print("\n4. Token Revocation:")

    print(f"  Token valid before revocation: {verify_token(access_token) is not None}")
    revoke_token(access_token)

    try:
        verify_token(access_token)
        print("  ❌ Token should have been revoked")
    except TokenRevokedError:
        print("  ✅ Token successfully revoked")


def demonstrate_jwt_authenticator():
    """Demonstrate high-level JWTAuthenticator usage"""
    print("\n=== JWT Authenticator Demo ===")

    authenticator = JWTAuthenticator()

    # 1. Create user token pair
    print("\n1. Creating Token Pair:")

    tokens = authenticator.create_user_tokens(
        user_id=456,
        external_id="test_user_456",
        email="testuser@example.com",
        roles=["user", "beta_tester"],
    )

    print(f"  Access Token: {tokens['access_token'][:50]}...")
    print(f"  Refresh Token: {tokens['refresh_token'][:50]}...")
    print(f"  Token Type: {tokens['token_type']}")

    # 2. Refresh access token
    print("\n2. Token Refresh:")

    new_access_token = authenticator.refresh_access_token(tokens["refresh_token"])
    print(f"  New Access Token: {new_access_token[:50]}...")
    print(f"  Different from original: {new_access_token != tokens['access_token']}")

    # 3. User logout
    print("\n3. User Logout:")

    authenticator.logout_user(new_access_token, tokens["refresh_token"])
    print("  ✅ User logged out - tokens revoked")


def demonstrate_security_features():
    """Demonstrate security utilities"""
    print("\n=== Security Features Demo ===")

    # 1. CSRF token generation
    print("\n1. CSRF Protection:")

    user_id = 789
    csrf_token = generate_csrf_token(user_id)
    print(f"  CSRF Token: {csrf_token[:50]}...")

    verification = verify_csrf_token(csrf_token, user_id)
    print(f"  CSRF Verification: {verification}")

    wrong_user_verification = verify_csrf_token(csrf_token, 999)
    print(f"  Wrong User Verification: {wrong_user_verification}")

    # 2. Input sanitization
    print("\n2. Input Sanitization:")

    dirty_input = {
        "email": "  USER@EXAMPLE.COM  ",
        "name": "<script>alert('xss')</script>John Doe",
        "note": "Safe content here",
    }

    clean_input = sanitize_auth_input(dirty_input)
    print(f"  Original: {dirty_input}")
    print(f"  Sanitized: {clean_input}")

    # 3. Secure token generation
    print("\n3. Secure Token Generation:")

    for length in [16, 32, 64]:
        secure_token = generate_secure_token(length)
        print(f"  Length {length}: {secure_token}")


def demonstrate_password_manager():
    """Demonstrate PasswordManager functionality"""
    print("\n=== Password Manager Demo ===")

    manager = PasswordManager()

    # 1. Secure password hashing
    print("\n1. Secure Password Hashing:")

    password = "DemoPassword123!"
    hash_result = manager.hash_password_secure(password)

    print(f"  Algorithm: {hash_result['algorithm']}")
    print(f"  Rounds: {hash_result['rounds']}")
    print(f"  Salt: {hash_result['salt']}")
    print(f"  Hash: {hash_result['hash'][:50]}...")

    # 2. Password verification with upgrade check
    print("\n2. Password Verification & Upgrade:")

    verify_result = manager.verify_and_upgrade(password, hash_result["hash"], hash_result["salt"])

    print(f"  Valid: {verify_result['is_valid']}")
    print(f"  Needs Upgrade: {verify_result['needs_upgrade']}")

    # 3. Password policy check
    print("\n3. Password Policy Check:")

    policy_result = manager.check_password_policy("WeakPass", "user@example.com")

    print(f"  Policy Valid: {policy_result['is_valid']}")
    print(f"  Errors: {policy_result.get('errors', [])}")


def demonstrate_error_handling():
    """Demonstrate error handling"""
    print("\n=== Error Handling Demo ===")

    # 1. Invalid token handling
    print("\n1. Invalid Token Handling:")

    try:
        verify_token("invalid.jwt.token")
    except TokenInvalidError as e:
        print(f"  ✅ Caught invalid token: {e}")

    # 2. Expired token simulation
    print("\n2. Expired Token Simulation:")

    try:
        from datetime import timedelta

        expired_token = create_access_token(
            user_id=1,
            external_id="test",
            email="test@example.com",
            expires_delta=timedelta(seconds=-1),  # Already expired
        )
        verify_token(expired_token)
    except TokenExpiredError as e:
        print(f"  ✅ Caught expired token: {e}")

    # 3. Password validation errors
    print("\n3. Password Validation Errors:")

    weak_passwords = ["123", "password", "abc"]

    for weak_pass in weak_passwords:
        try:
            validate_password_strength(weak_pass)
        except PasswordTooWeakError as e:
            print(f"  ✅ Caught weak password '{weak_pass}': {e}")


async def demonstrate_full_auth_flow():
    """Demonstrate complete authentication flow"""
    print("\n=== Complete Authentication Flow Demo ===")

    authenticator = JWTAuthenticator()
    manager = PasswordManager()

    # 1. User registration simulation
    print("\n1. User Registration Flow:")

    user_data = {"email": "demo@example.com", "password": "SecureDemo123!", "name": "Demo User"}

    # Validate password
    try:
        password_check = manager.check_password_policy(user_data["password"], user_data["email"])
        print(
            f"  Password validation: {password_check['strength']} (Score: {password_check['score']})"
        )
    except PasswordTooWeakError as e:
        print(f"  Password validation failed: {e}")
        return

    # Hash password
    password_hash = hash_password(user_data["password"])
    print(f"  Password hashed: {password_hash[:30]}...")

    # 2. Login simulation
    print("\n2. Login Flow:")

    # Verify password
    login_success = verify_password(user_data["password"], password_hash)
    print(f"  Password verification: {login_success}")

    if login_success:
        # Create tokens
        tokens = authenticator.create_user_tokens(
            user_id=999,
            external_id="demo_user_999",
            email=user_data["email"],
            roles=["user", "demo"],
        )

        print(f"  Login successful - Access token created")
        print(f"  Token type: {tokens['token_type']}")

        # 3. Protected resource access
        print("\n3. Protected Resource Access:")

        try:
            payload = verify_token(tokens["access_token"], "access")
            print(f"  ✅ Access granted - User: {payload['email']}")
            print(f"  Roles: {payload['roles']}")

        except Exception as e:
            print(f"  ❌ Access denied: {e}")

        # 4. Token refresh
        print("\n4. Token Refresh:")

        new_access_token = authenticator.refresh_access_token(tokens["refresh_token"])
        print(f"  ✅ New access token generated")
        print(f"  New token different: {new_access_token != tokens['access_token']}")

        # 5. Logout
        print("\n5. Logout:")

        authenticator.logout_user(new_access_token, tokens["refresh_token"])
        print("  ✅ User logged out - tokens revoked")

        # Try to use revoked token
        try:
            verify_token(new_access_token)
            print("  ❌ Token should have been revoked")
        except Exception:
            print("  ✅ Token correctly revoked")


def demonstrate_security_scenarios():
    """Demonstrate security scenarios and protections"""
    print("\n=== Security Scenarios Demo ===")

    # 1. Rate limiting simulation
    print("\n1. Rate Limiting Protection:")

    from api.auth.security_utils import RateLimiter

    rate_limiter = RateLimiter()
    test_ip = "192.168.1.100"

    # Simulate multiple login attempts
    for attempt in range(7):
        is_limited = rate_limiter.is_rate_limited(test_ip, max_attempts=5, window_minutes=15)

        if not is_limited:
            rate_limiter.record_attempt(test_ip)
            print(f"  Attempt {attempt + 1}: Allowed")
        else:
            print(f"  Attempt {attempt + 1}: ❌ Rate limited")

    # 2. CSRF protection
    print("\n2. CSRF Protection:")

    user_id = 123
    csrf_token = generate_csrf_token(user_id)

    # Valid verification
    valid_check = verify_csrf_token(csrf_token, user_id)
    print(f"  Valid CSRF check: {valid_check}")

    # Invalid verification (wrong user)
    invalid_check = verify_csrf_token(csrf_token, 456)
    print(f"  Invalid CSRF check: {invalid_check}")

    # 3. Input sanitization
    print("\n3. Input Sanitization:")

    malicious_input = {
        "email": "<script>alert('xss')</script>user@evil.com",
        "name": "'; DROP TABLE users; --",
        "note": "Normal content",
    }

    sanitized = sanitize_auth_input(malicious_input)
    print(f"  Original: {malicious_input}")
    print(f"  Sanitized: {sanitized}")


def demonstrate_token_management():
    """Demonstrate advanced token management"""
    print("\n=== Token Management Demo ===")

    authenticator = JWTAuthenticator()

    # 1. Multiple user sessions
    print("\n1. Multiple User Sessions:")

    user_sessions = []
    for i in range(3):
        tokens = authenticator.create_user_tokens(
            user_id=100 + i,
            external_id=f"user_{100 + i}",
            email=f"user{100 + i}@example.com",
            roles=["user"],
        )
        user_sessions.append(tokens)
        print(f"  Session {i + 1} created for user {100 + i}")

    # 2. Token validation
    print("\n2. Token Validation:")

    for i, session in enumerate(user_sessions):
        try:
            payload = verify_token(session["access_token"])
            print(f"  Session {i + 1}: ✅ Valid (User: {payload['sub']})")
        except Exception as e:
            print(f"  Session {i + 1}: ❌ Invalid ({e})")

    # 3. Bulk token revocation
    print("\n3. Bulk Token Revocation:")

    # Revoke all tokens for user 101
    authenticator.logout_all_user_sessions(101)
    print("  All sessions revoked for user 101")

    # Check if tokens are revoked
    for i, session in enumerate(user_sessions):
        try:
            verify_token(session["access_token"])
            print(f"  Session {i + 1}: Still valid")
        except Exception:
            print(f"  Session {i + 1}: ❌ Revoked")


def show_system_configuration():
    """Show current system configuration"""
    print("\n=== System Configuration ===")

    from api.settings import settings

    print(f"Environment: {settings.environment}")
    print(f"JWT Algorithm: {settings.jwt_algorithm}")
    print(f"Access Token Expiry: {settings.jwt_access_token_expire_minutes} minutes")
    print(f"Refresh Token Expiry: {settings.jwt_refresh_token_expire_days} days")
    print(f"Password Min Length: {settings.password_min_length}")
    print(f"bcrypt Rounds: {settings.password_bcrypt_rounds}")
    print(f"CSRF Protection: {settings.enable_csrf_protection}")
    print(f"Email Verification: {settings.enable_email_verification}")
    print(f"Max Concurrent Sessions: {settings.max_concurrent_sessions}")
    print(f"Auth Rate Limit (IP): {settings.auth_max_attempts_per_ip}")
    print(f"Auth Rate Limit (User): {settings.auth_max_attempts_per_user}")


async def main():
    """Run all demonstrations"""
    print("Bet-That JWT Authentication System Demo")
    print("=" * 50)

    show_system_configuration()
    demonstrate_password_security()
    demonstrate_jwt_tokens()
    demonstrate_jwt_authenticator()
    demonstrate_security_features()
    demonstrate_security_scenarios()
    demonstrate_token_management()

    await demonstrate_full_auth_flow()

    print("\n" + "=" * 50)
    print("Demo completed! Check the API documentation at /docs for endpoint details.")
    print("\nNext steps:")
    print("1. Update your frontend to use JWT tokens")
    print("2. Configure production environment variables")
    print("3. Set up email service for verification/reset emails")
    print("4. Implement role-based access control")
    print("5. Set up monitoring for authentication events")


if __name__ == "__main__":
    asyncio.run(main())
