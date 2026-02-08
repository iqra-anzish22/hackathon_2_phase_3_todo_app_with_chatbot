# JWT Token Structure

**Feature**: 001-multiuser-todo
**Date**: 2026-02-04
**Purpose**: Define JWT token payload structure and validation requirements

## Overview

This document specifies the JWT (JSON Web Token) structure used for authentication between the Next.js frontend (Better Auth) and FastAPI backend. The token is issued by Better Auth on the frontend and validated by the backend on every API request.

---

## Token Format

**Standard**: JWT (JSON Web Token) - RFC 7519
**Algorithm**: HS256 (HMAC with SHA-256)
**Encoding**: Base64URL

**Structure**:
```
<header>.<payload>.<signature>
```

**Example Token**:
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyLXV1aWQtMTIzIiwiZW1haWwiOiJ1c2VyQGV4YW1wbGUuY29tIiwiaWF0IjoxNzA3MDQ4MDAwLCJleHAiOjE3MDcxMzQ0MDB9.signature
```

---

## Header

```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

**Fields**:
- `alg` (string): Algorithm used for signing (always "HS256")
- `typ` (string): Token type (always "JWT")

---

## Payload (Claims)

### Required Claims

```json
{
  "sub": "user-uuid-123",
  "email": "user@example.com",
  "iat": 1707048000,
  "exp": 1707134400
}
```

**Field Definitions**:

| Claim | Type | Required | Description |
|-------|------|----------|-------------|
| `sub` | string | Yes | Subject - Unique user identifier (UUID or string) |
| `email` | string | Yes | User's email address |
| `iat` | integer | Yes | Issued At - Unix timestamp when token was created |
| `exp` | integer | Yes | Expiration - Unix timestamp when token expires |

### Optional Claims

Better Auth may include additional claims. The backend MUST NOT rely on optional claims for authorization decisions.

**Potential Optional Claims**:
- `name`: User's display name
- `jti`: JWT ID (unique token identifier)
- `nbf`: Not Before timestamp

---

## Claim Validation Rules

### Backend Validation (FastAPI)

The backend MUST validate the following:

1. **Signature Verification**
   - Verify HMAC signature using `BETTER_AUTH_SECRET`
   - Reject if signature invalid

2. **Expiration Check**
   - Compare `exp` claim with current Unix timestamp
   - Reject if `exp` < current time

3. **Required Claims**
   - Verify `sub` claim exists and is non-empty
   - Verify `email` claim exists and is valid format
   - Reject if any required claim missing

4. **User ID Extraction**
   - Extract user ID from `sub` claim
   - Use this ID for all ownership checks
   - NEVER accept user_id from request body/query

### Frontend Responsibilities (Better Auth)

Better Auth automatically handles:
- Token generation with correct structure
- Signature creation using `BETTER_AUTH_SECRET`
- Expiration time calculation (24 hours default)
- Token storage in HTTP-only cookies
- Token refresh (if configured)

---

## Token Lifecycle

### 1. Token Issuance (Frontend)

**Trigger**: User signs up or signs in via Better Auth

**Process**:
1. User provides credentials (email/password)
2. Better Auth validates credentials
3. Better Auth generates JWT with user claims
4. Better Auth signs token with `BETTER_AUTH_SECRET`
5. Better Auth stores token in HTTP-only cookie
6. Frontend receives authentication confirmation

**Token Properties**:
- Issued At (`iat`): Current timestamp
- Expiration (`exp`): Current timestamp + 24 hours
- Subject (`sub`): User's unique ID from Better Auth database

### 2. Token Usage (API Requests)

**Process**:
1. Frontend makes API request
2. Browser automatically includes auth cookie
3. Frontend extracts token from cookie (server-side)
4. Frontend adds token to Authorization header
5. Backend receives request with token
6. Backend validates token
7. Backend extracts user_id from `sub` claim
8. Backend processes request with authenticated user context

**Header Format**:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 3. Token Expiration

**Default Expiration**: 24 hours from issuance

**Expiration Handling**:
- Backend rejects expired tokens with 401 Unauthorized
- Frontend detects 401 and redirects to sign-in page
- User must re-authenticate to get new token
- Optional: Implement token refresh for seamless UX

### 4. Token Revocation

**Not Implemented**: Token revocation is not required for this hackathon project.

**Future Consideration**: Implement token blacklist or short-lived tokens with refresh tokens for production.

---

## Security Considerations

### Shared Secret

**Environment Variable**: `BETTER_AUTH_SECRET`

**Requirements**:
- Minimum 32 characters (256 bits)
- Cryptographically random
- MUST be identical in frontend and backend
- NEVER committed to version control
- Stored in `.env` files (gitignored)

**Generation**:
```bash
# Generate secure random secret
openssl rand -base64 32
```

**Example**:
```
BETTER_AUTH_SECRET=Kx9mP2vN8qR5tY7wZ3aB6cD1eF4gH0jL
```

### Token Storage

**Frontend Storage**: HTTP-only cookies

**Benefits**:
- Prevents XSS attacks (JavaScript cannot access)
- Automatic inclusion in requests
- Secure flag for HTTPS-only transmission
- SameSite flag for CSRF protection

