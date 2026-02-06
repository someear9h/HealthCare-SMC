from fastapi import APIRouter
from models.risk_engine import compute_risk

router = APIRouter()

@router.get("/districts")
def get_risk_by_district():
    data = compute_risk()

    return data.to_dict(orient="records")
