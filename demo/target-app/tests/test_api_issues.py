"""Issue CRUD API contract (slice S1).

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


def test_create_issue_returns_201_with_shape(client: TestClient) -> None:
    response = client.post(
        "/issues", json={"title": "ship it", "body": "build the thing", "priority": 1}
    )
    assert response.status_code == 201
    created = response.json()
    assert created["title"] == "ship it"
    assert created["body"] == "build the thing"
    assert created["status"] == "open"
    assert created["priority"] == 1
    assert isinstance(created["id"], int)


def test_create_issue_defaults(client: TestClient) -> None:
    response = client.post("/issues", json={"title": "defaults"})
    assert response.status_code == 201
    created = response.json()
    assert created["status"] == "open"
    assert created["priority"] == 2
    assert created["body"] is None


def test_create_issue_closed_status(client: TestClient) -> None:
    response = client.post("/issues", json={"title": "done", "status": "closed"})
    assert response.status_code == 201
    assert response.json()["status"] == "closed"


def test_create_issue_rejects_empty_title(client: TestClient) -> None:
    response = client.post("/issues", json={"title": ""})
    assert response.status_code == 422


def test_create_issue_rejects_bad_status(client: TestClient) -> None:
    response = client.post("/issues", json={"title": "x", "status": "wip"})
    assert response.status_code == 422


def test_create_issue_rejects_priority_zero(client: TestClient) -> None:
    response = client.post("/issues", json={"title": "x", "priority": 0})
    assert response.status_code == 422


def test_create_issue_rejects_priority_four(client: TestClient) -> None:
    response = client.post("/issues", json={"title": "x", "priority": 4})
    assert response.status_code == 422


def test_get_issue_returns_created(client: TestClient) -> None:
    created = client.post("/issues", json={"title": "fetch me"}).json()
    response = client.get(f"/issues/{created['id']}")
    assert response.status_code == 200
    assert response.json() == created


def test_get_issue_missing_returns_404(client: TestClient) -> None:
    response = client.get("/issues/9999")
    assert response.status_code == 404


def test_list_issues_empty_initially(client: TestClient) -> None:
    response = client.get("/issues")
    assert response.status_code == 200
    assert response.json() == []


def test_list_issues_returns_all(client: TestClient) -> None:
    client.post("/issues", json={"title": "one"})
    client.post("/issues", json={"title": "two"})
    response = client.get("/issues")
    assert response.status_code == 200
    titles = [issue["title"] for issue in response.json()]
    assert titles == ["one", "two"]


def test_update_issue_title(client: TestClient) -> None:
    created = client.post("/issues", json={"title": "old"}).json()
    response = client.patch(f"/issues/{created['id']}", json={"title": "new"})
    assert response.status_code == 200
    assert response.json()["title"] == "new"
    assert response.json()["id"] == created["id"]


def test_update_issue_status_closed(client: TestClient) -> None:
    created = client.post("/issues", json={"title": "close me"}).json()
    response = client.patch(f"/issues/{created['id']}", json={"status": "closed"})
    assert response.status_code == 200
    assert response.json()["status"] == "closed"


def test_update_issue_missing_returns_404(client: TestClient) -> None:
    response = client.patch("/issues/9999", json={"title": "ghost"})
    assert response.status_code == 404


def test_update_issue_rejects_bad_priority(client: TestClient) -> None:
    created = client.post("/issues", json={"title": "x"}).json()
    response = client.patch(f"/issues/{created['id']}", json={"priority": 99})
    assert response.status_code == 422


def test_openapi_docs_available(client: TestClient) -> None:
    response = client.get("/docs")
    assert response.status_code == 200
