import pytest

from app.agents.evaluator import Evaluation
from app.agents.reflector import Reflection
from app.agents.loop_detector import LoopDetector
from app.agents.supervisor import Supervisor


class MockAgent:
    def __init__(self):
        self.calls = []

    async def run(self, query, **kwargs):
        self.calls.append(query)
        return "insufficient result"


class MockEvaluator:
    async def evaluate(self, query, result):
        return Evaluation(
            sufficient=False,
            reason="Still insufficient.",
        )


class MockReflector:
    async def reflect(self, query, result, reason):
        return Reflection(
            analysis="Same task is being repeated.",
            revised_task="research something",
        )


@pytest.mark.asyncio
async def test_supervisor_detects_reflection_loop():
    agent = MockAgent()

    supervisor = Supervisor(
        agents={"research": agent},
        evaluator=MockEvaluator(),
        reflector=MockReflector(),
        loop_detector=LoopDetector(max_repeats=1),
        max_reflections=5,
    )

    state = await supervisor.run("research something")

    assert len(agent.calls) == 1
    assert state.error == "Loop detected for task: research something"