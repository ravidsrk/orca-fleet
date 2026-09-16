"""Shared FastAPI dependencies (slice S0 skeleton; S1+ adds DB sessions)."""


def get_app_name() -> str:
    return "fixture-target-app"
