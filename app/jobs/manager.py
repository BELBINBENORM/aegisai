import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any


@dataclass
class Job:
    task: asyncio.Task[Any]
    status: str = "running"
    error: str | None = None


class JobManager:
    def __init__(self) -> None:
        self.jobs: dict[str, Job] = {}

    def submit(
        self,
        job_id: str,
        job: Callable[[], Awaitable[Any]],
    ) -> None:
        task = asyncio.create_task(self._run(job_id, job))
        self.jobs[job_id] = Job(task=task)
        
    def is_running(self, job_id: str) -> bool:
        job = self.jobs.get(job_id)

        if job is None:
            return False

        return job.status == "running"

    async def _run(
        self,
        job_id: str,
        job: Callable[[], Awaitable[Any]],
    ) -> None:
        try:
            await job()

            if job_id in self.jobs:
                self.jobs[job_id].status = "completed"

        except Exception as exc:
            if job_id in self.jobs:
                self.jobs[job_id].status = "failed"
                self.jobs[job_id].error = str(exc)

    def get_status(self, job_id: str) -> dict[str, Any] | None:
        job = self.jobs.get(job_id)

        if job is None:
            return None

        return {
            "status": job.status,
            "error": job.error,
        }


job_manager = JobManager()