#!/usr/bin/env python3
"""
Outbreak Simulation Script - Trigger 'CRITICAL' ward status

This script simulates a disease outbreak in Ward-B by injecting
a massive surge of dengue cases with current timestamp.
This spikes the growth_rate and recent_cases metrics,
pushing the ward risk score above 75 (CRITICAL threshold).

Usage:
  python3 simulate_outbreak.py
"""

import sys
from datetime import datetime, timedelta
from core.database import SessionLocal
from models.orm import HealthRecord, Facility
from services.ward_risk_service import WardRiskService

def trigger_ward_b_outbreak():
    """Trigger CRITICAL status for Ward-B via massive case surge."""
    
    db = SessionLocal()
    
    try:
        print("🦟 OUTBREAK SIMULATION - Triggering Ward-B CRITICAL Status")
        print("=" * 70)
        
        # Step 1: Verify Ward-B exists
        print("\n[1/4] Checking Ward-B facilities...")
        ward_b_facilities = (
            db.query(Facility)
            .filter(Facility.ward == "Ward-B")
            .all()
        )
        
        if not ward_b_facilities:
            print("✗ No facilities in Ward-B found. Creating test facility...")
            test_facility = Facility(
                facility_id="WAR_B_001",
                facility_type="PHC",
                district="Solapur",
                subdistrict="Central",
                ward="Ward-B"
            )
            db.add(test_facility)
            db.commit()
            ward_b_facilities = [test_facility]
        
        print(f"✓ Found {len(ward_b_facilities)} facilities in Ward-B")
        for fac in ward_b_facilities:
            print(f"  - {fac.facility_id} ({fac.facility_type})")
        
        # Step 2: Inject massive surge of dengue cases
        print("\n[2/4] Injecting disease outbreak data...")
        facility_id = ward_b_facilities[0].facility_id
        
        # Inject 60 records of dengue cases in the last 6 hours
        # This will create a massive growth spike and case volume
        now = datetime.utcnow()
        records_added = 0
        
        for i in range(60):
            # Spread records across last 6 hours
            minutes_ago = (i % 360) // 60  # 0-359 minutes
            timestamp = now - timedelta(minutes=minutes_ago)
            
            record = HealthRecord(
                facility_id=facility_id,
                indicator_name="New Dengue Cases",  # Pre-normalized
                total_cases=5,  # 5 * 60 = 300 cases total
                month="Feb",
                timestamp=timestamp
            )
            db.add(record)
            records_added += 1
        
        db.commit()
        print(f"✓ Injected {records_added} dengue case records")
        print(f"  - Total cases: {records_added * 5} cases")
        print(f"  - Timespan: Last 6 hours")
        
        # Step 3: Calculate ward risk
        print("\n[3/4] Calculating Ward-B risk score...")
        ward_service = WardRiskService(db)
        ward_risk = ward_service.compute_ward_risk("Ward-B")
        
        print(f"\n✓ Ward Risk Analysis:")
        print(f"  - Ward: {ward_risk['ward']}")
        print(f"  - Risk Score: {ward_risk['risk_score']} / 100")
        print(f"  - Risk Level: {ward_risk['risk_level']}")
        print(f"  - Recent Cases (24h): {ward_risk['recent_cases']}")
        print(f"  - ICU Pressure: {ward_risk['icu_pressure']:.1%}")
        print(f"  - Growth Rate: {ward_risk['growth_rate']:.2f}")
        
        if ward_risk['risk_level'] == "CRITICAL":
            print(f"\n🔴 SUCCESS: Ward-B is now in CRITICAL status!")
            print(f"   (Risk score {ward_risk['risk_score']} >= 75)")
        else:
            print(f"\n⚠️  Current Level: {ward_risk['risk_level']} (Score: {ward_risk['risk_score']})")
            print(f"   Additional records may be needed to reach CRITICAL (75+)")
        
        # Step 4: Show all wards
        print("\n[4/4] Full Ward Risk Distribution:")
        all_wards = ward_service.get_all_wards_risk()
        print(f"\n✓ Total Wards: {all_wards['total_wards']}")
        print(f"  - Critical: {all_wards['critical_count']}")
        print(f"  - High: {all_wards['high_count']}")
        print(f"  - Medium/Low: {all_wards['total_wards'] - all_wards['critical_count'] - all_wards['high_count']}")
        
        print("\nTop 5 Riskiest Wards:")
        for idx, ward in enumerate(all_wards['wards'][:5], 1):
            print(f"  {idx}. {ward['ward']}: {ward['risk_level']} (Score: {ward['risk_score']})")
        
        print("\n" + "=" * 70)
        print("Outbreak simulation complete. Check /analytics/ward-risk for Ward-B status")
        
    except Exception as e:
        print(f"\n✗ Error during simulation: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    trigger_ward_b_outbreak()
