#!/usr/bin/env python3
from datetime import datetime, timedelta
from core.database import SessionLocal
from models.orm import FacilityStatus, PatientTransaction, Facility
from services.prediction_service import PredictionService

def trigger_hsp002_crisis():
    db = SessionLocal()
    try:
        print("🏥 SCARCITY SIMULATION - High Velocity Admissions")
        
        # 1. Set Infrastructure to Critical Status
        # Directly addresses PS Section 4: Real-time visibility into infrastructure
        status = FacilityStatus(
            facility_id="HSP002",
            beds_available=2, # Only 2 beds left
            icu_available=0,
            medicine_stock_status="Critical",
            timestamp=datetime.utcnow()
        )
        db.add(status); db.commit()

        # 2. Inject high-velocity 'CASE' transactions in the last 2 hours
        # PredictionService will see a high 'admissions per hour' count
        print("\n[2/3] Streaming 100 patient admissions...")
        now = datetime.utcnow()
        for i in range(100):
            timestamp = now - timedelta(minutes=i)
            tx = PatientTransaction(
                facility_id="HSP002",
                transaction_type="CASE",
                department="Emergency",
                indicator_name="Acute Respiratory Distress",
                count=1,
                month="Feb",
                timestamp=timestamp
            )
            db.add(tx)
        
        db.commit()

        # 3. Run Prediction logic (Capacity / Velocity)
        pred_service = PredictionService(db)
        prediction = pred_service.predict_bed_demand("HSP002")
        
        print(f"✓ Avg Admission Rate: {prediction['avg_admission_rate']:.2f}/hr")
        print(f"✓ Hours Remaining: {prediction['beds_remaining_hours']:.2f}")
        
        if prediction['crisis_likely']:
            print("🔴 SUCCESS: HSP002 is in CRISIS status!")

    except Exception as e:
        print(f"✗ Error: {e}"); db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    trigger_hsp002_crisis()