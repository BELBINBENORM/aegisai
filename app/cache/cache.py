from app.cache.redis import get_redis


async def get_cached(key: str):
    client = await get_redis()

    if client is None:
        return None

    return await client.get(key)


async def set_cached(key: str, value: str, expire: int = 300):
    client = await get_redis()

    if client is None:
        return

    await client.set(key, value, ex=expire)


async def delete_cached(key: str):
    client = await get_redis()

    if client is None:
        return

    await client.delete(key)