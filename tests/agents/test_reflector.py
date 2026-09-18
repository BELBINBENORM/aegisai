import pytest

from app.agents.reflector import AgentReflector, Reflection


@pytest.mark.asyncio
async def test_agent_reflector():
    class MockClient:
        async def generate(self, prompt, response_schema):
            assert response_schema is Reflection

            return Reflection(
                analysis="The result lacks technical details.",
                revised_task="Research the technical architecture in detail.",
            )

    reflector = AgentReflector(client=MockClient())

    result = await reflector.reflect(
        query="Explain the AegisAI architecture",
        result="AegisAI is an AI project.",
        reason="The result lacks enough technical detail.",
    )

    assert result.analysis == "The result lacks technical details."
    assert result.revised_task == (
        "Research the technical architecture in detail."
    )