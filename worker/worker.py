import asyncio
from datetime import datetime,timezone
from app.jobs.manager import get_queued
from app.database.connection import AsyncSessionLocal
from app.database.models import Job
from app.rag.ingestion import ingest_document
from app.config.settings import settings
async def main():
    while True:
        item=await get_queued()
        if not item: await asyncio.sleep(1); continue
        async with AsyncSessionLocal() as db:
            job=await db.get(Job,item["job_id"])
            if not job: continue
            job.status="running"; job.started_at=datetime.now(timezone.utc); await db.commit()
            try:
                if item["type"]=="document_ingestion": await ingest_document(db,item["payload"]["document_id"],settings.object_storage_dir)
                job.status="completed"; job.progress=100; job.completed_at=datetime.now(timezone.utc)
            except Exception as e:
                job.status="failed"; job.error=str(e); job.completed_at=datetime.now(timezone.utc)
            await db.commit()
if __name__=="__main__": asyncio.run(main())
