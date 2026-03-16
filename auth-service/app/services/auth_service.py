"""
Authentication Service Layer

Contains the business logic for authentication.

Responsibilities:
- Register users
- Login users
- Validate credentials
- Generate JWT tokens
"""

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from datetime import timedelta

from app.repository import user_repository
from app.schemas.user import UserCreate, UserLogin
from app.schemas.token import Token

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token
)

from app.core.config import settings


# -----------------------------------
# Register User
# -----------------------------------

async def register_user(
    user_data: UserCreate,
    db: AsyncSession
):

    # Check if email already exists
    existing_user = await user_repository.get_user_by_email(
        db,
        user_data.email
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash password
    hashed_password = hash_password(user_data.password)

    # Create user
    new_user = await user_repository.create_user(
        db=db,
        email=user_data.email,
        password_hash=hashed_password
    )

    return new_user


# -----------------------------------
# Login User
# -----------------------------------

async def login_user(
    user_data: UserLogin,
    db: AsyncSession
) -> Token:

    # Find user by email
    user = await user_repository.get_user_by_email(
        db,
        user_data.email
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Verify password
    if not verify_password(
        user_data.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Check if account active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    # Token payload
    token_data = {
        "sub": str(user.id),
        "role": user.role
    }

    # Token expiration
    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    # Generate JWT
    access_token = create_access_token(
        data=token_data,
        expires_delta=access_token_expires
    )

    return Token(
        access_token=access_token,
        token_type="bearer"
    )