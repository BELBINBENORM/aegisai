from unittest.mock import patch

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
        )

    assert response.status_code == 200
    assert "data: Hello\n\n" in response.text
    assert "data:  world\n\n" in response.text
    assert "data: [DONE]\n\n" in response.text