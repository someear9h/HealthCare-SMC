#!/usr/bin/env python3
"""
Test script for UHDE Health Ingest Endpoints
Demonstrates how to use the API and validates functionality.
"""

import requests
import json
from datetime import datetime
import time

BASE_URL = "http://localhost:8000"

# Sample health data records
HOSPITAL_RECORDS = [
    {
        "source_name": "Civil Hospital Solapur",
        "facility_id": "HSP001",
        "facility_type": "Hospital",
        "district": "Solapur",
        "subdistrict": "Solapur City",
        "ward": "Ward-10",
        "indicatorname": "New RTI/STI cases identified - Male",
        "total_cases": 42,
        "month": "Feb"
    },
    {
        "source_name": "Civil Hospital Solapur",
        "facility_id": "HSP001",
        "facility_type": "Hospital",
        "district": "Solapur",
        "subdistrict": "Solapur City",
        "ward": "Ward-10",
        "indicatorname": "Maternal deaths",
        "total_cases": 3,
        "month": "Feb"
    },
]

LAB_RECORDS = [
    {
        "source_name": "SMC Central Diagnostic Lab",
        "facility_id": "LAB001",
        "facility_type": "Lab",
        "district": "Solapur",
        "subdistrict": "Solapur City",
        "indicatorname": "TB tests conducted - Positive",
        "total_cases": 18,
        "month": "Feb"
    },
]

PHC_RECORDS = [
    {
        "source_name": "Mohol Primary Health Center",
        "facility_id": "PHC001",
        "facility_type": "PHC",
        "district": "Solapur",
        "subdistrict": "Mohol",
        "ward": "Ward-A",
        "indicatorname": "Immunization - Children vaccinated",
        "total_cases": 150,
        "month": "Feb"
    },
]

AMBULANCE_RECORDS = [
    {
        "source_name": "Emergency Ambulance Service",
        "facility_id": "AMB001",
        "facility_type": "Ambulance",
        "district": "Solapur",
        "subdistrict": "Solapur City",
        "indicatorname": "Emergency calls responded",
        "total_cases": 87,
        "month": "Feb"
    },
]


def test_endpoint(endpoint: str, records: list, name: str):
    """Test an ingest endpoint with sample records."""
    print(f"\n{'='*70}")
    print(f"Testing: {name}")
    print(f"{'='*70}")
    
    success_count = 0
    error_count = 0
    
    for i, record in enumerate(records, 1):
        try:
            print(f"\n[{i}/{len(records)}] Sending record...")
            print(f"  Source: {record['source_name']}")
            print(f"  Indicator: {record['indicatorname']}")
            print(f"  Cases: {record['total_cases']}")
            
            # Make POST request
            response = requests.post(
                f"{BASE_URL}{endpoint}/",
                json=record,
                timeout=10
            )
            
            # Check response status
            if response.status_code == 200:
                data = response.json()
                print(f"  ✓ Status: {response.status_code}")
                print(f"  ✓ Response: {data['status']}")
                print(f"  ✓ Outbreak Detected: {data['outbreak_detected']}")
                print(f"  ✓ Message: {data['message']}")
                success_count += 1
            elif response.status_code == 422:
                print(f"  ✗ Validation Error (422)")
                print(f"  Details: {response.json()}")
                error_count += 1
            else:
                print(f"  ✗ Error {response.status_code}")
                print(f"  Response: {response.text}")
                error_count += 1
                
        except Exception as e:
            print(f"  ✗ Exception: {str(e)}")
            error_count += 1
    
    print(f"\nResults for {name}:")
    print(f"  ✓ Successful: {success_count}")
    print(f"  ✗ Failed: {error_count}")
    
    return success_count, error_count


