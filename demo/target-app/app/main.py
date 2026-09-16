"""Fixture target app skeleton (slice S0). Domain routes arrive in S1+."""

from fastapi import FastAPI

from app.deps import get_app_name

app = FastAPI(title="fixture-target-app")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok", "app": get_app_name()}


# Route precedence (coordinator merge-resolution E1): pages include BEFORE the
# API includes — /issues/new must precede /issues/{issue_id} (else the literal
# "new" matches the untyped param route and 422s). S1 lines byte-identical,
# only moved; S1 behavior pinned by its tests, re-verified at this head.
# S2: slice S2 router includes (append-only region; S2 owns these lines only).
from app.routers import pages as pages_router  # noqa: E402

app.include_router(pages_router.router)

# S1: slice S1 router includes (append-only region; S1 owns these lines only).
from app.routers import issues as issues_router  # noqa: E402
from app.routers import comments as comments_router  # noqa: E402

app.include_router(issues_router.router)
app.include_router(comments_router.router)
