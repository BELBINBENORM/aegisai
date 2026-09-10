import os
import redis.asyncio as redis

REDIS_URL = os.getenv("REDIS_URL")

redis_client = redis.from_url(REDIS_URL) if REDIS_URL else None


async def get_redis():
    if redis_client is None:
        return None

    try:
        await redis_client.ping()
        return redis_client
    except Exception:
        return None