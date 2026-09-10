from dotenv import load_dotenv
import os
import joblib
import json

import pandas as pd
import numpy as np

from sklearn.pipeline import Pipeline

from pydantic import BaseModel
from fastapi import FastAPI
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from src.configs import (
    FINAL_PIPELINE, LOCALITY_REFERENCE, FINAL_METRICS
)

class InputSchema(BaseModel):
    locality: str
    gender: str
    occupancy: str
    available_for: str
    food_included: bool
    wifi: bool
    laundry: bool
    room_ac: bool
    parking: str

class OutputSchema(BaseModel):
    predicted_rent: float
    lower: float
    upper: float
    locality: str
    occupancy: str

@asynccontextmanager
async def load_artifacts_at_startup(app: FastAPI) -> AsyncGenerator:
    try:
        app.state.pipeline = joblib.load(FINAL_PIPELINE)
        app.state.locality_reference = joblib.load(LOCALITY_REFERENCE)
        with open(FINAL_METRICS) as f:
            app.state.metric = json.load(f)

        print(f'Artifacts loaded!')

    except FileNotFoundError:
        print(f'Artifacts files not found')
        app.state.pipeline = None
        app.state.locality_reference = None

    except Exception as e:
        import traceback
        traceback.print_exc()

        app.state.pipeline = None
        app.state.locality_reference = None
        app.state.metric = None

    yield
    print(f'snooze...')

# load_dotenv(find_dotenv())

app = FastAPI(title='Chennai PG Intelligence', version='dev-1.0',lifespan=load_artifacts_at_startup)

@app.get('/')
def health_check():
    return {'status': 'As you can see im not dead!?'}

@app.post('/prediction', response_model=OutputSchema)
async def predict(user_input: InputSchema):

    model: Pipeline = app.state.pipeline
    input_loc_ref: pd.DataFrame = app.state.locality_reference.loc[user_input.locality]
    test_metric = app.state.metric['test_mae']

    input_dict = {

        # user inputs
        'locality': user_input.locality,
        'gender': user_input.gender,
        'occupancy': user_input.occupancy,
        'available_for': user_input.available_for,
        # amenities
        'food_included': user_input.food_included,
        'wifi': user_input.wifi,
        'laundry': user_input.laundry,
        'room_ac': user_input.room_ac,
        'parking': user_input.parking,

        # model derived inputs
        'latitude': input_loc_ref['latitude'],
        'longitude': input_loc_ref['longitude'],
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

    pred = model.predict(input_df)
    predicted_rent = float(np.expm1(pred[0]))
    lower = predicted_rent - test_metric
    upper = predicted_rent + test_metric

    print(f'Expected Rent For: {user_input.occupancy} sharing Hostel/PGs in {user_input.locality} is: {round(predicted_rent)}')
    print(f'Actual Rent in {user_input.locality} for {user_input.occupancy} sharing rooms typically ranges from {round(lower)} to {round(upper)}')

    return OutputSchema(
        predicted_rent=round(predicted_rent, 2),
        lower=round(predicted_rent - test_metric, 2),
        upper=round(predicted_rent + test_metric, 2),
        locality=user_input.locality,
        occupancy=user_input.occupancy,
    )