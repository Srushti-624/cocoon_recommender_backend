from datetime import datetime, date, timedelta
from typing import List, Dict, Any
from src.services.ml_service import ml_service
from src.services.rule_engine import apply_temperature_constraints, get_optimal_rearing_duration
from src.utils.date_utils import calculate_end_date, generate_date_range

def date_to_datetime(d: date) -> datetime:
    """Convert date to datetime for MongoDB compatibility"""
    return datetime.combine(d, datetime.min.time())

async def generate_recommendation(
    city: str,
    user_id: str,
    weather_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate a single recommendation for the given city using real weather data
    """
    # Extract weather features
    avg_temp = weather_data.get("avg_temp", 25.0)
    max_temp = weather_data.get("max_temp", 29.0)
    humidity = weather_data.get("humidity", 65.0)
    rainfall = weather_data.get("rainfall", 0.0)
    
    # Get ML prediction
    prediction = ml_service.predict_price(
        city=city,
        temperature=avg_temp,
        max_temp=max_temp,
        humidity=humidity,
        rainfall=rainfall
    )
    
    # Apply rule-based constraints (using average temp)
    start_date = date.today() + timedelta(days=1)  # Start tomorrow by default
    start_date = apply_temperature_constraints(start_date, avg_temp)
    
    # Calculate end date based on optimal rearing duration
    duration_days = get_optimal_rearing_duration(avg_temp)
    end_date = calculate_end_date(start_date, duration_days)
    
    # Convert dates to datetime for MongoDB
    return {
        "user_id": user_id,
        "city": city,
        "start_date": date_to_datetime(start_date),
        "end_date": date_to_datetime(end_date),
        "predicted_price": prediction["predicted_price"],
        "confidence_score": prediction.get("confidence_score", 0.0),
        "weather_conditions": {
            "temperature": avg_temp,
            "max_temp": max_temp,
            "humidity": humidity,
            "rainfall": rainfall
        },
        "created_at": datetime.utcnow()
    }

async def generate_10day_predictions(
    city: str,
    weather_forecasts: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Generate predictions for the next 10 days using real weather forecast
    """
    predictions = []
    
    # We only need 10 days, but API might return more
    forecast_days = weather_forecasts[:10]
    
    for day_weather in forecast_days:
        # Parse date from weather string format "YYYY-MM-DD"
        prediction_date = datetime.strptime(day_weather["date"], "%Y-%m-%d").date()
        
        avg_temp = day_weather.get("avg_temp", 25.0)
        max_temp = day_weather.get("max_temp", 29.0)
        humidity = day_weather.get("humidity", 65.0)
        rainfall = day_weather.get("rainfall", 0.0)
        
        # Get price prediction
        prediction = ml_service.predict_price(
            city=city,
            temperature=avg_temp,
            max_temp=max_temp,
            humidity=humidity,
            rainfall=rainfall,
            month=prediction_date.month # Pass the specific month of the forecast date
        )
        
        # Calculate rearing duration and end date
        duration = get_optimal_rearing_duration(avg_temp)
        end_date = calculate_end_date(prediction_date, duration)
        
        predictions.append({
            "date": prediction_date,
            "predicted_price": prediction["predicted_price"],
            "end_date": end_date,
            "temperature": avg_temp,
            "is_best_date": False
        })
    
    # Find best date (highest predicted price)
    if predictions:
        best_prediction = max(predictions, key=lambda x: x["predicted_price"])
        best_prediction["is_best_date"] = True
    
    return predictions

async def save_recommendation(recommendation_data: Dict[str, Any], recommendations_collection) -> str:
    """
    Save recommendation to database
    
    Args:
        recommendation_data: Recommendation details
        recommendations_collection: MongoDB collection
        
    Returns:
        Inserted recommendation ID
    """
    result = await recommendations_collection.insert_one(recommendation_data)
    return str(result.inserted_id)

async def get_user_recommendations(
    user_id: str,
    recommendations_collection,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Get user's recommendation history
    
    Args:
        user_id: User ID
        recommendations_collection: MongoDB collection
        limit: Maximum number of recommendations to return
        
    Returns:
        List of recommendations
    """
    cursor = recommendations_collection.find(
        {"user_id": user_id}
    ).sort("created_at", -1).limit(limit)
    
    recommendations = []
    async for doc in cursor:
        recommendations.append({
            "id": str(doc["_id"]),
            "city": doc["city"],
            "start_date": doc["start_date"],
            "end_date": doc["end_date"],
            "predicted_price": doc["predicted_price"],
            "created_at": doc["created_at"]
        })
    
    return recommendations
