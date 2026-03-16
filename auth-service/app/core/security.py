"""
Security utilities module.

Handles:
- Password hashing
- Password verification
- JWT token creation
- JWT token decoding
"""

from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings


# --------------------------------------------------
# Password Hashing Configuration
# --------------------------------------------------

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


# --------------------------------------------------
# Hash Password
# --------------------------------------------------

def hash_password(password: str) -> str:
    """
    Convert plain password into a secure hashed password.

    We never store plain passwords in the database.
    """
    return pwd_context.hash(password)


# --------------------------------------------------
# Verify Password
# --------------------------------------------------

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Compare user password with stored hashed password.
    """
    return pwd_context.verify(plain_password, hashed_password)


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
# Decode JWT Token
# --------------------------------------------------

def decode_access_token(token: str):
    """
    Decode JWT token and return payload.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None