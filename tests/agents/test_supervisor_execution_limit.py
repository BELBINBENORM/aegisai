import pytest

from app.agents.execution_limiter import ExecutionLimiter
from app.agents.supervisor import Supervisor


class MockAgent:
    def __init__(self):
        self.calls = 0

    async def run(self, query, **kwargs):
        self.calls += 1
        return "result"


@pytest.mark.asyncio
async def test_supervisor_respects_execution_limit():
    agent = MockAgent()

    supervisor = Supervisor(
        agents={"research": agent},
        execution_limiter=ExecutionLimiter(max_attempts=1),
    )

    state = await supervisor.run("research something")

    assert agent.calls == 1
    assert state.error is None