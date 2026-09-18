from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy import select
from app.api.auth import get_current_user_id
from app.database.connection import get_db
from app.database.models import Session
from app.schemas.api import SessionCreate,SessionUpdate
router=APIRouter(prefix="/sessions",tags=["sessions"])
async def owned(db,user_id,sid):
    obj=(await db.execute(select(Session).where(Session.id==sid,Session.user_id==user_id))).scalar_one_or_none()
    if not obj: raise HTTPException(404,"Session not found")
    return obj
@router.post("")
async def create(req:SessionCreate,user_id=Depends(get_current_user_id),db=Depends(get_db)):
    s=Session(user_id=user_id,name=req.name,metadata_json=req.metadata); db.add(s); await db.commit(); await db.refresh(s); return {"session_id":s.id,"name":s.name,"status":"active"}
@router.get("")
async def list_sessions(user_id=Depends(get_current_user_id),db=Depends(get_db)):
    rows=(await db.execute(select(Session).where(Session.user_id==user_id).order_by(Session.created_at.desc()))).scalars().all(); return [{"session_id":s.id,"name":s.name,"status":"active"} for s in rows]
@router.get("/{sid}")
async def get(sid:int,user_id=Depends(get_current_user_id),db=Depends(get_db)):
    s=await owned(db,user_id,sid); return {"session_id":s.id,"name":s.name,"status":"active","metadata":s.metadata_json}
@router.patch("/{sid}")
async def update(sid:int,req:SessionUpdate,user_id=Depends(get_current_user_id),db=Depends(get_db)):
    s=await owned(db,user_id,sid)
    if req.name is not None:s.name=req.name
    if req.metadata is not None:s.metadata_json=req.metadata
    await db.commit(); return {"session_id":s.id,"name":s.name,"status":"active"}
@router.delete("/{sid}")
async def delete(sid:int,user_id=Depends(get_current_user_id),db=Depends(get_db)):
    s=await owned(db,user_id,sid); await db.delete(s); await db.commit(); return {"deleted":True}
