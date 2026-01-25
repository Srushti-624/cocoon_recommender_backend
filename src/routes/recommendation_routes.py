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

@router.post("/predict", response_model=PredictionResponse, status_code=status.HTTP_201_CREATED)
async def generate_cocoon_recommendation(
    request: PredictionRequest,
    user_id: str = Depends(verify_farmer_role)
):
    """
    Generate cocoon rearing recommendation based on city and weather
    
    - Fetches weather data for the specified city
    - Generates ML-based price prediction
    - Applies rule-based constraints
    - Calculates optimal start and end dates
    - Saves recommendation to database
    """
    try:
        # For now, using mock temperature data
        # TODO: Integrate with weather API or database
        city_temperatures = {
            "Bengaluru": 24.0,
            "Ramanagar": 26.0,
            "Siddlaghatta": 25.0
        }
        
        temperature = city_temperatures.get(request.city, 25.0)
        humidity = 65.0  # Default humidity
        
        # Generate recommendation
        recommendation = await generate_recommendation(
            city=request.city,
            user_id=user_id,
            temperature=temperature,
            humidity=humidity
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
        
    except Exception as e:
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
    
    - Returns list of past recommendations
    - Sorted by creation date (newest first)
    - Limited to specified number of results
    """
    try:
        recommendations_collection = get_recommendations_collection()
        
        recommendations = await get_user_recommendations(
            user_id=user_id,
            recommendations_collection=recommendations_collection,
            limit=limit
        )
        
        history_items = [
            RecommendationHistoryItem(**rec)
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
    
    - Generates predictions for next 10 days
    - Identifies best start date within the window
    - Returns data suitable for chart visualization
    """
    try:
        # Mock temperature data
        city_temperatures = {
            "Bengaluru": 24.0,
            "Ramanagar": 26.0,
            "Siddlaghatta": 25.0
        }
        
        base_temperature = city_temperatures.get(city, 25.0)
        
        # Generate 10-day predictions
        predictions = await generate_10day_predictions(
            city=city,
            base_temperature=base_temperature,
            humidity=65.0
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
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate 10-day predictions: {str(e)}"
        )
