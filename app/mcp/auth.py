from fastapi import Header, HTTPException
from app.config.settings import settings


VALID_API_KEYS = {
    settings.mcp_api_key: {"echo"},
}


def require_api_key(
    x_api_key: str | None = Header(default=None),
) -> set[str]:
    if x_api_key not in VALID_API_KEYS:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key",
        )

    return VALID_API_KEYS[x_api_key]


def authorize_tool(
    allowed_tools: set[str],
    tool_name: str,
) -> None:
    if tool_name not in allowed_tools:
        raise HTTPException(
            status_code=403,
            detail=f"Tool not authorized: {tool_name}",
        )