def test_validation_errors():
    """Test invalid payloads to verify validation."""
    print(f"\n{'='*70}")
    print("Testing: Validation Error Handling")
    print(f"{'='*70}")
    
    invalid_records = [
        (
            "Missing required field (total_cases)",
            {
                "source_name": "Test Hospital",
                "facility_id": "TEST001",
                "facility_type": "Hospital",
                "district": "Solapur",
                "indicatorname": "Test Indicator",
                "month": "Feb"
                # total_cases missing
            }
        ),
        (
            "Invalid facility_type",
            {
                "source_name": "Test Hospital",
                "facility_id": "TEST001",
                "facility_type": "InvalidType",  # Invalid
                "district": "Solapur",
                "indicatorname": "Test Indicator",
                "total_cases": 42,
                "month": "Feb"
            }
        ),
        (
            "Negative total_cases",
            {
                "source_name": "Test Hospital",
                "facility_id": "TEST001",
                "facility_type": "Hospital",
                "district": "Solapur",
                "indicatorname": "Test Indicator",
                "total_cases": -5,  # Invalid: must be >= 0
                "month": "Feb"
            }
        ),
    ]
    
    validation_passed = 0
    
    for desc, payload in invalid_records:
        print(f"\n[{desc}]")
        try:
            response = requests.post(
                f"{BASE_URL}/ingest/hospital/",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 422:
                print(f"  ✓ Correctly rejected with 422")
                print(f"  Details: {response.json()['detail']}")
                validation_passed += 1
            else:
                print(f"  ✗ Expected 422, got {response.status_code}")
                
        except Exception as e:
            print(f"  ✗ Exception: {str(e)}")
    
    print(f"\nValidation Tests Passed: {validation_passed}/{len(invalid_records)}")
    return validation_passed


def test_health_checks():
    """Test health check endpoints."""
    print(f"\n{'='*70}")
    print("Testing: Health Check Endpoints")
    print(f"{'='*70}")
    
    endpoints = [
        "/ingest/hospital/health",
        "/ingest/lab/health",
        "/ingest/phc/health",
        "/ingest/ambulance/health"
    ]
    
    health_ok = 0
    
    for endpoint in endpoints:
        try:
            print(f"\nChecking {endpoint}...")
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"  ✓ Status: {data.get('status')}")
                print(f"  ✓ Service: {data.get('service')}")
                print(f"  ✓ Timestamp: {data.get('timestamp')}")
                health_ok += 1
            else:
                print(f"  ✗ Unexpected status: {response.status_code}")
                
        except Exception as e:
            print(f"  ✗ Exception: {str(e)}")
    
    print(f"\nHealth Checks Passed: {health_ok}/{len(endpoints)}")
    return health_ok


def test_logs_endpoints():
    """Test logs endpoints."""
    print(f"\n{'='*70}")
    print("Testing: Logs Endpoints")
    print(f"{'='*70}")
    
    try:
        print("\n[GET /logs/recent]")
        response = requests.get(f"{BASE_URL}/logs/recent", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✓ Status: {response.status_code}")
            print(f"  ✓ Records retrieved: {len(data)}")
            if data:
                print(f"  Latest record (first): {data[0].get('indicatorname', 'N/A')}")
        else:
            print(f"  ✗ Unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"  ✗ Exception: {str(e)}")


def print_summary(total_success, total_error):
    """Print final test summary."""
    print(f"\n{'='*70}")
    print("TEST SUMMARY")
    print(f"{'='*70}")
    print(f"✓ Total Successful: {total_success}")
    print(f"✗ Total Failed: {total_error}")
    
    if total_error == 0 and total_success > 0:
        print(f"\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  Some tests failed. Review the output above.")


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("UHDE HEALTH INGEST API - TEST SUITE")
    print("="*70)
    print(f"Base URL: {BASE_URL}")
    print(f"Timestamp: {datetime.utcnow().isoformat()}")
    
    # Wait for server to be ready
    max_retries = 5
    for attempt in range(max_retries):
        try:
            requests.get(f"{BASE_URL}/", timeout=2)
            break
        except requests.exceptions.ConnectionError:
            if attempt < max_retries - 1:
                print(f"\nWaiting for server... (attempt {attempt+1}/{max_retries})")
                time.sleep(1)
            else:
                print("\n✗ Cannot connect to server. Is it running on localhost:8000?")
                print("  Start with: python3 main.py")
                return
    
    total_success = 0
    total_error = 0
    
    # Test each endpoint
    s, e = test_endpoint("/ingest/hospital", HOSPITAL_RECORDS, "Hospital Ingest")
    total_success += s
    total_error += e
    
    s, e = test_endpoint("/ingest/lab", LAB_RECORDS, "Lab Ingest")
    total_success += s
    total_error += e
    
    s, e = test_endpoint("/ingest/phc", PHC_RECORDS, "PHC Ingest")
    total_success += s
    total_error += e
    
    s, e = test_endpoint("/ingest/ambulance", AMBULANCE_RECORDS, "Ambulance Ingest")
    total_success += s
    total_error += e
    
    # Test validation
    test_validation_errors()
    
    # Test health checks
    test_health_checks()
    
    # Test logs
    test_logs_endpoints()
    
    # Summary
    print_summary(total_success, total_error)


if __name__ == "__main__":
    main()
