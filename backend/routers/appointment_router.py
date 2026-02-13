from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from core.database import get_db
from models.orm import PatientTransaction, Appointment
from models.schemas import AppointmentCreate, AvailabilityResponse
from datetime import datetime, timedelta

router = APIRouter(prefix="/appointments", tags=["Citizen: Appointments"])

@router.get("/check-availability/{facility_id}/{dept}", response_model=AvailabilityResponse)
async def check_availability(facility_id: str, dept: str, db: Session = Depends(get_db)):
    """
    REALISTIC LOGIC:
    Queries the database to count actual 'CASE' transactions from the last 4 hours.
    """
    # 1. Define the lookback window (Last 4 hours is standard for clinical load)
    window = datetime.utcnow() - timedelta(hours=4)

    # 2. Query the DB for the ACTUAL count of patients ingested
    current_load = db.query(func.count(PatientTransaction.id)).filter(
        PatientTransaction.facility_id == facility_id,
        PatientTransaction.department == dept,
        PatientTransaction.transaction_type == "CASE",
        PatientTransaction.timestamp >= window
    ).scalar() or 0

    # 3. Define capacity (In a real system, this comes from the 'Facility' table)
    max_capacity = 10 
    
    # 4. Determine availability based on the LIVE load
    is_available = current_load < max_capacity
    
    # Custom message based on load
    if not is_available:
        message = f"High demand in {dept}. Redirecting to nearest PHC."
    else:
        message = "Slots available."

    return {
        "facility_id": facility_id,
        "department": dept,
        "is_available": is_available,
        "current_load": current_load, # This will now show '1' after your ingestion
        "max_capacity": max_capacity,
        "suggested_slots": [datetime.utcnow() + timedelta(hours=1)],
        "message": message
    }


@router.post("/book")
async def book_appointment(req: AppointmentCreate, db: Session = Depends(get_db)):
    """
    REALISTIC BOOKING LOGIC:
    1. Re-check availability (Safety Check)
    2. Save using the ORM Model, not the Schema.
    """
    window = datetime.utcnow() - timedelta(hours=4)
    current_load = db.query(func.count(PatientTransaction.id)).filter(
        PatientTransaction.facility_id == req.facility_id,
        PatientTransaction.department == req.department,
        PatientTransaction.transaction_type == "CASE",
        PatientTransaction.timestamp >= window
    ).scalar() or 0

    if current_load >= 10:
        raise HTTPException(
            status_code=400, 
            detail=f"Facility {req.facility_id} is over capacity for {req.department}."
        )

    # ########################################################################
    # THE FIX: Use the 'Appointment' ORM Model here, NOT 'AppointmentCreate'
    # ########################################################################
    new_app = Appointment(
        appointment_id=f"APP-{int(datetime.utcnow().timestamp())}",
        facility_id=req.facility_id,
        department=req.department,
        scheduled_time=req.preferred_time, # Map Schema field to Model field
        appointment_type=req.appointment_type,
        status="BOOKED"
    )
    
    db.add(new_app)
    db.commit()
    db.refresh(new_app)
    
    return {
        "status": "success", 
        "appointment_id": new_app.appointment_id, 
        "message": "Booking confirmed"
    }