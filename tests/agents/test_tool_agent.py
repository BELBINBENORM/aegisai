import pytest

from app.agents.tool_agent import ToolAgent
from app.agents.state import AgentState
from app.agents.tool_provider import ToolProvider


class MockAgent:
    async def run(self, query, tools):
        return AgentState(
            query=query,
            final_answer="tool result",
        )


class MockToolProvider(ToolProvider):
    async def get_tools(self):
        return []


@pytest.mark.asyncio
async def test_tool_agent():
    agent = ToolAgent(
        agent=MockAgent(),
        tool_provider=MockToolProvider(),
    )

    state = await agent.run(
        query="Calculate something",
    )

    assert state.query == "Calculate something"
    assert state.final_answer == "tool result"