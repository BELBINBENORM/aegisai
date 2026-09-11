import redis.asyncio as redis

from app.config.settings import settings


redis_client = (
    redis.from_url(settings.redis_url)
    if settings.redis_url
    else None
)


async def get_redis():
    if redis_client is None:
        return None

    try:
        await redis_client.ping()
        return redis_client
    except Exception:
        return None