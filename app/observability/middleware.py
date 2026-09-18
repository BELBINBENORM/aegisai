import time,uuid
from fastapi import Request
async def request_id_middleware(request:Request,call_next):
    rid=request.headers.get("X-Request-ID") or str(uuid.uuid4()); request.state.request_id=rid; start=time.perf_counter()
    response=await call_next(request); response.headers["X-Request-ID"]=rid; response.headers["X-Response-Time-ms"]=f"{(time.perf_counter()-start)*1000:.1f}"; return response
