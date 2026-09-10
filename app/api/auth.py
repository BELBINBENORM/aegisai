from fastapi import Header, HTTPException

from app.config.settings import settings


async def verify_api_key(
    x_api_key: str | None = Header(default=None),
) -> None:
    if x_api_key != settings.api_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key",
        )

async def get_current_user_id(
    x_user_id: int | None = Header(default=None) ) -> int:
    if x_user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Missing user ID",
        )

    return x_user_id