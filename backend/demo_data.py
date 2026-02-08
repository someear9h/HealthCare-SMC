#!/usr/bin/env python3
"""Demo data insertion script for testing the platform.

Populates the database with sample facilities, health records, and status updates
to demonstrate the dashboard functionality.

Usage:
    python3 demo_data.py

This script will:
1. Create sample facilities
2. Insert health records (simulated admissions)
3. Insert facility status updates (resource levels)
4. Insert ambulance fleet data
"""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from core.database import SessionLocal, init_db
from models.orm import Facility, HealthRecord, FacilityStatus, Ambulance


def populate_demo_data():
    """Insert demo data into database."""
    db = SessionLocal()
    init_db()

    print("📊 Inserting demo data...")

    # 1. Create facilities
    facilities = [
        {
            "facility_id": "HSP001",
            "facility_type": "Hospital",
            "district": "Solapur",
            "subdistrict": "Solapur City",
            "ward": "Ward-10",
        },
        {
            "facility_id": "HSP002",
            "facility_type": "Hospital",
            "district": "Solapur",
            "subdistrict": "Solapur City",
            "ward": "Ward-12",
        },
        {
            "facility_id": "HSP003",
            "facility_type": "Hospital",
            "district": "Solapur",
            "subdistrict": "Mohol",
            "ward": "Ward-A",
        },
        {
            "facility_id": "LAB001",
            "facility_type": "Lab",
            "district": "Solapur",
            "subdistrict": "Solapur City",
            "ward": "Ward-10",
        },
        {
            "facility_id": "PHC001",
            "facility_type": "PHC",
            "district": "Solapur",
            "subdistrict": "Mohol",
            "ward": "Ward-B",
        },
    ]

    for fac in facilities:
        existing = db.query(Facility).filter(Facility.facility_id == fac["facility_id"]).first()
        if not existing:
            facility = Facility(**fac)
            db.add(facility)
    db.commit()
    print(f"✓ Created {len(facilities)} facilities")

    # 2. Insert health records (last 24 hours, simulating admissions)
    now = datetime.utcnow()
    facility_ids = [f["facility_id"] for f in facilities[:3]]  # Only hospitals

    health_records = []
    for fid in facility_ids:
        for hour in range(0, 24, 6):
            timestamp = now - timedelta(hours=hour)
            cases = 5 + (hour % 3) * 2  # Varying cases
            record = HealthRecord(
                facility_id=fid,
                indicator_name="RTI/STI Cases",
                total_cases=cases,
                month="Feb",
                timestamp=timestamp,
            )
            db.add(record)
            health_records.append(record)

    db.commit()
    print(f"✓ Created {len(health_records)} health records")

    # 3. Insert facility status (capacity snapshots)
    facility_status_data = [
        {"facility_id": "HSP001", "beds": 50, "icu": 10, "vent": 5, "oxygen": 100, "medicine": "Adequate"},
        {"facility_id": "HSP002", "beds": 3, "icu": 1, "vent": 2, "oxygen": 15, "medicine": "Critical"},  # Crisis
        {"facility_id": "HSP003", "beds": 30, "icu": 8, "vent": 4, "oxygen": 60, "medicine": "Low"},
        {"facility_id": "LAB001", "beds": 10, "icu": 0, "vent": 0, "oxygen": 5, "medicine": "Adequate"},
        {"facility_id": "PHC001", "beds": 20, "icu": 2, "vent": 1, "oxygen": 30, "medicine": "Adequate"},
    ]

    status_records = []
    for data in facility_status_data:
        status = FacilityStatus(
            facility_id=data["facility_id"],
            beds_available=data["beds"],
            icu_available=data["icu"],
            ventilators_available=data["vent"],
            oxygen_units_available=data["oxygen"],
            medicine_stock_status=data["medicine"],
            timestamp=now,
        )
        db.add(status)
        status_records.append(status)

    db.commit()
    print(f"✓ Created {len(status_records)} facility status records")

    # 4. Insert ambulance fleet
    ambulances = [
        {"vehicle_id": "AMB-001", "ward": "Ward-10", "status": "AVAILABLE", "lat": 19.8601, "lng": 75.3272},
        {"vehicle_id": "AMB-002", "ward": "Ward-12", "status": "BUSY", "lat": 19.8615, "lng": 75.3280},
        {"vehicle_id": "AMB-003", "ward": "Ward-A", "status": "AVAILABLE", "lat": 19.8550, "lng": 75.3100},
        {"vehicle_id": "AMB-004", "ward": "Ward-B", "status": "OFFLINE", "lat": 19.8450, "lng": 75.3000},
        {"vehicle_id": "AMB-005", "ward": "Ward-10", "status": "AVAILABLE", "lat": 19.8620, "lng": 75.3290},
    ]

    amb_records = []
    for amb in ambulances:
        existing = db.query(Ambulance).filter(Ambulance.vehicle_id == amb["vehicle_id"]).first()
        if not existing:
            ambulance = Ambulance(**amb, last_updated=now)
            db.add(ambulance)
            amb_records.append(ambulance)

    db.commit()
    print(f"✓ Created {len(amb_records)} ambulances")

    print("\n✅ Demo data inserted successfully!")
    print(f"\nDatabase file: health_smc.db")
    print(f"Start server: python3 main.py")
    print(f"Visit dashboard: http://localhost:3000")

    db.close()


if __name__ == "__main__":
    populate_demo_data()
