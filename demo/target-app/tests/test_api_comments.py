"""Per-issue comment API contract (slice S1).

Seam: HTTP via TestClient against an Alembic-migrated throwaway SQLite DB.
(No conftest.py: the S1 slice scope allows only tests/test_api_*.py, so each
test module carries its own fixture.)
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


@pytest.fixture()
def issue_id(client: TestClient) -> int:
    created = client.post("/issues", json={"title": "commented"}).json()
    return int(created["id"])


def test_add_comment_returns_201(client: TestClient, issue_id: int) -> None:
    response = client.post(
        f"/issues/{issue_id}/comments", json={"body": "first!"}
    )
    assert response.status_code == 201
    comment = response.json()
    assert comment["body"] == "first!"
    assert comment["issue_id"] == issue_id
    assert isinstance(comment["id"], int)


def test_add_comment_missing_issue_404(client: TestClient) -> None:
    response = client.post("/issues/9999/comments", json={"body": "ghost"})
    assert response.status_code == 404


def test_add_comment_rejects_empty_body(client: TestClient, issue_id: int) -> None:
    response = client.post(f"/issues/{issue_id}/comments", json={"body": ""})
    assert response.status_code == 422


def test_list_comments_empty_initially(client: TestClient, issue_id: int) -> None:
    response = client.get(f"/issues/{issue_id}/comments")
    assert response.status_code == 200
    assert response.json() == []


def test_list_comments_returns_added(client: TestClient, issue_id: int) -> None:
    client.post(f"/issues/{issue_id}/comments", json={"body": "a"})
    client.post(f"/issues/{issue_id}/comments", json={"body": "b"})
    response = client.get(f"/issues/{issue_id}/comments")
    assert response.status_code == 200
    assert [c["body"] for c in response.json()] == ["a", "b"]


def test_list_comments_missing_issue_404(client: TestClient) -> None:
    response = client.get("/issues/9999/comments")
    assert response.status_code == 404


def test_comments_isolated_per_issue(client: TestClient) -> None:
    first = client.post("/issues", json={"title": "first"}).json()
    second = client.post("/issues", json={"title": "second"}).json()
    client.post(f"/issues/{first['id']}/comments", json={"body": "only here"})
    response = client.get(f"/issues/{second['id']}/comments")
    assert response.status_code == 200
    assert response.json() == []


def test_comment_ids_unique(client: TestClient, issue_id: int) -> None:
    one = client.post(f"/issues/{issue_id}/comments", json={"body": "a"}).json()
    two = client.post(f"/issues/{issue_id}/comments", json={"body": "b"}).json()
    assert one["id"] != two["id"]
