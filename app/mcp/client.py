from typing import Any

import httpx

from app.config.settings import settings


class MCPClient:
    def __init__(
        self,
        base_url: str,
        api_key: str | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or settings.mcp_api_key

    def _headers(self) -> dict[str, str]:
        return {
            "X-API-Key": self.api_key,
        }

    async def list_tools(self) -> list[dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/mcp/tools",
                headers=self._headers(),
            )
            response.raise_for_status()

            return response.json()["tools"]

    async def call_tool(
        self,
        name: str,
        arguments: dict[str, Any],
    ) -> Any:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/mcp/tools/{name}",
                json={"arguments": arguments},
                headers=self._headers(),
            )
            response.raise_for_status()

            return response.json()["result"]