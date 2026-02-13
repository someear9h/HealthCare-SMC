"""Ward risk heatmap service for municipal intelligence.

UPDATED: Now uses individual PatientTransaction counting for live risk scoring.
"""

from __future__ import annotations

from typing import Dict, List, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

# ########################################################################
# HUGE CHANGE: IMPORT PATIENTTRANSACTION INSTEAD OF HEALTHRECORD
# ########################################################################
from models.orm import PatientTransaction, FacilityStatus, Facility
from repositories.status_repository import StatusRepository
from repositories.facility_repository import FacilityRepository


class WardRiskService:
    """Service for ward-level risk aggregation and scoring.

    Fulfills PS Section 2.3: Identifying high-risk and vulnerable zones.
    """

    def __init__(self, db: Session):
        self.db = db
        self.status_repo = StatusRepository(db)
        self.facility_repo = FacilityRepository(db)

    def get_ward_cases_24h(self, ward: str) -> int:
        """Count individual 'CASE' transactions in ward over last 24 hours."""
        # ########################################################################
        # LOGIC CHANGE: SUM() -> COUNT()
        # We count the rows where transaction_type is 'CASE'.
        # ########################################################################
        result = (
            self.db.query(func.count(PatientTransaction.id))
            .join(Facility, Facility.facility_id == PatientTransaction.facility_id)
            .filter(
                Facility.ward == ward,
                PatientTransaction.transaction_type == "CASE",
                PatientTransaction.timestamp >= datetime.utcnow() - timedelta(hours=24),
            )
            .scalar()
        )
        return result or 0

    def get_ward_cases_6h(self, ward: str) -> int:
        """Count individual 'CASE' transactions in ward over last 6 hours."""
        result = (
            self.db.query(func.count(PatientTransaction.id))
            .join(Facility, Facility.facility_id == PatientTransaction.facility_id)
            .filter(
                Facility.ward == ward,
                PatientTransaction.transaction_type == "CASE",
                PatientTransaction.timestamp >= datetime.utcnow() - timedelta(hours=6),
            )
            .scalar()
        )
        return result or 0

    def get_ward_icu_pressure(self, ward: str) -> float:
        """Calculate ICU pressure for ward (Stays same - based on FacilityStatus)."""
        facilities = self.db.query(Facility).filter(Facility.ward == ward).all()
        if not facilities: return 0.0

        total_icu_capacity = 0
        total_icu_available = 0

        for facility in facilities:
            latest_status = self.status_repo.get_latest_by_facility(facility.facility_id)
            if latest_status:
                total_icu_capacity += 20 # Baseline baseline
                total_icu_available += latest_status.icu_available

        if total_icu_capacity == 0: return 0.0
        pressure = (total_icu_capacity - total_icu_available) / total_icu_capacity
        return max(0.0, min(1.0, pressure))

    def compute_ward_risk(self, ward: str) -> Dict[str, Any]:
        """Compute risk score (0-100) using count-based data."""
        cases_24h = self.get_ward_cases_24h(ward)
        cases_6h = self.get_ward_cases_6h(ward)
        icu_pressure = self.get_ward_icu_pressure(ward)

        # Normalization (adjusted for individual patient velocity)
        # Assume > 200 individual cases in 24h for a single ward is critical
        cases_normalized = min(100.0, (cases_24h / 200.0) * 100.0)

        growth_rate = 0.0
        growth_normalized = 0.0
        if cases_24h > 0:
            growth_rate = cases_6h / (cases_24h / 4.0)
            growth_normalized = min(100.0, (growth_rate / 1.5) * 100.0)

        icu_normalized = icu_pressure * 100.0

        risk_score = (cases_normalized * 0.5 + growth_normalized * 0.3 + icu_normalized * 0.2)

        if risk_score >= 75: risk_level = "CRITICAL"
        elif risk_score >= 50: risk_level = "HIGH"
        elif risk_score >= 25: risk_level = "MEDIUM"
        else: risk_level = "LOW"

        # KEEP THESE KEYS SAME FOR FRONTEND COMPATIBILITY
        return {
            "ward": ward,
            "risk_score": round(risk_score, 1),
            "risk_level": risk_level,
            "recent_cases": cases_24h, # Frontend uses this for Heatmap labels
            "icu_pressure": round(icu_pressure, 3),
            "growth_rate": round(growth_rate, 2),
        }

    def get_all_wards_risk(self) -> Dict[str, Any]:
        """Fetch risk for all wards for the GIS Heatmap."""
        wards = self.db.query(Facility.ward).distinct().all()
        risks = [self.compute_ward_risk(w[0]) for w in wards if w[0]]
        risks.sort(key=lambda x: x["risk_score"], reverse=True)

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "total_wards": len(risks),
            "critical_count": sum(1 for r in risks if r["risk_level"] == "CRITICAL"),
            "high_count": sum(1 for r in risks if r["risk_level"] == "HIGH"),
            "wards": risks,
        }