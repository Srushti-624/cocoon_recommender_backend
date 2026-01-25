"""
Test script to verify ML model loading
Run this to check if the model loads correctly
"""
import sys
sys.path.append('src')

from services.ml_service import MLService

print("=" * 60)
print("Testing ML Model Loading")
print("=" * 60)

# Create service instance
ml = MLService()

# Try to load model
success = ml.load_model()

print("\n" + "=" * 60)
if success:
    print("✅ Model loading: SUCCESS")
    print("\nTesting prediction...")
    
    # Test prediction
    result = ml.predict_price(
        city="Bengaluru",
        temperature=24.0,
        humidity=65.0
    )
    
    print(f"\nTest Prediction Result:")
    print(f"  Price: ₹{result['predicted_price']}")
    print(f"  Confidence: {result['confidence_score']}")
    print(f"  Status: {result['model_status']}")
    
else:
    print("❌ Model loading: FAILED")
    print("\nPlease check:")
    print("  1. Model file exists at: model/xgb_model.pkl")
    print("  2. Label encoders exist at: model/le_city.pkl, model/le_season.pkl")
    print("  3. All pickle files are valid")

print("=" * 60)
