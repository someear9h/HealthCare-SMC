"""Facility repository for data access."""

from __future__ import annotations

from typing import Optional, List, Dict, Any
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import func

from models.orm import Facility
from repositories.base_repository import BaseRepository


class FacilityRepository(BaseRepository[Facility]):
    """Repository for Facility model.

    Responsibilities: insert, fetch, aggregate facility data.
    """

    def __init__(self, db: Session):
        super().__init__(db, Facility)

    def get_by_facility_id(self, facility_id: str) -> Optional[Facility]:
        """Fetch facility by facility_id (unique).

        Args:
            facility_id: Unique facility identifier.

        Returns:
            Facility instance or None.
        """
        return self.db.query(Facility).filter(Facility.facility_id == facility_id).first()

    def get_by_type(self, facility_type: str, limit: int = 100) -> List[Facility]:
        """Fetch facilities by type.

        Args:
            facility_type: Type filter (Hospital, Lab, PHC, Private).
            limit: Max records.

        Returns:
            List of Facility instances.
        """
        return (
            self.db.query(Facility)
            .filter(Facility.facility_type == facility_type)
            .limit(limit)
            .all()
        )

    def get_by_district(self, district: str, limit: int = 100) -> List[Facility]:
        """Fetch facilities in district.

        Args:
            district: District name.
            limit: Max records.

        Returns:
            List of Facility instances.
        """
        return (
            self.db.query(Facility)
            .filter(Facility.district == district)
            .limit(limit)
            .all()
        )

    def get_by_ward(self, ward: str, limit: int = 100) -> List[Facility]:
        """Fetch facilities in ward.

        Args:
            ward: Ward name/code.
            limit: Max records.

        Returns:
            List of Facility instances.
        """
        return (
            self.db.query(Facility)
            .filter(Facility.ward == ward)
            .limit(limit)
            .all()
        )

    def count_by_type(self) -> Dict[str, int]:
        """Count facilities by type.

        Returns:
            Dict mapping facility_type to count.
        """
        results = (
            self.db.query(
                Facility.facility_type,
                func.count(Facility.id).label("count")
            )
            .group_by(Facility.facility_type)
            .all()
        )
        return {ftype: count for ftype, count in results}

    def get_or_create(self, facility_id: str, **kwargs: Any) -> Facility:
        """Upsert: get existing facility or create new one.

        Args:
            facility_id: Unique identifier.
            **kwargs: Other facility fields.

        Returns:
            Facility instance.
        """
        facility = self.get_by_facility_id(facility_id)
        if facility:
            return facility
        kwargs["facility_id"] = facility_id
        return self.create(**kwargs)
