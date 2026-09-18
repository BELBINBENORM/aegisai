import asyncio
from typing import Any, Awaitable


class ParallelAgentExecutor:
    async def run(
        self,
        tasks: list[Awaitable[Any]],
    ) -> list[Any]:
        if not tasks:
            return []

        return await asyncio.gather(
            *tasks,
            return_exceptions=True,
        )