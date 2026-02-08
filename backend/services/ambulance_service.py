"""Ambulance intelligence service for operational insights.

Provides nearest-ambulance queries and fleet status.
Uses simple distance math; ready for PostGIS on PostgreSQL later.
"""

from __future__ import annotations

from typing import List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

from repositories.ambulance_repository import AmbulanceRepository


class AmbulanceService:
    """Service for ambulance management and location queries.

    Features:
    - Update GPS location and status
    - Find nearest ambulances to coordinates
    - Fleet status aggregation
    """

    def __init__(self, db: Session):
        """Initialize service with DB session.

        Args:
            db: SQLAlchemy session.
        """
        self.db = db
        self.ambulance_repo = AmbulanceRepository(db)

    def update_ambulance(
        self,
        vehicle_id: str,
        lat: float,
        lng: float,
        status: str = "AVAILABLE",
    ) -> Dict[str, Any]:
        """Update ambulance location and status.

        Args:
            vehicle_id: Vehicle identifier.
            lat: Latitude.
            lng: Longitude.
            status: AVAILABLE, BUSY, or OFFLINE.

        Returns:
            Updated ambulance dict with distance N/A.

        Raises:
            ValueError: If ambulance not found.
        """
        ambulance = self.ambulance_repo.get_or_create(
            vehicle_id=vehicle_id,
            ward="Unknown",
            lat=lat,
            lng=lng,
            status=status,
        )

        # If already exists, update it
        if ambulance.id == self.ambulance_repo.get_by_vehicle_id(vehicle_id).id:
            ambulance = self.ambulance_repo.update_location(
                vehicle_id=vehicle_id,
                lat=lat,
                lng=lng,
                status=status,
            )

        if not ambulance:
            raise ValueError(f"Ambulance {vehicle_id} not found")

        return {
            "vehicle_id": ambulance.vehicle_id,
            "ward": ambulance.ward,
            "status": ambulance.status,
            "lat": ambulance.lat,
            "lng": ambulance.lng,
            "last_updated": ambulance.last_updated.isoformat(),
        }

    def find_nearest(
        self,
        lat: float,
        lng: float,
        limit: int = 3,
        max_distance_km: float = 50.0,
    ) -> List[Dict[str, Any]]:
        """Find nearest ambulances to coordinates.

        Uses simple Euclidean distance approximation.
        For precise geodetic calculations, use PostGIS on PostgreSQL.

        Args:
            lat: Query latitude.
            lng: Query longitude.
            limit: Max ambulances to return.
            max_distance_km: Max distance filter (km).

        Returns:
            List of nearest ambulances with distances, sorted by proximity.
        """
        results = self.ambulance_repo.find_nearest(
            lat=lat,
            lng=lng,
            limit=limit,
            max_distance_km=max_distance_km,
        )

        return results

    def find_nearest_available(
        self,
        lat: float,
        lng: float,
        limit: int = 3,
    ) -> List[Dict[str, Any]]:
        """Find nearest available (not BUSY or OFFLINE) ambulances.

        Args:
            lat: Query latitude.
            lng: Query longitude.
            limit: Max ambulances to return.

        Returns:
            List of nearest available ambulances.
        """
        all_nearest = self.find_nearest(lat, lng, limit * 2)  # Get more, filter available

        available = [a for a in all_nearest if a["status"] == "AVAILABLE"]
        return available[:limit]

    def get_fleet_status(self) -> Dict[str, Any]:
        """Get fleet-wide status summary.

        Returns:
            Dict with total, available, busy, offline counts.
        """
        status_counts = self.ambulance_repo.count_by_status()

        total = sum(status_counts.values())

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "total_ambulances": total,
            "status_breakdown": status_counts,
            "availability_rate": round(
                (status_counts.get("AVAILABLE", 0) / total * 100) if total > 0 else 0,
                1
            ),
        }

    def get_ward_ambulances(self, ward: str) -> List[Dict[str, Any]]:
        """Get all ambulances stationed in a ward.

        Args:
            ward: Ward identifier.

        Returns:
            List of ambulances in ward.
        """
        ambulances = self.ambulance_repo.get_by_ward(ward)
        return [
            {
                "id": a.id,
                "vehicle_id": a.vehicle_id,
                "ward": a.ward,
                "status": a.status,
                "lat": a.lat,
                "lng": a.lng,
                "last_updated": a.last_updated.isoformat(),
            }
            for a in ambulances
        ]
