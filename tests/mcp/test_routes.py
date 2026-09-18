from fastapi.testclient import TestClient
from app.config.settings import settings
from app.mcp.routes import router


def test_mcp_tools_endpoint():
    from fastapi import FastAPI

    app = FastAPI()
    app.include_router(router)

    client = TestClient(app)

    response = client.get(
        "/mcp/tools", 
        headers={"X-API-Key": settings.mcp_api_key},
    )

    assert response.status_code == 200
    data = response.json()

    assert len(data["tools"]) == 1
    assert data["tools"][0]["name"] == "echo"

def test_mcp_tool_endpoint():
    from fastapi import FastAPI

    app = FastAPI()
    app.include_router(router)

    client = TestClient(app)

    response = client.post(
        "/mcp/tools/echo",
        json={"arguments": {"text": "hello"}},
        headers={"X-API-Key": "aegisai-mcp-key"},
    )

    assert response.status_code == 200
    assert response.json() == {"result": "hello"}