import pytest

from app.agents.verification_agent import VerificationAgent
from app.agents.state import AgentState
from app.agents.tool_provider import ToolProvider


class MockAgent:
    async def run(self, query, tools):
        return AgentState(
            query=query,
            final_answer="verification result",
        )


class MockToolProvider(ToolProvider):
    async def get_tools(self):
        return []


@pytest.mark.asyncio
async def test_verification_agent():
    agent = VerificationAgent(
        agent=MockAgent(),
        tool_provider=MockToolProvider(),
    )

    state = await agent.run(
        query="Verify this answer",
    )

    assert state.query == "Verify this answer"
    assert state.final_answer == "verification result"