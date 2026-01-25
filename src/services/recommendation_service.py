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
    temperature: float,
    humidity: float = None
) -> Dict[str, Any]:
    """
    Generate a single recommendation for the given city and weather conditions
    
    Args:
        city: City name
        user_id: User ID making the request
        temperature: Current/forecasted temperature
        humidity: Current/forecasted humidity
        
    Returns:
        Dictionary with recommendation details
    """
    # Get ML prediction
    prediction = ml_service.predict_price(
        city=city,
        temperature=temperature,
        humidity=humidity
    )
    
    # Apply rule-based constraints
    start_date = date.today() + timedelta(days=1)  # Start tomorrow by default
    start_date = apply_temperature_constraints(start_date, temperature)
    
    # Calculate end date based on optimal rearing duration
    duration_days = get_optimal_rearing_duration(temperature)
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
            "temperature": temperature,
            "humidity": humidity
        },
        "created_at": datetime.utcnow()
    }

async def generate_10day_predictions(
    city: str,
    base_temperature: float,
    humidity: float = None
) -> List[Dict[str, Any]]:
    """
    Generate predictions for the next 10 days
    
    Args:
        city: City name
        base_temperature: Current temperature (will vary slightly for each day)
        humidity: Current humidity
        
    Returns:
        List of predictions for 10 days with best date highlighted
    """
    predictions = []
    start_date = date.today()
    
    # Generate predictions for next 10 days
    for day_offset in range(10):
        prediction_date = start_date + timedelta(days=day_offset)
        
        # Simulate slight temperature variation (±2°C)
        import random
        temp_variation = random.uniform(-2, 2)
        day_temperature = base_temperature + temp_variation
        
        # Get price prediction
        prediction = ml_service.predict_price(
            city=city,
            temperature=day_temperature,
            humidity=humidity
        )
        
        # Calculate rearing duration and end date
        duration = get_optimal_rearing_duration(day_temperature)
        end_date = calculate_end_date(prediction_date, duration)
        
        predictions.append({
            "date": prediction_date,
            "predicted_price": prediction["predicted_price"],
            "end_date": end_date,
            "temperature": day_temperature,
            "is_best_date": False  # Will be set later
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
