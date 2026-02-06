from pydantic import BaseModel
from typing import List

class OutbreakResponse(BaseModel):
    district: str
    indicatorname: str
    month: str
    total_cases: int
    baseline: int
    surge_percent: float
    explanation: str