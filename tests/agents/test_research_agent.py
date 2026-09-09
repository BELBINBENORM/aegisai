import pytest

from app.agents.research_agent import ResearchAgent
from app.agents.state import AgentState


class MockAgent:
    async def run(self, query, tools):
        return AgentState(
            query=query,
            final_answer="research result",
        )


@pytest.mark.asyncio
async def test_research_agent():
    agent = ResearchAgent(agent=MockAgent())

    state = await agent.run(
        query="Research AegisAI",
        tools=[],
    )

    assert state.query == "Research AegisAI"
    assert state.final_answer == "research result"