from pathlib import Path

PROJECT_PATH = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_PATH / 'Data' / 'raw' / 'dataset.csv'

# preprocess.py

TARGET = 'rent'
MIN_RENT = 1000
MAX_RENT = 15000
DEPOSIT_RENT_RATIO_CAP = 5

DUP_SUBSET_COLS = ['id', 'occupancy']
DROP_COLS = ['id', 'title', 'address', 'total_bathrooms', 'warden', 'cooking_allowed', 'gate_closing_time', 'guardian_required', 'nonveg_allowed', 'smoking_allowed', 'lunch', 'breakfast', 'dinner']
DROP_ROWS_COLS = ['rent', 'deposit', 'occupancy', 'attached_bathroom']

BOOL_COLS = ['attached_bathroom', 'mess', 'wifi', 'laundry', 'power_backup',
        'refrigerator', 'common_tv', 'room_cleaning','room_ac', 
        'room_cupboard', 'room_tv', 'room_geyser', 'room_bedding',
        'room_attached_bath', 'food_included', 
]

NUM_COLS = ['latitude', 'longitude', 'transit_score', 'lifestyle_score', 'deposit']

SCORE_MIN = 0.0
SCORE_MAX = 10.0

ORDINAL_COL = ['occupancy']
ORDINAL_CAT = [['SINGLE', 'DOUBLE', 'THREE', 'FOUR']]
OHE_COL = ['gender', 'parking', 'available_for']
TARGET_ENC_COL = ['locality']

# train.py

MODELS_DIR = PROJECT_PATH / 'models'

NUM_REFRENCE_COL = ['latitude', 'longitude', 'transit_score', 'lifestyle_score', 'deposit']
BINARY_REFERENCE_COL = ['attached_bathroom', 'mess', 'power_backup', 'refrigerator', 'common_tv', 'room_cleaning', 'room_cupboard', 'room_tv', 'room_geyser', 'room_bedding', 'room_attached_bath']

# predict.py

FINAL_PIPELINE = MODELS_DIR / 'full_pipeline.pkl'
LOCALITY_REFERENCE = MODELS_DIR / 'locality_reference.pkl'
FINAL_METRICS = MODELS_DIR / 'metrics.json'