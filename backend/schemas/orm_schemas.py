"""Pydantic schemas for ORM models.

Separate read/write schemas for API contracts.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, validator


class FacilityBase(BaseModel):
    """Base facility schema."""

    facility_id: str = Field(..., min_length=1)
    facility_type: str
    district: str
    subdistrict: str
    ward: str


class FacilityCreate(FacilityBase):
    """Schema for facility creation."""

    pass


class FacilityRead(FacilityBase):
    """Schema for facility response."""

    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class HealthRecordBase(BaseModel):
    """Base health record schema."""

    facility_id: str = Field(..., min_length=1)
    indicator_name: str
    total_cases: int = Field(..., ge=0)
    month: str


class HealthRecordCreate(HealthRecordBase):
    """Schema for health record creation."""

    timestamp: Optional[datetime] = None


class HealthRecordRead(HealthRecordBase):
    """Schema for health record response."""

    id: int
    timestamp: datetime

    class Config:
        from_attributes = True


class FacilityStatusBase(BaseModel):
    """Base facility status schema."""

    facility_id: str = Field(..., min_length=1)
    beds_available: int = Field(..., ge=0)
    icu_available: int = Field(..., ge=0)
    ventilators_available: int = Field(..., ge=0)
    oxygen_units_available: int = Field(..., ge=0)
    medicine_stock_status: str  # Adequate, Low, Critical


class FacilityStatusCreate(FacilityStatusBase):
    """Schema for facility status creation."""

    timestamp: Optional[datetime] = None


class FacilityStatusRead(FacilityStatusBase):
    """Schema for facility status response."""

    id: int
    timestamp: datetime

    class Config:
        from_attributes = True


class AmbulanceBase(BaseModel):
    """Base ambulance schema."""

    vehicle_id: str = Field(..., min_length=1)
    ward: str
    status: str = Field(default="AVAILABLE")
    lat: float
    lng: float


class AmbulanceCreate(AmbulanceBase):
    """Schema for ambulance creation."""

    pass


class AmbulanceUpdate(BaseModel):
    """Schema for ambulance location/status update."""

    status: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None


class AmbulanceRead(AmbulanceBase):
    """Schema for ambulance response."""

    id: int
    last_updated: datetime

    class Config:
        from_attributes = True


class PredictionResponse(BaseModel):
    """Bed demand prediction response."""

    facility_id: str
    beds_remaining_hours: int
    crisis_likely: bool
    avg_admission_rate: float


class WardRiskResponse(BaseModel):
    """Ward-level risk aggregation."""

    ward: str
    risk_score: float
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    recent_cases: int
    icu_pressure: float


class NearestAmbulanceResponse(BaseModel):
    """Nearest ambulance with distance."""

    vehicle_id: str
    ward: str
    status: str
    lat: float
    lng: float
    distance_km: float

    class Config:
        from_attributes = True
