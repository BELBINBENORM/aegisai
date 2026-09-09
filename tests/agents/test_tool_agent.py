import pytest

from app.agents.state import AgentState
from app.agents.tool_agent import ToolAgent


class MockAgent:
    async def run(self, query, tools):
        return AgentState(
            query=query,
            final_answer="tool result",
        )


@pytest.mark.asyncio
async def test_tool_agent():
    agent = ToolAgent(agent=MockAgent())

    state = await agent.run(
        query="Use the calculator",
        tools=[],
    )

    assert state.query == "Use the calculator"
    assert state.final_answer == "tool result"