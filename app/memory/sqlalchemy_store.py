from typing import List
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from app.database.models.memory import Memory as MemoryModel
from app.memory.models import Memory
from app.memory.store import MemoryStore
from app.rag.embeddings import generate_embedding

class SQLAlchemyMemoryStore(MemoryStore):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]): self.session_factory=session_factory
    async def save(self, memory: Memory) -> None:
        async with self.session_factory() as session:
            embedding=memory.embedding or await generate_embedding(memory.content)
            model=MemoryModel(id=memory.id,user_id=int(memory.user_id),content=memory.content,embedding=embedding,metadata_json=memory.metadata or {},created_at=memory.created_at)
            session.add(model); await session.commit()
    async def get(self,memory_id):
        async with self.session_factory() as session:
            model=(await session.execute(select(MemoryModel).where(MemoryModel.id==memory_id))).scalar_one_or_none()
            return self._to_domain(model) if model else None
    async def list(self,user_id: str)->List[Memory]:
        async with self.session_factory() as session:
            result=await session.execute(select(MemoryModel).where(MemoryModel.user_id==int(user_id)).order_by(MemoryModel.created_at)); return [self._to_domain(x) for x in result.scalars().all()]
    async def search(self,user_id,query,limit=5):
        async with self.session_factory() as session:
            q=await generate_embedding(query); distance=MemoryModel.embedding.cosine_distance(q)
            result=await session.execute(select(MemoryModel).where(MemoryModel.user_id==int(user_id),MemoryModel.embedding.is_not(None)).order_by(distance).limit(limit)); return [self._to_domain(x) for x in result.scalars().all()]
    @staticmethod
    def _to_domain(model):
        metadata=model.metadata_json or {}
        if isinstance(metadata,str):
            import json; metadata=json.loads(metadata)
        return Memory(id=model.id,user_id=str(model.user_id),content=model.content,metadata=metadata,created_at=model.created_at,embedding=list(model.embedding) if model.embedding else None)
    async def delete_older_than(self,user_id,before: datetime)->None:
        async with self.session_factory() as session:
            result=await session.execute(select(MemoryModel).where(MemoryModel.user_id==int(user_id),MemoryModel.created_at<before))
            for memory in result.scalars().all(): await session.delete(memory)
            await session.commit()
