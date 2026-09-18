from __future__ import annotations

from upstash_redis.asyncio import Redis

from app.config.settings import settings

_client: Redis | None = None


def _configured() -> bool:
    return bool(settings.upstash_redis_rest_url and settings.upstash_redis_rest_token)


async def get_redis() -> Redis | None:
    """Return the shared managed Redis client when Upstash is configured and reachable."""
    global _client

    if not _configured():
        return None

    if _client is None:
        _client = Redis(
            url=settings.upstash_redis_rest_url,
            token=settings.upstash_redis_rest_token,
        )

    try:
        await _client.ping()
    except Exception:
        return None

    return _client
