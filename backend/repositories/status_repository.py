"""Facility status repository for resource tracking."""

from __future__ import annotations

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import func

from models.orm import FacilityStatus, Facility
from repositories.base_repository import BaseRepository


class StatusRepository(BaseRepository[FacilityStatus]):
    """Repository for FacilityStatus model.

    Responsibilities: insert, fetch, aggregate resource status.
    """

    def __init__(self, db: Session):
        super().__init__(db, FacilityStatus)

    def get_latest_by_facility(self, facility_id: str) -> Optional[FacilityStatus]:
        """Fetch most recent status record for facility.

        Args:
            facility_id: Facility identifier.

        Returns:
            FacilityStatus instance or None.
        """
        return (
            self.db.query(FacilityStatus)
            .filter(FacilityStatus.facility_id == facility_id)
            .order_by(FacilityStatus.timestamp.desc())
            .first()
        )

    def get_recent_by_facility(
        self,
        facility_id: str,
        limit: int = 10,
        hours: int = 24,
    ) -> List[FacilityStatus]:
        """Fetch recent status records for facility.

        Args:
            facility_id: Facility identifier.
            limit: Max records.
            hours: Lookback window in hours.

        Returns:
            List of FacilityStatus instances.
        """
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        return (
            self.db.query(FacilityStatus)
            .filter(
                FacilityStatus.facility_id == facility_id,
                FacilityStatus.timestamp >= cutoff,
            )
            .order_by(FacilityStatus.timestamp.desc())
            .limit(limit)
            .all()
        )

    def get_city_totals(self) -> Dict[str, int]:
        """Aggregate resource availability across all facilities.

        Returns:
            Dict with keys: total_beds, total_icu, total_ventilators, total_oxygen.
        """
        # Get latest status for each facility
        subquery = (
            self.db.query(
                FacilityStatus.facility_id,
                func.max(FacilityStatus.timestamp).label("latest_ts"),
            )
            .group_by(FacilityStatus.facility_id)
            .subquery()
        )

        results = (
            self.db.query(FacilityStatus)
            .join(
                subquery,
                (FacilityStatus.facility_id == subquery.c.facility_id)
                & (FacilityStatus.timestamp == subquery.c.latest_ts),
            )
            .all()
        )

        totals = {
            "total_beds": sum(r.beds_available for r in results),
            "total_icu": sum(r.icu_available for r in results),
            "total_ventilators": sum(r.ventilators_available for r in results),
            "total_oxygen": sum(r.oxygen_units_available for r in results),
        }
        return totals

    def get_facility_totals(self, facility_id: str) -> Dict[str, int]:
        """Get current totals for a single facility (latest record).

        Args:
            facility_id: Facility identifier.

        Returns:
            Dict with resource counts.
        """
        latest = self.get_latest_by_facility(facility_id)
        if not latest:
            return {
                "beds_available": 0,
                "icu_available": 0,
                "ventilators_available": 0,
                "oxygen_units_available": 0,
            }
        return {
            "beds_available": latest.beds_available,
            "icu_available": latest.icu_available,
            "ventilators_available": latest.ventilators_available,
            "oxygen_units_available": latest.oxygen_units_available,
        }

    def has_crisis(self, facility_id: str) -> bool:
        """Check if facility is in resource crisis.

        Thresholds:
        - beds < 5
        - icu < 2
        - oxygen < 5
        - medicine_stock_status == "Critical"

        Args:
            facility_id: Facility identifier.

        Returns:
            True if facility meets any crisis threshold.
        """
        latest = self.get_latest_by_facility(facility_id)
        if not latest:
            return False
        return (
            latest.beds_available < 5
            or latest.icu_available < 2
            or latest.oxygen_units_available < 5
            or latest.medicine_stock_status == "Critical"
        )

    def get_critical_facilities(self) -> List[FacilityStatus]:
        """Get all facilities currently in crisis.

        Returns:
            List of FacilityStatus records in crisis.
        """
        # Get latest status for each facility
        subquery = (
            self.db.query(
                FacilityStatus.facility_id,
                func.max(FacilityStatus.timestamp).label("latest_ts"),
            )
            .group_by(FacilityStatus.facility_id)
            .subquery()
        )

        results = (
            self.db.query(FacilityStatus)
            .join(
                subquery,
                (FacilityStatus.facility_id == subquery.c.facility_id)
                & (FacilityStatus.timestamp == subquery.c.latest_ts),
            )
            .filter(
                (FacilityStatus.beds_available < 5)
                | (FacilityStatus.icu_available < 2)
                | (FacilityStatus.oxygen_units_available < 5)
                | (FacilityStatus.medicine_stock_status == "Critical")
            )
            .all()
        )
        return results

    def get_average_capacity(self, hours: int = 24) -> Dict[str, float]:
        """Calculate average capacity over time window.

        Args:
            hours: Lookback window in hours.

        Returns:
            Dict with average values.
        """
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        results = (
            self.db.query(
                func.avg(FacilityStatus.beds_available).label("avg_beds"),
                func.avg(FacilityStatus.icu_available).label("avg_icu"),
                func.avg(FacilityStatus.ventilators_available).label("avg_ventilators"),
                func.avg(FacilityStatus.oxygen_units_available).label("avg_oxygen"),
            )
            .filter(FacilityStatus.timestamp >= cutoff)
            .first()
        )

        return {
            "avg_beds": float(results.avg_beds or 0),
            "avg_icu": float(results.avg_icu or 0),
            "avg_ventilators": float(results.avg_ventilators or 0),
            "avg_oxygen": float(results.avg_oxygen or 0),
        }
