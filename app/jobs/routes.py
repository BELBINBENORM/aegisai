import uuid

from fastapi import APIRouter

from app.jobs.manager import job_manager

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("")
async def create_job():
    job_id = str(uuid.uuid4())

    async def job():
        # Placeholder for background work.
        return None

    job_manager.submit(job_id, job)

    return {
        "job_id": job_id,
        "status": "submitted",
    }


@router.get("/{job_id}")
async def get_job(job_id: str):
    return {
        "job_id": job_id,
        "status": "running" if job_manager.is_running(job_id) else "completed",
    }