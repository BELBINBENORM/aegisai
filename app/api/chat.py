import uuid
from fastapi import APIRouter,Depends,HTTPException,Request
from sqlalchemy import select
from app.api.auth import get_current_user_id
from app.api.sessions import owned
from app.database.connection import get_db
from app.schemas.api import ChatRequest
from app.agents.main_agent import MainAgent
from app.cache.cache import get_cached
from app.cache.keys import response_key
from app.config.settings import settings
router=APIRouter(prefix="/sessions/{sid}/chat",tags=["chat"])
@router.post("")
async def chat(sid:int,req:ChatRequest,request:Request,user_id=Depends(get_current_user_id),db=Depends(get_db)):
    await owned(db,user_id,sid); rid=getattr(request.state,"request_id",str(uuid.uuid4()))
    cached=await get_cached(response_key(user_id,sid,req.message,settings.model_name))
    if cached:return {"status":"completed","answer":cached["answer"],"citations":cached.get("citations",[]),"request_id":rid}
    result=await MainAgent().run(db,user_id,sid,req.message,rid)
    return {**result,"request_id":rid}
