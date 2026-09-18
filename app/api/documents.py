import hashlib,uuid
from pathlib import Path
from fastapi import APIRouter,Depends,UploadFile,File,HTTPException
from sqlalchemy import select
from app.api.auth import get_current_user_id
from app.api.sessions import owned
from app.database.connection import get_db
from app.database.models import Document,Job
from app.documents.storage import LocalFileStorage
from app.security.file_security import validate_upload
from app.jobs.manager import enqueue_job
from app.config.settings import settings
router=APIRouter(prefix="/sessions/{sid}/documents",tags=["documents"])
@router.post("")
async def upload(sid:int,file:UploadFile=File(...),user_id=Depends(get_current_user_id),db=Depends(get_db)):
    await owned(db,user_id,sid); data=await file.read(); validate_upload(file.filename or "",file.content_type,len(data),settings.max_upload_bytes)
    checksum=hashlib.sha256(data).hexdigest(); key=f"{uuid.uuid4()}-{Path(file.filename).name}"; storage=LocalFileStorage(); path=Path(settings.object_storage_dir)/key; path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(data)
    doc=Document(session_id=sid,filename=file.filename,content_type=file.content_type or "application/octet-stream",storage_key=key,checksum=checksum,size_bytes=len(data),status="processing"); db.add(doc); await db.flush()
    job=Job(type="document_ingestion",status="queued",payload={"document_id":doc.id}); db.add(job); await db.commit(); await db.refresh(doc)
    await enqueue_job(str(job.id),"document_ingestion",{"document_id":doc.id})
    return {"document_id":doc.id,"filename":doc.filename,"session_id":sid,"status":doc.status,"job_id":job.id}
@router.get("")
async def list_docs(sid:int,user_id=Depends(get_current_user_id),db=Depends(get_db)):
    await owned(db,user_id,sid); rows=(await db.execute(select(Document).where(Document.session_id==sid).order_by(Document.created_at.desc()))).scalars().all(); return [{"document_id":d.id,"filename":d.filename,"status":d.status} for d in rows]
@router.get("/{did}")
async def get_doc(sid:int,did:int,user_id=Depends(get_current_user_id),db=Depends(get_db)):
    await owned(db,user_id,sid); d=(await db.execute(select(Document).where(Document.id==did,Document.session_id==sid))).scalar_one_or_none()
    if not d: raise HTTPException(404,"Document not found")
    return {"document_id":d.id,"filename":d.filename,"status":d.status,"error":d.error,"size_bytes":d.size_bytes}
@router.delete("/{did}")
async def delete_doc(sid:int,did:int,user_id=Depends(get_current_user_id),db=Depends(get_db)):
    await owned(db,user_id,sid); d=(await db.execute(select(Document).where(Document.id==did,Document.session_id==sid))).scalar_one_or_none()
    if not d: raise HTTPException(404,"Document not found")
    await LocalFileStorage().delete(d.storage_key); await db.delete(d); await db.commit(); return {"deleted":True}
