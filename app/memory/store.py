from abc import ABC, abstractmethod
from typing import List

from app.memory.models import Memory


class MemoryStore(ABC):
    @abstractmethod
    async def save(self, memory: Memory) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get(self, memory_id: str) -> Memory | None:
        raise NotImplementedError

    @abstractmethod
    async def list(self, user_id: str) -> List[Memory]:
        raise NotImplementedError

    @abstractmethod
    async def search(self, user_id: str, query: str) -> List[Memory]:
        raise NotImplementedError
