import pandas as pd

HEALTH_PATH = "../datasets/health.csv"


MONTH_MAP = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}


def load_monthly_health_data():

    df = pd.read_csv(HEALTH_PATH)

    # normalize columns
    df.columns = df.columns.str.strip().str.lower()

    numeric_cols = [
        "reportedvalueforpublicfacility",
        "reportedvalueforprivatefacility",
        "reportedvalueforrural",
        "reportedvalueforurban"
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["total_cases"] = df[numeric_cols].sum(axis=1)

    df.dropna(subset=["total_cases"], inplace=True)

    # normalize month
    df["month"] = df["month"].astype(str).str.strip().str.lower()

    df["month_num"] = df["month"].map(MONTH_MAP)

    # remove bad rows
    df = df[df["month_num"].notna()]

    df["month_num"] = df["month_num"].astype(int)

    return df
