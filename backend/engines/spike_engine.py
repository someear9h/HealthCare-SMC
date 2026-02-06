import pandas as pd
from engines.monthly_loader import load_monthly_health_data

# ⭐ Strong thresholds for high-confidence outbreaks
MIN_CASE_THRESHOLD = 75
SPIKE_MULTIPLIER = 1.75
ROLLING_WINDOW = 3

# Strictly clinical disease and mortality keywords
DISEASE_KEYWORDS = [
    "malaria", "dengue", "tuberculosis", "tb ", "hiv", 
    "sti", "rti", "hepatitis", "encephalitis", 
    "diarrhea", "cholera", "influenza", "pneumonia", 
    "measles", "maternal death", "neonatal death", 
    "death", "low birth weight", "hb level<7", 
    "hypertension", "syphilis"
]

# Keywords that indicate "Activity" rather than "Disease" to be excluded
EXCLUSION_KEYWORDS = [
    "immunisation", "vaccination", "sterilization", 
    "camp", "iucd", "condom", "pill", "distributed",
    "sessions", "training", "vhnd", "admitted", "counselling"
]

def detect_outbreaks():
    df = load_monthly_health_data()

    # 1. Filter ONLY disease indicators
    pattern = "|".join(DISEASE_KEYWORDS)
    df = df[
        df["indicatorname"]
        .str.lower()
        .str.contains(pattern, na=False, regex=True)
    ]

    # 2. Hard Exclusion: Remove any operational or family planning activity
    exclude_pattern = "|".join(EXCLUSION_KEYWORDS)
    df = df[
        ~df["indicatorname"]
        .str.lower()
        .str.contains(exclude_pattern, na=False, regex=True)
    ]

    # aggregate
    grouped = (
        df.groupby(
            ["district", "indicatorname", "month_num"],
            as_index=False
        )["total_cases"]
        .sum()
    )

    grouped = grouped.sort_values(by=["district", "indicatorname", "month_num"])

    # remove noise
    grouped = grouped[grouped["total_cases"] >= MIN_CASE_THRESHOLD]

    # rolling baseline
    grouped["baseline"] = (
        grouped
        .groupby(["district", "indicatorname"])["total_cases"]
        .transform(lambda x: x.rolling(ROLLING_WINDOW, min_periods=2).mean())
    )

    grouped = grouped[grouped["baseline"] > 0]

    # spike logic
    grouped["spike"] = (
        grouped["total_cases"] > grouped["baseline"] * SPIKE_MULTIPLIER
    )

    outbreaks = grouped[grouped["spike"]].copy()

    outbreaks["surge_percent"] = (
        (outbreaks["total_cases"] - outbreaks["baseline"]) / outbreaks["baseline"]
    ) * 100

    MONTH_REVERSE = {
        1:"Jan",2:"Feb",3:"Mar",4:"Apr", 5:"May",6:"Jun",
        7:"Jul",8:"Aug", 9:"Sep",10:"Oct",11:"Nov",12:"Dec"
    }

    outbreaks["month"] = outbreaks["month_num"].map(MONTH_REVERSE)
    return outbreaks.sort_values("surge_percent", ascending=False)

def explain_outbreak(row):
    # Since we filtered everything else out, everything here is a Disease Signal
    return (
        f"🚨 🔴 DISEASE OUTBREAK SIGNAL\n"
        f"In {row['month']}, {row['district']} reported "
        f"{int(row['total_cases'])} cases of "
        f"'{row['indicatorname']}'.\n"
        f"Baseline: {int(row['baseline'])} | "
        f"Surge: {row['surge_percent']:.1f}%.\n"
        f"---"
    )