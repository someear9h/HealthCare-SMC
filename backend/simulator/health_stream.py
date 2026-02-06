import requests
import time
import pandas as pd

API_URL = "http://localhost:8000/ingestion/ingest"

# Sample data rows you provided
data = [
    ["Maharashtra",27,"Solapur",496,"Malshiras",4250,"2021-2022","May","1.3.1","New cases of PW with hypertension detected","M1 [Ante Natal Care (ANC)]",5,0,5,0,"22-04-2025"],
    ["Maharashtra",27,"Solapur",496,"Malshiras",4250,"2021-2022","May","1.6.1.a","Number of PW tested using POC test for Syphilis","M1 [Ante Natal Care (ANC)]",204,0,204,0,"22-04-2025"],
    ["Maharashtra",27,"Solapur",496,"Mohol",4248,"2021-2022","May","4.4.2","Number of newborns having weight less than 2.5 kg","M4",12,0,12,0,"22-04-2025"],
    ["Maharashtra",27,"Solapur",496,"Pandharpur",4249,"2021-2022","May","1.1","Total number of pregnant women registered for ANC","M1",85,0,70,15,"22-04-2025"],
    ["Maharashtra",27,"Solapur",496,"Malshiras",4250,"2021-2022","May","7.1.1","New RTI/STI cases identified - Male","M7",45,0,45,0,"22-04-2025"],
    ["Maharashtra",27,"Solapur",496,"Mohol",4248,"2021-2022","May","9.1.12","Child immunisation - OPV3","M9",150,0,140,10,"22-04-2025"],
    ["Maharashtra",27,"Solapur",496,"Pandharpur",4249,"2021-2022","May","14.9.1","Inpatient Deaths - Male","M14",8,0,8,0,"22-04-2025"],
    ["Maharashtra",27,"Solapur",496,"Malshiras",4250,"2021-2022","May","1.4.3","Number of PW having Hb level<7","M1",22,0,22,0,"22-04-2025"],
    ["Maharashtra",27,"Solapur",496,"Mohol",4248,"2021-2022","May","11.3.1","Dengue - RDT Test Positive","M11",14,0,10,4,"22-04-2025"],
    ["Maharashtra",27,"Solapur",496,"Pandharpur",4249,"2021-2022","May","8.2.2","Interval Mini-lap sterilizations conducted","M8",55,0,50,5,"22-04-2025"]
]

columns = [
    "stateut", "state_code", "district", "district_code", "subdistrict", 
    "subdistrict_code", "financialyear", "month", "indicatorcode", 
    "indicatorname", "codesection", "reportedvalueforpublicfacility", 
    "reportedvalueforprivatefacility", "reportedvalueforrural", 
    "reportedvalueforurban", "datagovupdatedate"
]

def run_simulation():
    df = pd.DataFrame(data, columns=columns)
    print("🚀 Starting Data Stream Simulation...")
    
    for _, row in df.iterrows():
        payload = row.to_dict()
        response = requests.post(API_URL, json=payload)
        if response.status_code == 200:
            print(f"✅ Ingested: {payload['indicatorname']} for {payload['subdistrict']}")
        else:
            print(f"❌ Failed: {response.text}")
        time.sleep(2) # 2-second delay between entries

if __name__ == "__main__":
    run_simulation()