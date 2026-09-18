from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from app.api.auth import get_current_user_id
from app.database.connection import get_db
from app.database.models import Job, Document, Session
router=APIRouter(prefix='/jobs',tags=['jobs'])
@router.post('')
async def create_job(user_id=Depends(get_current_user_id), db=Depends(get_db)):
    job=Job(id=str(uuid4()),type='generic',status='queued',progress=0,payload={}); db.add(job); await db.commit(); await db.refresh(job)
    return {'job_id':job.id,'status':job.status}
@router.get('/{job_id}')
async def status(job_id:str,user_id=Depends(get_current_user_id),db=Depends(get_db)):
    job=(await db.execute(select(Job).where(Job.id==job_id))).scalar_one_or_none()
    if not job: raise HTTPException(404,'Job not found')
    doc_id=job.payload.get('document_id') if job.payload else None
    if doc_id:
        doc=(await db.execute(select(Document).where(Document.id==doc_id))).scalar_one_or_none()
        owned=(await db.execute(select(Session).where(Session.id==doc.session_id,Session.user_id==user_id))).scalar_one_or_none() if doc else None
        if not owned: raise HTTPException(404,'Job not found')
    return {'job_id':job.id,'type':job.type,'status':job.status,'progress':job.progress,'created_at':job.created_at,'started_at':job.started_at,'completed_at':job.completed_at,'error':job.error}
