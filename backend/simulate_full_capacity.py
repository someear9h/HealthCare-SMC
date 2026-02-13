"""
Simulator: Trigger 'Appointment Not Available' status.
Focus: HSP123 - Orthopedics (Specialty-Aware Overload)
"""

from datetime import datetime, timedelta
from core.database import SessionLocal
from models.orm import PatientTransaction, Facility

def trigger_appointment_block():
    db = SessionLocal()
    try:
        print("🚨 SIMULATING APPOINTMENT BLOCK - High Specialty Load")
        print("=" * 60)

        # 1. Target: HSP123 Orthopedics
        facility_id = "HSP123"
        dept = "Orthopedics"
        
        # 2. Inject 15 'CASE' transactions (Capacity is 10)
        # We use a very recent timestamp to ensure it's caught in the 'last 2 hours' window
        print(f"[1/2] Injecting 15 active cases into {dept} at {facility_id}...")
        now = datetime.utcnow()
        
        for i in range(15):
            # Spread transactions over the last 30 minutes
            timestamp = now - timedelta(minutes=i*2)
            
            tx = PatientTransaction(
                facility_id=facility_id,
                transaction_type="CASE",
                department=dept,
                indicator_name="Emergency Fracture",
                month="Feb",
                timestamp=timestamp
            )
            db.add(tx)
        
        db.commit()
        print(f"✓ Injected 15 individual patient transactions.")

        # 3. Simulate the Check
        print(f"\n[2/2] Testing Availability API Logic...")
        # (This mimics the logic inside your Appointment Router)
        active_load = db.query(PatientTransaction).filter(
            PatientTransaction.facility_id == facility_id,
            PatientTransaction.department == dept,
            PatientTransaction.transaction_type == "CASE",
            PatientTransaction.timestamp >= (now - timedelta(hours=2))
        ).count()

        capacity = 10 # Hardcoded for demo logic
        
        print(f"  - Current Load: {active_load}")
        print(f"  - Max Capacity: {capacity}")
        
        if active_load >= capacity:
            print(f"\n🔴 SUCCESS: Appointments for {dept} are now BLOCKED.")
            print(f"   Dashboard will now suggest Telemedicine or Redirect.")
        else:
            print(f"\n⚠️  Warning: Load ({active_load}) still below capacity ({capacity}).")

    except Exception as e:
        print(f"✗ Error during simulation: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    trigger_appointment_block()