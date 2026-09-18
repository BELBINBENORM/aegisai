import httpx
from app.config.settings import settings
async def search_web(query:str,limit:int=5):
    if not settings.web_search_url: return {"available":False,"results":[]}
    headers={"Authorization":f"Bearer {settings.web_search_api_key}"} if settings.web_search_api_key else {}
    async with httpx.AsyncClient(timeout=15) as client:
        r=await client.get(settings.web_search_url,params={"q":query,"limit":limit},headers=headers); r.raise_for_status(); return {"available":True,"results":r.json()}
