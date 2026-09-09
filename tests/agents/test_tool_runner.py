from unittest import result

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
async def test_tool_runner_generate_response(monkeypatch):
    class MockResponse:
        text = "final answer"
        function_calls = None

    async def mock_generate_response(
        self,
        contents,
        function_declarations,
        model="gemini-3.6-flash",
    ):
        assert contents == [{"role": "user", "content": "hello"}]
        assert function_declarations[0]["name"] == "echo"
        return MockResponse()

    monkeypatch.setattr(
        FunctionCallingClient,
        "generate_response",
        mock_generate_response,
    )

    runner = ToolRunner()

    response = await runner.generate_response(
        contents=[{"role": "user", "content": "hello"}],
        tools=[EchoTool()],
    )

    assert response.text == "final answer"
    assert response.function_calls is None