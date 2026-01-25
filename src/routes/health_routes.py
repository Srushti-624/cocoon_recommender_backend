from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Any
from src.database.mongo import mongodb
from src.services.ml_service import ml_service

router = APIRouter(prefix="/api/health", tags=["Health"])

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    database: Dict[str, Any]
    ml_model: Dict[str, Any]
    api: Dict[str, Any]

@router.get("/", response_model=HealthResponse)
async def health_check():
    """
    System health check endpoint
    
    - Checks database connection status
    - Checks ML model loading status
    - Returns API server status
    - Provides timestamp of check
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "database": {},
        "ml_model": {},
        "api": {}
    }
    
    # Check database connection
    try:
        if mongodb.client is not None:
            # Ping database to verify connection
            await mongodb.client.admin.command('ping')
            health_status["database"] = {
                "status": "connected",
                "type": "MongoDB"
            }
        else:
            health_status["database"] = {
                "status": "disconnected",
                "error": "Client not initialized"
            }
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["database"] = {
            "status": "error",
            "error": str(e)
        }
        health_status["status"] = "unhealthy"
    
    # Check ML model status
    try:
        ml_health = ml_service.health_check()
        health_status["ml_model"] = ml_health
        
        if not ml_health.get("model_loaded"):
            health_status["status"] = "degraded"
            health_status["ml_model"]["warning"] = "Model not loaded - using fallback predictions"
    except Exception as e:
        health_status["ml_model"] = {
            "status": "error",
            "error": str(e)
        }
        health_status["status"] = "degraded"
    
    # API server status
    health_status["api"] = {
        "status": "running",
        "version": "1.0.0"
    }
    
    return HealthResponse(**health_status)

@router.get("/database")
async def database_health():
    """
    Detailed database health check
    
    - Tests database connection
    - Returns collection statistics
    """
    try:
        if mongodb.client is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database client not initialized"
            )
        
        # Ping database
        await mongodb.client.admin.command('ping')
        
        # Get database stats
        from src.core.config import settings
        db = mongodb.client[settings.DATABASE_NAME]
        stats = await db.command("dbStats")
        
        return {
            "status": "connected",
            "database_name": settings.DATABASE_NAME,
            "collections": stats.get("collections", 0),
            "data_size": stats.get("dataSize", 0),
            "storage_size": stats.get("storageSize", 0)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database health check failed: {str(e)}"
        )

@router.get("/ml-model")
async def ml_model_health():
    """
    Detailed ML model health check
    
    - Returns model loading status
    - Provides model metadata
    - Tests prediction capability
    """
    try:
        health = ml_service.health_check()
        
        # Test prediction if model is loaded
        if health.get("model_loaded"):
            try:
                test_prediction = ml_service.predict_price(
                    city="Bengaluru",
                    temperature=25.0,
                    humidity=65.0
                )
                health["test_prediction"] = {
                    "status": "success",
                    "sample_price": test_prediction.get("predicted_price")
                }
            except Exception as e:
                health["test_prediction"] = {
                    "status": "failed",
                    "error": str(e)
                }
        
        return health
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"ML model health check failed: {str(e)}"
        )
