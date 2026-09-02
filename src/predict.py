from pathlib import Path
import numpy as np
import pandas as pd
import joblib

PROJECT_ROOT  = Path(__file__).resolve().parents[1]
PIPELINE_PATH = PROJECT_ROOT / "models" / "xgb_pipeline.pkl"

# load pipeline
def load_pipeline(path: Path = PIPELINE_PATH):
    if not path.exists():
        raise FileNotFoundError(
            f"Pipeline not found at {path}. Run train.py first."
        )
    return joblib.load(path)


# load once at module level
# so FastAPI doesn't reload it on every request
_pipeline = load_pipeline()

def predict_rent(input_dict: dict) -> dict:
    """
    Predict monthly PG rent from raw input.

    Input:  dict of raw PG features (same column names as raw CSV)
    Output: dict with predicted rent and confidence range
    """

    # convert input dict to single row dataframe cuz, my pipeline expects a dataframe, not a dict
    input_df = pd.DataFrame([input_dict])

    # pipeline handles all preprocessing internally
    # BasicFeatureTransformer -> LocalityMedianImputer -> ColumnTransformer -> XGBoost
    log_prediction = _pipeline.predict(input_df)

    # back transform from log scale to actual rupees
    predicted_rent = float(np.expm1(log_prediction[0]))

    # confidence range model has MAE of ~₹1,087
    # give user a realistic lower and upper band
    lower = round(predicted_rent - 1087, 2)
    upper = round(predicted_rent + 1087, 2)

    return {
        "predicted_rent" : round(predicted_rent, 2),
        "range_low"      : max(lower, 0),   # rent can't be negative
        "range_high"     : upper,
        "currency"       : "INR",
    }

if __name__ == "__main__":

    sample = {
        "latitude"          : 12.9716,
        "longitude"         : 80.2209,
        "locality"          : "Velachery",
        "transit_score"     : 7.5,
        "lifestyle_score"   : 6.2,
        "occupancy"         : "DOUBLE",
        "deposit"           : 10000,
        "attached_bathroom" : False,
        "food_included"     : True,
        "mess"              : False,
        "wifi"              : True,
        "laundry"           : False,
        "power_backup"      : True,
        "refrigerator"      : False,
        "common_tv"         : False,
        "room_cleaning"     : False,
        "room_ac"           : False,
        "room_cupboard"     : True,
        "room_tv"           : False,
        "room_geyser"       : True,
        "room_bedding"      : False,
        "room_attached_bath": False,
        "gender"            : "MALE",
        "parking"           : "Bike",
        "available_for"     : "Anyone",
        "transit_score_missing": 1,
        "lifestyle_score_missing": 1,

    }

    result = predict_rent(sample)

    print(f"Predicted Rent  ₹{result['predicted_rent']:,.2f}")
    print(f"Expected Range  ₹{result['range_low']:,.2f} — ₹{result['range_high']:,.2f}")