import joblib
import json
import pandas as pd
import numpy as np

from sklearn.pipeline import Pipeline

from configs import (
    FINAL_PIPELINE, LOCALITY_REFERENCE, FINAL_METRICS
)

def load_artifacts():
    """ SHOULD BE LOADED AT MODULE LEVEL
    1. loads the final_pipeline.pkl
    2. locality_reference.pkl
    3. metrics.json
    4. returns all
    """

    pipeline: Pipeline = joblib.load(FINAL_PIPELINE)
    locality_reference: pd.DataFrame = joblib.load(LOCALITY_REFERENCE)
    with open(FINAL_METRICS) as f:
        metrics: dict = json.load(f)

    return pipeline, locality_reference, metrics

# loaded at module lvl
_pipeline, _locality_ref, _metrics = load_artifacts()

def predict(locality: str, gender: str, occupancy: str, available_for: str, food_included: bool, wifi: bool, laundry: bool, room_ac: bool, parking: str) -> float:

    input_loc_ref = _locality_ref.loc[locality]
    input_dict = {

        # user inputs
        'locality': locality,
        'gender': gender,
        'occupancy': occupancy,
        'available_for': available_for,
        # amenities
        'food_included': food_included,
        'wifi': wifi,
        'laundry': laundry,
        'room_ac': room_ac,
        'parking': parking,

        # model derived inputs
        'latitude': input_loc_ref['latitude'],
        'longitude': input_loc_ref['longtitude'],
        'transit_score': np.nan,
        'lifestyle_score': np.nan,
        'deposit': input_loc_ref['deposit'],
        'attached_bathroom': input_loc_ref['attached_bathroom'],
        'mess': input_loc_ref['mess'],
        'power_backup': input_loc_ref['power_backup'],
        'refrigerator': input_loc_ref['refrigerator'],
        'common_tv': input_loc_ref['common_tv'],
        'room_cleaning': input_loc_ref['room_cleaning'],
        'room_cupboard': input_loc_ref['room_cupboard'],
        'room_tv': input_loc_ref['room_tv'],
        'room_geyser': input_loc_ref['room_geyser'],
        'room_bedding': input_loc_ref['room_bedding'],
        'room_attached_bath': input_loc_ref['room_attached_bath'],
    }

    input_df = pd.DataFrame([input_dict])
    log_pred = _pipeline.predict(input_dict)
    predicted_rent = float(np.expm1(log_pred[0]))

    lower = predicted_rent - _metrics['test_mae']
    upper = predicted_rent + _metrics['test_mae']

    print(f'Expected Rent is: {predicted_rent}')
    print(f'Actual Rent Around: {lower} - {upper}')

    return predicted_rent    