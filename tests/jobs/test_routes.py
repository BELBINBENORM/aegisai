from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_create_job():
    response = client.post("/jobs")

    assert response.status_code == 200

    data = response.json()

    assert "job_id" in data
    assert data["status"] == "submitted"


def test_get_job():
    create_response = client.post("/jobs")
    job_id = create_response.json()["job_id"]

    response = client.get(f"/jobs/{job_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["job_id"] == job_id
    assert data["status"] in {"running", "completed"}