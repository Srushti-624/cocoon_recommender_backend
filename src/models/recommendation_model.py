from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date

class PredictionRequest(BaseModel):
    city: str = Field(..., description="City for weather-based prediction (e.g., Bengaluru, Ramanagar, Siddlaghatta)")

class PredictionResponse(BaseModel):
    recommendation_id: str
    city: str
    start_date: date
    end_date: date
    predicted_price: float
    confidence_score: Optional[float] = None
    weather_conditions: Optional[dict] = None
    created_at: datetime

class RecommendationHistoryItem(BaseModel):
    id: str
    city: str
    start_date: date
    end_date: date
    predicted_price: float
    created_at: datetime

class RecommendationHistoryResponse(BaseModel):
    recommendations: List[RecommendationHistoryItem]
    total: int

class TenDayPrediction(BaseModel):
    date: date
    predicted_price: float
    end_date: date
    is_best_date: bool = False

class TenDayGraphResponse(BaseModel):
    predictions: List[TenDayPrediction]
    best_start_date: date
    best_predicted_price: float
