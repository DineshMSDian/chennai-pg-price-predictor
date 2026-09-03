from pathlib import Path

PROJECT_PATH = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_PATH / 'Data' / 'raw' / 'dataset.csv'

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
        'room_attached_bath',
]

SCORE_MIN = 0.0
SCORE_MAX = 10.0

ORDINAL_COL = ['occupancy']
ORDINAL_CAT = [['SINGLE', 'DOUBLE', 'THREE', 'FOUR']]
OHE_COL = ['gender', 'parking', 'available_for']
TARGET_ENC_COL = ['locality']

# train.py

MODELS_DIR = PROJECT_PATH / 'models'

BEST_PARAMS = {
    'colsample_bytree': 0.8,
    'learning_rate': 0.1,
    'max_depth': 4,
    'n_estimators': 300,
    'reg_alpha': 0,
    'reg_lambda': 1,
    'subsample': 0.8,
    'random_state': 42,
    'objective': 'reg:squarederror',
}