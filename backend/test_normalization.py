#!/usr/bin/env python3
"""Test script for indicator name normalization."""

from utils.indicator_normalizer import normalize_indicator_name, INDICATOR_MAPPING

# Test cases to validate normalization
test_cases = [
    ('New malaria-cases identified', 'New Malaria Cases'),
    ('Malaria cases', 'New Malaria Cases'),
    ('new Malaria CASES', 'New Malaria Cases'),
    ('TB-Cases', 'Tuberculosis Cases'),
    ('Tuberculosis', 'Tuberculosis Cases'),
    ('dengue fever', 'Dengue Cases'),
    ('New Dengue', 'Dengue Cases'),
    ('Diarrhea cases', 'Diarrhea Cases'),
    ('diarrhoea', 'Diarrhea Cases'),
    ('measles', 'Measles Cases'),
    ('influenza like illness', 'Influenza Cases'),
    ('maternal death', 'Maternal Mortality'),
]

print('Testing Indicator Name Normalization:')
print('=' * 70)

all_passed = True
for input_name, expected_output in test_cases:
    result = normalize_indicator_name(input_name)
    status = '✓' if result == expected_output else '✗'
    if result != expected_output:
        all_passed = False
    print(f'{status} Input: "{input_name}"')
    print(f'  Expected: "{expected_output}"')
    print(f'  Got:      "{result}"')
    print()

print('=' * 70)
if all_passed:
    print('✓ All normalization tests PASSED!')
else:
    print('✗ Some tests FAILED - check output above')

print(f'\nTotal mappings available: {len(INDICATOR_MAPPING)}')
