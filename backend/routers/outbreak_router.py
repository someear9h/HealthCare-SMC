from fastapi import APIRouter, HTTPException
from typing import List
from engines.spike_engine import detect_outbreaks, explain_outbreak
from schemas.outbreak_schema import OutbreakResponse

router = APIRouter()

@router.get("/", response_model=List[OutbreakResponse])
def get_detected_outbreaks():
    try:
        df = detect_outbreaks()
        
        # Convert DataFrame to list of dictionaries and add the text explanation
        results = []
        for _, row in df.iterrows():
            results.append({
                "district": row["district"],
                "indicatorname": row["indicatorname"],
                "month": row["month"],
                "total_cases": int(row["total_cases"]),
                "baseline": int(row["baseline"]),
                "surge_percent": round(row["surge_percent"], 2),
                "explanation": explain_outbreak(row)
            })
            
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))