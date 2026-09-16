"""Fixture target app skeleton (slice S0). Domain routes arrive in S1+."""

from fastapi import FastAPI

from app.deps import get_app_name

app = FastAPI(title="fixture-target-app")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok", "app": get_app_name()}


# S1: slice S1 router includes (append-only region; S1 owns these lines only).
from app.routers import issues as issues_router  # noqa: E402
from app.routers import comments as comments_router  # noqa: E402

app.include_router(issues_router.router)
app.include_router(comments_router.router)
