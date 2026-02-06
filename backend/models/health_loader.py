import pandas as pd

HEALTH_PATH = "../datasets/health.csv"

def load_health_data():

    df = pd.read_csv(HEALTH_PATH)

    # normalize column names
    df.columns = df.columns.str.strip().str.lower()

    # Create ONE unified numeric column
    numeric_cols = [
        "reportedvalueforpublicfacility",
        "reportedvalueforprivatefacility",
        "reportedvalueforrural",
        "reportedvalueforurban"
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["total_cases"] = df[numeric_cols].sum(axis=1)

    # drop rows where total is missing
    df.dropna(subset=["total_cases"], inplace=True)

    return df
