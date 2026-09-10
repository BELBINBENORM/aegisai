import pytest

from app.agents.agent import Agent
from app.memory.manager import MemoryManager


class FakeResponse:
    function_calls = []
    text = "Answer"


class FakeToolRunner:
    async def generate_response(self, contents, tools):
        self.contents = contents
        return FakeResponse()


@pytest.mark.asyncio
async def test_agent_loads_matching_memories():
    memory_manager = MemoryManager()

    await memory_manager.remember(
        user_id="user-1",
        content="User likes Python.",
    )

    await memory_manager.remember(
        user_id="user-1",
        content="User likes cooking.",
    )

    runner = FakeToolRunner()

    agent = Agent(
        tool_runner=runner,
        memory_manager=memory_manager,
    )

    state = await agent.run(
        query="Python",
        tools=[],
        user_id="user-1",
    )

    assert state.memory_context.contents() == [
        "User likes Python.",
    ]

    assert {
        "role": "memory",
        "content": "User likes Python.",
    } in state.messages


@pytest.mark.asyncio
async def test_agent_without_user_id_does_not_load_memory():
    memory_manager = MemoryManager()

    await memory_manager.remember(
        user_id="user-1",
        content="User likes Python.",
    )

    agent = Agent(
        tool_runner=FakeToolRunner(),
        memory_manager=memory_manager,
    )

    state = await agent.run(
        query="Python",
        tools=[],
    )

    assert state.memory_context.memories == []