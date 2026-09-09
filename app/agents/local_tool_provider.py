from app.agents.tool import Tool
from app.agents.tool_provider import ToolProvider


class LocalToolProvider(ToolProvider):
    def __init__(self, tools: list[Tool] | None = None) -> None:
        self.tools = tools or []

    async def get_tools(self) -> list[Tool]:
        return self.tools