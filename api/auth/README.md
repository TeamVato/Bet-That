# JWT Authentication System

A comprehensive JWT authentication system for the Bet-That sports betting arbitrage platform.

## Features

- **Secure JWT tokens** with configurable algorithms (HS256/RS256)
- **Password security** with bcrypt hashing and strength validation
- **Token management** with blacklisting and revocation
- **Rate limiting** for authentication endpoints
- **Session management** with concurrent session limits
- **CSRF protection** for web applications
- **Security logging** for audit trails
- **Email verification** support
- **Password reset** functionality

## Quick Start

### 1. Configuration

Add these environment variables to your `.env.api` file:

```bash
# JWT Settings
JWT_SECRET_KEY=your-256-bit-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=30

# Password Security
PASSWORD_BCRYPT_ROUNDS=12
PASSWORD_MIN_LENGTH=8

# Rate Limiting
AUTH_MAX_ATTEMPTS_PER_IP=10
AUTH_MAX_ATTEMPTS_PER_USER=5
AUTH_RATE_LIMIT_WINDOW_MINUTES=15

# Security Features
ENABLE_CSRF_PROTECTION=true
ENABLE_EMAIL_VERIFICATION=true
MAX_CONCURRENT_SESSIONS=5
```

### 2. Database Migration

Run the JWT authentication migration:

```bash
sqlite3 storage/odds.db < migrations/002_add_jwt_auth_fields.sql
```

### 3. Basic Usage

#### User Registration

```python
from api.auth import endpoints as auth

# Register new user
response = await auth.register_user({
    "email": "user@example.com",
    "password": "SecurePassword123!",
    "name": "John Doe"
})
```

#### User Login

```python
# Login with email/password
response = await auth.login_user({
    "username": "user@example.com",  # OAuth2 form uses 'username' field
    "password": "SecurePassword123!"
})

# Response includes:
# - access_token (15min expiry)
# - refresh_token (30 day expiry)
# - csrf_token (if enabled)
# - user information
```

#### Protected Endpoints

```python
from fastapi import Depends
from api.auth.dependencies import CurrentUser

@router.get("/protected")
async def protected_endpoint(current_user: CurrentUser):
    return {"message": f"Hello {current_user.email}"}
```

#### Token Refresh

```python
# Refresh access token
response = await auth.refresh_access_token({
    "refresh_token": "your-refresh-token",
    "rotate_refresh_token": False
})
```

## Authentication Methods

### JWT Token Authentication (Recommended)

```http
GET /api/protected-endpoint
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

### Legacy Header Authentication (Backward Compatibility)

```http
GET /api/protected-endpoint
X-User-Id: external-user-id
```

## Security Features

### Token Structure

**Access Token Payload:**

```json
{
  "sub": "123",
  "external_id": "user_external_id",
  "email": "user@example.com",
  "roles": ["user"],
  "iat": 1640995200,
  "exp": 1640996100,
  "iss": "bet-that-api",
  "aud": "bet-that-users",
  "type": "access",
  "jti": "unique-token-id"
}
```

**Refresh Token Payload:**

```json
{
  "sub": "123",
  "external_id": "user_external_id",
  "email": "user@example.com",
  "iat": 1640995200,
  "exp": 1643587200,
  "iss": "bet-that-api",
  "aud": "bet-that-users",
  "type": "refresh",
  "jti": "unique-token-id"
}
```

### Password Security

- **bcrypt hashing** with configurable rounds (default: 12)
- **Password strength validation** with multiple criteria
- **Salt generation** for additional security
- **Automatic hash upgrading** when security standards improve

### Rate Limiting

- **IP-based limiting**: 10 attempts per 15 minutes
- **User-based limiting**: 5 attempts per 15 minutes
- **Automatic blocking**: 60 minutes after limit exceeded
- **Cleanup routines** for expired rate limit data

### Token Revocation

- **Individual token revocation** via JTI blacklisting
- **User session revocation** (logout all devices)
- **Database-backed blacklist** for persistence
- **Automatic cleanup** of expired blacklist entries

## API Endpoints

### Authentication Endpoints

| Method | Endpoint                          | Description               |
| ------ | --------------------------------- | ------------------------- |
| POST   | `/auth/register`                  | Register new user         |
| POST   | `/auth/login`                     | Login with email/password |
| POST   | `/auth/refresh`                   | Refresh access token      |
| POST   | `/auth/logout`                    | Logout current session    |
| POST   | `/auth/password/reset`            | Request password reset    |
| POST   | `/auth/password/reset/confirm`    | Confirm password reset    |
| POST   | `/auth/password/change`           | Change password           |
| POST   | `/auth/email/verify`              | Verify email address      |
| POST   | `/auth/email/verification/resend` | Resend verification email |
| GET    | `/auth/me`                        | Get current user info     |
| POST   | `/auth/tokens/validate`           | Validate JWT token        |

### Legacy Compatibility

| Method | Endpoint             | Description              |
| ------ | -------------------- | ------------------------ |
| POST   | `/auth/legacy/login` | Legacy external ID login |

## Dependencies

### FastAPI Dependencies

```python
from api.auth.dependencies import (
    CurrentUser,          # Requires JWT authentication
    OptionalUser,         # Optional JWT authentication
    VerifiedUser,         # Requires verified email
    JWTPayload,          # Raw JWT payload
)

