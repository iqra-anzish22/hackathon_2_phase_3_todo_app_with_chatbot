"""
API dependencies for authentication and authorization.
Provides dependency injection for JWT verification and user extraction.
"""
from typing import Optional
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..core.security import verify_jwt
from ..core.errors import AppException, ERROR_MISSING_TOKEN


# HTTP Bearer token security scheme
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> str:
    """
    Dependency to get the current authenticated user ID from JWT token.

    Args:
        credentials: HTTP Bearer credentials from Authorization header (optional)

    Returns:
        str: Authenticated user ID (from JWT 'sub' claim)

    Raises:
        AppException: 401 with specific error code:
            - MISSING_TOKEN: No Authorization header provided
            - TOKEN_EXPIRED: JWT exp claim is in the past
            - INVALID_TOKEN: Malformed JWT, invalid signature, or missing claims
    """
    # Check if Authorization header is present
    if not credentials:
        raise AppException(
            status_code=401,
            error_code=ERROR_MISSING_TOKEN,
            message="Authentication required. Please sign in."
        )

    # Verify JWT and extract user ID
    token = credentials.credentials
    payload = verify_jwt(token)

    # Return user ID from 'sub' claim
    return payload["sub"]