**Cookie Configuration**:
```typescript
{
  httpOnly: true,
  secure: true, // HTTPS only in production
  sameSite: 'lax',
  maxAge: 86400 // 24 hours in seconds
}
```

### Token Transmission

**Development**: HTTP allowed (localhost)
**Production**: HTTPS required

**Header Format**:
```
Authorization: Bearer <token>
```

**Security Rules**:
- Never log tokens in production
- Never include tokens in URLs
- Never store tokens in localStorage (XSS vulnerable)
- Always use HTTPS in production

---

## Example Payloads

### Valid Token Payload

```json
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",
  "email": "alice@example.com",
  "iat": 1707048000,
  "exp": 1707134400
}
```

**Decoded Values**:
- User ID: `550e8400-e29b-41d4-a716-446655440000`
- Email: `alice@example.com`
- Issued: 2026-02-04 10:00:00 UTC
- Expires: 2026-02-05 10:00:00 UTC (24 hours later)

### Expired Token Payload

```json
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",
  "email": "alice@example.com",
  "iat": 1706961600,
  "exp": 1707048000
}
```

**Status**: Expired (exp < current time)
**Backend Response**: 401 Unauthorized

### Invalid Token (Missing Required Claim)

```json
{
  "email": "alice@example.com",
  "iat": 1707048000,
  "exp": 1707134400
}
```

**Issue**: Missing `sub` claim
**Backend Response**: 401 Unauthorized

---

## Backend Implementation

### JWT Verification Function

```python
from jose import JWTError, jwt
from fastapi import HTTPException, status
from datetime import datetime

def verify_jwt(token: str, secret: str) -> dict:
    """
    Verify JWT token and return payload.

    Args:
        token: JWT token string
        secret: Shared secret for signature verification

    Returns:
        dict: Token payload with validated claims

    Raises:
        HTTPException: 401 if token invalid or expired
    """
    try:
        # Decode and verify token
        payload = jwt.decode(
            token,
            secret,
            algorithms=["HS256"]
        )

        # Validate required claims
        user_id: str = payload.get("sub")
        email: str = payload.get("email")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID"
            )

        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing email"
            )

        return payload

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
```

### User Extraction

```python
from pydantic import BaseModel

class CurrentUser(BaseModel):
    user_id: str
    email: str

def extract_user(payload: dict) -> CurrentUser:
    """Extract user information from validated JWT payload."""
    return CurrentUser(
        user_id=payload["sub"],
        email=payload["email"]
    )
```

---

## Frontend Implementation

### Token Access (Server Component)

```typescript
// frontend/src/app/(protected)/tasks/page.tsx
import { cookies } from 'next/headers'

export default async function TasksPage() {
  const token = cookies().get('auth-token')?.value

  if (!token) {
    redirect('/signin')
  }

  // Use token for API calls
  const response = await fetch('http://localhost:8000/api/tasks', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  })

  // ...
}
```

### API Client with Token

```typescript
// frontend/src/lib/api.ts
export async function apiRequest(
  endpoint: string,
  options: RequestInit = {}
) {
  // Token automatically included from cookies
  const response = await fetch(
    `${process.env.NEXT_PUBLIC_API_URL}${endpoint}`,
    {
      ...options,
      credentials: 'include', // Include cookies
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      }
    }
  )

  if (response.status === 401) {
    // Token expired or invalid
    window.location.href = '/signin'
  }

  return response
}
```

---

## Testing

### Valid Token Test

```python
def test_valid_token():
    token = create_test_token(user_id="test-user-123")
    response = client.get(
        "/api/tasks",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
```

### Expired Token Test

```python
def test_expired_token():
    token = create_expired_token(user_id="test-user-123")
    response = client.get(
        "/api/tasks",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401
```

### Invalid Signature Test

```python
def test_invalid_signature():
    token = create_token_with_wrong_secret(user_id="test-user-123")
    response = client.get(
        "/api/tasks",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401
```

### Missing Token Test

```python
def test_missing_token():
    response = client.get("/api/tasks")
    assert response.status_code == 401
```

---

## Troubleshooting

### Common Issues

**Issue**: 401 Unauthorized despite valid credentials
- **Cause**: BETTER_AUTH_SECRET mismatch between frontend and backend
- **Solution**: Verify both .env files have identical secret

**Issue**: Token expires too quickly
- **Cause**: Better Auth expiration configuration
- **Solution**: Adjust Better Auth JWT expiration setting

**Issue**: Token not included in requests
- **Cause**: Cookie not set or incorrect domain
- **Solution**: Verify Better Auth cookie configuration

**Issue**: CORS errors with Authorization header
- **Cause**: Backend CORS not configured for Authorization header
- **Solution**: Add Authorization to allowed headers in CORS config

---

## Summary

**Token Type**: JWT with HS256 algorithm
**Required Claims**: sub, email, iat, exp
**Expiration**: 24 hours (configurable)
**Storage**: HTTP-only cookies (frontend)
**Transmission**: Authorization: Bearer header
**Validation**: Signature, expiration, required claims
**Security**: Shared secret, HTTPS in production, no localStorage
