"""
Redis configuration module.

Handles:
- Redis connection
- Token blacklisting
- Blacklist checking
"""

from redis.asyncio import Redis
from app.core.config import settings


# --------------------------------------------------
# Redis Client
# --------------------------------------------------

redis_client = Redis.from_url(
    settings.REDIS_URL,
    encoding="utf-8",
    decode_responses=True
)


# --------------------------------------------------
# Add Token to Blacklist
# --------------------------------------------------

async def blacklist_token(token: str, expires_in: int):
    """
    Add token to Redis blacklist.
    expires_in = seconds until token naturally expires
    Redis auto deletes it after that time.
    """
    await redis_client.setex(
        f"blacklist:{token}",  # key
        expires_in,            # TTL in seconds
        "true"                 # value (doesn't matter)
    )


# --------------------------------------------------
# Check if Token is Blacklisted
# --------------------------------------------------

async def is_token_blacklisted(token: str) -> bool:
    """
    Check if token exists in Redis blacklist.
    Returns True if blacklisted, False if valid.
    """
    value = await redis_client.get(f"blacklist:{token}")
    return value is not None