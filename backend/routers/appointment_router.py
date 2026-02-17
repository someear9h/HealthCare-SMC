from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import Session, relationship
from core.database import Base, get_db

# ########################################################################
# 1. ORM MODELS (Database Tables)
# Solves PS 4.1: Real-time visibility into health infrastructure.
# ########################################################################
class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(String, unique=True, index=True)
    facility_id = Column(String, nullable=False)
    department = Column(String, nullable=True, index=True)
    appointment_type = Column(String, default="IN_PERSON")
    scheduled_time = Column(DateTime, nullable=False)
    status = Column(String, default="BOOKED")
    created_at = Column(DateTime, default=datetime.utcnow)

# Note: We assume PatientTransaction is defined in your main models file, 
# but we import it here to use in the load calculation logic.
from models.orm import PatientTransaction 

# ########################################################################
# 2. SCHEMAS (Data Validation)
# ########################################################################
class AppointmentCreate(BaseModel):
    facility_id: str = Field(..., example="HSP123")
    department: str = Field(..., example="Neurology")
    preferred_time: datetime = Field(default_factory=datetime.utcnow) # Dynamic Default
    appointment_type: Optional[str] = "IN_PERSON"

class AvailabilityResponse(BaseModel):
    facility_id: str
    department: str
    is_available: bool
    current_load: int
    max_capacity: int
    suggested_slots: List[datetime]
    message: str

# ########################################################################
# 3. SERVICE LOGIC
# ########################################################################
FACILITY_METADATA = {
    "HSP123": {
        "Neurology": {"max_load": 10},
        "Orthopedics": {"max_load": 10}
    }
}

def calculate_clinical_load(db: Session, facility_id: str, dept: str):
    """
    Counts 'CASE' transactions from the LAST 4 HOURS.
    Ensures real-time monitoring.
    """
    # FIX: Use dynamic UTC window
    window = datetime.utcnow() - timedelta(hours=4)
    
    return db.query(func.count(PatientTransaction.id)).filter(
        PatientTransaction.facility_id == facility_id,
        PatientTransaction.department == dept,
        PatientTransaction.transaction_type == "CASE",
        PatientTransaction.timestamp >= window
    ).scalar() or 0

# ########################################################################
# 4. ROUTER (API Endpoints)
# ########################################################################
router = APIRouter(prefix="/appointments", tags=["Citizen: Appointments"])

@router.get("/check-availability/{facility_id}/{dept}", response_model=AvailabilityResponse)
async def check_availability(facility_id: str, dept: str, db: Session = Depends(get_db)):
    """Checks live load and capacity."""
    current_load = calculate_clinical_load(db, facility_id, dept)
    
    # Logic: Get capacity from metadata or default to 10
    max_capacity = FACILITY_METADATA.get(facility_id, {}).get(dept, {}).get("max_load", 10)
    
    is_available = current_load < max_capacity
    
    message = "Slots available." if is_available else f"High demand in {dept}. Redirecting to PHC."

    return {
        "facility_id": facility_id,
        "department": dept,
        "is_available": is_available,
        "current_load": current_load,
        "max_capacity": max_capacity,
        "suggested_slots": [datetime.utcnow() + timedelta(hours=2)],
        "message": message
    }

@router.post("/book")
async def book_appointment(req: AppointmentCreate, db: Session = Depends(get_db)):
    """Saves appointment if capacity permits."""
    current_load = calculate_clinical_load(db, req.facility_id, req.department)
    
    if current_load >= 10:
        raise HTTPException(status_code=400, detail="Department over capacity.")

    new_app = Appointment(
        appointment_id=f"APP-{int(datetime.utcnow().timestamp())}",
        facility_id=req.facility_id,
        department=req.department,
        scheduled_time=req.preferred_time,
        appointment_type=req.appointment_type,
        status="BOOKED"
    )
    
    db.add(new_app)
    db.commit()
    db.refresh(new_app)
    return {"status": "success", "appointment_id": new_app.appointment_id}