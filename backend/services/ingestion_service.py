from typing import Dict, Any
from datetime import datetime
from models.schemas import IngestRecord
from core.data_access import make_csv_accessor, CSVDataAccess
from engines.outbreak_engine import detect_outbreaks


# Define the canonical fieldnames for CSV storage
FIELDNAMES = [
    "source_name",
    "facility_id",
    "facility_type",
    "district",
    "subdistrict",
    "ward",
    "indicatorname",
    "total_cases",
    "month",
    "timestamp",
    "ingestion_timestamp",
]


# Create CSV accessors (could be swapped with DB-backed class)
ingested_store: CSVDataAccess = make_csv_accessor("ingested_events", FIELDNAMES)
failed_store: CSVDataAccess = make_csv_accessor("failed_events", FIELDNAMES)


def normalize_keys(payload: Dict[str, Any]) -> Dict[str, Any]:
    # lower-case keys and strip spaces
    return {k.strip().lower(): v for k, v in payload.items()}


def prepare_record(payload: Dict[str, Any]) -> IngestRecord:
    p = normalize_keys(payload)
    # Ensure timestamp is proper iso string or datetime; pydantic will parse
    # Add ingestion timestamp
    p["ingestion_timestamp"] = datetime.utcnow()
    # Pydantic will validate and coerce
    rec = IngestRecord(**p)
    return rec


def process_ingest(payload: Dict[str, Any]) -> Dict[str, Any]:
    try:
        rec = prepare_record(payload)
    except Exception as e:
        # Log bad record
        failed_store.append({
            **{k: payload.get(k, "") for k in FIELDNAMES},
            "ingestion_timestamp": datetime.utcnow().isoformat(),
        })
        return {"status": "failed", "error": str(e)}

    # Persist
    row = {k: getattr(rec, k) if hasattr(rec, k) else "" for k in FIELDNAMES}
    # ensure timestamp fields are strings
    row["timestamp"] = rec.timestamp.isoformat() if rec.timestamp else ""
    row["ingestion_timestamp"] = rec.ingestion_timestamp.isoformat() if rec.ingestion_timestamp else datetime.utcnow().isoformat()
    ingested_store.append(row)

    # Run detection
    outbreak = detect_outbreaks(ingested_store, row)

    return {"status": "ingested", "outbreak_detected": bool(outbreak)}


def get_recent(n: int = 50):
    return ingested_store.read_last(n)


def get_failed(n: int = 50):
    return failed_store.read_last(n)
