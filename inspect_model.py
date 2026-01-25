"""
Script to inspect the XGBoost model and find out what features it expects
"""
import pickle
import sys

print("=" * 60)
print("Inspecting XGBoost Model Features")
print("=" * 60)

try:
    # Load the model
    with open('model/xgb_model.pkl', 'rb') as f:
        model = pickle.load(f)
    
    print(f"\nModel Type: {type(model).__name__}")
    print(f"\nModel expects {model.n_features_in_} features")
    
    # Try to get feature names
    if hasattr(model, 'feature_names_in_'):
        print(f"\nFeature names:")
        for i, name in enumerate(model.feature_names_in_):
            print(f"  {i+1}. {name}")
    else:
        print(f"\nFeature names not stored in model")
        print(f"Model expects {model.n_features_in_} features but names are unknown")
    
    # Get booster info
    if hasattr(model, 'get_booster'):
        booster = model.get_booster()
        feature_names = booster.feature_names
        if feature_names:
            print(f"\nBooster feature names:")
            for i, name in enumerate(feature_names):
                print(f"  {i+1}. {name}")
    
    print("\n" + "=" * 60)
    
except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
