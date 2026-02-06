import pandas as pd
from engines.monthly_loader import load_monthly_health_data


# ⭐ MUCH stronger thresholds (realistic)
MIN_CASE_THRESHOLD = 75
SPIKE_MULTIPLIER = 1.75
ROLLING_WINDOW = 3


# Only REAL health conditions
DISEASE_KEYWORDS = [
    "malaria",
    "dengue",
    "tuberculosis",
    "tb ",
    "hiv",
    "sti",
    "rti",
    "hepatitis",
    "encephalitis",
    "diarrhea",
    "cholera",
    "influenza",
    "pneumonia",
    "measles",
    "maternal death",
    "neonatal death",
    "death",
    "low birth weight",
    "hb level<7",
    "hypertension"
]


def detect_outbreaks():

    df = load_monthly_health_data()

    # ⭐ Filter ONLY disease indicators
    pattern = "|".join(DISEASE_KEYWORDS)

    df = df[
        df["indicatorname"]
        .str.lower()
        .str.contains(pattern, na=False, regex=True)
    ]

    # aggregate
    grouped = (
        df.groupby(
            ["district", "indicatorname", "month_num"],
            as_index=False
        )["total_cases"]
        .sum()
    )

    # sort BEFORE rolling
    grouped = grouped.sort_values(
        by=["district", "indicatorname", "month_num"]
    )

    # remove tiny noise
    grouped = grouped[grouped["total_cases"] >= MIN_CASE_THRESHOLD]

    # rolling baseline
    grouped["baseline"] = (
        grouped
        .groupby(["district", "indicatorname"])["total_cases"]
        .transform(
            lambda x: x.rolling(
                ROLLING_WINDOW,
                min_periods=2
            ).mean()
        )
    )

    # avoid divide-by-zero
    grouped = grouped[grouped["baseline"] > 0]

    # spike logic
    grouped["spike"] = (
        grouped["total_cases"] >
        grouped["baseline"] * SPIKE_MULTIPLIER
    )

    outbreaks = grouped[grouped["spike"]].copy()

    outbreaks["surge_percent"] = (
        (outbreaks["total_cases"] - outbreaks["baseline"])
        / outbreaks["baseline"]
    ) * 100

    # prettier month
    MONTH_REVERSE = {
        1:"Jan",2:"Feb",3:"Mar",4:"Apr",
        5:"May",6:"Jun",7:"Jul",8:"Aug",
        9:"Sep",10:"Oct",11:"Nov",12:"Dec"
    }

    outbreaks["month"] = outbreaks["month_num"].map(MONTH_REVERSE)

    outbreaks = outbreaks.sort_values(
        "surge_percent",
        ascending=False
    )

    return outbreaks[[
        "district",
        "indicatorname",
        "month",
        "total_cases",
        "baseline",
        "surge_percent"
    ]]


def explain_outbreak(row):

    signal_type = classify_signal(row["indicatorname"])

    return (
        f"{signal_type}\n"
        f"In {row['month']}, {row['district']} reported "
        f"{int(row['total_cases'])} cases of "
        f"'{row['indicatorname']}'.\n"
        f"Baseline: {int(row['baseline'])} | "
        f"Surge: {row['surge_percent']:.1f}%.\n"
    )



def classify_signal(indicator):

    indicator = indicator.lower()

    disease_words = [
        "malaria","dengue","sti","rti",
        "tuberculosis","death","pneumonia",
        "syphilis","diarrhea"
    ]

    activity_words = [
        "immunisation","vaccination",
        "sterilization","tested",
        "screened"
    ]

    if any(word in indicator for word in disease_words):
        return "🔴 Disease Signal"

    if any(word in indicator for word in activity_words):
        return "🟢 Healthcare Activity"

    return "🟠 Operational / Other"
