from typing import Any

import httpx


class MCPClient:
    def __init__(
        self,
        base_url: str,
        api_key: str | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    async def list_tools(self) -> list[dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            headers = {}
            if self.api_key:
                headers["X-API-Key"] = self.api_key
            response = await client.get(
                f"{self.base_url}/mcp/tools",
                headers=headers,
            )
            response.raise_for_status()

            return response.json()["tools"]

    async def call_tool(
        self,
        name: str,
        arguments: dict[str, Any],
    ) -> Any:
        async with httpx.AsyncClient() as client:
            headers = {}
            if self.api_key:
                headers["X-API-Key"] = self.api_key
            response = await client.post(
                f"{self.base_url}/mcp/tools/{name}",
                json={"arguments": arguments},
                headers=headers,
            )
            response.raise_for_status()

            return response.json()["result"]