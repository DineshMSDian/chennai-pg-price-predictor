from typing import Any

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import OrdinalEncoder, OneHotEncoder, TargetEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

from pathlib import Path
from configs import (
    DATA_PATH,
    DUP_SUBSET_COLS, DROP_COLS, DROP_ROWS_COLS,
    TARGET, MIN_RENT, MAX_RENT, DEPOSIT_RENT_RATIO_CAP,
    BOOL_COLS, NUM_COLS,
    SCORE_MIN, SCORE_MAX,
    ORDINAL_COL, OHE_COL, TARGET_ENC_COL, 
    ORDINAL_CAT,
)
def load_and_clean(dataset: Path = DATA_PATH) -> pd.DataFrame:

    df = pd.read_csv(DATA_PATH)
    df = df.drop_duplicates(subset=DUP_SUBSET_COLS)
    df = df.drop(columns=DROP_COLS)
    df = df.dropna(subset=DROP_ROWS_COLS)

    df = df[df[TARGET] >= MIN_RENT] 
    df = df[df[TARGET] <= MAX_RENT] 
    df = df[df['deposit'] / df[TARGET] <= DEPOSIT_RENT_RATIO_CAP]

    df[BOOL_COLS] = df[BOOL_COLS].fillna(False).astype(bool)
    df['parking'] = df['parking'].fillna('No Parking')
    df['available_for'] = df['available_for'].replace('Both', 'Anyone')

    df['transit_score'] = df['transit_score'].where(
        df['transit_score'].between(SCORE_MIN, SCORE_MAX), other=np.nan
    )
    df['lifestyle_score'] = df['lifestyle_score'].where(
        df['lifestyle_score'].between(SCORE_MIN, SCORE_MAX), other=np.nan
    )

    # df['transit_score_missing'] = df['transit_score'].isna().astype(int)
    # df['lifestyle_score_missing'] = df['lifestyle_score'].isna().astype(int)
    
    return df

def split_data(df: pd.DataFrame):

    X = df.drop(columns=TARGET)
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

    return (X_train, X_val, X_test, y_train, y_val, y_test)

def transform_target(y_train, y_val, y_test):

    return(
        np.log1p(y_train),
        np.log1p(y_val),
        np.log1p(y_test)
    )

class BasicFeatureTransformation(BaseEstimator, TransformerMixin):

    # this class act as an sklearn compatible custom transformer for my custom imputation strategy
    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        X = X.copy()

        X['deposit'] = np.log1p(X['deposit'])
        X[BOOL_COLS] = X[BOOL_COLS].astype('int8')

        return X
 
class LocalMedianImputation(BaseEstimator, TransformerMixin):

    # this class act as an sklearn compatible custom transformer for my custom imputation strategy
    def fit(self, X, y=None):
        self.transit_local_median_ = X.groupby('locality')['transit_score'].median()
        self.lifestyle_local_median_ = X.groupby('locality')['lifestyle_score'].median()
        self.transit_global_median_ = X['transit_score'].median()
        self.lifestyle_global_median_ = X['lifestyle_score'].median()

        return self

    def transform(self, X, y=None):
        X = X.copy()

        X['transit_score'] = (
            X['transit_score']
            .fillna(X['locality'].map(self.transit_local_median_))
            .fillna(self.transit_global_median_)
        )

        X['lifestyle_score'] = (
            X['lifestyle_score']
            .fillna(X['locality'].map(self.lifestyle_local_median_))
            .fillna(self.lifestyle_global_median_)
        )

        return X

def transformer_pipeline() -> ColumnTransformer:

    # starting the pipeline with encodings
    ordinal_pipeline = Pipeline([
        ('encoder', OrdinalEncoder(categories=ORDINAL_CAT, handle_unknown='use_encoded_value', unknown_value=-1))
    ])

    ohe_pipeline = Pipeline([
        ('encoder', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])

    target_enc_pipeline = Pipeline([
        ('encoder', TargetEncoder(target_type='continuous'))
    ])

    # defining columns for their transformation
    full_pipeline = ColumnTransformer([
        ('numerical', 'passthrough', NUM_COLS),
        ('bool', 'passthrough', BOOL_COLS),
        ('ordinal_col', ordinal_pipeline, ORDINAL_COL),
        ('ohe_col', ohe_pipeline, OHE_COL),
        ('target_enc_col', target_enc_pipeline, TARGET_ENC_COL)
    ],
        remainder='drop',
        n_jobs=-1,
    )

    return full_pipeline

def preprocess(dataset: Path = DATA_PATH):

    df = load_and_clean()
    X_train, X_val, X_test, y_train, y_val, y_test = split_data(df)
    y_train_log, y_val_log, y_test_log = transform_target(y_train, y_val, y_test)

    preprocessor = Pipeline([
        ('basic_imputation', BasicFeatureTransformation()),
        ('score_imputation', LocalMedianImputation()),
        ('column_transformation', transformer_pipeline()),
    ])

    return (
        X_train, X_val, X_test, y_train_log, y_val_log, y_test_log, preprocessor
    )
    
if __name__ == '__main__':
    df = load_and_clean()
    print(df.shape)

    X_train, X_val, X_test, y_train_log, y_val_log, y_test_log, preprocessor = preprocess()
    X_train_processed = preprocessor.fit_transform(X_train, y_train_log)
    X_val_processed = preprocessor.transform(X_val)
    X_test_processed = preprocessor.transform(X_test)

    print(f'X_train shape: {X_train_processed.shape}')
    print(f'X_val shape: {X_val_processed.shape}')
    print(f'X_test shape: {X_test_processed.shape}')
    print(f"Features after encoding: {X_train_processed.shape[1]}")
    print("Preprocessing complete.")