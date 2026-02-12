from fastapi import APIRouter, BackgroundTasks, HTTPException
from typing import Dict, Any
from datetime import datetime
from models.schemas import HealthIngestPayload, HealthIngestResponse
from services.ingestion_service import process_ingest
from core.ws_manager import manager

router = APIRouter(prefix="/ingest/hospital", tags=["Ingest: Hospital"])


def _bg_broadcast_ingest(payload: Dict[str, Any]) -> None:
    """
    Background task to broadcast ingestion event to WebSocket clients.
    Runs in a separate thread to avoid blocking the HTTP response.
    """
    import asyncio

    async def _broadcast():
        await manager.broadcast({
            "type": "ingest_hospital",
            "timestamp": datetime.utcnow().isoformat(),
            "payload": payload
        })

    try:
        asyncio.run(_broadcast())
    except Exception:
        # Silently fail if broadcast cannot complete
        pass


@router.post(
    "/",
    response_model=HealthIngestResponse,
    summary="Ingest Hospital Health Data",
    description="Post health data from a hospital facility to the UHDE. Validates all fields, persists to storage, runs outbreak detection, and broadcasts to live WebSocket clients.",
    responses={
        200: {
            "description": "Successfully ingested health record",
            "example": {
                "status": "ingested",
                "outbreak_detected": False,
                "message": "Record successfully validated and persisted",
                "facility_id": "HSP123"
            }
        },
        422: {
            "description": "Validation error in payload",
            "example": {
                "detail": [
                    {
                        "loc": ["body", "total_cases"],
                        "msg": "ensure this value is greater than or equal to 0",
                        "type": "value_error.number.not_ge"
                    }
                ]
            }
        },
        500: {
            "description": "Server error during processing",
            "example": {
                "detail": "Failed to process record"
            }
        }
    }
)
async def ingest_hospital_data(
    payload: HealthIngestPayload,
    background_tasks: BackgroundTasks
) -> HealthIngestResponse:
    """
    Ingest hospital health data into the Smart Health system.
    
    **Request Body:**
    - `source_name`: Name of the hospital (e.g., "Civil Hospital Solapur")
    - `facility_id`: Unique facility identifier (e.g., "HSP123")
    - `facility_type`: Type of facility (e.g., "Hospital")
    - `district`: District name (e.g., "Solapur")
    - `subdistrict`: Sub-district/taluka (optional)
    - `ward`: Ward/zone identifier (optional)
    - `indicatorname`: Health indicator (e.g., "New RTI/STI cases identified - Male")
    - `total_cases`: Number of cases (non-negative integer)
    - `month`: Reporting month (e.g., "Feb")
    - `timestamp`: Datetime of the data point (auto-filled if omitted)
    
    **Processing Steps:**
    1. Validates payload against Pydantic schema
    2. Normalizes column names and values
    3. Persists to CSV storage
    4. Runs outbreak detection algorithm
    5. Broadcasts to WebSocket clients (background task)
    
    **Response:**
    - `status`: "ingested" on success, "failed" on error
    - `outbreak_detected`: Boolean indicating if outbreak signal detected
    - `message`: Details about the ingestion result
    - `facility_id`: Echo of the facility ID for reference
    """
    try:
        # Convert Pydantic model to dict for processing
        record_dict = payload.dict(exclude_unset=False)
        
        # Ensure timestamp is set
        if not record_dict.get("timestamp"):
            record_dict["timestamp"] = datetime.utcnow()
        
        # Schedule WebSocket broadcast in background
        background_tasks.add_task(_bg_broadcast_ingest, record_dict)
        
        # Process ingestion: normalize, validate, persist, detect outbreaks
        result = process_ingest(record_dict)
        
        # Build response
        return HealthIngestResponse(
            status=result.get("status", "unknown"),
            outbreak_detected=result.get("outbreak_detected", False),
            message=f"Health and Vaccination data from {payload.source_name} processed",
            facility_id=payload.facility_id
        )
        
    except ValueError as ve:
        # Validation error
        raise HTTPException(
            status_code=422,
            detail=f"Validation error: {str(ve)}"
        )
    except Exception as e:
        # Unexpected error
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process hospital record: {str(e)}"
        )


@router.get(
    "/health",
    summary="Health Check",
    description="Verify that the hospital ingest endpoint is operational.",
    tags=["Health"]
)
async def health_check() -> Dict[str, str]:
    """
    Simple health check endpoint for the hospital ingest router.
    Returns 200 OK if the endpoint is operational.
    """
    return {
        "status": "ok",
        "service": "Hospital Ingest API",
        "timestamp": datetime.utcnow().isoformat()
    }

