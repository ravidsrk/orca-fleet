"""Prometheus /metrics contract (slice S3).

Seam: HTTP via TestClient against an Alembic-migrated throwaway SQLite DB.
(No conftest.py: the S3 slice scope allows only tests/test_telemetry_*.py, so
each test module carries its own fixture.)
"""

from collections.abc import Generator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.models import get_db
from app.telemetry import ISSUE_COUNT

FIXTURE_DIR = Path(__file__).resolve().parent.parent


def _migrated_url(tmp_path: Path) -> str:
    cfg = Config()
    cfg.set_main_option("script_location", str(FIXTURE_DIR / "alembic"))
    url = f"sqlite:///{tmp_path / 'test.db'}"
    cfg.set_main_option("sqlalchemy.url", url)
    command.upgrade(cfg, "head")
    return url


@pytest.fixture()
def client(tmp_path: Path) -> Generator[TestClient, None, None]:
    url = _migrated_url(tmp_path)
    engine = create_engine(url)
    testing_sessions = sessionmaker(bind=engine, autoflush=False)

    def _override():  # type: ignore[no-untyped-def]
        db = testing_sessions()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_metrics_exposes_histogram_and_gauge(client: TestClient) -> None:
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    body = response.text
    assert "http_request_duration_seconds_bucket" in body
    assert "app_issues_total" in body


def test_issue_create_increments_gauge(client: TestClient) -> None:
    ISSUE_COUNT.set(0)
    assert client.post("/issues", json={"title": "one"}).status_code == 201
    assert client.post("/issues", json={"title": "two"}).status_code == 201
    body = client.get("/metrics").text
    assert "app_issues_total 2.0" in body


def test_latency_histogram_observes_requests(client: TestClient) -> None:
    assert client.get("/issues").status_code == 200
    body = client.get("/metrics").text
    line = next(
        line
        for line in body.splitlines()
        if line.startswith(
            'http_request_duration_seconds_count{method="GET",path="/issues"'
        )
    )
    assert float(line.rsplit(" ", 1)[1]) >= 1
