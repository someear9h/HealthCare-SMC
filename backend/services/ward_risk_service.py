"""Ward risk heatmap service for municipal intelligence.

Aggregates health data by ward and computes risk scores.
Combines case volume, growth rate, and ICU pressure.
"""

from __future__ import annotations

from typing import Dict, List, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from models.orm import HealthRecord, FacilityStatus, Facility
from repositories.health_repository import HealthRepository
from repositories.status_repository import StatusRepository
from repositories.facility_repository import FacilityRepository


class WardRiskService:
    """Service for ward-level risk aggregation and scoring.

    Risk score combines:
    1. Recent case count (last 24h) — weight 0.5
    2. Growth rate (compare last 6h vs last 24h) — weight 0.3
    3. ICU pressure (low availability) — weight 0.2
    """

    def __init__(self, db: Session):
        """Initialize service with DB session.

        Args:
            db: SQLAlchemy session.
        """
        self.db = db
        self.health_repo = HealthRepository(db)
        self.status_repo = StatusRepository(db)
        self.facility_repo = FacilityRepository(db)

    def get_ward_cases_24h(self, ward: str) -> int:
        """Get total cases in ward over last 24 hours.

        Args:
            ward: Ward identifier.

        Returns:
            Total case count.
        """
        result = (
            self.db.query(func.sum(HealthRecord.total_cases))
            .join(Facility, Facility.facility_id == HealthRecord.facility_id)
            .filter(
                Facility.ward == ward,
                HealthRecord.timestamp >= datetime.utcnow() - timedelta(hours=24),
            )
            .scalar()
        )
        return result or 0

    def get_ward_cases_6h(self, ward: str) -> int:
        """Get total cases in ward over last 6 hours.

        Args:
            ward: Ward identifier.

        Returns:
            Total case count.
        """
        result = (
            self.db.query(func.sum(HealthRecord.total_cases))
            .join(Facility, Facility.facility_id == HealthRecord.facility_id)
            .filter(
                Facility.ward == ward,
                HealthRecord.timestamp >= datetime.utcnow() - timedelta(hours=6),
            )
            .scalar()
        )
        return result or 0

    def get_ward_icu_pressure(self, ward: str) -> float:
        """Calculate ICU pressure for ward.

        ICU pressure = (total_icu_capacity - available_icu) / total_icu_capacity

        Args:
            ward: Ward identifier.

        Returns:
            Pressure float between 0.0 and 1.0.
        """
        facilities = (
            self.db.query(Facility)
            .filter(Facility.ward == ward)
            .all()
        )

        if not facilities:
            return 0.0

        total_icu_capacity = 0
        total_icu_available = 0

        for facility in facilities:
            latest_status = self.status_repo.get_latest_by_facility(facility.facility_id)
            if latest_status:
                # Assume total capacity = available + some implied occupancy
                # For simplicity: assume 20 ICU beds per facility as baseline
                total_icu_capacity += 20
                total_icu_available += latest_status.icu_available

        if total_icu_capacity == 0:
            return 0.0

        pressure = (total_icu_capacity - total_icu_available) / total_icu_capacity
        return max(0.0, min(1.0, pressure))  # Clamp to [0, 1]

    def compute_ward_risk(self, ward: str) -> Dict[str, Any]:
        """Compute risk score for ward.

        Risk formula (0-100):
        risk = (
            cases_24h_normalized * 0.5 +
            growth_rate_normalized * 0.3 +
            icu_pressure_normalized * 0.2
        )

        Args:
            ward: Ward identifier.

        Returns:
            Dict with ward, risk_score, risk_level, recent_cases, icu_pressure.
        """
        cases_24h = self.get_ward_cases_24h(ward)
        cases_6h = self.get_ward_cases_6h(ward)
        icu_pressure = self.get_ward_icu_pressure(ward)

        # Normalize case count (0-100 scale; assume > 500 cases = 100)
        cases_normalized = min(100.0, (cases_24h / 500.0) * 100.0)

        # Compute growth rate (6h vs 24h)
        growth_rate = 0.0
        growth_normalized = 0.0
        if cases_24h == 0:
            growth_rate = 0.0
            growth_normalized = 0.0
        else:
            # Expect ~1/4 of daily cases in 6h normally
            growth_rate = cases_6h / (cases_24h / 4.0) if cases_24h > 0 else 0.0
            # Normalize growth: >1.5 is rapid growth
            growth_normalized = min(100.0, (growth_rate / 1.5) * 100.0)

        icu_normalized = icu_pressure * 100.0

        # Weighted risk score
        risk_score = (
            cases_normalized * 0.5 +
            growth_normalized * 0.3 +
            icu_normalized * 0.2
        )

        # Determine risk level
        if risk_score >= 75:
            risk_level = "CRITICAL"
        elif risk_score >= 50:
            risk_level = "HIGH"
        elif risk_score >= 25:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        return {
            "ward": ward,
            "risk_score": round(risk_score, 1),
            "risk_level": risk_level,
            "recent_cases": cases_24h,
            "icu_pressure": round(icu_pressure, 3),
            "growth_rate": round(growth_rate, 2),
        }

    def get_all_wards_risk(self) -> Dict[str, Any]:
        """Compute risk for all wards.

        Returns:
            Dict with timestamp and list of ward risks sorted by risk_score desc.
        """
        # Get unique wards from facilities table
        wards = (
            self.db.query(Facility.ward)
            .distinct()
            .all()
        )

        risks = []
        for (ward,) in wards:
            if ward:  # Skip None wards
                risk = self.compute_ward_risk(ward)
                risks.append(risk)

        # Sort by risk_score descending
        risks.sort(key=lambda x: x["risk_score"], reverse=True)

        critical_count = sum(1 for r in risks if r["risk_level"] == "CRITICAL")
        high_count = sum(1 for r in risks if r["risk_level"] == "HIGH")

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "total_wards": len(risks),
            "critical_count": critical_count,
            "high_count": high_count,
            "wards": risks,
        }

    def get_critical_wards(self) -> List[Dict[str, Any]]:
        """Get wards above CRITICAL threshold.

        Returns:
            List of wards in CRITICAL state, sorted by risk_score desc.
        """
        all_risks = self.get_all_wards_risk()
        critical = [r for r in all_risks["wards"] if r["risk_level"] == "CRITICAL"]
        return critical

    def get_high_risk_wards(self) -> List[Dict[str, Any]]:
        """Get wards in HIGH or CRITICAL state.

        Returns:
            List of high-risk wards.
        """
        all_risks = self.get_all_wards_risk()
        high_risk = [r for r in all_risks["wards"] if r["risk_level"] in ["HIGH", "CRITICAL"]]
        return high_risk
