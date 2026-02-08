"""Ambulance management endpoints.

POST /ambulances/update-location - Update ambulance GPS and status
GET /ambulances/nearest - Find nearest ambulances
GET /ambulances/status - Fleet status summary
"""

from __future__ import annotations

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from core.database import get_db
from services.ambulance_service import AmbulanceService
from schemas.orm_schemas import AmbulanceRead, AmbulanceUpdate, NearestAmbulanceResponse

router = APIRouter()


@router.post("/update-location", tags=["Ambulances"])
def update_ambulance_location(
    vehicle_id: str = Query(..., description="Vehicle identifier"),
    lat: float = Query(..., description="Latitude"),
    lng: float = Query(..., description="Longitude"),
    status: Optional[str] = Query(None, description="AVAILABLE, BUSY, or OFFLINE"),
    db: Session = Depends(get_db),
):
    """Update ambulance location and optionally status.

    Args:
        vehicle_id: Vehicle ID.
        lat: Latitude coordinate.
        lng: Longitude coordinate.
        status: Optional status update.

    Returns:
        Updated ambulance details.
    """
    try:
        service = AmbulanceService(db)
        ambulance = service.update_ambulance(
            vehicle_id=vehicle_id,
            lat=lat,
            lng=lng,
            status=status or "AVAILABLE",
        )
        return {"status": "updated", "ambulance": ambulance}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/nearest", tags=["Ambulances"])
def find_nearest_ambulances(
    lat: float = Query(..., description="Query latitude"),
    lng: float = Query(..., description="Query longitude"),
    limit: int = Query(3, ge=1, le=10, description="Max ambulances to return"),
    max_distance_km: float = Query(50.0, ge=1, description="Max distance filter (km)"),
    available_only: bool = Query(False, description="Only available ambulances?"),
    db: Session = Depends(get_db),
):
    """Find nearest ambulances to coordinates.

    Args:
        lat: Query latitude.
        lng: Query longitude.
        limit: Max results.
        max_distance_km: Distance filter.
        available_only: If true, only AVAILABLE status.

    Returns:
        List of nearest ambulances with distances.
    """
    service = AmbulanceService(db)
    if available_only:
        ambulances = service.find_nearest_available(lat, lng, limit)
    else:
        ambulances = service.find_nearest(lat, lng, limit, max_distance_km)

    return {
        "count": len(ambulances),
        "ambulances": ambulances,
    }


@router.get("/status", tags=["Ambulances"])
def get_fleet_status(db: Session = Depends(get_db)):
    """Get fleet-wide status summary.

    Returns:
        Fleet status with breakdowns by availability.
    """
    service = AmbulanceService(db)
    status = service.get_fleet_status()
    return status


@router.get("/ward/{ward}", tags=["Ambulances"])
def get_ward_ambulances(ward: str, db: Session = Depends(get_db)):
    """Get ambulances stationed in ward.

    Args:
        ward: Ward identifier.

    Returns:
        List of ambulances in ward.
    """
    service = AmbulanceService(db)
    ambulances = service.get_ward_ambulances(ward)
    return {"ward": ward, "ambulances": ambulances}
