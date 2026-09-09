from abc import ABC, abstractmethod


class AgentRouter(ABC):
    @abstractmethod
    async def route(self, query: str) -> str:
        raise NotImplementedError