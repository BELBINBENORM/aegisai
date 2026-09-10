import pytest
from fastapi.testclient import TestClient

from app.config.settings import settings
from app.main import app


client = TestClient(app)


def test_root_requires_api_key():
    response = client.get("/")

    assert response.status_code == 401


def test_root_rejects_invalid_api_key():
    response = client.get(
        "/",
        headers={"X-API-Key": "wrong-key"},
    )

    assert response.status_code == 401


def test_root_accepts_valid_api_key():
    response = client.get(
        "/",
        headers={"X-API-Key": settings.api_key},
    )

    assert response.status_code == 200
    assert response.json()["message"] == f"Welcome to {settings.app_name}!"