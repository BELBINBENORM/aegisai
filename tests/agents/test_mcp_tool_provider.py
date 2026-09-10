import pytest

from app.agents.mcp_tool_provider import MCPToolProvider
from app.mcp.client import MCPClient


class MockMCPClient(MCPClient):
    async def list_tools(self):
        return [
            {
                "name": "echo",
                "description": "Echo text",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string"},
                    },
                },
            }
        ]

    async def call_tool(self, name, arguments):
        return arguments["text"]


@pytest.mark.asyncio
async def test_mcp_tool_provider_discovers_tools():
    provider = MCPToolProvider(
        MockMCPClient("http://localhost:8000")
    )

    tools = await provider.get_tools()

    assert len(tools) == 1
    assert tools[0].name == "echo"
    assert tools[0].description == "Echo text"


@pytest.mark.asyncio
async def test_mcp_tool_executes_through_client():
    provider = MCPToolProvider(
        MockMCPClient("http://localhost:8000")
    )

    tools = await provider.get_tools()

    result = await tools[0].execute(text="hello")

    assert result == "hello"