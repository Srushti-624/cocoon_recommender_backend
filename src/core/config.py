from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    MONGODB_URI: str
    DATABASE_NAME: str = "cocoon_recommender"
    
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60 * 24 * 7  # 7 days
    
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
    ]  # Specific origins for development (required when using credentials)
    
    MODEL_PATH_XGBOOST: str = "model/xgb_model.pkl"
    MODEL_PATH_CITY_ENCODER: str = "model/le_city.pkl"
    MODEL_PATH_SEASON_ENCODER: str = "model/le_season.pkl"
    
    OPEN_METEO_API_BASE: str = "https://api.open-meteo.com/v1/forecast"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
