import asyncio

import pytest

from app.agents.parallel import ParallelAgentExecutor


@pytest.mark.asyncio
async def test_parallel_agents():
    executor = ParallelAgentExecutor()

    async def task_one():
        await asyncio.sleep(0.01)
        return "rag result"

    async def task_two():
        await asyncio.sleep(0.01)
        return "research result"

    results = await executor.run(
        [
            task_one(),
            task_two(),
        ]
    )

    assert results == [
        "rag result",
        "research result",
    ]


@pytest.mark.asyncio
async def test_parallel_agents_empty():
    executor = ParallelAgentExecutor()

    results = await executor.run([])

    assert results == []

@pytest.mark.asyncio
async def test_parallel_agents_handles_failure():
    executor = ParallelAgentExecutor()

    async def successful_task():
        return "success"

    async def failing_task():
        raise RuntimeError("agent failed")

    results = await executor.run(
        [
            successful_task(),
            failing_task(),
        ]
    )

    assert results[0] == "success"
    assert isinstance(results[1], RuntimeError)
    assert str(results[1]) == "agent failed"