from models.health_loader import load_health_data
import pandas as pd


MATERNAL_SECTIONS = ["M1", "M2", "M3", "M4"]


def compute_risk():

    df = load_health_data()

    # ✅ Restrict ONLY to maternal universe
    maternal_df = df[
        df["codesection"].str.startswith(tuple(MATERNAL_SECTIONS), na=False)
    ].copy()

    # -----------------------------
    # HIGH RISK INDICATORS
    # -----------------------------

    anemia = maternal_df[
        maternal_df["indicatorname"].str.contains(
            r"hb level<7", case=False, na=False, regex=True
        )
    ].groupby("district")["total_cases"].sum()

    hypertension = maternal_df[
        maternal_df["indicatorname"].str.contains(
            r"hypertension", case=False, na=False
        )
    ].groupby("district")["total_cases"].sum()

    low_weight = maternal_df[
        maternal_df["indicatorname"].str.contains(
            r"weight less than|low birth", case=False, na=False, regex=True
        )
    ].groupby("district")["total_cases"].sum()

    # ✅ TRUE denominator
    pregnancies = maternal_df[
        maternal_df["indicatorname"].str.contains(
            r"pregnant women registered", case=False, na=False
        )
    ].groupby("district")["total_cases"].sum()

    # --------------------------------------------------
    # ⭐ CRITICAL FIX — USE MAX INSTEAD OF SUM
    # Prevents double / triple counting
    # --------------------------------------------------

    risk_events = pd.concat(
        [anemia, hypertension, low_weight],
        axis=1
    )

    risk_events.columns = [
        "severe_anemia",
        "hypertension",
        "low_birth_weight"
    ]

    # Replace NaN with 0 BEFORE max
    risk_events = risk_events.fillna(0)

    # ⭐ Take highest indicator as proxy for vulnerable population
    risk_events["risk_events"] = risk_events.max(axis=1)

    risk_df = risk_events[["risk_events"]]

    # Add denominator
    risk_df["pregnancies"] = pregnancies

    # Drop districts with no pregnancies
    risk_df = risk_df.dropna(subset=["pregnancies"])
    risk_df = risk_df[risk_df["pregnancies"] > 0]

    # --------------------------------------------------
    # FINAL METRIC
    # --------------------------------------------------

    risk_df["risk_score"] = (
        risk_df["risk_events"] / risk_df["pregnancies"]
    ) * 100

    # ⭐ OPTIONAL BUT VERY PROFESSIONAL
    # per 1000 pregnancies metric
    risk_df["risk_per_1000"] = (
        risk_df["risk_events"] / risk_df["pregnancies"]
    ) * 1000

    risk_df.reset_index(inplace=True)

    return risk_df.sort_values(by="risk_score", ascending=False)
