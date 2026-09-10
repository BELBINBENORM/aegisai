import json
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.database.models.memory import Memory as MemoryModel
from app.memory.models import Memory
from app.memory.store import MemoryStore


class SQLAlchemyMemoryStore(MemoryStore):
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        self.session_factory = session_factory

    async def save(self, memory: Memory) -> None:
        async with self.session_factory() as session:
            model = MemoryModel(
                id=memory.id,
                user_id=int(memory.user_id),
                content=memory.content,
                metadata_json=json.dumps(memory.metadata),
                created_at=memory.created_at,
            )

            session.add(model)
            await session.commit()

    async def get(self, memory_id: str) -> Memory | None:
        async with self.session_factory() as session:
            result = await session.execute(
                select(MemoryModel).where(
                    MemoryModel.id == memory_id
                )
            )
            model = result.scalar_one_or_none()

            if model is None:
                return None

            return self._to_domain(model)

    async def list(self, user_id: str) -> List[Memory]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(MemoryModel)
                .where(MemoryModel.user_id == int(user_id))
                .order_by(MemoryModel.created_at)
            )

            return [
                self._to_domain(model)
                for model in result.scalars().all()
            ]

    async def search(
        self,
        user_id: str,
        query: str,
    ) -> List[Memory]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(MemoryModel)
                .where(
                    MemoryModel.user_id == int(user_id),
                    MemoryModel.content.ilike(f"%{query}%"),
                )
                .order_by(MemoryModel.created_at)
            )

            return [
                self._to_domain(model)
                for model in result.scalars().all()
            ]

    @staticmethod
    def _to_domain(model: MemoryModel) -> Memory:
        return Memory(
            id=model.id,
            user_id=str(model.user_id),
            content=model.content,
            metadata=json.loads(model.metadata_json),
            created_at=model.created_at,
        )