import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import OrdinalEncoder, OneHotEncoder, TargetEncoder
from sklearn.compose import ColumnTransformer
from pathlib import Path

from configs import (
    DATA_PATH, DUP_SUBSET_COLS, DROP_COLS, DROP_ROWS_COLS,
    TARGET, MIN_RENT, MAX_RENT, DEPOSIT_RENT_RATIO_CAP,
    BOOL_COLS, 
    SCORE_MIN, SCORE_MAX,
    ORDINAL_COL, ORDINAL_CAT, OHE_COL, TARGET_ENC_COL
)

# porting my preprocessing.ipynb into reproducable preprocessing (pipeline)script

# 1 Data loading and basic cleanups
def load_and_clean(dataset: Path = DATA_PATH) -> pd.DataFrame:

    """
    Load the raw dataset and perform initial data cleaning.

    Cleaning steps:
    1. Load the dataset.
    2. Remove duplicate listings.
    3. Drop unnecessary columns.
    4. Remove rows with missing required values.
    5. Filter invalid target values and extreme deposit-to-rent ratios.
    6. Normalize boolean and categorical values.
    7. Replace invalid score values with NaN.
    8. Create missing-value indicator features for score columns.

    Parameters
    dataset : Path, default=DATA_PATH
        Path to the raw CSV dataset.

    Returns
    pd.DataFrame
        Cleaned dataframe ready for preprocessing.
    """

    df = pd.read_csv(dataset)
    print(df.shape)

    df = df.drop_duplicates(subset=DUP_SUBSET_COLS)
    print(df.shape)

    df = df.drop(columns=DROP_COLS)
    print(df.shape)

    df = df.dropna(subset=DROP_ROWS_COLS)
    df = df[df[TARGET] >= MIN_RENT] # ignores pgs rent lsited below 1000
    df = df[df[TARGET] <= MAX_RENT] # ignores pgs rent lsited above 1500
    df = df[df['deposit'] / df[TARGET] <= DEPOSIT_RENT_RATIO_CAP] # handles outlier

    df[BOOL_COLS] = df[BOOL_COLS].fillna(False).astype(bool)
    df['parking'] = df['parking'].fillna('No Parking')
    df['available_for'] = df['available_for'].replace('Both', 'Anyone')

    df['transit_score'] = df['transit_score'].where(
        df['transit_score'].between(SCORE_MIN, SCORE_MAX), other=np.nan
    )

    df['lifestyle_score'] = df['lifestyle_score'].where(
        df['lifestyle_score'].between(SCORE_MIN, SCORE_MAX), other=np.nan
    )

    df['transit_score_missing'] = df['transit_score'].isna().astype(int)
    df['lifestyle_score_missing'] = df['lifestyle_score'].isna().astype(int)

    return df

# 2 split the data
def split_dataset(df: pd.DataFrame):
    """
    1. seperate target and features
    2. Train/Validation/Test
        2.1 First spilt (Train = 70%, temp = 30%) here i use validation so, just used temp and then splt the temp -> val/test = 15% each
        2.2 Second Split (temp = 30%, split it inro Validation/Train -> 15%)
    """

    X = df.drop(columns = TARGET)
    y = df[TARGET]
 
    X_train, X_temp, y_train, y_temp = train_test_split(
        X,
        y,
        test_size=0.30,
        random_state=42,
        stratify=X['occupancy'] 
    )

    X_val, X_test, y_val, y_test = train_test_split(
        X_temp,
        y_temp,
        test_size=0.50,
        random_state=42,
        stratify=X_temp['occupancy'] 
    )

    return X_train, X_val, X_test, y_train, y_val, y_test

# 3 imputations
def target_transformation(y_train, y_val, y_test):

    """
    returns the log1p transfromed target
    """
    
    return (
        np.log1p(y_train), np.log1p(y_val), np.log1p(y_test)
    )

# 3.1.2 custom imputations, custom transformers
"""
Custom transformers are used because the project contains custom preprocessing
logic that is not directly available in standard sklearn transformers:

- Log transform deposit using np.log1p().
- Convert boolean columns to int8.
- Impute score features using locality wise medians with a global median fallback.

These custom transformations are wrapped as sklearn compatible transformers so
they can be integrated into the Pipeline and applied consistently without data leakage.
"""

class BasicFeatureTransformer(BaseEstimator, TransformerMixin):

    """
    This transformer contains transformations that don't need to learn anything from the training data.
    Because there's nothing to learn. It only performs 
    - log1p deposit
    - bool columns -> int8
    so fit only returns self
    """

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X = X.copy()
        X['deposit'] = np.log1p(X['deposit'])
        X[BOOL_COLS] = X[BOOL_COLS].astype('int8')

        return X

class LocalityMedianImputer(BaseEstimator, TransformerMixin):
    """
    Impute transit_score and lifestyle_score using
    locality medians learned from training data only.
    Falls back to global train median if locality has no median.

    Must run BEFORE locality gets encoded to a number.
    """

    def fit(self, X, y=None):
        self.transit_medians_ = X.groupby('locality')['transit_score'].median()
        self.lifestyle_medians_ = X.groupby('locality')['lifestyle_score'].median()
        self.transit_global_ = X['transit_score'].median()
        self.lifestyle_global_ = X['lifestyle_score'].median()

        return self

    def transform(self, X):
        X = X.copy()

        X['transit_score'] = (
            X['transit_score']
            .fillna(X['locality'].map(self.transit_medians_))
            .fillna(self.transit_global_)
        )

        X['lifestyle_score'] = (
            X['lifestyle_score']
            .fillna(X['locality'].map(self.lifestyle_medians_))
            .fillna(self.lifestyle_global_)
        )

        return X

def build_preprocessor(numerical_features: list[str]) -> Pipeline:

    """
    Assembles the full preprocessing pipeline.
    
        Order matters:
        1. BasicFeatureTransformer  — log deposit, bool -> int8
        2. LocalityMedianImputer    — impute scores using locality string
        3. ColumnTransformer        — encode all columns
                                      (locality string -> float happens here
    """

    # inner pipeline (occupancy, categorical, locality)
    """
    This controls:
    What happens to this particular group of columns?
    """

    occupancy_pipeline = Pipeline(steps=[
        ('encoder', OrdinalEncoder(
            categories = ORDINAL_CAT,
            handle_unknown = 'use_encoded_value',
            unknown_value = -1,
        )),
    ])

    ohe_pipeline = Pipeline(steps=[
        ('encoder', OneHotEncoder(
            handle_unknown='ignore',
            sparse_output=False,
        ))
    ])

    locality_pipeline = Pipeline(steps=[
        ('encoder', TargetEncoder(
            target_type='continuous',
        ))
    ])

    # Coulumn transformer
    """
    This controls:
    Which columns go into which pipeline?
    """

    column_transformer = ColumnTransformer(
        transformers=[
            ('numerical', numerical_features, 'passthrough'),
            ('occupancy', occupancy_pipeline, ORDINAL_COL),
            ('ohe_col', ohe_pipeline, OHE_COL),
            ('locality', locality_pipeline, TARGET_ENC_COL)
        ]
    )

    # Outer pipeline
    """
    This controls:
    What happens first, second, third?
    """

    preprocessor = Pipeline([
        ('basic_feature', BasicFeatureTransformer),
        ('locality_imputation', LocalityMedianImputer),
        ('column_transformer', column_transformer),
    ])

    return preprocessor