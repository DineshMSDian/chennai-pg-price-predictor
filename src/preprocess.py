import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.base import BaseEstimator, TransformerMixin

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

# Phase 1: Data Loading and Basic cleanups
def load_and_clean(path: Path = DATA_PATH) -> pd.DataFrame:
    """Load raw data and perform dataset-level cleaning.
    Everything here happens before train/val/test split

    Args:
        path (Path, optional): Path of the Dataset file (CSV). Defaults to DATA_PATH.

    Returns:
        pd.DataFrame: It returns a DataFrame
    """

    # Dumped from my preprocessing notebook (refer dev or preprocessing branch)

    # 1.1 Import the raw dataset
    df = pd.read_csv(path)

    # 1.2 Deduplication
    df.drop_duplicates(subset=['id', 'occupancy'])

    # 1.3 Drop columns
    df = df.drop(columns=DROP_COLS)

    # 1.4 Drop rows
    df = df.dropna(subset=['rent', 'deposit', 'occupancy', 'attached_bathroom'])
    # SELF-NOTe
    # Modified the rent ratio cap for future proof, previous one (in noyebook) is remove the current dataset specific outliers,
    # this logic, eliminates the premium PG segements, so no more costly PGs
    df = df[df[TARGET] >= MIN_RENT]
    df = df[df[TARGET] <= RENT_CAP]
    df = df[df['deposit'] / df[TARGET] <= DEPOSIT_RENT_RATIO_CAP]

    # 1.5 fix datatypes & renaming
    df[BOOL_COLS] = df[BOOL_COLS].fillna(False).astype(bool)
    df['parking'] = df['parking'].fillna('No Parking')
    df['available_for'] = df['available_for'].replace('Both', 'Anyone')

    # 1.6 fixes for before doing imputations
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

# Phase 2: Data Spliting (train/val/test)
def split_data(df: pd.DataFrame):
    """
    Split into train / val / test.
    70% train, 15% val, 15% test.
    Stratified on occupancy to ensure all occupancy types
    are represented in each split.
    """

    # This logics also dumped from my notebook 9preprocessing.ipynb from preprocessing branch)

    # 2.1 Target and feature
    X = df.drop(columns=TARGET)
    y = df[TARGET]

    # 2.2 Train/Validation/Test
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

# Phase 3: Imputations 
"""
in my notebook 3.1 is rent and deposit transformation, but here
3.1 Rent transformation
3.2 depsoit transformtion, cast bool dtypes and score imputation are all in one custom transformer
"""

# 3.1 Transform rent
def target_transformation(y_train, y_val, y_test):
    """
    Log-transform rent.
    Reduces right skew and makes XGBoost perform better
    on the rent distribution.
    Back-transform predictions with np.expm1().
    """

    return (
        np.log1p(y_train),
        np.log1p(y_val),
        np.log1p(y_test),
    )

# 3.2 (Deposit Tranformation); 3.2 (Cast bool -> int8) ; 3.3 score imputation
# Custom transformer
"""
Custom transformers are used to convert our notebook preprocessing steps into reusable sklearn-compatible steps that can be added to a Pipeline.
This keeps the preprocessing consistent and ensures learned transformations use training data only.
"""
class BasicFEatureTransformer(BaseEstimator, TransformerMixin):
    """
    This transformer contains transformations that don't need to learn anything from the training data.
    Because there's nothing to learn. It only performs 
    - log1p deposit
    - bool columns → int8
    so fit only returns self
    """

    # here fit returns self, because here nothing learns, it just perform 2 modifications only
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X = X.copy()
        X['deposit'] = np.log1p(X['deposit'])
        X['BOOL_COLS'] = X[BOOL_COLS].astype('int8')

        return X

class LocalityMedianImputer(BaseEstimator, TransformerMixin):
    """
    Impute transit_score and lifestyle_score using
    locality medians learned from training data only.
    Falls back to global train median if locality has no median.

    Must run BEFORE locality gets encoded to a number.
    """

    # here fit needed, because it learning (local and global median) information from the training data
    def fit(self, X, y=None):
        self.transit_medians_ = X.groupby('locality')['transit_score'].median()
        self.lifestyle_medians_ = X.gropuby('locality')['lifestyle_score'].median()
        self.transit_global_ = X['transit_score'].median()
        self.lifestyle_global_ = X['lifestyle_score'].medians()

    def transform(self, X):
        X = X.copy

        X['transit_score'] = (
            X['transit-score']
            .fillna(X['locality'].map(self.transit_medians_))
            .fillna(self.transit_global_)
        )

        X['lifestyle_score'] = (
            X['lifestyle_score']
            .fillna(X['locality'].map(self.lifestyle_medians_))
            .fillna(self.lifestyle_global_)
        )

        return X