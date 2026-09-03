import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline

from configs import (
    DATA_PATH, DUP_SUBSET_COLS, DROP_COLS, DROP_ROWS_COLS,
    TARGET, MIN_RENT, MAX_RENT, DEPOSIT_RENT_RATIO_CAP,
    BOOL_COLS, 
    SCORE_MIN, SCORE_MAX,
)

# porting my preprocessing.ipynb into reproducable preprocessing (pipeline)script

# 1.1 import raw dataset
# notebook: df = pd.read_csv(r'D:\Hustle\Chennai-PG\Data\raw\chennai_pg_dataset.csv')
# but now i need to change this hardcoded path to pick dynamically

df = pd.read_csv(DATA_PATH)
print(df.shape)

# 1.2 deduplication
df = df.drop_duplicates(subset=DUP_SUBSET_COLS)
print(df.shape)

# 1.3 Drop col
df = df.drop(columns=DROP_COLS)
print(df.shape)

# 1.4 Drop rows and hanlde outlier
df = df.dropna(subset=DROP_ROWS_COLS)
df = df[df[TARGET] >= MIN_RENT] # ignores pgs rent lsited below 1000
df = df[df[TARGET] <= MAX_RENT] # ignores pgs rent lsited above 1500
df = df[df['deposit'] / df[TARGET] <= DEPOSIT_RENT_RATIO_CAP] # handles outlier

# 1.5 datatype and renaming
df[BOOL_COLS] = df[BOOL_COLS].fillna(False).astype(bool)
df['parking'] = df['parking'].fillna('No Parking')
df['available_for'] = df['available_for'].replace('Both', 'Anyone')

# 1.6 fixes for before doing imputations

## df["transit_score"] = df["transit_score"].replace(-10, np.nan)
# New Logic for Future proof

df['transit_score'] = df['transit_score'].where(
    df['transit_score'].between(SCORE_MIN, SCORE_MAX), other=np.nan
)

df['lifestyle_score'] = df['lifestyle_score'].where(
    df['lifestyle_score'].between(SCORE_MIN, SCORE_MAX), other=np.nan
)

# creating tag for msiing values rows
df['transit_score_missing'] = df['transit_score'].isna().astype(int)
df['lifestyle_score_missing'] = df['lifestyle_score'].isna().astype(int)
print(df.shape)