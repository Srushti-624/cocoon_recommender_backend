import joblib
import pandas as pd
import os

# Define the get_season function, as it's part of the feature engineering
def get_season(month):
    if month in [12,1,2]:
        return "Winter"
    if month in [3,4,5]:
        return "Summer"
    if month in [6,7,8,9]:
        return "Monsoon"
    return "PostMonsoon"

# Define feature columns (must match the order used during training)
FEATURE_COLUMNS = [
    "city",
    "month",
    "season",
    "avg_temp",
    "max_temp",
    "avg_humidity",
    "rainfall"
]

# --- 1. Load the models ---
# Ensure the 'model' directory exists or adjust paths if saved elsewhere
model_path = "model/xgb_model.pkl"
le_city_path = "model/le_city.pkl"
le_season_path = "model/le_season.pkl"

if not os.path.exists(model_path):
    raise FileNotFoundError(f"Model file not found at {model_path}. Please ensure it's saved correctly.")
if not os.path.exists(le_city_path):
    raise FileNotFoundError(f"City LabelEncoder file not found at {le_city_path}. Please ensure it's saved correctly.")
if not os.path.exists(le_season_path):
    raise FileNotFoundError(f"Season LabelEncoder file not found at {le_season_path}. Please ensure it's saved correctly.")

xgb_model = joblib.load(model_path)
le_city = joblib.load(le_city_path)
le_season = joblib.load(le_season_path)

print("Models loaded successfully!")


# --- 2. Prepare new input data for prediction ---
# Example input data (modify these values as needed)
input_city = "Siddlaghatta"
input_month = 4  # April
input_season = get_season(input_month) # Use the get_season function
input_avg_temp = 28.0
input_max_temp = 32.5
input_avg_humidity = 45.0
input_rainfall = 5.0

# Create a dictionary for the new input
new_data = {
    "city": [input_city],
    "month": [input_month],
    "season": [input_season],
    "avg_temp": [input_avg_temp],
    "max_temp": [input_max_temp],
    "avg_humidity": [input_avg_humidity],
    "rainfall": [input_rainfall]
}

# Convert to DataFrame
input_df = pd.DataFrame(new_data)

# Label encode the categorical features using the loaded encoders
# Ensure the input categorical values are known to the encoders
try:
    input_df["city"] = le_city.transform(input_df["city"])
    input_df["season"] = le_season.transform(input_df["season"])
except ValueError as e:
    print(f"Error encoding categorical features. Make sure the input city/season are valid.\nError: {e}")
    # You might want to handle this error more gracefully, e.g., by skipping prediction

# Ensure column order matches the training features
input_df_encoded = input_df[FEATURE_COLUMNS]

print("Prepared input data (encoded):")
display(input_df_encoded)

# --- 3. Make a prediction ---
predicted_price = xgb_model.predict(input_df_encoded)[0]

print(f"\nPredicted Market Price for {input_city} in {input_season} (Month {input_month}): ₹{predicted_price:.2f}")