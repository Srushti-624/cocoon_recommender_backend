import joblib
import os
from pathlib import Path
from typing import Optional, Dict, Any
import pandas as pd
from datetime import datetime

# Feature columns must match the order used during training
FEATURE_COLUMNS = [
    "city",
    "month",
    "season",
    "avg_temp",
    "max_temp",
    "avg_humidity",
    "rainfall"
]

def get_season(month: int) -> str:
    """Get season from month - matches training data format"""
    if month in [12, 1, 2]:
        return "Winter"
    if month in [3, 4, 5]:
        return "Summer"
    if month in [6, 7, 8, 9]:
        return "Monsoon"
    return "PostMonsoon"  # Note: No hyphen, matches training data


class MLService:
    def __init__(self):
        self.model = None
        self.le_city = None
        self.le_season = None
        self.model_loaded = False
        
    def load_model(self):
        """Load XGBoost model and label encoders on startup"""
        try:
            model_path = Path("model/xgb_model.pkl")
            le_city_path = Path("model/le_city.pkl")
            le_season_path = Path("model/le_season.pkl")
            
            # Check if files exist
            if not model_path.exists():
                print(f"[WARNING] Model file not found at {model_path}")
                return False
            
            # Load model and encoders using joblib (matches training code)
            print(f"[LOADING] ML model from {model_path}...")
            self.model = joblib.load(model_path)
            print(f"[SUCCESS] Model loaded: {type(self.model).__name__}")
            
            if le_city_path.exists():
                self.le_city = joblib.load(le_city_path)
                print(f"[SUCCESS] Loaded city encoder")
            else:
                print(f"[WARNING] City encoder not found")
                
            if le_season_path.exists():
                self.le_season = joblib.load(le_season_path)
                print(f"[SUCCESS] Loaded season encoder")
            else:
                print(f"[WARNING] Season encoder not found")
            
            self.model_loaded = True
            print(f"[SUCCESS] ML Service initialized!")
            return True
            
        except Exception as e:
            print(f"[ERROR] Loading ML model: {e}")
            import traceback
            traceback.print_exc()
            self.model_loaded = False
            return False
    
    def predict_price(
        self,
        city: str,
        temperature: float,
        humidity: Optional[float] = None,
        max_temp: Optional[float] = None,
        rainfall: Optional[float] = None,
        month: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Predict cocoon price based on input features
        """
        if not self.model_loaded or self.model is None:
            print(f"[WARNING] Model not loaded - returning fallback prediction")
            return {
                "predicted_price": 450.0,
                "confidence_score": 0.0,
                "model_status": "not_loaded"
            }
        
        try:
            # Use current month if not provided
            if month is None:
                month = datetime.now().month
            
            # Get season from month
            season = get_season(month)
            
            # Default values for optional parameters
            if humidity is None:
                humidity = 65.0
            if max_temp is None:
                max_temp = temperature + 4.0  # Estimate max temp
            if rainfall is None:
                # Estimate rainfall based on season
                rainfall_by_season = {
                    "Monsoon": 150.0,
                    "PostMonsoon": 80.0,
                    "Winter": 20.0,
                    "Summer": 40.0
                }
                rainfall = rainfall_by_season.get(season, 50.0)
            
            print(f"[PREDICT] city={city}, month={month}, season={season}, temp={temperature}")
            
            # Create input dataframe (matches run_model.py format)
            new_data = {
                "city": [city],
                "month": [month],
                "season": [season],
                "avg_temp": [temperature],
                "max_temp": [max_temp],
                "avg_humidity": [humidity],
                "rainfall": [rainfall]
            }
            
            input_df = pd.DataFrame(new_data)
            
            # Encode categorical features using the loaded encoders
            if self.le_city is not None:
                input_df["city"] = self.le_city.transform(input_df["city"])
            else:
                print("[WARNING] City encoder not available")
                return self._fallback_response("city_encoder_missing")
                
            if self.le_season is not None:
                input_df["season"] = self.le_season.transform(input_df["season"])
            else:
                print("[WARNING] Season encoder not available")
                return self._fallback_response("season_encoder_missing")
            
            # Ensure column order matches training features
            input_df_encoded = input_df[FEATURE_COLUMNS].copy()
            
            # Explicitly set column names (required for XGBoost feature validation)
            input_df_encoded.columns = FEATURE_COLUMNS
            
            print(f"   Encoded features: {input_df_encoded.to_dict('records')[0]}")
            print(f"   DataFrame columns: {list(input_df_encoded.columns)}")
            
            # Make prediction using DMatrix to ensure feature names are passed
            import xgboost as xgb
            dmatrix = xgb.DMatrix(input_df_encoded, feature_names=FEATURE_COLUMNS)
            predicted_price = self.model.get_booster().predict(dmatrix)[0]
            
            print(f"   Result: Rs.{predicted_price:.2f}")
            
            return {
                "predicted_price": float(predicted_price),
                "confidence_score": 0.85,
                "model_status": "active"
            }
            
        except Exception as e:
            print(f"[ERROR] Prediction failed: {e}")
            import traceback
            traceback.print_exc()
            return self._fallback_response(str(e))
    
    def _fallback_response(self, reason: str) -> Dict[str, Any]:
        """Return fallback prediction when model fails"""
        return {
            "predicted_price": 450.0,
            "confidence_score": 0.0,
            "model_status": "error",
            "error": reason
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Check ML service health status"""
        return {
            "model_loaded": self.model_loaded,
            "model_type": type(self.model).__name__ if self.model else None,
            "city_encoder": self.le_city is not None,
            "season_encoder": self.le_season is not None,
            "status": "healthy" if self.model_loaded else "model_not_loaded"
        }


# Global ML service instance
ml_service = MLService()