# Usage examples
@router.get("/profile")
async def get_profile(user: CurrentUser):
    return {"email": user.email}

@router.get("/public")
async def public_endpoint(user: OptionalUser):
    if user:
        return {"message": f"Hello {user.email}"}
    return {"message": "Hello anonymous user"}
```

### Legacy Migration Support

```python
from api.deps import (
    get_current_user,           # Supports both JWT and legacy
    require_authentication,     # Requires any auth method
    require_jwt_authentication, # JWT only
)
```

## Security Best Practices

### Production Deployment

1. **Use RS256 algorithm** with RSA key pairs:

   ```bash
   JWT_ALGORITHM=RS256
   JWT_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n..."
   JWT_PUBLIC_KEY="-----BEGIN PUBLIC KEY-----\n..."
   ```

2. **Strong secret keys** (256-bit minimum):

   ```bash
   JWT_SECRET_KEY=$(openssl rand -base64 32)
   ```

3. **Enable all security features**:

   ```bash
   ENABLE_CSRF_PROTECTION=true
   ENABLE_EMAIL_VERIFICATION=true
   ```

4. **Configure rate limiting**:
   ```bash
   AUTH_MAX_ATTEMPTS_PER_IP=5
   AUTH_RATE_LIMIT_WINDOW_MINUTES=15
   ```

### Token Management

- **Short-lived access tokens** (15 minutes)
- **Longer-lived refresh tokens** (30 days)
- **Automatic token rotation** for enhanced security
- **Session limits** to prevent token accumulation

### Monitoring

- **Authentication logs** for security auditing
- **Rate limit monitoring** for attack detection
- **Failed login tracking** per IP and user
- **Token revocation logging** for compliance

## Error Handling

The system provides specific error types for different scenarios:

```python
from api.auth.exceptions import (
    AuthenticationError,      # Base auth error
    TokenExpiredError,        # Token has expired
    TokenInvalidError,        # Invalid/malformed token
    TokenRevokedError,        # Token has been revoked
    PasswordTooWeakError,     # Password strength requirements
    RateLimitExceededError,   # Too many attempts
    UserNotFoundError,        # User doesn't exist
    UserInactiveError,        # Account is inactive
    EmailNotVerifiedError,    # Email verification required
)
```

## Testing

Run the authentication tests:

```bash
# Run all auth tests
pytest tests/auth/

# Run specific test file
pytest tests/auth/test_jwt_auth.py -v

# Run with coverage
pytest tests/auth/ --cov=api.auth --cov-report=html
```

## Migration from Legacy Auth

### Phase 1: Dual Authentication Support

- Keep existing X-User-Id header support
- Add JWT token support in parallel
- Update frontend to use JWT tokens
- Monitor both auth methods

### Phase 2: JWT Migration

- Update all endpoints to prefer JWT
- Add JWT token generation for existing users
- Deprecate X-User-Id header
- Send migration notices

### Phase 3: Legacy Removal

- Remove X-User-Id header support
- Enforce JWT authentication
- Clean up legacy auth code
- Update documentation

## Troubleshooting

### Common Issues

1. **Token verification fails**:
   - Check JWT_SECRET_KEY matches between token creation and verification
   - Verify token hasn't expired
   - Check token format (should start with "eyJ")

2. **Password validation fails**:
   - Ensure password meets strength requirements
   - Check for common/forbidden passwords
   - Verify special character requirements

3. **Rate limiting issues**:
   - Check IP address extraction
   - Verify rate limit configuration
   - Monitor auth_logs table for patterns

### Debugging

Enable debug logging:

```python
import logging
logging.getLogger("api.auth").setLevel(logging.DEBUG)
```

Check authentication logs:

```sql
SELECT * FROM auth_logs
WHERE created_at > datetime('now', '-1 hour')
ORDER BY created_at DESC;
```

## Security Considerations

1. **Never log passwords** or tokens in plain text
2. **Use HTTPS** in production for all authentication
3. **Implement CSRF protection** for web applications
4. **Monitor authentication logs** for suspicious activity
5. **Regularly rotate secrets** and update dependencies
6. **Use secure session storage** on the client side
7. **Implement proper token cleanup** and maintenance routines
