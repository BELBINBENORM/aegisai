import pytest
from unittest.mock import AsyncMock, patch

from app.agents.agent import Agent
from app.agents.tool import Tool
from app.agents.tool_runner import ToolRunner


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


class MockResponse:
    function_calls = None
    text = "hello from Gemini"


class MockToolRunner(ToolRunner):
    async def generate_response(self, contents, tools):
        return MockResponse()


@pytest.mark.asyncio
async def test_agent_run():
    agent = Agent(
        tool_runner=MockToolRunner(),
        max_steps=3,
    )

    state = await agent.run(
        query="Say hello",
        tools=[EchoTool()],
    )

    assert state.final_answer == "hello from Gemini"
    assert state.error is None
    assert state.step_count == 1


@pytest.mark.asyncio
async def test_agent_handles_tool_error():
    class FailingTool(Tool):
        name = "failing"
        description = "Fails."
        parameters = {
            "type": "object",
            "properties": {},
        }

        async def execute(self, **kwargs):
            raise RuntimeError("tool failed")

    class ToolCall:
        name = "failing"
        args = {}

    class ToolResponse:
        function_calls = [ToolCall()]
        text = None

    class FailingToolRunner(ToolRunner):
        async def generate_response(self, contents, tools):
            return ToolResponse()

    agent = Agent(tool_runner=FailingToolRunner())

    state = await agent.run(
        query="test",
        tools=[FailingTool()],
    )

    assert state.final_answer is None
    assert state.error == "tool failed"


@pytest.mark.asyncio
async def test_agent_respects_step_limit():
    class NoResponse:
        function_calls = None
        text = None

    class NoResultToolRunner(ToolRunner):
        async def generate_response(self, contents, tools):
            return NoResponse()

    agent = Agent(
        tool_runner=NoResultToolRunner(),
        max_steps=3,
    )

    state = await agent.run(
        query="test",
        tools=[EchoTool()],
    )

    assert state.step_count == 3
    assert state.final_answer is None
    assert state.error == "Agent reached the maximum step limit."


@pytest.mark.asyncio
async def test_agent_tool_call_loop():
    class ToolCall:
        name = "echo"
        args = {"message": "hello"}

    class ToolResponse:
        function_calls = [ToolCall()]
        text = None

    class FinalResponse:
        function_calls = None
        text = "The tool returned: hello"

    class LoopToolRunner(ToolRunner):
        def __init__(self):
            self.calls = 0

        async def generate_response(self, contents, tools):
            self.calls += 1

            if self.calls == 1:
                return ToolResponse()

            assert contents[-1]["role"] == "tool"
            assert contents[-1]["content"] == "hello"

            return FinalResponse()

    agent = Agent(
        tool_runner=LoopToolRunner(),
        max_steps=3,
    )

    state = await agent.run(
        query="Echo hello",
        tools=[EchoTool()],
    )

    assert state.final_answer == "The tool returned: hello"
    assert state.error is None
    assert state.step_count == 2
    assert len(state.tool_calls) == 1
    assert state.tool_calls[0]["name"] == "echo"


@pytest.mark.asyncio
async def test_agent_handles_unknown_tool():
    class ToolCall:
        name = "unknown_tool"
        args = {}

    class ToolResponse:
        function_calls = [ToolCall()]
        text = None

    class UnknownToolRunner(ToolRunner):
        async def generate_response(self, contents, tools):
            return ToolResponse()

    agent = Agent(tool_runner=UnknownToolRunner())

    state = await agent.run(
        query="Use the unknown tool",
        tools=[EchoTool()],
    )

    assert state.final_answer is None
    assert state.error == "Unknown tool requested: unknown_tool"


@pytest.mark.asyncio
async def test_agent_records_tool_arguments():
    class ToolCall:
        name = "echo"
        args = {"message": "record me"}

    class ToolResponse:
        function_calls = [ToolCall()]
        text = None

    class FinalResponse:
        function_calls = None
        text = "done"

    class RecordingToolRunner(ToolRunner):
        def __init__(self):
            self.calls = 0

        async def generate_response(self, contents, tools):
            self.calls += 1
            return ToolResponse() if self.calls == 1 else FinalResponse()

    agent = Agent(tool_runner=RecordingToolRunner())

    state = await agent.run(
        query="record this",
        tools=[EchoTool()],
    )

    assert state.final_answer == "done"
    assert state.tool_calls == [
        {
            "name": "echo",
            "arguments": {"message": "record me"},
        }
    ]

@pytest.mark.asyncio
async def test_agent_returns_cached_response():
    agent = Agent(
        memory_manager=None,
    )

    with patch(
        "app.agents.agent.get_cached",
        new=AsyncMock(return_value="cached answer"),
    ) as get_cached_mock, patch(
        "app.agents.agent.set_cached",
        new=AsyncMock(),
    ) as set_cached_mock:

        state = await agent.run(
            query="hello",
            tools=[],
            user_id="user-1",
        )

    assert state.final_answer == "cached answer"
    get_cached_mock.assert_awaited_once()
    set_cached_mock.assert_not_awaited()

@pytest.mark.asyncio
async def test_agent_generates_and_caches_response():
    agent = Agent(memory_manager=None)

    response = AsyncMock()
    response.function_calls = []
    response.text = "new answer"

    agent.tool_runner.generate_response = AsyncMock(
        return_value=response
    )

    with patch(
        "app.agents.agent.get_cached",
        new=AsyncMock(return_value=None),
    ), patch(
        "app.agents.agent.set_cached",
        new=AsyncMock(),
    ) as set_cached_mock:

        state = await agent.run(
            query="hello",
            tools=[],
            user_id="user-1",
        )

    assert state.final_answer == "new answer"
    set_cached_mock.assert_awaited_once()