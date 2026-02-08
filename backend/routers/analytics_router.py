"""Analytics endpoints for bed demand and ward risk insights.

GET /analytics/predicted-capacity - Bed demand predictions
GET /analytics/ward-risk - Ward risk heatmap
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.database import get_db
from services.prediction_service import PredictionService
from services.ward_risk_service import WardRiskService
from repositories.status_repository import StatusRepository

router = APIRouter()


@router.get("/predicted-capacity", tags=["Analytics"])
def get_predicted_capacity(db: Session = Depends(get_db)):
    """Get bed demand predictions across all facilities.

    Returns:
        Dict with facility predictions and crisis summary.
    """
    service = PredictionService(db)
    predictions = service.predict_all_facilities()
    return predictions


@router.get("/predicted-capacity/{facility_id}", tags=["Analytics"])
def get_facility_predicted_capacity(facility_id: str, db: Session = Depends(get_db)):
    """Get bed demand prediction for specific facility.

    Args:
        facility_id: Facility identifier.

    Returns:
        Dict with bed demand prediction.
    """
    service = PredictionService(db)
    prediction = service.predict_bed_demand(facility_id)
    return prediction


@router.get("/ward-risk", tags=["Analytics"])
def get_ward_risk_heatmap(db: Session = Depends(get_db)):
    """Get ward-level risk heatmap across all wards.

    Returns:
        Dict with all ward risks, sorted by risk_score desc.
    """
    service = WardRiskService(db)
    risks = service.get_all_wards_risk()
    return risks


@router.get("/city-totals", tags=["Analytics"])
def get_city_totals(db: Session = Depends(get_db)):
    """Return aggregated city totals for resources from latest facility status records."""
    status_repo = StatusRepository(db)
    totals = status_repo.get_city_totals()
    return {"city_totals": totals}


@router.get("/ward-risk/{ward}", tags=["Analytics"])
def get_ward_risk(ward: str, db: Session = Depends(get_db)):
    """Get risk assessment for specific ward.

    Args:
        ward: Ward identifier.

    Returns:
        Dict with ward risk details.
    """
    service = WardRiskService(db)
    risk = service.compute_ward_risk(ward)
    return risk


@router.get("/critical-wards", tags=["Analytics"])
def get_critical_wards(db: Session = Depends(get_db)):
    """Get wards in CRITICAL state.

    Returns:
        List of critical wards.
    """
    service = WardRiskService(db)
    wards = service.get_critical_wards()
    return {"critical_wards": wards}


@router.get("/high-risk-wards", tags=["Analytics"])
def get_high_risk_wards(db: Session = Depends(get_db)):
    """Get wards in HIGH or CRITICAL state.

    Returns:
        List of high-risk wards.
    """
    service = WardRiskService(db)
    wards = service.get_high_risk_wards()
    return {"high_risk_wards": wards}
