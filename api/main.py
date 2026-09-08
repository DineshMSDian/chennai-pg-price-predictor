from fastapi import FastAPI
from pydantic import BaseModel
import joblib

# initialize the API
app = FastAPI()

# Input validation using pydantic
class InputFeatures(BaseModel):

    # user inputs
    locality: str
    occupancy: str
    gender: str
    available_for: str
    parking: str
    food_included: bool
    wifi: bool
    room_ac: bool
    laundry: bool

    # optional user inputs (have defaults)
    attached_bathroom: bool
    mess: bool
    power_backup: bool
    refrigerator: bool
    common_tv: bool
    room_cleaning: bool
    room_cupboard: bool
    room_tv: bool
    room_geyser: bool
    room_bedding: bool
    room_attached_bath: bool

    # defaults