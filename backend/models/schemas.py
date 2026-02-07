from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


class HealthIngestPayload(BaseModel):
    """Pydantic schema for health data ingestion with Swagger documentation examples."""
    
    source_name: str = Field(
        ..., 
        example="Civil Hospital Solapur",
        description="Name of the healthcare facility or source system"
    )
    facility_id: str = Field(
        ..., 
        example="HSP123",
        description="Unique identifier for the facility"
    )
    facility_type: str = Field(
        ..., 
        example="Hospital",
        description="Type of facility: Hospital, Clinic, Lab, PHC, Ambulance, etc."
    )
    district: str = Field(
        ..., 
        example="Solapur",
        description="District name"
    )
    subdistrict: Optional[str] = Field(
        None,
        example="Mohol",
        description="Sub-district or taluka name (optional)"
    )
    ward: Optional[str] = Field(
        None,
        example="Ward-12",
        description="Ward or zone identifier (optional)"
    )
    indicatorname: str = Field(
        ..., 
        example="New RTI/STI cases identified - Male",
        description="Health indicator or disease name"
    )
    total_cases: int = Field(
        ..., 
        example=42,
        description="Total number of cases reported",
        ge=0
    )
    month: str = Field(
        ..., 
        example="Feb",
        description="Month of reporting (e.g., Jan, Feb, Mar, ...)"
    )
    timestamp: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
        description="Timestamp of the data point (auto-filled if omitted)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "source_name": "Civil Hospital Solapur",
                "facility_id": "HSP123",
                "facility_type": "Hospital",
                "district": "Solapur",
                "subdistrict": "Mohol",
                "ward": "Ward-12",
                "indicatorname": "New RTI/STI cases identified - Male",
                "total_cases": 42,
                "month": "Feb",
                "timestamp": "2026-02-07T10:30:00"
            }
        }

    @validator("total_cases", pre=True)
    def coerce_total_cases(cls, v):
        if v is None:
            return 0
        try:
            return int(v)
        except Exception:
            raise ValueError("total_cases must be an integer")

    @validator("month")
    def month_must_be_valid(cls, v):
        if not isinstance(v, str) or len(v.strip()) == 0:
            raise ValueError("month is required and must be a non-empty string")
        return v.strip()

    @validator("facility_type")
    def facility_type_must_be_valid(cls, v):
        valid_types = {"Hospital", "Clinic", "Lab", "PHC", "Ambulance", "Lab Center"}
        if v not in valid_types:
            raise ValueError(f"facility_type must be one of {valid_types}")
        return v


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

    @validator("month")
    def month_must_be_simple(cls, v):
        if not isinstance(v, str) or len(v.strip()) == 0:
            raise ValueError("month is required and must be a string")
        return v.strip()
