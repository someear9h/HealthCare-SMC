from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any
from datetime import datetime

from core.database import get_db
from models.schemas import PatientTransactionSchema, HealthIngestResponse
from services.ingestion_service import process_ingest
from core.ws_manager import manager

router = APIRouter(tags=["Ingest: Clinical Events"])

def _bg_broadcast_patient_event(payload: Dict[str, Any]) -> None:
    import asyncio
    async def _broadcast():
        await manager.broadcast({
            "type": f"patient_{payload['transaction_type'].lower()}",
            "timestamp": datetime.utcnow().isoformat(),
            "payload": payload
        })
    try:
        asyncio.run(_broadcast())
    except Exception: pass

@router.post("/", response_model=HealthIngestResponse)
async def ingest_patient_transaction(
    payload: PatientTransactionSchema,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> HealthIngestResponse:
    """Register a live clinical event (CASE or VACCINATION)."""
    try:
        # Pass the validated Pydantic dict directly to the service
        event_dict = payload.dict()
        
        result = process_ingest(db, event_dict)
        
        if result["status"] == "failed":
            raise Exception(result.get("error"))

        background_tasks.add_task(_bg_broadcast_patient_event, event_dict)
        
        return HealthIngestResponse(
            status="ingested",
            outbreak_detected=result.get("outbreak_detected", False),
            message=f"Patient {payload.transaction_type} recorded in {payload.department}",
            facility_id=payload.facility_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))