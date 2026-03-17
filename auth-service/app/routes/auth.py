"""
Authentication API Routes
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.schemas.token import Token, RefreshTokenRequest

from app.services import auth_service
from app.core.database import get_db

from app.core.security import oauth2_scheme


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# ----------------------------------
# Register User
# ----------------------------------

@router.post(
    "/register",
    response_model=UserResponse
)
async def register_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):

    return await auth_service.register_user(
        user_data,
        db
    )


# ----------------------------------
# Login User
# ----------------------------------

@router.post(
    "/login",
    response_model=Token
)
async def login_user(
    user_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):

    return await auth_service.login_user(
        user_data,
        db
    )
    
# ----------------------------------
# Refresh Token
# ----------------------------------

@router.post(
    "/refresh",
    response_model=Token
)
async def refresh_token(
    token_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    return await auth_service.refresh_access_token(
        token_data.refresh_token,
        db
    )


# ----------------------------------
# Logout User
# ----------------------------------

@router.post("/logout")
async def logout(
    token: str = Depends(oauth2_scheme)
):
    return await auth_service.logout_user(token)