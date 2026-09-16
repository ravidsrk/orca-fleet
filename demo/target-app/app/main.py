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


# S2: slice S2 router includes (append-only region; S2 owns these lines only).
from app.routers import pages as pages_router  # noqa: E402

app.include_router(pages_router.router)

# S1's GET /issues/{issue_id} matches the literal path /issues/new first and
# 422s (FastAPI registers {issue_id} without an int convertor, so declaration
# order decides; the S1 region is frozen, so the pages entry is lifted ahead
# of it here). Only UI paths change hands — every S1 path still falls through
# to the S1 routers exactly as before (the full suite pins that).
for _entry in list(app.router.routes):
    _is_pages_router = getattr(_entry, "original_router", None) is pages_router.router
    _is_new_form_route = getattr(_entry, "path", "") == "/issues/new" and "GET" in (
        getattr(_entry, "methods", None) or set()
    )
    if _is_pages_router or _is_new_form_route:
        app.router.routes.remove(_entry)
        app.router.routes.insert(0, _entry)
