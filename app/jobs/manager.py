import asyncio
from collections.abc import Awaitable, Callable


class JobManager:
    def __init__(self) -> None:
        self.jobs: dict[str, asyncio.Task] = {}

    def submit(
        self,
        job_id: str,
        job: Callable[[], Awaitable[None]],
    ) -> None:
        task = asyncio.create_task(job())
        self.jobs[job_id] = task

        task.add_done_callback(
            lambda _: self.jobs.pop(job_id, None)
        )

    def is_running(self, job_id: str) -> bool:
        task = self.jobs.get(job_id)
        return task is not None and not task.done()


job_manager = JobManager()