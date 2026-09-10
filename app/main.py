from fastapi import FastAPI, Depends

from app.api.health import router as health_router
from app.api.auth import verify_api_key
from app.api.rate_limit import rate_limit
from app.api.stream import router as stream_router
from app.api.agent_stream import router as agent_stream_router

from app.config.settings import settings

from app.mcp.routes import router as mcp_router

from app.observability.middleware import request_id_middleware

from app.jobs.routes import router as jobs_router

app = FastAPI(title=settings.app_name, version="1.0.0")

app.middleware("http")(request_id_middleware)

app.include_router(health_router)   
app.include_router(mcp_router)
app.include_router(jobs_router)
app.include_router(stream_router)
app.include_router(agent_stream_router)

@app.get("/", dependencies=[Depends(verify_api_key),
                            Depends(rate_limit)])
async def root():
    return {"message": f"Welcome to {settings.app_name}!"}