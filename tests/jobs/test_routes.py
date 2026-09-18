from fastapi.testclient import TestClient
from app.main import app
from app.config.settings import settings
client = TestClient(app)
HEADERS = {"X-API-Key": settings.api_key}

def test_create_job():
    response = client.post("/jobs", headers=HEADERS)
    assert response.status_code == 200
    data = response.json(); assert "job_id" in data; assert data["status"] in {"queued", "submitted"}

def test_get_job():
    create_response = client.post("/jobs", headers=HEADERS)
    job_id = create_response.json()["job_id"]
    response = client.get(f"/jobs/{job_id}", headers=HEADERS)
    assert response.status_code == 200
    assert response.json()["job_id"] == job_id

def test_jobs_require_auth():
    assert client.get("/jobs/missing").status_code == 401
