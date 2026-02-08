"""
Security utilities for JWT verification and authentication.
Handles JWT token validation, password hashing, and token creation.
"""
from jose import JWTError, jwt, ExpiredSignatureError
from passlib.context import CryptContext
from datetime import datetime, timedelta
from .config import settings
from .errors import AppException, ERROR_TOKEN_EXPIRED, ERROR_INVALID_TOKEN


# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a plain text password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        str: Hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a hashed password.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password from database

    Returns:
        bool: True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: str, expires_delta: timedelta = None) -> str:
    """
    Create a JWT access token for a user.

    Args:
        user_id: User ID to encode in token
        expires_delta: Optional custom expiration time (default: 24 hours)

    Returns:
        str: Encoded JWT token
    """
    if expires_delta is None:
        expires_delta = timedelta(hours=24)

    expire = datetime.utcnow() + expires_delta

    payload = {
        "sub": user_id,  # Subject (user ID)
        "exp": expire,   # Expiration time
        "iat": datetime.utcnow()  # Issued at
    }

    encoded_jwt = jwt.encode(
        payload,
        settings.BETTER_AUTH_SECRET,
        algorithm="HS256"
    )

    return encoded_jwt


def verify_jwt(token: str) -> dict:
    """
    Verify JWT token and return payload.

    Args:
        token: JWT token string

    Returns:
        dict: Token payload with validated claims

    Raises:
        AppException: 401 with specific error code (TOKEN_EXPIRED or INVALID_TOKEN)
    """
    try:
        # Decode and verify token
        payload = jwt.decode(
            token,
            settings.BETTER_AUTH_SECRET,
            algorithms=["HS256"]
        )

        # Validate required claims
        user_id: str = payload.get("sub")

        if not user_id:
            raise AppException(
                status_code=401,
                error_code=ERROR_INVALID_TOKEN,
                message="Invalid authentication token. Please sign in again."
            )

        return payload

    except ExpiredSignatureError:
        raise AppException(
            status_code=401,
            error_code=ERROR_TOKEN_EXPIRED,
            message="Your session has expired. Please sign in again."
        )
    except JWTError:
        raise AppException(
            status_code=401,
            error_code=ERROR_INVALID_TOKEN,
            message="Invalid authentication token. Please sign in again."
        )
