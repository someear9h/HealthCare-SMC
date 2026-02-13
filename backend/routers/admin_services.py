from fastapi import APIRouter, HTTPException
from models.schemas import HealthProgramSchema
from core.ws_manager import manager


router = APIRouter()

@router.post("/awareness/create", tags=["Admin: Citizen Engagement"])
async def create_health_program(program: HealthProgramSchema):
    """
    Creates a new wellness program or vaccination drive alert.
    These automatically sync to the Citizen Dashboard via WebSockets.
    """
    # 1. Persist to DB
    # 2. Broadcast to all "Citizen" WebSocket clients
    await manager.broadcast({"type": "new_program", "payload": program.dict()})
    return {"status": "published", "target_wards": program.target_wards}

@router.get("/appointments/slots/{facility_id}", tags=["Citizen: Access"])
async def get_available_slots(facility_id: str):
    """
    Returns available appointment timings for a specific hospital or PHC.
    """
    # Logic: Fetch slots based on existing 'total_cases' and doctor availability
    return {"facility": facility_id, "available_slots": ["10:00 AM", "02:00 PM"]}