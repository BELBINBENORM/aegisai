import asyncio

import pytest

from app.jobs.manager import JobManager


@pytest.mark.asyncio
async def test_job_manager_runs_job():
    manager = JobManager()
    completed = False

    async def job():
        nonlocal completed
        completed = True

    manager.submit("job-1", job)

    await asyncio.sleep(0)

    assert completed is True


@pytest.mark.asyncio
async def test_job_manager_tracks_running_job():
    manager = JobManager()

    finished = asyncio.Event()

    async def job():
        await finished.wait()

    manager.submit("job-1", job)

    await asyncio.sleep(0)

    assert manager.is_running("job-1") is True

    finished.set()
    await asyncio.sleep(0)

    assert manager.is_running("job-1") is False