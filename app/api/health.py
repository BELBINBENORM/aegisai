from fastapi import APIRouter
from sqlalchemy import text
from app.database.connection import AsyncSessionLocal
from app.cache.redis import get_redis
router=APIRouter()
@router.get("/health")
async def health():
    db_ok=False; redis_ok=False
    try:
        async with AsyncSessionLocal() as db: await db.execute(text("SELECT 1")); db_ok=True
    except Exception: pass
    try: redis_ok=bool(await get_redis())
    except Exception: pass
    return {"status":"ok" if db_ok else "degraded","database":db_ok,"redis":redis_ok}
