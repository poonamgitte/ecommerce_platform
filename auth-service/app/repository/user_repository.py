"""
User Repository Layer

Responsible only for database operations.

Repository layer isolates database logic from
business logic (services layer).

This makes the code:
- easier to maintain
- easier to test
- easier to change database later
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User


# ----------------------------------
# Create User
# ----------------------------------

async def create_user(
    db: AsyncSession,
    email: str,
    password_hash: str,
    role: str = "customer"
) -> User:
    """
    Create a new user in the database
    """

    new_user = User(
        email=email,
        password_hash=password_hash,
        role=role
    )

    db.add(new_user)

    # commit changes
    await db.commit()

    # refresh instance to get DB values
    await db.refresh(new_user)

    return new_user


# ----------------------------------
# Get User by Email
# ----------------------------------

async def get_user_by_email(
    db: AsyncSession,
    email: str
) -> User | None:
    """
    Fetch user using email
    """

    result = await db.execute(
        select(User).where(User.email == email)
    )

    return result.scalar_one_or_none()


# ----------------------------------
# Get User by ID
# ----------------------------------

async def get_user_by_id(
    db: AsyncSession,
    user_id
) -> User | None:
    """
    Fetch user using UUID
    """

    result = await db.execute(
        select(User).where(User.id == user_id)
    )

    return result.scalar_one_or_none()