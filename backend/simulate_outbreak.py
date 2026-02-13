#!/usr/bin/env python3
import sys
from datetime import datetime, timedelta
from core.database import SessionLocal
from models.orm import PatientTransaction, Facility
from services.ward_risk_service import WardRiskService

def trigger_ward_b_outbreak():
    db = SessionLocal()
    try:
        print("🦟 OUTBREAK SIMULATION - Transactional Event Stream")
        
        # 1. Ensure Ward-B exists
        ward_b_fac = db.query(Facility).filter(Facility.ward == "Ward-B").first()
        if not ward_b_fac:
            ward_b_fac = Facility(facility_id="WAR_B_001", facility_type="PHC", 
                                  district="Solapur", subdistrict="Central", ward="Ward-B")
            db.add(ward_b_fac); db.commit()

        # 2. Inject 300 INDIVIDUAL Patient Transactions (CASE)
        # This spikes the velocity (count) that WardRiskService now looks for
        print("\n[2/4] Injecting 300 individual Dengue transactions...")
        now = datetime.utcnow()
        for i in range(300):
            # Spread transactions across the last 3 hours to spike growth_rate
            seconds_ago = i * 36 
            timestamp = now - timedelta(seconds=seconds_ago)
            
            # Using our new individual patient model
            tx = PatientTransaction(
                facility_id=ward_b_fac.facility_id,
                transaction_type="CASE",
                department="General Medicine",
                indicator_name="Dengue",
                count=1,
                month="Feb",
                timestamp=timestamp
            )
            db.add(tx)
        
        db.commit()
        
        # 3. Calculate Risk based on COUNT()
        ward_service = WardRiskService(db)
        ward_risk = ward_service.compute_ward_risk("Ward-B")
        print(f"✓ Ward: {ward_risk['ward']} | Risk: {ward_risk['risk_score']} ({ward_risk['risk_level']})")
        
    except Exception as e:
        print(f"✗ Error: {e}"); db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    trigger_ward_b_outbreak()