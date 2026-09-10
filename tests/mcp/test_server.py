import pytest

from app.agents.tool import Tool
from app.mcp.server import MCPServer
from app.mcp.resource import MCPResource
from app.mcp.prompt import MCPPrompt


class EchoTool(Tool):
    name = "echo"
    description = "Echo text"
    parameters = {
        "type": "object",
        "properties": {
            "text": {"type": "string"},
        },
        "required": ["text"],
    }

    async def execute(self, **kwargs):
        return kwargs["text"]


def test_register_and_list_tools():
    server = MCPServer()
    server.register_tool(EchoTool())

    tools = server.list_tools()

    assert len(tools) == 1
    assert tools[0]["name"] == "echo"


@pytest.mark.asyncio
async def test_call_tool():
    server = MCPServer()
    server.register_tool(EchoTool())

    result = await server.call_tool(
        "echo",
        {"text": "hello"},
    )

    assert result == "hello"


@pytest.mark.asyncio
async def test_call_unknown_tool():
    server = MCPServer()

    with pytest.raises(ValueError, match="Unknown tool"):
        await server.call_tool("missing", {})


def test_register_and_read_resource():
    server = MCPServer()

    resource = MCPResource(
        uri="config://app",
        name="App config",
        content={"environment": "test"},
    )

    server.register_resource(resource)

    assert server.list_resources() == [
        {
            "uri": "config://app",
            "name": "App config",
            "content": {"environment": "test"},
        }
    ]

    assert server.read_resource("config://app") == {
        "environment": "test"
    }

def test_register_and_render_prompt():
    server = MCPServer()

    prompt = MCPPrompt(
        name="greeting",
        template="Hello, {name}!",
    )

    server.register_prompt(prompt)

    assert server.list_prompts() == [
        {
            "name": "greeting",
            "template": "Hello, {name}!",
        }
    ]

    assert server.get_prompt(
        "greeting",
        {"name": "Alice"},
    ) == "Hello, Alice!"