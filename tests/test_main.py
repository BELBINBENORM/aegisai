from fastapi.testclient import TestClient

from app.config.settings import settings
from app.main import app


def test_mcp_router_uses_mcp_api_key_only():
    client = TestClient(app)

    response = client.get(
        "/mcp/tools",
        headers={"X-API-Key": settings.mcp_api_key},
    )

    assert response.status_code == 200


def test_mcp_router_rejects_normal_api_key():
    client = TestClient(app)

    response = client.get(
        "/mcp/tools",
        headers={"X-API-Key": settings.api_key},
    )

    assert response.status_code == 401
