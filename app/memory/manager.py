from datetime import datetime, timezone
from typing import Any, List
from uuid import uuid4

from app.memory.local_store import LocalMemoryStore
from app.memory.models import Memory
from app.memory.store import MemoryStore


class MemoryManager:
    def __init__(
        self,
        store: MemoryStore | None = None,
    ) -> None:
        self.store = store or LocalMemoryStore()

    async def remember(
        self,
        user_id: str,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> Memory:
        memory = Memory(
            id=str(uuid4()),
            user_id=user_id,
            content=content,
            metadata=metadata or {},
            created_at=datetime.now(timezone.utc),
        )

        await self.store.save(memory)
        return memory

    async def get(self, memory_id: str) -> Memory | None:
        return await self.store.get(memory_id)

    async def list(self, user_id: str) -> List[Memory]:
        return await self.store.list(user_id)

    async def search(
        self,
        user_id: str,
        query: str,
    ) -> List[Memory]:
        return await self.store.search(user_id, query)