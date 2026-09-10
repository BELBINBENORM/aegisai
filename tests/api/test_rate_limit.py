import pytest
from fastapi import HTTPException
from starlette.requests import Request

from app.api.rate_limit import (
    MAX_REQUESTS,
    _requests,
    rate_limit,
)


def make_request(ip: str) -> Request:
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/",
        "headers": [],
        "client": (ip, 12345),
        "server": ("testserver", 80),
        "scheme": "http",
    }

    return Request(scope)


@pytest.mark.asyncio
async def test_rate_limit_allows_requests():
    _requests.clear()

    request = make_request("127.0.0.1")

    for _ in range(MAX_REQUESTS):
        await rate_limit(request)


@pytest.mark.asyncio
async def test_rate_limit_blocks_excess_requests():
    _requests.clear()

    request = make_request("127.0.0.2")

    for _ in range(MAX_REQUESTS):
        await rate_limit(request)

    with pytest.raises(HTTPException) as exc_info:
        await rate_limit(request)

    assert exc_info.value.status_code == 429
    assert exc_info.value.detail == "Too many requests"