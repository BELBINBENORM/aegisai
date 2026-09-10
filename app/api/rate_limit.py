import time

from fastapi import HTTPException, Request


_requests: dict[str, list[float]] = {}

MAX_REQUESTS = 30
WINDOW_SECONDS = 60


async def rate_limit(request: Request) -> None:
    client = request.client

    if client is None:
        return

    key = client.host
    now = time.time()

    requests = _requests.get(key, [])

    requests = [
        timestamp
        for timestamp in requests
        if now - timestamp < WINDOW_SECONDS
    ]

    if len(requests) >= MAX_REQUESTS:
        raise HTTPException(
            status_code=429,
            detail="Too many requests",
        )

    requests.append(now)
    _requests[key] = requests