from sqlalchemy import select,delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import Memory
class MemoryService:
    async def add(self,db,user_id,session_id,content,importance=.5):
        m=Memory(user_id=user_id,session_id=session_id,content=content,importance=importance); db.add(m); await db.commit(); return m
    async def recent(self,db,user_id,session_id,limit=6):
        return list((await db.execute(select(Memory).where(Memory.user_id==user_id,Memory.session_id==session_id).order_by(Memory.created_at.desc()).limit(limit))).scalars().all())
    async def cleanup(self,db,user_id,max_items=100):
        rows=(await db.execute(select(Memory).where(Memory.user_id==user_id).order_by(Memory.created_at.desc()))).scalars().all()
        for m in rows[max_items:]: await db.delete(m)
        await db.commit()
