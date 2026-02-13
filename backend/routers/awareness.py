from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import Session
from core.database import Base, get_db

# ########################################################################
# 1. ORM MODEL (The Database Table)
# ########################################################################
class HealthProgram(Base):
    __tablename__ = "health_programs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    program_type = Column(String)
    target_ward = Column(String, default="ALL")
    image_url = Column(String, nullable=True)
    scheduled_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

# ########################################################################
# 2. SCHEMAS (With Hardcoded Swagger Examples)
# ########################################################################
class ProgramCreate(BaseModel):
    title: str = Field(..., description="Program title")
    description: str = Field(..., description="Full program details")
    program_type: str = Field(default="AWARENESS", description="Category")
    target_ward: str = Field(default="Ward-B", description="Targeted ward")
    image_url: str = Field(default="https://images.unsplash.com/photo-1584036561566-baf8f5f1b144", description="Engaging image")
    scheduled_at: datetime = Field(default_factory=datetime.utcnow)

    # THIS IS THE MAGIC: Pre-fills the Swagger UI
    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Dengue Prevention Drive - Solapur",
                "description": "Clear stagnant water. Use mosquito nets. Join us at Ward-B PHC for free screening.",
                "program_type": "URGENT_AWARENESS",
                "target_ward": "Ward-B",
                "image_url": "https://images.unsplash.com/photo-1584036561566-baf8f5f1b144",
                "scheduled_at": "2026-02-14T10:00:00Z"
            }
        }
    }

class ProgramResponse(ProgramCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# ########################################################################
# 3. ROUTER (The API Logic)
# ########################################################################
router = APIRouter(prefix="/awareness", tags=["Citizen: Health Programs"])

@router.post("/", response_model=ProgramResponse)
async def create_program(req: ProgramCreate, db: Session = Depends(get_db)):
    """POST to broadcast. Values are pre-filled in API docs for demo."""
    new_program = HealthProgram(
        title=req.title,
        description=req.description,
        program_type=req.program_type,
        target_ward=req.target_ward,
        image_url=req.image_url,
        scheduled_at=req.scheduled_at
    )
    db.add(new_program)
    db.commit()
    db.refresh(new_program)
    return new_program

@router.get("/", response_model=List[ProgramResponse])
async def get_programs(ward: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(HealthProgram)
    if ward:
        query = query.filter((HealthProgram.target_ward == ward) | (HealthProgram.target_ward == "ALL"))
    return query.order_by(HealthProgram.created_at.desc()).all()