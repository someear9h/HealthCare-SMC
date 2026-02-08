"""Indicator name normalization utility for data consistency.

Standardizes disease and health indicator names to prevent
data fragmentation when aggregating similar indicators
with different capitalization, spacing, or punctuation.
"""

import re
from typing import Dict


# Standard mapping dictionary for similar indicator names
# Maps various input strings to a canonical standard form
INDICATOR_MAPPING = {
    # Malaria variants
    'malaria': 'New Malaria Cases',
    'new malaria': 'New Malaria Cases',
    'malaria cases': 'New Malaria Cases',
    'new malaria cases': 'New Malaria Cases',
    'malaria identified': 'New Malaria Cases',
    'new malaria cases identified': 'New Malaria Cases',
    
    # Dengue variants
    'dengue': 'Dengue Cases',
    'dengue cases': 'Dengue Cases',
    'dengue fever': 'Dengue Cases',
    'new dengue': 'Dengue Cases',
    
    # Tuberculosis variants
    'tb': 'Tuberculosis Cases',
    'tuberculosis': 'Tuberculosis Cases',
    'new tb': 'Tuberculosis Cases',
    'tb cases': 'Tuberculosis Cases',
    'tuberculosis cases': 'Tuberculosis Cases',
    
    # Diarrhea variants
    'diarrhea': 'Diarrhea Cases',
    'diarrhoea': 'Diarrhea Cases',
    'diarrheal': 'Diarrhea Cases',
    'acute diarrhea': 'Diarrhea Cases',
    
    # HIV variants
    'hiv': 'HIV Cases',
    'hiv positive': 'HIV Cases',
    'new hiv': 'HIV Cases',
    
    # Hepatitis variants
    'hepatitis': 'Hepatitis Cases',
    'hepatitis a': 'Hepatitis Cases',
    'hepatitis b': 'Hepatitis Cases',
    'hepatitis c': 'Hepatitis Cases',
    
    # Measles variants
    'measles': 'Measles Cases',
    'measles cases': 'Measles Cases',
    'new measles': 'Measles Cases',
    
    # Pneumonia variants
    'pneumonia': 'Pneumonia Cases',
    'pneumonia cases': 'Pneumonia Cases',
    'acute pneumonia': 'Pneumonia Cases',
    
    # Encephalitis variants
    'encephalitis': 'Encephalitis Cases',
    'viral encephalitis': 'Encephalitis Cases',
    
    # Cholera variants
    'cholera': 'Cholera Cases',
    'acute cholera': 'Cholera Cases',
    'cholera cases': 'Cholera Cases',
    
    # Influenza variants
    'influenza': 'Influenza Cases',
    'flu': 'Influenza Cases',
    'seasonal flu': 'Influenza Cases',
    'influenza like illness': 'Influenza Cases',
    
    # Mortality variants
    'maternal death': 'Maternal Mortality',
    'maternal deaths': 'Maternal Mortality',
    'neonatal death': 'Neonatal Mortality',
    'neonatal deaths': 'Neonatal Mortality',
    'death': 'Deaths',
    'deaths': 'Deaths',
    
    # Low birth weight variants
    'low birth weight': 'Low Birth Weight',
    'lbw': 'Low Birth Weight',
    
    # Hypertension variants
    'hypertension': 'Hypertension Cases',
    'high blood pressure': 'Hypertension Cases',
}


def normalize_indicator_name(indicator_name: str) -> str:
    """Normalize indicator name for consistent aggregation.
    
    Steps:
    1. Convert to lowercase
    2. Replace hyphens and underscores with spaces
    3. Strip extra whitespace
    4. Lookup in mapping dictionary for standard name
    5. Return canonical form or original if no match
    
    Args:
        indicator_name: Raw indicator name from data
        
    Returns:
        Normalized indicator name (standardized form)
        
    Examples:
        'New malaria-cases identified' -> 'New Malaria Cases'
        'Malaria cases' -> 'New Malaria Cases'
        'new Malaria CASES' -> 'New Malaria Cases'
        'TB-Cases' -> 'Tuberculosis Cases'
    """
    if not indicator_name or not isinstance(indicator_name, str):
        return indicator_name or "Unknown"
    
    # Step 1: Convert to lowercase for comparison
    normalized = indicator_name.lower().strip()
    
    # Step 2: Replace hyphens, underscores, and extra spaces with single space
    normalized = re.sub(r'[-_]+', ' ', normalized)
    normalized = re.sub(r'\s+', ' ', normalized)
    
    # Step 3: Look up in mapping dictionary
    # Check for exact match or partial match for disease keywords
    for key, canonical_form in INDICATOR_MAPPING.items():
        if normalized == key or key in normalized:
            return canonical_form
    
    # Step 4: If no exact match, try to identify disease keywords and standardize
    # Extract disease keywords and capitalize properly
    diseases = ['malaria', 'dengue', 'tuberculosis', 'tb', 'diarrhea', 'hiv', 
                'hepatitis', 'measles', 'pneumonia', 'encephalitis', 'cholera', 
                'influenza', 'flu', 'death', 'mortality']
    
    for disease in diseases:
        if disease in normalized:
            # Convert first letter of disease to uppercase + "Cases" suffix
            disease_title = disease.replace('tb', 'TB').title().replace('hiv', 'HIV')
            if 'death' in normalized or 'mortality' in normalized:
                return 'Deaths'
            return f'{disease_title} Cases'
    
    # Step 5: If still no match, return original indicator name
    # (but with consistent capitalization and spacing)
    return indicator_name.strip()


def normalize_disease_names(df, column_name: str = 'indicatorname') -> None:
    """Normalize disease names in a pandas DataFrame in-place.
    
    Args:
        df: Pandas DataFrame containing health indicator data
        column_name: Name of the column to normalize (default: 'indicatorname')
        
    Returns:
        None (modifies DataFrame in-place)
        
    Example:
        >>> health_df['indicatorname'] = health_df['indicatorname'].apply(normalize_indicator_name)
    """
    if column_name in df.columns:
        df[column_name] = df[column_name].apply(normalize_indicator_name)


def get_indicator_mapping_reference() -> Dict[str, str]:
    """Return the mapping dictionary for reference.
    
    Returns:
        Dict mapping non-standard names to canonical forms
    """
    return INDICATOR_MAPPING.copy()
