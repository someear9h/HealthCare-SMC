from typing import Dict, Any
from datetime import datetime
from models.schemas import PatientTransactionSchema
from models.orm import PatientTransaction
from core.data_access import make_csv_accessor, CSVDataAccess
from engines.outbreak_engine import detect_outbreaks

# Canonical fieldnames for the CSV Audit Trail
FIELDNAMES = [
    "facility_id",
    "transaction_type",
    "department",
    "indicator_name",
    "count",
    "month",
    "timestamp",
    "ingestion_timestamp",
]

ingested_store: CSVDataAccess = make_csv_accessor("patient_events", FIELDNAMES)
failed_store: CSVDataAccess = make_csv_accessor("failed_patient_events", FIELDNAMES)

def process_ingest(db, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Processes individual clinical events for live analytics."""
    try:
        # 1. Validate clinical data via Schema
        # We exclude ingestion_timestamp from the schema validation to avoid crashes
        rec = PatientTransactionSchema(**payload)
        
        # 2. Capture the exact moment of ingestion for the audit log
        ingestion_dt = datetime.utcnow()
        
        # 3. SQL Persistence: Specialty-Aware tracking
        new_event = PatientTransaction(
            facility_id=rec.facility_id,
            transaction_type=rec.transaction_type,
            department=rec.department,
            indicator_name=rec.indicator_name,
            count=rec.count,
            month=rec.month,
            timestamp=rec.timestamp or ingestion_dt
        )
        db.add(new_event)
        db.commit()

        # 4. CSV Persistence: Audit trail for Outbreak Engine
        row = rec.dict()
        row["timestamp"] = row["timestamp"].isoformat() if row["timestamp"] else ""
        row["ingestion_timestamp"] = ingestion_dt.isoformat()
        ingested_store.append(row)

        # 5. Live Outbreak Detection
        outbreak = detect_outbreaks(ingested_store, row)

        return {
            "status": "ingested", 
            "outbreak_detected": bool(outbreak),
            "type": rec.transaction_type,
            "department": rec.department
        }

    except Exception as e:
        db.rollback()
        failed_store.append({
            "facility_id": payload.get("facility_id", "UNKNOWN"),
            "ingestion_timestamp": datetime.utcnow().isoformat(),
            "indicator_name": f"Error: {str(e)}"
        })
        return {"status": "failed", "error": str(e)}

def get_recent(n: int = 50):
    return ingested_store.read_last(n)

def get_failed(n: int = 50):
    return failed_store.read_last(n)