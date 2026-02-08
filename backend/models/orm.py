"""SQLAlchemy ORM models for Health Intelligence Platform.

Portable types only (Integer, String, DateTime, Boolean, Float, ForeignKey).
No SQLite-specific tricks—ready for PostgreSQL migration.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey, Index
from sqlalchemy.orm import relationship

from core.database import Base


class Facility(Base):
    """Core facility record for health intelligence.

    Indexed for fast queries on facility_id, type, district, subdistrict, ward.
    """

    __tablename__ = "facilities"

    id = Column(Integer, primary_key=True, index=True)
    facility_id = Column(String, unique=True, nullable=False, index=True)
    facility_type = Column(String, nullable=False, index=True)  # Hospital, Lab, PHC, Private
    district = Column(String, nullable=False, index=True)
    subdistrict = Column(String, nullable=False, index=True)
    ward = Column(String, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    health_records = relationship("HealthRecord", back_populates="facility", cascade="all, delete-orphan")
    status_records = relationship("FacilityStatus", back_populates="facility", cascade="all, delete-orphan")


class HealthRecord(Base):
    """Health indicator records (outbreaks, cases, etc.) by facility.

    Tracks epidemic indicators for municipal intelligence.
    """

    __tablename__ = "health_records"

    id = Column(Integer, primary_key=True, index=True)
    facility_id = Column(String, ForeignKey("facilities.facility_id"), nullable=False, index=True)
    indicator_name = Column(String, nullable=False, index=True)
    total_cases = Column(Integer, nullable=False, default=0)
    month = Column(String, nullable=False, index=True)  # e.g., "Feb" or "2026-02"
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationship
    facility = relationship("Facility", back_populates="health_records")


class FacilityStatus(Base):
    """Real-time facility capacity and resource status.

    Updated frequently; used for crisis detection and municipal dashboard.
    """

    __tablename__ = "facility_status"

    id = Column(Integer, primary_key=True, index=True)
    facility_id = Column(String, ForeignKey("facilities.facility_id"), nullable=False, index=True)
    beds_available = Column(Integer, nullable=False, default=0)
    icu_available = Column(Integer, nullable=False, default=0)
    ventilators_available = Column(Integer, nullable=False, default=0)
    oxygen_units_available = Column(Integer, nullable=False, default=0)
    medicine_stock_status = Column(String, nullable=False)  # Adequate, Low, Critical
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationship
    facility = relationship("Facility", back_populates="status_records")


class Ambulance(Base):
    """Ambulance vehicle tracking for municipal intelligence.

    Enables nearest-ambulance queries and operational dashboards.
    """

    __tablename__ = "ambulances"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(String, unique=True, nullable=False, index=True)
    ward = Column(String, nullable=False, index=True)
    status = Column(String, nullable=False, default="AVAILABLE")  # AVAILABLE, BUSY, OFFLINE
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
