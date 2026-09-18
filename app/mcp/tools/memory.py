from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import Message,Memory
async def get_chat_history(db:AsyncSession,session_id:int,limit:int=20):
    rows=(await db.execute(select(Message).where(Message.session_id==session_id).order_by(Message.created_at.desc()).limit(limit))).scalars().all()
    return [{"role":r.role,"content":r.content} for r in reversed(rows)]
async def get_memories(db:AsyncSession,user_id:int,session_id:int,limit:int=6):
    rows=(await db.execute(select(Memory).where(Memory.user_id==user_id,Memory.session_id==session_id).order_by(Memory.created_at.desc()).limit(limit))).scalars().all()
    return [{"id":r.id,"content":r.content} for r in rows]
