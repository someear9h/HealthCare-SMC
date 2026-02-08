"""Bed demand prediction service for municipal intelligence.

Predicts bed shortage risk using rolling admission rates.
Production-grade insight without heavy ML.
"""

from __future__ import annotations

from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import math

from repositories.health_repository import HealthRepository
from repositories.status_repository import StatusRepository


class PredictionService:
    """Service for bed capacity forecasting.

    Algorithm:
    1. Calculate average admissions (cases) over last 6 hours
    2. Project 24-hour admissions at current rate
    3. Compare against current bed availability
    4. Flag crisis if projection + safety margin exceeds capacity
    """

    def __init__(self, db: Session):
        """Initialize service with DB session.

        Args:
            db: SQLAlchemy session.
        """
        self.db = db
        self.health_repo = HealthRepository(db)
        self.status_repo = StatusRepository(db)

    def predict_bed_demand(self, facility_id: str) -> Dict[str, Any]:
        """Predict bed demand and crisis likelihood.

        Args:
            facility_id: Facility to analyze.

        Returns:
            Dict with predictions:
            - facility_id: Facility identifier
            - avg_admission_rate: Cases/hour over last 6 hours
            - projected_24h_admissions: Forecast for next 24 hours
            - beds_remaining_hours: Hours until beds full at current rate
            - crisis_likely: Boolean flag
        """
        # Get health records from last 6 hours
        last_6h_records = self.health_repo.get_last_n_hours_by_facility(
            facility_id=facility_id,
            hours=6,
        )

        if not last_6h_records:
            # No recent data; assume stable
            return {
                "facility_id": facility_id,
                "avg_admission_rate": 0.0,
                "projected_24h_admissions": 0,
                "beds_remaining_hours": None,
                "crisis_likely": False,
            }

        # Calculate admission rate (cases per hour)
        total_admissions = sum(r.total_cases for r in last_6h_records)
        avg_admission_rate = total_admissions / 6.0

        # Project 24-hour admissions
        projected_24h = int(avg_admission_rate * 24)

        # Get current bed capacity
        latest_status = self.status_repo.get_latest_by_facility(facility_id)
        if not latest_status:
            # No status data; cannot predict
            return {
                "facility_id": facility_id,
                "avg_admission_rate": avg_admission_rate,
                "projected_24h_admissions": projected_24h,
                "beds_remaining_hours": float("inf"),
                "crisis_likely": False,
            }

        beds_available = latest_status.beds_available

        # Calculate hours until beds full (with safety margin of 1.2x)
        # If no admissions, infinite hours
        if avg_admission_rate <= 0:
            beds_remaining_hours = float("inf")
            crisis_likely = False
        else:
            # Hours = available_beds / (admission_rate * 1.2 safety margin)
            safety_margin = 1.2
            adjusted_rate = avg_admission_rate * safety_margin
            beds_remaining_hours = beds_available / adjusted_rate

            # Crisis if less than 24 hours of bed capacity at projected rate
            crisis_likely = beds_remaining_hours < 24

        # Ensure JSON-serializable: replace non-finite with None
        beds_remaining_safe = round(beds_remaining_hours, 1) if math.isfinite(beds_remaining_hours) else None

        return {
            "facility_id": facility_id,
            "avg_admission_rate": round(avg_admission_rate, 2),
            "projected_24h_admissions": projected_24h,
            "beds_remaining_hours": beds_remaining_safe,
            "crisis_likely": crisis_likely,
        }

    def predict_icu_demand(self, facility_id: str) -> Dict[str, Any]:
        """Predict ICU bed demand (similar logic to bed demand).

        Args:
            facility_id: Facility to analyze.

        Returns:
            Dict with ICU predictions.
        """
        # Get health records from last 6 hours
        last_6h_records = self.health_repo.get_last_n_hours_by_facility(
            facility_id=facility_id,
            hours=6,
        )

        if not last_6h_records:
            return {
                "facility_id": facility_id,
                "avg_admission_rate": 0.0,
                "projected_24h_admissions": 0,
                "icu_remaining_hours": None,
                "crisis_likely": False,
            }

        total_admissions = sum(r.total_cases for r in last_6h_records)
        avg_admission_rate = total_admissions / 6.0
        projected_24h = int(avg_admission_rate * 24)

        latest_status = self.status_repo.get_latest_by_facility(facility_id)
        if not latest_status:
            return {
                "facility_id": facility_id,
                "avg_admission_rate": avg_admission_rate,
                "projected_24h_admissions": projected_24h,
                "icu_remaining_hours": float("inf"),
                "crisis_likely": False,
            }

        icu_available = latest_status.icu_available

        if avg_admission_rate <= 0:
            icu_remaining_hours = float("inf")
            crisis_likely = False
        else:
            safety_margin = 1.5  # More conservative for ICU
            adjusted_rate = avg_admission_rate * safety_margin
            icu_remaining_hours = icu_available / adjusted_rate
            # ICU crisis if less than 12 hours capacity (more aggressive threshold)
            crisis_likely = icu_remaining_hours < 12

        icu_remaining_safe = round(icu_remaining_hours, 1) if math.isfinite(icu_remaining_hours) else None

        return {
            "facility_id": facility_id,
            "avg_admission_rate": round(avg_admission_rate, 2),
            "projected_24h_admissions": projected_24h,
            "icu_remaining_hours": icu_remaining_safe,
            "crisis_likely": crisis_likely,
        }

    def predict_all_facilities(self) -> Dict[str, Any]:
        """Predict bed demand across all facilities.

        Returns:
            Dict with facility predictions and crisis summary.
        """
        # Get all unique facility IDs that have health records
        from repositories.facility_repository import FacilityRepository
        
        facility_repo = FacilityRepository(self.db)
        facilities = facility_repo.get_all(limit=1000)

        predictions = []
        total_crisis_count = 0

        for facility in facilities:
            pred = self.predict_bed_demand(facility.facility_id)
            predictions.append(pred)
            if pred["crisis_likely"]:
                total_crisis_count += 1

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "total_facilities": len(predictions),
            "crisis_count": total_crisis_count,
            "predictions": predictions,
        }
