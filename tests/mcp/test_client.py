import httpx
import pytest
from app.config.settings import settings
from app.mcp.client import MCPClient


@pytest.mark.asyncio
async def test_list_tools(monkeypatch):
    async def mock_get(self, url, headers=None):
        assert headers == {"X-API-Key": settings.mcp_api_key}

        return httpx.Response(
            200,
            json={
                "tools": [
                    {
                        "name": "echo",
                        "description": "Echo text",
                    }
                ]
            },
            request=httpx.Request("GET", url),
        )

    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)

    client = MCPClient(
        "http://localhost:8000",
        api_key="aegisai-mcp-key",
    )

    tools = await client.list_tools()

    assert tools[0]["name"] == "echo"


@pytest.mark.asyncio
async def test_call_tool(monkeypatch):
    async def mock_post(self, url, json, headers=None):
        assert headers == {"X-API-Key": "aegisai-mcp-key"}

        return httpx.Response(
            200,
            json={"result": "hello"},
            request=httpx.Request("POST", url),
        )

    monkeypatch.setattr(httpx.AsyncClient, "post", mock_post)

    client = MCPClient(
        "http://localhost:8000",
        api_key="aegisai-mcp-key",
    )

    result = await client.call_tool(
        "echo",
        {"text": "hello"},
    )

    assert result == "hello"