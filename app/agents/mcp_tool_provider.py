from typing import Any

from app.agents.tool import Tool
from app.agents.tool_provider import ToolProvider
from app.mcp.client import MCPClient


class MCPTool(Tool):
    def __init__(
        self,
        client: MCPClient,
        name: str,
        description: str,
        parameters: dict[str, Any],
    ) -> None:
        self.client = client
        self.name = name
        self.description = description
        self.parameters = parameters

    async def execute(self, **kwargs: Any) -> Any:
        return await self.client.call_tool(
            self.name,
            kwargs,
        )


class MCPToolProvider(ToolProvider):
    def __init__(self, client: MCPClient) -> None:
        self.client = client

    async def get_tools(self) -> list[Tool]:
        definitions = await self.client.list_tools()

        return [
            MCPTool(
                client=self.client,
                name=tool["name"],
                description=tool.get("description", ""),
                parameters=tool.get(
                    "parameters",
                    {"type": "object"},
                ),
            )
            for tool in definitions
        ]