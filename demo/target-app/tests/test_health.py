"""Health endpoint contract (slice S0 skeleton; S1+ extends the API)."""

from fastapi.testclient import TestClient

from app.main import app


def test_healthz_returns_ok() -> None:
    client = TestClient(app)
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "app": "fixture-target-app"}
