import json
from app.cache.redis import get_redis

async def get_cached(key: str):
    r = await get_redis()
    if not r:
        return None
    value = await r.get(key)
    if value is None:
        return None
    # Redis may contain legacy raw strings or JSON values.
    if not isinstance(value, (str, bytes, bytearray)):
        return value
    raw = value.decode() if isinstance(value, (bytes, bytearray)) else value
    try:
        return json.loads(raw)
    except (TypeError, json.JSONDecodeError):
        return raw

async def set_cached(key: str, value, expire: int):
    r = await get_redis()
    if not r:
        return
    # Preserve strings exactly; serialize structured values as JSON.
    payload = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
    await r.set(key, payload, ex=expire)

async def delete_cached(key: str):
    r = await get_redis()
    if r:
        await r.delete(key)

async def delete_prefix(prefix: str):
    r = await get_redis()
    if not r:
        return
    keys = [k async for k in r.scan_iter(match=prefix + '*')]
    if keys:
        await r.delete(*keys)
