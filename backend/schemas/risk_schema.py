from pydantic import BaseModel

class RiskResponse(BaseModel):
    district: str
    risk_score: float
