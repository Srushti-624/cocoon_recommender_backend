from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    MONGODB_URI: str
    DATABASE_NAME: str = "cocoon_recommender"
    
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60 * 24 * 7  # 7 days
    
    CORS_ORIGINS: List[str] = ["*"]
    
    MODEL_PATH_XGBOOST: str = "model/xgb_model.pkl"
    MODEL_PATH_CITY_ENCODER: str = "model/le_city.pkl"
    MODEL_PATH_SEASON_ENCODER: str = "model/le_season.pkl"
    
    OPEN_METEO_API_BASE: str = "https://api.open-meteo.com/v1/forecast"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
