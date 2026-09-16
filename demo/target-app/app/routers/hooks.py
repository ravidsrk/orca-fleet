"""Alertmanager webhook receiver (slice S3)."""

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/hooks", tags=["hooks"])

_last_receipt: dict[str, Any] | None = None


@router.post("/alerts")
def receive_alerts(payload: dict[str, Any]) -> dict[str, bool]:
    global _last_receipt
    _last_receipt = {
        "received_at": datetime.now(timezone.utc).isoformat(),
        "payload": payload,
    }
    return {"received": True}


@router.get("/alerts/last")
def last_alert() -> JSONResponse:
    if _last_receipt is None:
        return JSONResponse(status_code=404, content={"detail": "no alerts yet"})
    return JSONResponse(status_code=200, content=_last_receipt)
