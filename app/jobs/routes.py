import asyncio
import uuid

from fastapi import APIRouter, HTTPException

from app.jobs.manager import job_manager


router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("")
async def create_job():
    job_id = str(uuid.uuid4())

    async def job():
        await asyncio.sleep(1)

    job_manager.submit(job_id, job)

    return {
        "job_id": job_id,
        "status": "submitted",
    }


@router.get("/{job_id}")
async def get_job(job_id: str):
    result = job_manager.get_status(job_id)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    return {
        "job_id": job_id,
        **result,
    }