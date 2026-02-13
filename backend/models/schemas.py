from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime


class PatientTransactionSchema(BaseModel):
    facility_id: str = Field(..., example="HSP123")
    
    # "CASE" for disease reporting, "VACCINATION" for immunizations
    transaction_type: str = Field(..., example="CASE", description="CASE or VACCINATION")
    
    # Essential for "Brain vs Bone" specialty logic
    department: str = Field(..., example="Neurology", description="Specialty department")
    
    # Specific disease or vaccine name
    indicator_name: str = Field(..., example="Malaria", description="Disease/Vaccine name")
    
    # For individual transactions, this is usually 1
    count: int = Field(default=1, ge=1)
    
    month: str = Field(..., example="Feb")
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)

    @validator("transaction_type")
    def validate_type(cls, v):
        if v.upper() not in ["CASE", "VACCINATION"]:
            raise ValueError("transaction_type must be CASE or VACCINATION")
        return v.upper()

    class Config:
        json_schema_extra = {
            "example": {
                "facility_id": "HSP123",
                "transaction_type": "CASE",
                "department": "Neurology",
                "indicator_name": "New Patient Admission",
                "month": "Feb",
                "timestamp": "2026-02-13T20:30:00"
            }
        }
        
class HealthIngestResponse(BaseModel):
    """Response model for health data ingestion endpoint."""
    
    status: str = Field(
        ..., 
        example="ingested",
        description="Status of the ingestion: 'ingested', 'failed', 'validated'"
    )
    outbreak_detected: bool = Field(
        ..., 
        example=False,
        description="Whether an outbreak signal was detected based on the ingested data"
    )
    message: Optional[str] = Field(
        None,
        example="Record successfully ingested and validated",
        description="Additional message or error details"
    )
    facility_id: Optional[str] = Field(
        None,
        example="HSP123",
        description="Facility ID of the ingested record (for reference)"
    )


class IngestRecord(BaseModel):
    """Legacy schema for internal use - redirects to HealthIngestPayload."""
    source_name: str
    facility_id: str
    facility_type: str
    district: str
    subdistrict: Optional[str] = None
    ward: Optional[str] = None
    indicatorname: str
    total_cases: int
    vaccination_count: Optional[int] = 0
    month: str
    timestamp: datetime

    # internal fields
    ingestion_timestamp: Optional[datetime] = None

    @validator("total_cases", pre=True)
    def coerce_total_cases(cls, v):
        if v is None:
            return 0
        try:
            return int(v)
        except Exception:
            raise ValueError("total_cases must be an integer")
        
    @validator("vaccination_count", pre=True)
    def coerce_vaccination_count(cls, v):
        if v is None: return 0
        return int(v)

    @validator("month")
    def month_must_be_simple(cls, v):
        if not isinstance(v, str) or len(v.strip()) == 0:
            raise ValueError("month is required and must be a string")
        return v.strip()
    

class HealthProgramSchema(BaseModel):
    program_id: str = Field(..., example="PROG_DENGUE_001")
    title_en: str = Field(..., example="Dengue Awareness Drive")
    
    description_en: str = Field(..., example="Cleanup drive in Ward-12 this Sunday.")
    
    category: str = Field(..., example="Wellness", description="Wellness, Vaccination, Emergency, or Awareness")
    
    # Targeting specific wards to solve Challenge 3.2 (Engagement)
    target_wards: List[str] = Field(default=["All"], example=["Ward-12", "Ward-15"])
    
    is_urgent: bool = Field(default=False)
    expiry_date: Optional[datetime] = None

    @validator("target_wards", pre=True)
    def validate_wards(cls, v):
        if not v:
            return ["All"]
        return v

# ########################################################################
# SCHEMA FOR APPOINTMENTS & TELEMEDICINE SLOTS
# Solves PS Section 3.1: "Platforms for appointments and telemedicine"
# ########################################################################
class AppointmentSlotSchema(BaseModel):
    facility_id: str = Field(..., example="HSP123")
    doctor_name: str = Field(..., example="Dr. Patil")
    department: str = Field(..., example="General Physician")
    available_slots: List[str] = Field(..., example=["10:00 AM", "11:30 AM", "04:00 PM"])
    is_telemedicine_available: bool = Field(default=True)

    class Config:
        json_schema_extra = {
            "example": {
                "facility_id": "PHC_01",
                "doctor_name": "Dr. Deshmukh",
                "department": "Pediatrics",
                "available_slots": ["09:00 AM", "10:00 AM"],
                "is_telemedicine_available": True
            }
        }