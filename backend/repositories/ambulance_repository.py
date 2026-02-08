"""Ambulance repository for vehicle tracking."""

from __future__ import annotations

from typing import Optional, List, Dict, Any
from datetime import datetime
import math

from sqlalchemy.orm import Session
from sqlalchemy import func

from models.orm import Ambulance
from repositories.base_repository import BaseRepository


class AmbulanceRepository(BaseRepository[Ambulance]):
    """Repository for Ambulance model.

    Responsibilities: insert, fetch, locate nearest ambulances.
    """

    def __init__(self, db: Session):
        super().__init__(db, Ambulance)

    def get_by_vehicle_id(self, vehicle_id: str) -> Optional[Ambulance]:
        """Fetch ambulance by vehicle_id.

        Args:
            vehicle_id: Unique vehicle identifier.

        Returns:
            Ambulance instance or None.
        """
        return self.db.query(Ambulance).filter(Ambulance.vehicle_id == vehicle_id).first()

    def get_by_status(self, status: str, limit: int = 100) -> List[Ambulance]:
        """Fetch ambulances by status.

        Args:
            status: Status filter (AVAILABLE, BUSY, OFFLINE).
            limit: Max records.

        Returns:
            List of Ambulance instances.
        """
        return (
            self.db.query(Ambulance)
            .filter(Ambulance.status == status)
            .limit(limit)
            .all()
        )

    def get_by_ward(self, ward: str, limit: int = 100) -> List[Ambulance]:
        """Fetch ambulances in ward.

        Args:
            ward: Ward name/code.
            limit: Max records.

        Returns:
            List of Ambulance instances.
        """
        return (
            self.db.query(Ambulance)
            .filter(Ambulance.ward == ward)
            .limit(limit)
            .all()
        )

    def get_available(self, limit: int = 100) -> List[Ambulance]:
        """Fetch available ambulances.

        Args:
            limit: Max records.

        Returns:
            List of available Ambulance instances.
        """
        return self.get_by_status("AVAILABLE", limit)

    def update_location(
        self,
        vehicle_id: str,
        lat: float,
        lng: float,
        status: Optional[str] = None,
    ) -> Optional[Ambulance]:
        """Update ambulance GPS location and optionally status.

        Args:
            vehicle_id: Unique vehicle identifier.
            lat: Latitude coordinate.
            lng: Longitude coordinate.
            status: Optional new status.

        Returns:
            Updated Ambulance instance or None if not found.
        """
        ambulance = self.get_by_vehicle_id(vehicle_id)
        if not ambulance:
            return None

        update_dict = {
            "lat": lat,
            "lng": lng,
            "last_updated": datetime.utcnow(),
        }
        if status:
            update_dict["status"] = status

        for key, value in update_dict.items():
            setattr(ambulance, key, value)

        self.db.commit()
        self.db.refresh(ambulance)
        return ambulance

    def find_nearest(
        self,
        lat: float,
        lng: float,
        limit: int = 3,
        max_distance_km: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """Find nearest ambulances using Euclidean distance approximation.

        Uses simple (lat1-lat2)^2 + (lng1-lng2)^2 formula.
        For precise geodetic calculations, add PostGIS on PostgreSQL later.

        Args:
            lat: Query latitude.
            lng: Query longitude.
            limit: Max results to return.
            max_distance_km: Optional distance filter (rough km approximation).

        Returns:
            List of dicts with ambulance info and distance_km.
        """
        ambulances = self.get_all(limit=1000)

        results = []
        for amb in ambulances:
            # Rough distance in "degrees" (not exact km)
            distance_sq = (amb.lat - lat) ** 2 + (amb.lng - lng) ** 2
            distance_approx = math.sqrt(distance_sq)

            # Rough conversion to km (~111 km per degree)
            distance_km = distance_approx * 111

            if max_distance_km and distance_km > max_distance_km:
                continue

            results.append({
                "id": amb.id,
                "vehicle_id": amb.vehicle_id,
                "ward": amb.ward,
                "status": amb.status,
                "lat": amb.lat,
                "lng": amb.lng,
                "last_updated": amb.last_updated,
                "distance_km": round(distance_km, 2),
            })

        # Sort by distance and return top N
        results.sort(key=lambda x: x["distance_km"])
        return results[:limit]

    def count_by_status(self) -> Dict[str, int]:
        """Count ambulances by status.

        Returns:
            Dict mapping status to count.
        """
        results = (
            self.db.query(Ambulance.status, func.count(Ambulance.id).label("count"))
            .group_by(Ambulance.status)
            .all()
        )
        return {status: count for status, count in results}

    def get_or_create(self, vehicle_id: str, **kwargs: Any) -> Ambulance:
        """Upsert: get existing ambulance or create new one.

        Args:
            vehicle_id: Unique identifier.
            **kwargs: Other ambulance fields.

        Returns:
            Ambulance instance.
        """
        ambulance = self.get_by_vehicle_id(vehicle_id)
        if ambulance:
            return ambulance
        kwargs["vehicle_id"] = vehicle_id
        return self.create(**kwargs)
