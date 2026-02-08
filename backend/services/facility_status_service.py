from __future__ import annotations

from typing import Any, Dict
from pathlib import Path
import csv
import fcntl

from schemas.facility_status_schema import FacilityStatusPayload
from core.ws_manager import manager


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
CSV_PATH = DATA_DIR / "facility_status.csv"


def _ensure_csv_headers(path: Path) -> None:
    """Create CSV with headers if missing."""
    if not path.exists():
        headers = [
            "facility_id",
            "facility_type",
            "district",
            "subdistrict",
            "ward",
            "beds_available",
            "icu_available",
            "ventilators_available",
            "oxygen_units_available",
            "medicine_stock_status",
            "timestamp",
        ]
        with path.open("w", newline="", encoding="utf-8") as fh:
            # exclusive lock while creating
            fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
            writer = csv.writer(fh)
            writer.writerow(headers)
            fcntl.flock(fh.fileno(), fcntl.LOCK_UN)


def _append_record(path: Path, record: Dict[str, Any]) -> None:
    """Append a single record to CSV with file locking."""
    with path.open("a", newline="", encoding="utf-8") as fh:
        fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
        writer = csv.writer(fh)
        writer.writerow([
            record.get("facility_id"),
            record.get("facility_type"),
            record.get("district"),
            record.get("subdistrict"),
            record.get("ward"),
            record.get("beds_available"),
            record.get("icu_available"),
            record.get("ventilators_available"),
            record.get("oxygen_units_available"),
            record.get("medicine_stock_status"),
            record.get("timestamp"),
        ])
        fh.flush()
        fcntl.flock(fh.fileno(), fcntl.LOCK_UN)


def _compute_totals(path: Path) -> Dict[str, int]:
    """Read CSV and compute totals for numeric resources."""
    totals = {
        "total_beds": 0,
        "total_icu": 0,
        "total_ventilators": 0,
        "total_oxygen": 0,
    }
    if not path.exists():
        return totals

    with path.open("r", newline="", encoding="utf-8") as fh:
        fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
        reader = csv.DictReader(fh)
        for row in reader:
            try:
                totals["total_beds"] += int(row.get("beds_available") or 0)
                totals["total_icu"] += int(row.get("icu_available") or 0)
                totals["total_ventilators"] += int(row.get("ventilators_available") or 0)
                totals["total_oxygen"] += int(row.get("oxygen_units_available") or 0)
            except Exception:
                # skip malformed rows
                continue
        fcntl.flock(fh.fileno(), fcntl.LOCK_UN)

    return totals


def process_facility_status(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Validate payload, persist to CSV, compute city totals and detect crisis.

    Args:
        payload: Raw JSON-like dict from the ingestion endpoint.

    Returns:
        Dict containing facility_id, resource_crisis flag, and city totals.
    """
    # Validate using schema
    validated = FacilityStatusPayload(**payload)

    # Ensure CSV exists with headers
    _ensure_csv_headers(CSV_PATH)

    # Append record
    record = validated.dict()
    # Convert timestamp to ISO string for CSV
    record["timestamp"] = record["timestamp"].isoformat()
    _append_record(CSV_PATH, record)

    # Compute totals across all facilities
    totals = _compute_totals(CSV_PATH)

    # Detect resource crisis
    crisis = False
    if (
        validated.beds_available < 5
        or validated.icu_available < 2
        or validated.oxygen_units_available < 5
        or validated.medicine_stock_status == "Critical"
    ):
        crisis = True

    # Broadcast event to websocket manager
    event = {
        "type": "facility_status",
        "facility_id": validated.facility_id,
        "resource_crisis": crisis,
        "totals": totals,
    }
    # manager.broadcast will be called by router via BackgroundTasks to avoid awaiting here

    return {
        "facility_id": validated.facility_id,
        "resource_crisis": crisis,
        "city_totals": totals,
        "event": event,
    }
