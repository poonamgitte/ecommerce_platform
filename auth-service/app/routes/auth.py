"""
Authentication API Routes
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.schemas.token import Token

from app.services import auth_service
from app.core.database import get_db


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