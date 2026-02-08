"""
Authentication routes for user signup, signin, and profile.
Provides JWT-based authentication endpoints.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from ...core.database import get_db
from ...core.security import hash_password, verify_password, create_access_token
from ...core.errors import AppException, ERROR_EMAIL_EXISTS, ERROR_USER_NOT_FOUND
from ...models.user import User
from ...schemas.auth import SignupRequest, SigninRequest, AuthResponse, UserResponse
from ..dependencies import get_current_user


router = APIRouter()


@router.post(
    "/signup",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with email and password. Returns JWT token for immediate authentication.",
)
async def signup(
    request: SignupRequest,
    session: AsyncSession = Depends(get_db)
):
    """
    Register a new user account.

    - **email**: Valid email address (must be unique)
    - **password**: Minimum 8 characters
    - **name**: Optional user's full name

    Returns JWT access token valid for 24 hours.
    """
    # Check if email already exists
    statement = select(User).where(User.email == request.email)
    result = await session.execute(statement)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise AppException(
            status_code=400,
            error_code=ERROR_EMAIL_EXISTS,
            message="An account with this email already exists"
        )

    # Create new user
    hashed_password = hash_password(request.password)

    new_user = User(
        email=request.email,
        password_hash=hashed_password,
        name=request.name,
        email_verified=False
    )

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    # Generate JWT token
    access_token = create_access_token(new_user.id)

    # Return auth response
    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=new_user.id,
            email=new_user.email,
            name=new_user.name,
            email_verified=new_user.email_verified,
            created_at=new_user.created_at
        )
    )


@router.post(
    "/signin",
    response_model=AuthResponse,
    summary="Sign in to existing account",
    description="Authenticate with email and password. Returns JWT token for API access.",
)
async def signin(
    request: SigninRequest,
    session: AsyncSession = Depends(get_db)
):
    """
    Sign in to an existing account.

    - **email**: Registered email address
    - **password**: Account password

    Returns JWT access token valid for 24 hours.
    """
    # Find user by email
    statement = select(User).where(User.email == request.email)
    result = await session.execute(statement)
    user = result.scalar_one_or_none()

    # Check if user exists and password is correct
    if not user or not verify_password(request.password, user.password_hash):
        raise AppException(
            status_code=401,
            error_code="INVALID_CREDENTIALS",
            message="Invalid email or password"
        )

    # Generate JWT token
    access_token = create_access_token(user.id)

    # Return auth response
    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            email_verified=user.email_verified,
            created_at=user.created_at
        )
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
    description="Get authenticated user's profile information. Requires valid JWT token.",
)
async def get_me(
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Get current authenticated user's profile.

    Requires Authorization header with Bearer token:
    ```
    Authorization: Bearer <your_jwt_token>
    ```
    """
    # Fetch user from database
    statement = select(User).where(User.id == user_id)
    result = await session.execute(statement)
    user = result.scalar_one_or_none()

    if not user:
        raise AppException(
            status_code=404,
            error_code=ERROR_USER_NOT_FOUND,
            message="User not found"
        )

    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        email_verified=user.email_verified,
        created_at=user.created_at
    )
