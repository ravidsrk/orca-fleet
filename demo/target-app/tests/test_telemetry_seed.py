"""Seed script + F1 N+1 shape contract (slice S3).

The seed inserts a deterministic 1k-row corpus; the list endpoint fans out
one SELECT per row (F1, documented flaw — wall-clock oracle lives in
app.seed's docstring, not here: timing asserts are CI-flaky).
"""

from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.models import get_db
from app.seed import COMMENTS_PER_ISSUE
from app.seed import main as seed_main
from app.seed import seed


def _db_url(tmp_path: Path, name: str = "seed.db") -> str:
    return f"sqlite:///{tmp_path / name}"


def test_seed_inserts_count_rows(tmp_path: Path) -> None:
    url = _db_url(tmp_path)
    assert seed(count=50, database_url=url) == 50
    engine = create_engine(url)
    with engine.connect() as conn:
        assert conn.execute(text("SELECT COUNT(*) FROM issues")).scalar() == 50
        title = conn.execute(
            text("SELECT title FROM issues ORDER BY id LIMIT 1")
        ).scalar()
    assert title == "seeded issue 0001"


def test_seed_cli_seeds_named_database(tmp_path: Path) -> None:
    url = _db_url(tmp_path, "cli.db")
    assert seed_main(["--count", "3", "--database-url", url]) == 0
    engine = create_engine(url)
    with engine.connect() as conn:
        assert conn.execute(text("SELECT COUNT(*) FROM issues")).scalar() == 3


def test_list_issues_is_n_plus_one(tmp_path: Path) -> None:
    url = _db_url(tmp_path, "nplus1.db")
    rows = 5
    seed(count=rows, database_url=url)
    engine = create_engine(url)
    statements: list[str] = []
    event.listen(
        engine,
        "before_cursor_execute",
        lambda *a: statements.append(str(a[2])),
    )
    testing_sessions = sessionmaker(bind=engine, autoflush=False)

    def _override():  # type: ignore[no-untyped-def]
        db = testing_sessions()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override
    try:
        client = TestClient(app)
        response = client.get("/issues")
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    assert len(response.json()) == rows
    assert response.headers["X-Total-Comments"] == str(rows * COMMENTS_PER_ISSUE)
    selects = [s for s in statements if s.strip().upper().startswith("SELECT")]
    assert len(selects) >= 1 + 2 * rows, (
        f"expected N+1 (>= {1 + 2 * rows} SELECTs for {rows} rows), "
        f"saw {len(selects)}"
    )
