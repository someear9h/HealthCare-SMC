from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import pandas as pd

router = APIRouter()

# Global list to store ONLY the data ingested during this session
ingestion_buffer: List[Dict[str, Any]] = []

@router.post("/ingest")
async def ingest_data(record: Dict[str, Any]):
    try:
        # Normalize incoming data for consistency
        record = {k.lower(): v for k, v in record.items()}
        
        # Calculate total cases for the record
        record["total_cases"] = (
            record.get("reportedvalueforpublicfacility", 0) + 
            record.get("reportedvalueforprivatefacility", 0)
        )
        
        # Store in the buffer instead of the main historical dataset
        ingestion_buffer.append(record)
        
        # Keep only the last 50 entries to prevent memory bloat
        if len(ingestion_buffer) > 50:
            ingestion_buffer.pop(0)
            
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/logs")
async def get_logs():
    # Return ONLY the data from the simulator, newest first
    return ingestion_buffer[::-1]