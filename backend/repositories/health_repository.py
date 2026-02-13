"""Patient Transaction repository for individual clinical events."""

from __future__ import annotations

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import func

# ########################################################################
# HUGE CHANGE: IMPORTING THE NEW PATIENTTRANSACTION MODEL
# ########################################################################
from models.orm import PatientTransaction, Facility
from repositories.base_repository import BaseRepository
from utils.indicator_normalizer import normalize_indicator_name


class HealthRepository(BaseRepository[PatientTransaction]):
    """Repository for PatientTransaction model.

    Responsibilities: insert individual clinical events, count specialty loads.
    """

    def __init__(self, db: Session):
        super().__init__(db, PatientTransaction)

    def create_patient_event(
        self,
        facility_id: str,
        transaction_type: str,
        department: str,
        indicator_name: str,
        month: str,
        timestamp: Optional[datetime] = None,
    ) -> PatientTransaction:
        """Register a single clinical event (Case or Vaccination)."""
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        normalized_name = normalize_indicator_name(indicator_name)
        
        # ########################################################################
        # LOGIC: Capturing individual patient metadata
        # Directly solves PS 3.1 regarding specialty-aware access.
        # ########################################################################
        return self.create(
            facility_id=facility_id,
            transaction_type=transaction_type.upper(),
            department=department,
            indicator_name=normalized_name,
            count=1, # Individual entry
            month=month,
            timestamp=timestamp,
        )

    def count_active_cases_by_specialty(
        self,
        facility_id: str,
        department: str,
        hours: int = 4
    ) -> int:
        """
        Count active patient transactions for a specialty.
        This provides the 'Load Indicator' for our Smart Appointment logic.
        """
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        return (
            self.db.query(func.count(PatientTransaction.id))
            .filter(
                PatientTransaction.facility_id == facility_id,
                PatientTransaction.department == department,
                PatientTransaction.transaction_type == "CASE",
                PatientTransaction.timestamp >= cutoff
            )
            .scalar() or 0
        )

    def count_vaccinations_by_ward(self, ward: str) -> int:
        """
        Count total vaccinations in a ward.
        Directly addresses the PS requirement for vaccination tracking.
        """
        return (
            self.db.query(func.count(PatientTransaction.id))
            .join(Facility, Facility.facility_id == PatientTransaction.facility_id)
            .filter(
                Facility.ward == ward,
                PatientTransaction.transaction_type == "VACCINATION"
            )
            .scalar() or 0
        )

    def get_recent_stream(self, limit: int = 50) -> List[PatientTransaction]:
        """Fetch the live clinical stream for the Command Center log."""
        return (
            self.db.query(PatientTransaction)
            .order_by(PatientTransaction.timestamp.desc())
            .limit(limit)
            .all()
        )