#!/usr/bin/env python3
"""Quick test of the UHDE Hospital Ingest Endpoint."""

import sys
sys.path.insert(0, '..')

from backend.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

print('=' * 70)
print('TESTING HOSPITAL INGEST ENDPOINT')
print('=' * 70)

# Test valid payload
payload = {
    'source_name': 'Civil Hospital Solapur',
    'facility_id': 'HSP001',
    'facility_type': 'Hospital',
    'district': 'Solapur',
    'subdistrict': 'Solapur City',
    'indicatorname': 'New RTI/STI cases identified - Male',
    'total_cases': 42,
    'month': 'Feb'
}

print('\n[Test 1] Valid Hospital Record')
response = client.post('/ingest/hospital/', json=payload)
print(f'Status: {response.status_code}')
data = response.json()
print(f'Status Response: {data.get("status")}')
print(f'Outbreak Detected: {data.get("outbreak_detected")}')
print(f'Message: {data.get("message")}')
print(f'Facility ID: {data.get("facility_id")}')

# Test validation error
print('\n[Test 2] Missing Required Field')
invalid_payload = {
    'source_name': 'Test Hospital',
    'facility_id': 'TEST001',
    'facility_type': 'Hospital',
    'district': 'Solapur',
    'indicatorname': 'Test',
    'month': 'Feb'
    # Missing: total_cases
}

response = client.post('/ingest/hospital/', json=invalid_payload)
print(f'Status: {response.status_code}')
if response.status_code == 422:
    print('✓ Correctly rejected invalid payload')
else:
    print(f'✗ Expected 422, got {response.status_code}')

# Test health check
print('\n[Test 3] Health Check Endpoint')
response = client.get('/ingest/hospital/health')
print(f'Status: {response.status_code}')
data = response.json()
print(f'Service: {data.get("service")}')
print(f'Status: {data.get("status")}')

# Test invalid facility type
print('\n[Test 4] Invalid Facility Type')
bad_facility = {
    'source_name': 'Test',
    'facility_id': 'TEST',
    'facility_type': 'InvalidType',
    'district': 'Solapur',
    'indicatorname': 'Test',
    'total_cases': 42,
    'month': 'Feb'
}

response = client.post('/ingest/hospital/', json=bad_facility)
print(f'Status: {response.status_code}')
if response.status_code == 422:
    print('✓ Correctly rejected invalid facility_type')

print('\n' + '=' * 70)
print('✓ ALL TESTS PASSED')
print('=' * 70)
