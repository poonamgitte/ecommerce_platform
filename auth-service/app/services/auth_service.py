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

from app.repository import user_repository
from app.schemas.user import UserCreate, UserLogin
from app.schemas.token import Token
from datetime import datetime, timedelta, timezone

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_refresh_token
)

from app.core.config import settings

from app.core.redis import blacklist_token
from jose import jwt,JWTError


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

    # return Token(
    #     access_token=access_token,
    #     token_type="bearer"
    # )
    
    refresh_token = create_refresh_token(data=token_data)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )
    
    
# -----------------------------------
# Refresh Access Token
# -----------------------------------

async def refresh_access_token(
    refresh_token: str,
    db: AsyncSession
) -> Token:

    # Verify refresh token
    payload = verify_refresh_token(refresh_token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    # Get user id from payload
    user_id: str = payload.get("sub")

    # Get user from DB
    user = await user_repository.get_user_by_id(db, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    # Generate new tokens
    token_data = {
        "sub": str(user.id),
        "role": user.role
    }

    new_access_token = create_access_token(data=token_data)
    new_refresh_token = create_refresh_token(data=token_data)

    return Token(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer"
    )
    

# -----------------------------------
# Logout User
# -----------------------------------

async def logout_user(token: str) -> dict:

    try:
        # Decode token to get expiry (don't verify blacklist here)
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        # Get token expiry time
        exp = payload.get("exp")
        
        if exp:
            # Calculate remaining seconds until token expires
            now = datetime.now(timezone.utc).timestamp()
            expires_in = int(exp - now)

            if expires_in > 0:
                # Add to Redis blacklist with same TTL
                await blacklist_token(token, expires_in)

    except JWTError:
        pass  # Token already invalid, no need to blacklist

    return {"message": "Successfully logged out"}