"""
Database configuration module (Async SQLAlchemy).

This file is responsible for:

1. Creating the asynchronous database engine
2. Creating async database sessions
3. Providing DB dependency for FastAPI routes
"""

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker
)

from sqlalchemy.orm import declarative_base

from app.core.config import settings


# --------------------------------------------------
# Create Async Database Engine
# --------------------------------------------------

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True  # prints SQL queries in logs (useful for debugging)
)


# --------------------------------------------------
# Async Session Factory
# --------------------------------------------------

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


# --------------------------------------------------
# Base Model Class
# --------------------------------------------------

# All SQLAlchemy models will inherit from this Base
Base = declarative_base()


# --------------------------------------------------
# Dependency for FastAPI
# --------------------------------------------------

async def get_db():
    """
    Provides a database session to FastAPI routes.

    FastAPI will automatically:
    - create a session for the request
    - close it after the request ends
    """

    async with AsyncSessionLocal() as session:
        yield session