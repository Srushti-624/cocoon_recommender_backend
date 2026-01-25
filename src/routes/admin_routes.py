from fastapi import APIRouter, HTTPException, status, Depends, Query
from src.models.market_weather_model import MarketWeatherUpload, MarketWeatherResponse
from src.database.mongo import get_market_weather_collection, get_users_collection
from src.core.security import get_current_user_id
from datetime import datetime
from typing import List, Optional
from bson import ObjectId

router = APIRouter(prefix="/api/admin", tags=["Admin Management"])

async def verify_admin_role(user_id: str = Depends(get_current_user_id)) -> str:
    users_collection = get_users_collection()
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    
    if not user or user.get("role") != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin role required."
        )
    return user_id

@router.post("/market-weather", response_model=MarketWeatherResponse, status_code=status.HTTP_201_CREATED)
async def upload_market_weather_data(
    data: MarketWeatherUpload,
    user_id: str = Depends(verify_admin_role)
):
    """
    Upload market price and weather data.
    - Admin-only endpoint
    - Stores daily market prices and weather conditions
    - Used for ML model training and recommendations
    """
    market_weather_collection = get_market_weather_collection()
    
    data_doc = {
        **data.dict(),
        "uploaded_by": user_id,
        "created_at": datetime.utcnow()
    }
    
    result = await market_weather_collection.insert_one(data_doc)
    
    return MarketWeatherResponse(
        id=str(result.inserted_id),
        city=data.city,
        date=data.date,
        market_price=data.market_price,
        avg_temp=data.avg_temp,
        max_temp=data.max_temp,
        avg_humidity=data.avg_humidity,
        rainfall=data.rainfall,
        created_at=data_doc["created_at"]
    )

@router.get("/market-weather", response_model=List[MarketWeatherResponse])
async def get_market_weather_data(
    city: Optional[str] = Query(None, pattern="^(Bengaluru|Ramanagar|Siddlaghatta)$"),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = Query(100, ge=1, le=1000),
    user_id: str = Depends(verify_admin_role)
):
    """
    Retrieve stored market and weather data.
    - Admin-only endpoint
    - Supports filtering by city and date range
    - Returns paginated results for review and validation
    """
    market_weather_collection = get_market_weather_collection()
    
    query = {}
    if city:
        query["city"] = city
    if start_date or end_date:
        query["date"] = {}
        if start_date:
            query["date"]["$gte"] = start_date
        if end_date:
            query["date"]["$lte"] = end_date
    
    cursor = market_weather_collection.find(query).sort("date", -1).limit(limit)
    data_list = await cursor.to_list(length=limit)
    
    return [
        MarketWeatherResponse(
            id=str(doc["_id"]),
            city=doc["city"],
            date=doc["date"],
            market_price=doc["market_price"],
            avg_temp=doc.get("avg_temp"),
            max_temp=doc.get("max_temp"),
            avg_humidity=doc.get("avg_humidity"),
            rainfall=doc.get("rainfall"),
            created_at=doc["created_at"]
        )
        for doc in data_list
    ]
