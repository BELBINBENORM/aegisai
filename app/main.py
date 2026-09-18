from fastapi import FastAPI, Depends
from app.config.settings import settings
from app.api.auth import verify_api_key
from app.api.rate_limit import rate_limit
from app.api.health import router as health
from app.api.sessions import router as sessions
from app.api.documents import router as documents
from app.api.chat import router as chat
from app.api.stream import router as stream
from app.api.agent_stream import router as agent_stream
from app.jobs.routes import router as jobs
from app.mcp.routes import router as mcp
from app.observability.middleware import request_id_middleware
app = FastAPI(title=settings.app_name, version='2.0.0')
app.middleware('http')(request_id_middleware)
app.include_router(health)
protected = [Depends(verify_api_key), Depends(rate_limit)]
app.include_router(sessions, dependencies=protected)
app.include_router(documents, dependencies=protected)
app.include_router(chat, dependencies=protected)
app.include_router(stream, dependencies=protected)
app.include_router(agent_stream)
app.include_router(jobs, dependencies=protected)
app.include_router(mcp)
@app.get('/', dependencies=protected)
async def root(): return {'name': settings.app_name, 'version': '2.0.0'}
