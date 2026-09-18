import hashlib, hmac
from fastapi import Header, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.settings import settings
from app.database.connection import get_db
from app.database.models import User

async def verify_api_key(x_api_key: str | None = Header(default=None)) -> None:
    if not x_api_key or not settings.api_key or not hmac.compare_digest(x_api_key, settings.api_key):
        raise HTTPException(401, "Invalid or missing API key")

async def get_current_user_id(x_api_key: str | None = Header(default=None), db: AsyncSession = Depends(get_db)) -> int:
    await verify_api_key(x_api_key)
    credential_id = hashlib.sha256(x_api_key.encode()).hexdigest()[:32]
    email = f"api-{credential_id}@aegisai.local"
    user = (await db.execute(select(User).where(User.email == email))).scalar_one_or_none()
    if not user:
        user = User(email=email); db.add(user); await db.commit(); await db.refresh(user)
    return user.id
