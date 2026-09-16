"""Fixture target app skeleton (slice S0). Domain routes arrive in S1+."""

from fastapi import FastAPI

from app.deps import get_app_name

app = FastAPI(title="fixture-target-app")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok", "app": get_app_name()}
