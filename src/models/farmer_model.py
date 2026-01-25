from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class FarmerProfileCreate(BaseModel):
    district: str = Field(..., pattern="^(Bengaluru|Ramanagar|Siddlaghatta)$")
    experience_years: Optional[int] = Field(None, ge=0)
    farm_size_acres: Optional[float] = Field(None, ge=0)
    phone_number: Optional[str] = None

class FarmerProfileResponse(BaseModel):
    id: str
    user_id: str
    district: str
    experience_years: Optional[int] = None
    farm_size_acres: Optional[float] = None
    phone_number: Optional[str] = None
    created_at: datetime
    updated_at: datetime
