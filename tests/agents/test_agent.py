import pytest

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


class MockToolRunner(ToolRunner):
    async def run(self, prompt, tools):
        return "hello from agent"


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

    assert state.final_answer == "hello from agent"
    assert state.error is None
    assert state.step_count == 1


@pytest.mark.asyncio
async def test_agent_handles_tool_error():
    class FailingToolRunner(ToolRunner):
        async def run(self, prompt, tools):
            raise RuntimeError("tool failed")

    agent = Agent(tool_runner=FailingToolRunner())

    state = await agent.run(
        query="test",
        tools=[EchoTool()],
    )

    assert state.final_answer is None
    assert state.error == "tool failed"

@pytest.mark.asyncio
async def test_agent_respects_step_limit():
    class NoResultToolRunner(ToolRunner):
        async def run(self, prompt, tools):
            return None

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