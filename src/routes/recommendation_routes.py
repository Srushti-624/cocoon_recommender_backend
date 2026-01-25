from fastapi import APIRouter, HTTPException, status, Depends
from src.models.recommendation_model import (
    PredictionRequest,
    PredictionResponse,
    RecommendationHistoryResponse,
    RecommendationHistoryItem,
    TenDayGraphResponse,
    TenDayPrediction
)
from src.database.mongo import get_recommendations_collection, get_users_collection
from src.core.security import get_current_user_id
from src.services.recommendation_service import (
    generate_recommendation,
    generate_10day_predictions,
    save_recommendation,
    get_user_recommendations
)
from datetime import datetime, date
from bson import ObjectId

router = APIRouter(prefix="/api/recommendation", tags=["Recommendations"])

def datetime_to_date(dt) -> date:
    """Convert datetime to date, handling both datetime and date objects"""
    if isinstance(dt, datetime):
        return dt.date()
    elif isinstance(dt, date):
        return dt
    return dt

async def verify_farmer_role(user_id: str = Depends(get_current_user_id)) -> str:
    """Verify user has Farmer role"""
    users_collection = get_users_collection()
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    
    if not user or user.get("role") != "Farmer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Farmer role required."
        )
    return user_id

from src.services.weather_service import weather_service

@router.post("/predict", response_model=PredictionResponse, status_code=status.HTTP_201_CREATED)
async def generate_cocoon_recommendation(
    request: PredictionRequest,
    user_id: str = Depends(verify_farmer_role)
):
    """
    Generate cocoon rearing recommendation based on city and weather
    """
    try:
        # Fetch real weather data
        weather_data = await weather_service.get_weather_data(request.city)
        current_weather = weather_data.get("current")
        
        if not current_weather:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Could not fetch weather data"
            )
        
        # Generate recommendation
        recommendation = await generate_recommendation(
            city=request.city,
            user_id=user_id,
            weather_data=current_weather
        )
        
        # Save to database
        recommendations_collection = get_recommendations_collection()
        recommendation_id = await save_recommendation(
            recommendation,
            recommendations_collection
        )
        
        return PredictionResponse(
            recommendation_id=recommendation_id,
            city=recommendation["city"],
            start_date=datetime_to_date(recommendation["start_date"]),
            end_date=datetime_to_date(recommendation["end_date"]),
            predicted_price=recommendation["predicted_price"],
            confidence_score=recommendation.get("confidence_score"),
            weather_conditions=recommendation.get("weather_conditions"),
            created_at=recommendation["created_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error generating recommendation: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate recommendation: {str(e)}"
        )

@router.get("/history", response_model=RecommendationHistoryResponse)
async def get_recommendation_history(
    limit: int = 10,
    user_id: str = Depends(verify_farmer_role)
):
    """
    Get user's recommendation history
    """
    try:
        recommendations_collection = get_recommendations_collection()
        
        recommendations = await get_user_recommendations(
            user_id=user_id,
            recommendations_collection=recommendations_collection,
            limit=limit
        )
        
        history_items = [
            RecommendationHistoryItem(
                id=rec["id"],
                city=rec["city"],
                start_date=datetime_to_date(rec["start_date"]),
                end_date=datetime_to_date(rec["end_date"]),
                predicted_price=rec["predicted_price"],
                created_at=rec["created_at"]
            )
            for rec in recommendations
        ]
        
        return RecommendationHistoryResponse(
            recommendations=history_items,
            total=len(history_items)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch recommendation history: {str(e)}"
        )

@router.get("/10day-graph", response_model=TenDayGraphResponse)
async def get_10day_prediction_graph(
    city: str,
    user_id: str = Depends(verify_farmer_role)
):
    """
    Get 10-day prediction graph data for dashboard
    """
    try:
        # Fetch real 10-day weather forecast
        weather_data = await weather_service.get_weather_data(city, days=12) # Fetch extra days to be safe
        forecasts = weather_data.get("forecast", [])
        
        if not forecasts:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Could not fetch weather forecast"
            )
        
        # Generate 10-day predictions
        predictions = await generate_10day_predictions(
            city=city,
            weather_forecasts=forecasts
        )
        
        # Find best prediction
        best_prediction = max(predictions, key=lambda x: x["predicted_price"])
        
        # Convert to response model
        prediction_items = [
            TenDayPrediction(
                date=pred["date"],
                predicted_price=pred["predicted_price"],
                end_date=pred["end_date"],
                is_best_date=pred["is_best_date"]
            )
            for pred in predictions
        ]
        
        return TenDayGraphResponse(
            predictions=prediction_items,
            best_start_date=best_prediction["date"],
            best_predicted_price=best_prediction["predicted_price"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error generating 10-day graph: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate 10-day predictions: {str(e)}"
        )
