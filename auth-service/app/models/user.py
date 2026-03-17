"""
User model representing the users table.

This model stores authentication related information
for the ecommerce platform.
"""

import uuid

from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.core.database import Base


class User(Base):

    __tablename__ = "users"

    # --------------------------------------------------
    # Primary Key (UUID)
    # --------------------------------------------------
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )


    # --------------------------------------------------
    # User Email
    # --------------------------------------------------
    email = Column(
        String,
        unique=True,
        nullable=False,
        index=True
    )


    # --------------------------------------------------
    # Password Hash
    # --------------------------------------------------
    password_hash = Column(
        String,
        nullable=False
    )


    # --------------------------------------------------
    # Role
    # --------------------------------------------------
    role = Column(
        String,
        default="customer",
        nullable=False
    )


    # --------------------------------------------------
    # Account Status
    # --------------------------------------------------
    is_active = Column(
        Boolean,
        default=True
    )


    # --------------------------------------------------
    # Created Timestamp
    # --------------------------------------------------
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )


    # --------------------------------------------------
    # Updated Timestamp
    # --------------------------------------------------
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )