import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split

# Constants
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / 'Data' / 'raw' / 'chennai_pg_dataset.csv'

TARGET = 'rent'
MIN_RENT = 1000
RENT_CAP = 15000
DEPOSIT_RENT_RATIO_CAP = 5

# Column Gropus
DROP_COLS = [
    "id", "title", "address", "total_bathrooms", "warden",
    "cooking_allowed", "gate_closing_time", "guardian_required",
    "nonveg_allowed", "smoking_allowed",
    "lunch", "breakfast", "dinner",
]

BOOL_COLS = [
    "attached_bathroom", "food_included", "mess", "wifi", "laundry",
    "power_backup", "refrigerator", "common_tv", "room_cleaning",
    "room_ac", "room_cupboard", "room_tv", "room_geyser",
    "room_bedding", "room_attached_bath",
]

OHE_COLS         = ["gender", "parking", "available_for"]
ORDINAL_COLS     = ["occupancy"]
TARGET_ENC_COLS  = ["locality"]
ORDINAL_CATS     = [["SINGLE", "DOUBLE", "THREE", "FOUR"]]

def load_and_clean(path: Path = DATA_PATH) -> pd.DataFrame:
    """Load raw data and perform dataset-level cleaning.
    Everything here happens before train/val/test split

    Args:
        path (Path, optional): Path of the Dataset file (CSV). Defaults to DATA_PATH.

    Returns:
        pd.DataFrame: It returns a DataFrame
    """

    # Dumped from my preprocessing notebook (refer dev or preprocessing branch)
    df = pd.read_csv(path)
    df.drop_duplicates(subset=['id', 'occupancy']) 
    df = df.drop(columns=DROP_COLS)
    df = df.dropna(subset=['rent', 'deposit', 'occupancy', 'attached_bathroom'])

    # SELF-NOTe
    # Modified the rent ratio cap for future proof, previous one (in noyebook) is remove the current dataset specific outliers,
    # this logic, eliminates the premium PG segements, so no more costly PGs
    df = df[df[TARGET] >= MIN_RENT]
    df = df[df[TARGET] <= RENT_CAP]
    df = df[df['deposit'] / df[TARGET] <= DEPOSIT_RENT_RATIO_CAP]

    df[BOOL_COLS] = df[BOOL_COLS].fillna(False).astype(bool)
    df['parking'] = df['parking'].fillna('No Parking')
    df['available_for'] = df['available_for'].replace('Both', 'Anyone')

    ## df["transit_score"] = df["transit_score"].replace(-10, np.nan)
    # New Logic for Future proof
    SCORE_MIN = 0.0
    SCORE_MAX = 10.0

    df['transit_score'] = df['transit_score'].where(
        df['transit_score'].between(SCORE_MIN, SCORE_MAX), other=np.nan
    )

    df['lifestyle_score'] = df['lifestyle_score'].where(
        df['lifestyle_score'].between(SCORE_MIN, SCORE_MAX), other=np.nan
    )

    # creating tag for msiing values rows
    df['transit_score_missing'] = df['transit_score'].isna().astype(int)
    df['lifestyle_score_missing'] = df['lifestyle_score'].isna().astype(int)

    return df

def split_data(df: pd.DataFrame):
    """
    Split into train / val / test.
    70% train, 15% val, 15% test.
    Stratified on occupancy to ensure all occupancy types
    are represented in each split.
    """

    # This logics also dumped from my notebook 9preprocessing.ipynb from preprocessing branch)

    X = df.drop(columns=TARGET)
    y = df[TARGET]

    # First spilt (Train = 70%, temp = 30%) here i use validation so, just used temp and then splt the temp -> val/test = 15% each
    X_train, X_temp, y_train, y_temp = train_test_split(
        X,
        y,
        test_size=0.30,
        random_state=42,
        stratify=X['occupancy'] # self note: Bug Fix (refer commit description)
    )

    # Second Split (temp = 30%, split it inro Validation/Train -> 15%)
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp,
        y_temp,
        test_size=0.50,
        random_state=42,
        stratify=X_temp['occupancy'] # self note: Bug Fix (refer commit description)
    )

    return X_train, X_val, X_test, y_train, y_val, y_test

