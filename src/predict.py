from pathlib import Path
import json
import numpy as np
import pandas as pd
import joblib

from configs import(
    PIPELINE_PATH, 
    LOCALITY_REF_PATH, METRICS_PATH 
)

def load_pipeline():
    if not PIPELINE_PATH.exists():
        raise FileNotFoundError(
            f"Pipeline not found at {PIPELINE_PATH}\n"
            f"Run train.py first."
        )
    return joblib.load(PIPELINE_PATH)

# load once at module level
# so FastAPI doesn't reload it on every request
_pipeline = load_pipeline()

def load_locality_reference():
    if not LOCALITY_REF_PATH.exists():
        raise FileNotFoundError(
            f"Locality reference not found at {LOCALITY_REF_PATH}\n"
            f"Run train.py first."
        )
    return joblib.load(LOCALITY_REF_PATH)

_locality_ref = load_locality_reference()
LOCALITIES    = sorted(_locality_ref.index.tolist())


def load_metrics():
    if not METRICS_PATH.exists():
        raise FileNotFoundError(
            f"Metrics not found at {METRICS_PATH}\n"
            f"Run train.py first."
        )
    with open(METRICS_PATH) as f:
        return json.load(f)

_metrics = load_metrics()

def predict_rent(
        locality: str,
        occupancy: str,
        gender: str,
        available_for: str,
        parking: str,
        food_included: bool = False,
        wifi: bool = False,
        room_ac: bool = False,
        laundry: bool = False,
        attached_bathroom: bool = False,
        mess: bool = False,
        power_backup: bool = False,
        refrigerator: bool = False,
        common_tv: bool = False,
        room_cleaning: bool = False,
        room_cupboard: bool = False,
        room_tv: bool = False,
        room_geyser: bool = False,
        room_bedding: bool = False,
        room_attached_bath: bool = False,
) -> dict:

    if locality not in _locality_ref.index:
        raise ValueError(f"Unknown locality: {locality}. Choose from: {LOCALITIES}")

    loc = _locality_ref.loc[locality]

    input_dict = {
        # from locality reference, real training data medians
        'latitude': loc['latitude'],
        'longitude': loc['longitude'],
        'deposit': loc['deposit'],
        # let the pipeline's own LocalityMedianImputer fill these
        # exactly like it does for any missing value at training time
        'transit_score': np.nan,
        'lifestyle_score': np.nan,
        'transit_score_missing': 1, # if actually missing, imputer will fill
        'lifestyle_score_missing': 1,
        'locality': locality,
        'occupancy': occupancy,
        'gender': gender,
        'available_for': available_for,
        'parking': parking,
        'food_included': food_included,
        'wifi': wifi,
        'room_ac': room_ac,
        'laundry': laundry,
        'attached_bathroom': attached_bathroom,
        'mess': mess,
        'power_backup': power_backup,
        'refrigerator': refrigerator,
        'common_tv': common_tv,
        'room_cleaning': room_cleaning,
        'room_cupboard': room_cupboard,
        'room_tv': room_tv,
        'room_geyser': room_geyser,
        'room_bedding': room_bedding,
        'room_attached_bath': room_attached_bath,
    }

    input_df = pd.DataFrame([input_dict])
    log_pred = _pipeline.predict(input_df)
    predicted_rent = float(np.expm1(log_pred[0]))

    # estimated error range based on last training run test MAE
    test_mae = _metrics["test_mae"]
    lower    = round(max(predicted_rent - test_mae, 0), 2)
    upper    = round(predicted_rent + test_mae, 2)

    return {
        'predicted_rent': round(predicted_rent, 2),
        'range_low': lower,
        'range_high': upper,
        'currency': 'INR',
    }

if __name__ == "__main__":

    # test 1  basic prediction
    print("Test 1: Basic prediction")
    result = predict_rent(
        locality      = "Velachery",
        occupancy     = "DOUBLE",
        gender        = "MALE",
        available_for = "Anyone",
        parking       = "Bike",
        food_included = True,
        wifi          = True,
    )
    print(f"  Predicted Rent  ₹{result['predicted_rent']:,.2f}")
    print(f"  Expected Range  ₹{result['range_low']:,.2f} — ₹{result['range_high']:,.2f}")

    # test 2 — different locality and occupancy
    print("\nTest 2: Single room in Adyar")
    result2 = predict_rent(
        locality      = "Adyar",
        occupancy     = "SINGLE",
        gender        = "FEMALE",
        available_for = "Working Professional",
        parking       = "No Parking",
        food_included = True,
        wifi          = True,
        room_ac       = True,
    )
    print(f"  Predicted Rent  ₹{result2['predicted_rent']:,.2f}")
    print(f"  Expected Range  ₹{result2['range_low']:,.2f} — ₹{result2['range_high']:,.2f}")

    # test 3 — budget pg
    print("\nTest 3: Budget PG in Tambaram")
    result3 = predict_rent(
        locality      = "Tambaram",
        occupancy     = "FOUR",
        gender        = "MALE",
        available_for = "Student",
        parking       = "No Parking",
    )
    print(f"  Predicted Rent  ₹{result3['predicted_rent']:,.2f}")
    print(f"  Expected Range  ₹{result3['range_low']:,.2f} — ₹{result3['range_high']:,.2f}")

    print("\nAll tests passed.")