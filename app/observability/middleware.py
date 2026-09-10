from fastapi import Request

from app.observability.request_id import generate_request_id
from app.observability.logging import log_request


async def request_id_middleware(request: Request, call_next):
    request_id = generate_request_id()
    request.state.request_id = request_id

    log_request(request_id, request.method, request.url.path)

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id

    return response
