from fastapi import FastAPI
from app.api.health import router as health_router
from app.config.settings import settings

app = FastAPI(title=settings.app_name, version="1.0.0")
app.include_router(health_router)   


@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.app_name}!"}