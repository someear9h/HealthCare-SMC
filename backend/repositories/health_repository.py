"""Health records repository for epidemic intelligence."""

from __future__ import annotations

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import func

from models.orm import HealthRecord, Facility
from repositories.base_repository import BaseRepository
from utils.indicator_normalizer import normalize_indicator_name


class HealthRepository(BaseRepository[HealthRecord]):
    """Repository for HealthRecord model.

    Responsibilities: insert, fetch, aggregate epidemic data.
    """

    def __init__(self, db: Session):
        super().__init__(db, HealthRecord)

    def create_record(
        self,
        facility_id: str,
        indicator_name: str,
        total_cases: int,
        month: str,
        timestamp: Optional[datetime] = None,
    ) -> HealthRecord:
        """Create health indicator record with normalized indicator name.

        Args:
            facility_id: Facility identifier.
            indicator_name: Name of health indicator (will be normalized).
            total_cases: Case count (>= 0).
            month: Month/period identifier.
            timestamp: When recorded (default: now).

        Returns:
            HealthRecord instance.
        """
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        # Normalize indicator name to prevent data fragmentation
        normalized_name = normalize_indicator_name(indicator_name)
        
        return self.create(
            facility_id=facility_id,
            indicator_name=normalized_name,
            total_cases=total_cases,
            month=month,
            timestamp=timestamp,
        )

    def get_recent_by_facility(
        self,
        facility_id: str,
        limit: int = 10,
        hours: int = 24,
    ) -> List[HealthRecord]:
        """Fetch recent health records for facility.

        Args:
            facility_id: Facility identifier.
            limit: Max records.
            hours: Lookback window in hours.

        Returns:
            List of HealthRecord instances.
        """
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        return (
            self.db.query(HealthRecord)
            .filter(
                HealthRecord.facility_id == facility_id,
                HealthRecord.timestamp >= cutoff,
            )
            .order_by(HealthRecord.timestamp.desc())
            .limit(limit)
            .all()
        )

    def get_by_indicator(self, indicator_name: str, limit: int = 100) -> List[HealthRecord]:
        """Fetch records by indicator name across all facilities.

        Args:
            indicator_name: Indicator to filter.
            limit: Max records.

        Returns:
            List of HealthRecord instances.
        """
        return (
            self.db.query(HealthRecord)
            .filter(HealthRecord.indicator_name == indicator_name)
            .order_by(HealthRecord.timestamp.desc())
            .limit(limit)
            .all()
        )

    def get_by_month(self, month: str, limit: int = 100) -> List[HealthRecord]:
        """Fetch records for month.

        Args:
            month: Month identifier (e.g., "Feb", "2026-02").
            limit: Max records.

        Returns:
            List of HealthRecord instances.
        """
        return (
            self.db.query(HealthRecord)
            .filter(HealthRecord.month == month)
            .limit(limit)
            .all()
        )

    def sum_cases_by_indicator(self, indicator_name: str) -> int:
        """Total cases across all facilities for an indicator.

        Args:
            indicator_name: Indicator to sum (will be normalized).

        Returns:
            Total case count.
        """
        # Normalize the input indicator name for consistent lookup
        normalized_name = normalize_indicator_name(indicator_name)
        
        result = (
            self.db.query(func.sum(HealthRecord.total_cases))
            .filter(HealthRecord.indicator_name == normalized_name)
            .scalar()
        )
        return result or 0

    def sum_cases_by_facility(self, facility_id: str) -> int:
        """Total cases for a facility across all indicators.

        Args:
            facility_id: Facility identifier.

        Returns:
            Total case count.
        """
        result = (
            self.db.query(func.sum(HealthRecord.total_cases))
            .filter(HealthRecord.facility_id == facility_id)
            .scalar()
        )
        return result or 0

    def get_ward_cases(self, ward: str) -> int:
        """Sum cases for all facilities in a ward.

        Args:
            ward: Ward name/code.

        Returns:
            Total case count in ward.
        """
        result = (
            self.db.query(func.sum(HealthRecord.total_cases))
            .join(Facility, Facility.facility_id == HealthRecord.facility_id)
            .filter(Facility.ward == ward)
            .scalar()
        )
        return result or 0

    def get_last_n_hours_by_facility(
        self,
        facility_id: str,
        hours: int = 6,
    ) -> List[HealthRecord]:
        """Get records from last N hours for facility.

        Args:
            facility_id: Facility identifier.
            hours: Lookback window.

        Returns:
            List of HealthRecord instances.
        """
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        return (
            self.db.query(HealthRecord)
            .filter(
                HealthRecord.facility_id == facility_id,
                HealthRecord.timestamp >= cutoff,
            )
            .order_by(HealthRecord.timestamp.asc())
            .all()
        )
