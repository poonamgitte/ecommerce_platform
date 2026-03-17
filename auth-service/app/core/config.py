"""
Application configuration module.

This file loads environment variables and makes them available
throughout the application using a centralized Settings object.

Using a central config class is an industry best practice because
it avoids using os.getenv() everywhere in the project.
"""

from pydantic_settings import BaseSettings
# from dotenv import load_dotenv

# # Load environment variables from .env file
# load_dotenv()


class Settings(BaseSettings):

    # -----------------------------
    # Database Configuration
    # -----------------------------
    DATABASE_URL: str
    # Example:
    # postgresql+asyncpg://postgres:password@localhost:5432/auth_db


    # -----------------------------
    # JWT Authentication Settings
    # -----------------------------
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    
    # Redis
    REDIS_URL: str

    class Config:
        env_file = ".env"


# Global settings object used across the application
settings = Settings()