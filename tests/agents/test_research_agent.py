import pytest

from app.agents.research_agent import ResearchAgent
from app.agents.state import AgentState
from app.agents.tool_provider import ToolProvider


class MockAgent:
    async def run(self, query, tools):
        return AgentState(
            query=query,
            final_answer="research result",
        )


class MockToolProvider(ToolProvider):
    async def get_tools(self):
        return []


@pytest.mark.asyncio
async def test_research_agent():
    agent = ResearchAgent(
        agent=MockAgent(),
        tool_provider=MockToolProvider(),
    )

    state = await agent.run(
        query="Research AegisAI",
    )

    assert state.query == "Research AegisAI"
    assert state.final_answer == "research result"