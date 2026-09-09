import pytest

from app.agents.evaluator import AgentEvaluator, Evaluation


@pytest.mark.asyncio
async def test_agent_evaluator():
    class MockClient:
        async def generate(self, prompt, response_schema):
            assert response_schema is Evaluation

            return Evaluation(
                sufficient=True,
                reason="The result answers the request.",
            )

    evaluator = AgentEvaluator(client=MockClient())

    result = await evaluator.evaluate(
        query="What is AegisAI?",
        result="AegisAI is an AI engineering project.",
    )

    assert result.sufficient is True
    assert result.reason == "The result answers the request."


@pytest.mark.asyncio
async def test_agent_evaluator_detects_insufficient_result():
    class MockClient:
        async def generate(self, prompt, response_schema):
            return Evaluation(
                sufficient=False,
                reason="The result does not contain enough information.",
            )

    evaluator = AgentEvaluator(client=MockClient())

    result = await evaluator.evaluate(
        query="Explain AegisAI architecture",
        result="AegisAI is an AI project.",
    )

    assert result.sufficient is False
    assert "not contain enough information" in result.reason