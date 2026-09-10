from fastapi import FastAPI, Depends

from app.api.health import router as health_router
from app.api.auth import verify_api_key
from app.api.rate_limit import rate_limit

from app.config.settings import settings
from app.mcp.routes import router as mcp_router

from app.observability.middleware import request_id_middleware

app = FastAPI(title=settings.app_name, version="1.0.0")

app.middleware("http")(request_id_middleware)

app.include_router(health_router)   
app.include_router(mcp_router)

@app.get("/", dependencies=[Depends(verify_api_key),
                            Depends(rate_limit)])
async def root():
    return {"message": f"Welcome to {settings.app_name}!"}