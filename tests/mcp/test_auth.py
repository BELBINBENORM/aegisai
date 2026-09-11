from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.config.settings import settings
from app.mcp.routes import router


def create_client():
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def test_mcp_requires_api_key():
    client = create_client()

    response = client.get("/mcp/tools")

    assert response.status_code == 401


def test_mcp_accepts_valid_api_key():
    client = create_client()

    response = client.get(
        "/mcp/tools",
        headers={"X-API-Key": settings.mcp_api_key},
    )

    assert response.status_code == 200


def test_mcp_rejects_invalid_api_key():
    client = create_client()

    response = client.get(
        "/mcp/tools",
        headers={"X-API-Key": "wrong-key"},
    )

    assert response.status_code == 401


def test_mcp_rejects_unauthorized_tool():
    client = create_client()

    response = client.post(
        "/mcp/tools/not-allowed",
        json={"arguments": {}},
        headers={"X-API-Key": "aegisai-mcp-key"},
    )

    assert response.status_code == 403