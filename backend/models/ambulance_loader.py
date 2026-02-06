import pandas as pd

AMBULANCE_PATH = "../datasets/ambulance.csv"

def load_ambulance_data():
    df = pd.read_csv(AMBULANCE_PATH)

    df.columns = df.columns.str.strip().str.lower()

    return df
