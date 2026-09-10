from fastapi import FastAPI
from app.api.health import router as health_router
from app.config.settings import settings

from app.mcp.routes import router as mcp_router

app = FastAPI(title=settings.app_name, version="1.0.0")
app.include_router(health_router)   
app.include_router(mcp_router)

@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.app_name}!"}