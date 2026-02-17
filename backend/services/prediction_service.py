"""Bed demand prediction service for municipal intelligence.

FINAL FIX: Sanitized all non-finite float values (inf/nan) for JSON compliance.
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

    Solves PS Section 4.1: Real-time visibility into public health infrastructure.
    """

    def __init__(self, db: Session):
        self.db = db
        self.health_repo = HealthRepository(db)
        self.status_repo = StatusRepository(db)

    def _sanitize_float(self, value: float, default: Optional[float] = 999.0) -> Optional[float]:
        """Helper to ensure floats are JSON compliant."""
        if value is None or not math.isfinite(value):
            return default
        return round(value, 1)

    def predict_bed_demand(self, facility_id: str) -> Dict[str, Any]:
        """Predict bed demand using sanitized transaction counts."""
        last_6h_records = self.health_repo.get_last_n_hours_by_facility(
            facility_id=facility_id,
            hours=6,
        )

        # Basic admission rate calculation
        total_admissions = len(last_6h_records) if last_6h_records else 0
        avg_admission_rate = total_admissions / 6.0
        projected_24h = int(avg_admission_rate * 24)

        # Get current bed capacity
        latest_status = self.status_repo.get_latest_by_facility(facility_id)
        
        # DEFAULT VALUES IF NO DATA
        beds_available = latest_status.beds_available if latest_status else 0
        
        # Calculate hours until beds full
        if avg_admission_rate <= 0:
            beds_remaining_hours = 999.0 
            crisis_likely = False
        else:
            # Safety margin: 1.2x
            adjusted_rate = avg_admission_rate * 1.2
            beds_remaining_hours = beds_available / adjusted_rate
            crisis_likely = beds_remaining_hours < 24

        return {
            "facility_id": facility_id,
            "avg_admission_rate": round(avg_admission_rate, 2),
            "projected_24h_admissions": projected_24h,
            "beds_remaining_hours": self._sanitize_float(beds_remaining_hours),
            "crisis_likely": bool(crisis_likely),
        }

    def predict_icu_demand(self, facility_id: str) -> Dict[str, Any]:
        """Predict ICU bed demand using sanitized transaction counts."""
        last_6h_records = self.health_repo.get_last_n_hours_by_facility(
            facility_id=facility_id,
            hours=6,
        )

        total_admissions = len(last_6h_records) if last_6h_records else 0
        avg_admission_rate = total_admissions / 6.0
        projected_24h = int(avg_admission_rate * 24)

        latest_status = self.status_repo.get_latest_by_facility(facility_id)
        icu_available = latest_status.icu_available if latest_status else 0

        if avg_admission_rate <= 0:
            icu_remaining_hours = 999.0
            crisis_likely = False
        else:
            # ICU safety margin: 1.5x
            adjusted_rate = avg_admission_rate * 1.5
            icu_remaining_hours = icu_available / adjusted_rate
            crisis_likely = icu_remaining_hours < 12

        return {
            "facility_id": facility_id,
            "avg_admission_rate": round(avg_admission_rate, 2),
            "projected_24h_admissions": projected_24h,
            "icu_remaining_hours": self._sanitize_float(icu_remaining_hours),
            "crisis_likely": bool(crisis_likely),
        }

    def predict_all_facilities(self) -> Dict[str, Any]:
        """Fetch predictions for all facilities."""
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