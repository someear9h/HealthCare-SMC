from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, validator


class FacilityStatusPayload(BaseModel):
    """Pydantic model for facility status ingestion.

    Validates and normalizes incoming facility capacity reports.
    """

    facility_id: str = Field(..., description="Unique facility identifier")
    facility_type: Literal["Hospital", "Lab", "PHC", "Private"]
    district: str
    subdistrict: str
    ward: str

    beds_available: int = Field(..., ge=0)
    icu_available: int = Field(..., ge=0)
    ventilators_available: int = Field(..., ge=0)
    oxygen_units_available: int = Field(..., ge=0)

    medicine_stock_status: Literal["Adequate", "Low", "Critical"]

    timestamp: datetime

    @validator("facility_id", pre=True, always=True)
    def strip_facility_id(cls, v: str) -> str:
        if v is None:
            raise ValueError("facility_id must not be empty")
        v2 = v.strip()
        if not v2:
            raise ValueError("facility_id must not be empty")
        return v2

    @validator("facility_type", "district", "subdistrict", "ward", "medicine_stock_status", pre=True, each_item=False)
    def strip_strings(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip()
        return v

    @validator("timestamp", pre=True)
    def parse_timestamp(cls, v):
        if isinstance(v, str):
            # let pydantic parse ISO timestamps, but ensure stripping
            return v.strip()
        return v

    class Config:
        str_strip_whitespace = True
        use_enum_values = True
