from abc import ABC, abstractmethod

from app.agents.tool import Tool


class ToolProvider(ABC):
    @abstractmethod
    async def get_tools(self) -> list[Tool]:
        raise NotImplementedError