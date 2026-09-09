import pytest

from app.agents.evaluator import Evaluation
from app.agents.supervisor import Supervisor


class MockAgent:
    def __init__(self, result):
        self.result = result

    async def run(self, query, **kwargs):
        return self.result


class MockEvaluator:
    def __init__(self, sufficient=True):
        self.sufficient = sufficient

    async def evaluate(self, query, result):
        return Evaluation(
            sufficient=self.sufficient,
            reason="Evaluation result",
        )


@pytest.mark.asyncio
async def test_supervisor_accepts_sufficient_result():
    supervisor = Supervisor(
        agents={
            "research": MockAgent("good result"),
        },
        evaluator=MockEvaluator(sufficient=True),
    )

    state = await supervisor.run("research something")

    assert state.agent_results["research"] == ["good result"]
    assert state.error is None


@pytest.mark.asyncio
async def test_supervisor_stops_on_insufficient_result():
    supervisor = Supervisor(
        agents={
            "research": MockAgent("weak result"),
        },
        evaluator=MockEvaluator(sufficient=False),
    )

    state = await supervisor.run("research something")

    assert state.agent_results["research"] == ["weak result"]
    assert state.error == "Evaluation result"