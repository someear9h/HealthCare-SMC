from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, HTTPException
from typing import Dict
import asyncio

from schemas.facility_status_schema import FacilityStatusPayload
from services.facility_status_service import process_facility_status
from core.ws_manager import manager

router = APIRouter()


def _bg_broadcast(event: Dict) -> None:
    """Schedule websocket broadcast in event loop."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        asyncio.create_task(manager.broadcast(event))
    else:
        # Fire-and-forget
        try:
            asyncio.run(manager.broadcast(event))
        except Exception:
            pass


@router.post("/", tags=["Facility Status"])
def ingest_facility_status(payload: FacilityStatusPayload, background_tasks: BackgroundTasks):
    """Ingest facility status, persist and broadcast summary.

    Returns ingestion acknowledgment, crisis flag and city totals.
    """
    try:
        result = process_facility_status(payload.dict())
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    # Broadcast in background
    event = result.get("event")
    if event:
        background_tasks.add_task(_bg_broadcast, event)

    return {
        "status": "ingested",
        "resource_crisis": result.get("resource_crisis", False),
        "facility_id": result.get("facility_id"),
        "city_totals": result.get("city_totals"),
    }
