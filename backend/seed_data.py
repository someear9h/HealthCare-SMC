from core.database import SessionLocal, init_db
from models.orm import Facility, PatientTransaction
from datetime import datetime, timedelta

def seed_appointment_test_data():
    db = SessionLocal()
    init_db() # Ensure tables exist
    
    try:
        print("🌱 SEEDING DATA - Unified Digital Health Ecosystem")
        print("=" * 60)

        # 1. Seed Facilities
        facilities = [
            Facility(facility_id="HSP123", facility_type="Hospital", district="Solapur", subdistrict="North", ward="Ward-12"),
            Facility(facility_id="PHC001", facility_type="PHC", district="Solapur", subdistrict="South", ward="Ward-05")
        ]
        
        for f in facilities:
            existing = db.query(Facility).filter_by(facility_id=f.facility_id).first()
            if not existing:
                db.add(f)
                print(f"✓ Created Facility: {f.facility_id}")
        db.commit()

        # Optional: Clear old transactions to prevent "Infinite Load" creep
        db.query(PatientTransaction).delete()

        # 2. Seed 'Live' Load for HSP123 Orthopedics (CRISIS: 12/10 Load)
        print("\n[2/3] Seeding high load (12 patients) for HSP123 Orthopedics...")
        for _ in range(12):
            tx = PatientTransaction(
                facility_id="HSP123",
                transaction_type="CASE",
                department="Orthopedics",
                indicator_name="Bone Fracture",
                month="Feb",
                timestamp=datetime.utcnow() - timedelta(minutes=15)
            )
            db.add(tx)

        # 3. Seed 'Normal' Load for HSP123 Neurology (NORMAL: 2/5 Load)
        print("[3/3] Seeding normal load (2 patients) for HSP123 Neurology...")
        for _ in range(2):
            tx = PatientTransaction(
                facility_id="HSP123",
                transaction_type="CASE",
                department="Neurology",
                indicator_name="Consultation",
                month="Feb",
                timestamp=datetime.utcnow() - timedelta(hours=1)
            )
            db.add(tx)

        db.commit()
        print("\n" + "=" * 60)
        print("✓ Database seeded successfully with Specialty-Aware load!")

    except Exception as e:
        print(f"✗ Seeding failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_appointment_test_data()