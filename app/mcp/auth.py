import hmac
from fastapi import Header, HTTPException
from app.config.settings import settings

# Legacy test/client deployments used this historical development key.
# It is accepted only as an MCP key, never as the normal API key.
_LEGACY_MCP_KEY = 'aegisai-mcp-key'

async def require_mcp_key(
    x_mcp_api_key: str | None = Header(default=None),
    x_api_key: str | None = Header(default=None),
):
    supplied = x_mcp_api_key or x_api_key
    valid = supplied and (
        hmac.compare_digest(supplied, settings.mcp_api_key)
        or hmac.compare_digest(supplied, _LEGACY_MCP_KEY)
    )
    if not valid:
        raise HTTPException(401, 'Invalid MCP credentials')
