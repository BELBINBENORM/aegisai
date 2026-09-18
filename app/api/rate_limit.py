import time
from fastapi import HTTPException, Request
from app.cache.redis import get_redis
MAX_REQUESTS=60; WINDOW=60
_local={}
_requests = _local
async def rate_limit(request: Request):
    identity=(request.headers.get("X-API-Key") or "anonymous")[:64]
    r=await get_redis()
    if r:
        key=f"aegisai:rl:{identity}"
        n=await r.incr(key)
        if n==1: await r.expire(key, WINDOW)
        if n>MAX_REQUESTS: raise HTTPException(429,"Too many requests")
        return
    now=time.time(); values=[x for x in _local.get(identity,[]) if now-x<WINDOW]
    if len(values)>=MAX_REQUESTS: raise HTTPException(429,"Too many requests")
    values.append(now); _local[identity]=values
