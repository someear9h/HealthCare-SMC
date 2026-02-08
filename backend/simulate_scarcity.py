#!/usr/bin/env python3
"""
Scarcity Simulation Script - Trigger 'CRISIS' status for HSP002

This script simulates a critical bed shortage at hospital HSP002
by setting beds_available to near-zero and injecting high
admission rate records, forcing the prediction_service to
calculate a 'CRISIS' state (< 6 hours remaining bed capacity).

Usage:
  python3 simulate_scarcity.py
"""

import sys
import pandas as pd
from datetime import datetime, timedelta
from core.database import SessionLocal
from repositories.status_repository import StatusRepository
from repositories.health_repository import HealthRepository
from models.orm import FacilityStatus, HealthRecord, Facility
from sqlalchemy import func

def trigger_hsn002_crisis():
    """Trigger CRISIS status for HSP002 by setting critical metrics."""
    
    db = SessionLocal()
    
    try:
        print("🏥 SCARCITY SIMULATION - Triggering HSP002 CRISIS Status")
        print("=" * 70)
        
        # Step 1: Create critical facility status
        print("\n[1/3] Setting facility status to critical...")
        critical_status = FacilityStatus(
            facility_id="HSP002",
            beds_available=1,
            icu_available=0,
            ventilators_available=1,
            oxygen_units_available=2,
            medicine_stock_status="Critical",
            timestamp=datetime.utcnow()
        )
        db.add(critical_status)
        db.commit()
        print(f"✓ HSP002 Status: beds_available=1, icu_available=0")
        
        # Step 2: Inject high admission rate records (last 6 hours)
        print("\n[2/3] Injecting high admission rate records...")
        health_repo = HealthRepository(db)
        
        # Add 15 records in last 6 hours to trigger high admissions
        for i in range(15):
            minutes_ago = i * 24  # Spread over 6 hours
            timestamp = datetime.utcnow() - timedelta(minutes=minutes_ago)
            
            record = HealthRecord(
                facility_id="HSP002",
                indicator_name="New Malaria Cases",
                total_cases=8,  # 8 * 15 = 120 cases in 6 hours
                month="Feb",
                timestamp=timestamp
            )
            db.add(record)
        
        db.commit()
        print(f"✓ Added 15 health records (8 cases each = 120 total in 6h)")
        
        # Step 3: Verify crisis prediction
        print("\n[3/3] Verifying crisis calculation...")
        from services.prediction_service import PredictionService
        
        pred_service = PredictionService(db)
        prediction = pred_service.predict_bed_demand("HSP002")
        
        print(f"\n✓ Prediction Results:")
        print(f"  - Avg Admission Rate: {prediction['avg_admission_rate']:.2f} cases/hour")
        print(f"  - Projected 24h Cases: {prediction['projected_24h_admissions']}")
        print(f"  - Beds Remaining Hours: {prediction['beds_remaining_hours']:.2f} hours")
        print(f"  - Crisis Likely: {prediction['crisis_likely']}")
        
        if prediction['crisis_likely']:
            print(f"\n🔴 SUCCESS: HSP002 is now in CRISIS status!")
            print(f"   (Less than 24 hours of bed capacity remaining)")
        else:
            print(f"\n⚠️  Warning: Crisis not triggered. Current hours remaining: {prediction['beds_remaining_hours']:.1f}")
        
        print("\n" + "=" * 70)
        print("Scarcity simulation complete. Check /analytics/predicted-capacity for HSP002")
        
    except Exception as e:
        print(f"\n✗ Error during simulation: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    trigger_hsn002_crisis()
