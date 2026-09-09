import pytest

from app.agents.tool import Tool


class EchoTool(Tool):
    name = "echo"
    description = "Echo a message."
    parameters = {
        "type": "object",
        "properties": {
            "message": {
                "type": "string",
                "description": "Message to echo.",
            }
        },
        "required": ["message"],
    }

    async def execute(self, **kwargs):
        return kwargs["message"]


@pytest.mark.asyncio
async def test_tool_execution():
    tool = EchoTool()

    result = await tool.execute(message="hello")

    assert result == "hello"


def test_tool_function_declaration():
    tool = EchoTool()

    declaration = tool.function_declaration

    assert declaration["name"] == "echo"
    assert declaration["description"] == "Echo a message."
    assert declaration["parameters"]["type"] == "object"