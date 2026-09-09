import pytest

from app.agents.tool import Tool
from app.agents.tool_runner import ToolRunner
from app.llm.function_calling import FunctionCallingClient


class EchoTool(Tool):
    name = "echo"
    description = "Echo a message."

    parameters = {
        "type": "object",
        "properties": {
            "message": {"type": "string"},
        },
        "required": ["message"],
    }

    async def execute(self, **kwargs):
        return kwargs["message"]


class MockFunctionCall:
    name = "echo"
    args = {"message": "hello"}


@pytest.mark.asyncio
async def test_tool_runner(monkeypatch):
    async def mock_generate_function_call(
        self,
        prompt,
        function_declarations,
        model="gemini-3.6-flash",
    ):
        return MockFunctionCall()

    monkeypatch.setattr(
        FunctionCallingClient,
        "generate_function_call",
        mock_generate_function_call,
    )

    runner = ToolRunner()
    tool = EchoTool()

    result = await runner.run(
        prompt="Echo hello",
        tools=[tool],
    )

    assert result == "hello"