"""
Security utilities module.

Handles:
- Password hashing
- Password verification
- JWT token creation
- JWT token decoding
"""

from datetime import datetime, timedelta, timezone
import bcrypt
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession


from app.core.config import settings
from app.core.database import get_db

# Add import at top
from app.core.redis import is_token_blacklisted


from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Request


http_bearer = HTTPBearer()

async def oauth2_scheme(credentials: HTTPAuthorizationCredentials = Depends(http_bearer)):
    return credentials.credentials

# --------------------------------------------------
# Hash Password
# --------------------------------------------------

def hash_password(password: str) -> str:
    """
    Convert plain password into a secure hashed password.

    We never store plain passwords in the database.
    """
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


# --------------------------------------------------
# Verify Password
# --------------------------------------------------

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Compare user password with stored hashed password.
    """
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


# --------------------------------------------------
# Create JWT Token
# --------------------------------------------------

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
    Generate JWT access token.

    Payload example:
    {
        "sub": "user_id",
        "role": "customer",
        "exp": expiry_time
    }
    """

    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return encoded_jwt

# --------------------------------------------------
# Create Refresh Token
# --------------------------------------------------

def create_refresh_token(data: dict):
    """
    Generate long lived refresh token (7 days).
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=7)
    to_encode.update({
        "exp": expire,
        "type": "refresh"  # distinguish from access token
    })
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )


# --------------------------------------------------
# Verify Refresh Token
# --------------------------------------------------

def verify_refresh_token(token: str):
    """
    Decode and verify refresh token.
    Returns payload if valid, None if invalid.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        # Make sure it's a refresh token not access token
        if payload.get("type") != "refresh":
            return None
        return payload
    except JWTError:
        return None


# --------------------------------------------------
# Decode JWT Token
# --------------------------------------------------
    
async def decode_access_token(token: str):
    """
    Decode JWT token and check blacklist.
    Now async because it checks Redis.
    """
    try:
        # Check blacklist first
        if await is_token_blacklisted(token):
            return None

        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None
    

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Now awaited because it checks Redis
    payload = await decode_access_token(token)

    if payload is None:
        raise credentials_exception

    user_id: str = payload.get("sub")

    if user_id is None:
        raise credentials_exception

    from app.repository import user_repository

    user = await user_repository.get_user_by_id(db, user_id)

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    return user