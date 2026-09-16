"""Server-rendered UI smoke tests (slice S2).

Seam: HTTP via TestClient against an Alembic-migrated throwaway SQLite DB
(same seam as S1; no conftest.py — the S2 slice scope allows only
tests/test_ui_*.py, so this module carries its own fixture).

Covers S2-AC2: `/`, `/issues/new`, one `/issues/{id}` return 200 with key
markers. The HTML detail page lives at `/issues/{id}/view` because S1's JSON
`GET /issues/{id}` route is registered first and must keep serving JSON
(S1 tests pin that); the `/issues/{id}` smoke below guards the JSON detail
route still works with the UI mounted.
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


def test_list_page_returns_200_with_markers(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "<h1>Issues</h1>" in response.text
    assert 'href="/issues/new"' in response.text


def test_list_page_shows_created_issues(client: TestClient) -> None:
    created = client.post("/issues", json={"title": "visible bug"}).json()
    response = client.get("/")
    assert response.status_code == 200
    assert "visible bug" in response.text
    assert f'href="/issues/{created["id"]}/view"' in response.text


def test_new_form_returns_200_with_markers(client: TestClient) -> None:
    response = client.get("/issues/new")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "<form" in response.text
    assert 'action="/issues/new"' in response.text
    assert 'name="title"' in response.text
    assert '<select name="priority"' in response.text


def test_new_form_priority_select_has_no_label_f2(client: TestClient) -> None:
    """F2 pin: the priority <select> has no associated label (axe rule `label`).

    Other fields ARE labelled — the flaw is specific to priority. Do not fix
    outside a mission run; flaw location: app/templates/_form.html.
    """
    response = client.get("/issues/new")
    assert response.status_code == 200
    assert '<label for="title">' in response.text
    assert '<select name="priority"' in response.text
    assert 'for="priority"' not in response.text
    assert "aria-label" not in response.text
    assert "aria-labelledby" not in response.text


def test_create_issue_via_new_form_redirects(client: TestClient) -> None:
    response = client.post(
        "/issues/new",
        data={"title": "filed via form", "body": "has body", "priority": "1"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/"
    listing = client.get("/")
    assert "filed via form" in listing.text


def test_new_form_rejects_empty_title_with_422(client: TestClient) -> None:
    response = client.post("/issues/new", data={"title": ""})
    assert response.status_code == 422
    assert "<form" in response.text


def test_issue_detail_json_still_serves_with_markers(client: TestClient) -> None:
    """S2-AC2 smoke: GET /issues/{id} stays 200 with key markers (JSON, S1)."""
    created = client.post(
        "/issues", json={"title": "smoke detail", "body": "SMOKE-BODY-7"}
    ).json()
    response = client.get(f"/issues/{created['id']}")
    assert response.status_code == 200
    assert "smoke detail" in response.text
    assert "SMOKE-BODY-7" in response.text


def test_detail_view_returns_200_with_markers(client: TestClient) -> None:
    created = client.post(
        "/issues", json={"title": "shown bug", "body": "Shown body", "priority": 1}
    ).json()
    client.post(f"/issues/{created['id']}/comments", json={"body": "First comment"})
    response = client.get(f"/issues/{created['id']}/view")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "<h1>shown bug</h1>" in response.text
    assert "Shown body" in response.text
    assert "First comment" in response.text
    assert f'href="/issues/{created["id"]}/edit"' in response.text


def test_detail_view_missing_returns_404(client: TestClient) -> None:
    response = client.get("/issues/9999/view")
    assert response.status_code == 404


def test_edit_form_returns_200_with_prefilled_markers(client: TestClient) -> None:
    created = client.post("/issues", json={"title": "edit me"}).json()
    response = client.get(f"/issues/{created['id']}/edit")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "<form" in response.text
    assert f'action="/issues/{created["id"]}/edit"' in response.text
    assert 'value="edit me"' in response.text
    assert '<select name="priority"' in response.text


def test_edit_form_priority_select_has_no_label_f2(client: TestClient) -> None:
    """F2 pin (edit side): shared form keeps the priority select unlabelled."""
    created = client.post("/issues", json={"title": "edit me"}).json()
    response = client.get(f"/issues/{created['id']}/edit")
    assert response.status_code == 200
    assert '<label for="title">' in response.text
    assert '<select name="priority"' in response.text
    assert 'for="priority"' not in response.text
    assert "aria-label" not in response.text
    assert "aria-labelledby" not in response.text


def test_update_issue_via_edit_form_redirects(client: TestClient) -> None:
    created = client.post("/issues", json={"title": "before edit"}).json()
    response = client.post(
        f"/issues/{created['id']}/edit",
        data={"title": "after edit", "status": "closed", "priority": "3"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"] == f"/issues/{created['id']}/view"
    detail = client.get(f"/issues/{created['id']}/view")
    assert "<h1>after edit</h1>" in detail.text
    assert "closed" in detail.text


def test_edit_form_missing_returns_404(client: TestClient) -> None:
    assert client.get("/issues/9999/edit").status_code == 404
    assert client.post("/issues/9999/edit", data={"title": "ghost"}).status_code == 404
