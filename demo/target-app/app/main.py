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


# S3: slice S3 telemetry + hooks (append-only region; S3 owns these lines only).
from app import telemetry as telemetry_mod  # noqa: E402
from app.routers import hooks as hooks_router  # noqa: E402

telemetry_mod.configure_logging()
app.include_router(telemetry_mod.metrics_router)
app.include_router(hooks_router.router)
app.middleware("http")(telemetry_mod.telemetry_middleware)
