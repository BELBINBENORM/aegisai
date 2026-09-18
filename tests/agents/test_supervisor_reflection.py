import pytest

from app.agents.evaluator import Evaluation
from app.agents.reflector import Reflection
from app.agents.supervisor import Supervisor


class MockAgent:
    def __init__(self):
        self.calls = []

    async def run(self, query, **kwargs):
        self.calls.append(query)

        if len(self.calls) == 1:
            return "insufficient result"

        return "improved result"


class MockEvaluator:
    def __init__(self):
        self.calls = 0

    async def evaluate(self, query, result):
        self.calls += 1

        if self.calls == 1:
            return Evaluation(
                sufficient=False,
                reason="Missing important information.",
            )

        return Evaluation(
            sufficient=True,
            reason="Result is sufficient.",
        )


class MockReflector:
    async def reflect(self, query, result, reason):
        return Reflection(
            analysis="The result needs more detail.",
            revised_task="Provide a detailed answer with the missing information.",
        )


@pytest.mark.asyncio
async def test_supervisor_reflects_and_retries():
    agent = MockAgent()

    supervisor = Supervisor(
        agents={"research": agent},
        evaluator=MockEvaluator(),
        reflector=MockReflector(),
    )

    state = await supervisor.run("research something")

    assert agent.calls == [
        "research something",
        "Provide a detailed answer with the missing information.",
    ]

    assert state.agent_results["research"] == [
        "insufficient result",
        "improved result",
    ]

    assert state.error is None


@pytest.mark.asyncio
async def test_supervisor_stops_after_reflection_limit():
    class AlwaysInsufficientEvaluator:
        async def evaluate(self, query, result):
            return Evaluation(
                sufficient=False,
                reason="Still insufficient.",
            )

    class CountingReflector:
        def __init__(self):
            self.calls = 0

        async def reflect(self, query, result, reason):
            self.calls += 1

            return Reflection(
                analysis="Need another attempt.",
                revised_task=f"Attempt {self.calls}",
            )

    agent = MockAgent()
    reflector = CountingReflector()

    supervisor = Supervisor(
        agents={"research": agent},
        evaluator=AlwaysInsufficientEvaluator(),
        reflector=reflector,
        max_reflections=2,
    )

    state = await supervisor.run("research something")

    assert len(agent.calls) == 3
    assert reflector.calls == 2
    assert state.error == "Still insufficient."