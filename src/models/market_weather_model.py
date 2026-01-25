from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class MarketWeatherUpload(BaseModel):
    city: str = Field(..., pattern="^(Bengaluru|Ramanagar|Siddlaghatta)$")
    date: datetime
    market_price: float = Field(..., ge=0)
    avg_temp: Optional[float] = None
    max_temp: Optional[float] = None
    avg_humidity: Optional[float] = None
    rainfall: Optional[float] = None

class MarketWeatherResponse(BaseModel):
    id: str
    city: str
    date: datetime
    market_price: float
    avg_temp: Optional[float] = None
    max_temp: Optional[float] = None
    avg_humidity: Optional[float] = None
    rainfall: Optional[float] = None
    created_at: datetime
