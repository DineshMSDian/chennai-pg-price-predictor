import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from pathlib import Path

from configs import (
    DATA_PATH, DUP_SUBSET_COLS, DROP_COLS, DROP_ROWS_COLS,
    TARGET, MIN_RENT, MAX_RENT, DEPOSIT_RENT_RATIO_CAP,
    BOOL_COLS, 
    SCORE_MIN, SCORE_MAX,
)

# porting my preprocessing.ipynb into reproducable preprocessing (pipeline)script

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
    ----------
    dataset : Path, default=DATA_PATH
        Path to the raw CSV dataset.

    Returns
    -------
    pd.DataFrame
        Cleaned dataframe ready for preprocessing.
    """

    # import raw dataset
    df = pd.read_csv(dataset)
    print(df.shape)

    # deduplication
    df = df.drop_duplicates(subset=DUP_SUBSET_COLS)
    print(df.shape)

    # Drop col
    df = df.drop(columns=DROP_COLS)
    print(df.shape)

    # Keep rent values within the expected range.
    df = df.dropna(subset=DROP_ROWS_COLS)
    df = df[df[TARGET] >= MIN_RENT] # ignores pgs rent lsited below 1000
    df = df[df[TARGET] <= MAX_RENT] # ignores pgs rent lsited above 1500
    df = df[df['deposit'] / df[TARGET] <= DEPOSIT_RENT_RATIO_CAP] # handles outlier

    # datatype and renaming
    df[BOOL_COLS] = df[BOOL_COLS].fillna(False).astype(bool)
    df['parking'] = df['parking'].fillna('No Parking')
    df['available_for'] = df['available_for'].replace('Both', 'Anyone')

    # Handle invalid score values
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

def split_dataset(df: pd.DataFrame):
    X = df.drop(columns = TARGET)
    y = df[TARGET]

    # 2.2 Train/Validation/Test

    # First spilt (Train = 70%, temp = 30%) here i use validation so, just used temp and then splt the temp -> val/test = 15% each
    X_train, X_temp, y_train, y_temp = train_test_split(
        X,
        y,
        test_size=0.30,
        random_state=42,
        stratify=X['occupancy'] 
    )

    # Second Split (temp = 30%, split it inro Validation/Train -> 15%)
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp,
        y_temp,
        test_size=0.50,
        random_state=42,
        stratify=X_temp['occupancy'] 
    )

    return X_train, X_val, X_test, y_train, y_val, y_test