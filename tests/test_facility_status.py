import os
from pathlib import Path
import time

import pytest
from fastapi.testclient import TestClient

from backend.main import app


CLIENT = TestClient(app)
CSV_PATH = Path(__file__).resolve().parent.parent / "backend" / "data" / "facility_status.csv"


VALID_PAYLOAD = {
    "facility_id": "HSP123",
    "facility_type": "Hospital",
    "district": "Solapur",
    "subdistrict": "Mohol",
    "ward": "Ward-12",
    "beds_available": 12,
    "icu_available": 3,
    "ventilators_available": 4,
    "oxygen_units_available": 20,
    "medicine_stock_status": "Adequate",
    "timestamp": "2026-02-08T10:30:00",
}


def setup_function():
    # remove CSV if present to ensure fresh state
    try:
        if CSV_PATH.exists():
            CSV_PATH.unlink()
    except Exception:
        pass


def test_valid_payload_creates_csv_and_returns_200():
    resp = CLIENT.post("/facility-status/", json=VALID_PAYLOAD)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["status"] == "ingested"
    assert data["facility_id"] == "HSP123"
    assert "city_totals" in data
    # CSV created
    assert CSV_PATH.exists()


def test_negative_values_rejected():
    bad = VALID_PAYLOAD.copy()
    bad["beds_available"] = -1
    resp = CLIENT.post("/facility-status/", json=bad)
    assert resp.status_code == 422


def test_missing_facility_id_rejected():
    bad = VALID_PAYLOAD.copy()
    bad.pop("facility_id")
    resp = CLIENT.post("/facility-status/", json=bad)
    assert resp.status_code == 422


def test_crisis_detection_triggers_flag():
    bad = VALID_PAYLOAD.copy()
    bad["beds_available"] = 3
    resp = CLIENT.post("/facility-status/", json=bad)
    assert resp.status_code == 200
    data = resp.json()
    assert data["resource_crisis"] is True
