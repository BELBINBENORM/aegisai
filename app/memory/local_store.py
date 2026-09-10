from typing import List

from app.memory.models import Memory
from app.memory.store import MemoryStore


class LocalMemoryStore(MemoryStore):
    def __init__(self) -> None:
        self._memories: dict[str, Memory] = {}

    async def save(self, memory: Memory) -> None:
        self._memories[memory.id] = memory

    async def get(self, memory_id: str) -> Memory | None:
        return self._memories.get(memory_id)

    async def list(self, user_id: str) -> List[Memory]:
        return [
            memory
            for memory in self._memories.values()
            if memory.user_id == user_id
        ]

    async def search(self, user_id: str, query: str) -> List[Memory]:
        query = query.lower()

        return [
            memory
            for memory in self._memories.values()
            if memory.user_id == user_id
            and query in memory.content.lower()
        ]
