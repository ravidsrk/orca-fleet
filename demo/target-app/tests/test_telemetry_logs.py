"""Structured JSON log contract (slice S3).

Every request emits one JSON line on stdout (what promtail scrapes via
docker logs) with method/path/status_code/duration_ms fields.
"""

import json

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.telemetry import configure_logging


@pytest.fixture()
def client() -> TestClient:
    configure_logging()
    return TestClient(app)


def test_request_logs_json_line(
    client: TestClient, capsys: pytest.CaptureFixture[str]
) -> None:
    configure_logging()
    assert client.get("/healthz").status_code == 200
    captured = capsys.readouterr()
    lines = [line for line in captured.out.splitlines() if line.startswith("{")]
    assert lines, f"no JSON log line captured: {captured.out!r}"
    entry = json.loads(lines[-1])
    assert entry["method"] == "GET"
    assert entry["path"] == "/healthz"
    assert entry["status_code"] == 200
    assert entry["duration_ms"] >= 0
    assert entry["level"] == "info"
