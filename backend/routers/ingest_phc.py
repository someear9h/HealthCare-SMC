from fastapi import APIRouter, BackgroundTasks, HTTPException
from typing import Dict, Any
from datetime import datetime
from models.schemas import HealthIngestPayload, HealthIngestResponse
from services.ingestion_service import process_ingest
from core.ws_manager import manager

router = APIRouter(prefix="/ingest/phc", tags=["Ingest: PHC"])


def _bg_broadcast_ingest(payload: Dict[str, Any]) -> None:
    """Background task to broadcast ingestion event to WebSocket clients."""
    import asyncio

    async def _broadcast():
        await manager.broadcast({
            "type": "ingest_phc",
            "timestamp": datetime.utcnow().isoformat(),
            "payload": payload
        })

    try:
        asyncio.run(_broadcast())
    except Exception:
        pass


@router.post(
    "/",
    response_model=HealthIngestResponse,
    summary="Ingest PHC Health & Vaccination Data",
    description="Post disease indicators and vaccination counts from a PHC to the UHDE."
)
async def ingest_phc_data(
    payload: HealthIngestPayload,
    background_tasks: BackgroundTasks
) -> HealthIngestResponse:
    """
    Ingest PHC health data into the Smart Health system.
    Validates, persists, detects outbreaks, and broadcasts to WebSocket clients.
    """
    try:
        record_dict = payload.dict(exclude_unset=False)
        
        if not record_dict.get("timestamp"):
            record_dict["timestamp"] = datetime.utcnow()
        
        background_tasks.add_task(_bg_broadcast_ingest, record_dict)
        result = process_ingest(record_dict)
        
        return HealthIngestResponse(
            status=result.get("status", "unknown"),
            outbreak_detected=result.get("outbreak_detected", False),
            message=f"PHC record and vaccination data from {payload.source_name} successfully processed",
            facility_id=payload.facility_id
        )
        
    except ValueError as ve:
        raise HTTPException(status_code=422, detail=f"Validation error: {str(ve)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process PHC record: {str(e)}")


@router.get("/health", summary="Health Check")
async def health_check() -> Dict[str, str]:
    """Health check endpoint for the PHC ingest router."""
    return {
        "status": "ok",
        "service": "PHC Ingest API",
        "timestamp": datetime.utcnow().isoformat()
    }
