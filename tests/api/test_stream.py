from unittest.mock import patch
from app.config.settings import settings
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


async def fake_stream(prompt: str):
    yield "Hello"
    yield " world"


def test_stream_response():
    with patch(
        "app.api.stream.client.generate_stream",
        side_effect=fake_stream,
    ):
        response = client.get(
            "/stream",
            params={"prompt": "Say hello"},
            headers={"X-API-Key": settings.api_key},
        )

    assert response.status_code == 200
    assert "data: Hello\n\n" in response.text
    assert "data:  world\n\n" in response.text
    assert "data: [DONE]\n\n" in response.text


def test_stream_requires_api_key():
    response = client.get(
        "/stream",
        params={"prompt": "Say hello"},
    )

    assert response.status_code == 401