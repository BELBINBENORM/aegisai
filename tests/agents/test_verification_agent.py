import pytest

from app.agents.state import AgentState
from app.agents.verification_agent import VerificationAgent


class MockAgent:
    async def run(self, query, tools):
        return AgentState(
            query=query,
            final_answer="verified result",
        )


@pytest.mark.asyncio
async def test_verification_agent():
    agent = VerificationAgent(agent=MockAgent())

    state = await agent.run(
        query="Verify this answer",
        tools=[],
    )

    assert state.query == "Verify this answer"
    assert state.final_answer == "verified result"