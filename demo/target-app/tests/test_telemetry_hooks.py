"""Alertmanager webhook contract (slice S3).

POST /hooks/alerts receives Alertmanager webhook fires; GET
/hooks/alerts/last shows the most recent receipt (observable test-fire
destination per SPEC AC3.2).
"""

from fastapi.testclient import TestClient

from app.main import app
from app.routers import hooks


def _client() -> TestClient:
    hooks._last_receipt = None
    return TestClient(app)


def test_alerts_last_empty_returns_404() -> None:
    client = _client()
    response = client.get("/hooks/alerts/last")
    assert response.status_code == 404


def test_alerts_roundtrip() -> None:
    client = _client()
    payload = {
        "receiver": "fixture-app",
        "status": "firing",
        "alerts": [{"labels": {"alertname": "TestFire"}, "status": "firing"}],
    }
    received = client.post("/hooks/alerts", json=payload)
    assert received.status_code == 200
    assert received.json() == {"received": True}

    last = client.get("/hooks/alerts/last")
    assert last.status_code == 200
    body = last.json()
    assert "received_at" in body
    assert body["payload"]["alerts"][0]["labels"]["alertname"] == "TestFire"
