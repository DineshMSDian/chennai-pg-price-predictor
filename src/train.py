import pandas as pd
import joblib
import json

from xgboost import XGBRegressor

from sklearn.pipeline import Pipeline
from preprocess import preprocess
from optuna_tune import run_tuning, evaluate

from configs import (
    MODELS_DIR,
    NUM_REFRENCE_COL, BINARY_REFERENCE_COL
)

def run_optuna(X_train, X_val, y_train, y_val, preprocessor):

    X_train_processed = preprocessor.fit_transform(X_train, y_train)
    X_val_processed = preprocessor.transform(X_val)

    _best_params = run_tuning(X_train_processed, X_val_processed, y_train, y_val, 100)

    return _best_params

def train():

    # initializeing preprocessing
    X_train, X_val, X_test, y_train, y_val, y_test, preprocessor = preprocess()

    # here i send the old train/val sets to optuna, it returns the best_params, 
    final_params = run_optuna(X_train, X_val, y_train, y_val, preprocessor)

    # and after getting best_params, i combine my train/val to retrain the model with the best pramas optuna returns
    # so for tuning 70% train, 15& val, for retrain with best params 85% train_val (for retrain) and 15% to test
    X_train_val = pd.concat([X_train, X_val], axis=0, ignore_index=True)
    y_train_val = pd.concat([y_train, y_val], axis=0, ignore_index=True)

    X_train_val_processed = preprocessor.fit_transform(X_train_val, y_train_val)
    X_test_processed = preprocessor.transform(X_test)

    # retrain the model with combined dataset
    final_model = XGBRegressor(random_state=42, n_jobs=-1, **final_params)
    final_model.fit(X_train_val_processed, y_train_val)

    prediction = final_model.predict(X_test_processed)
    final_metrics = evaluate(y_test, prediction)

    print(f'final test results...')
    print(f'\ntest MAE: {final_metrics['actual_mae']}')
    print(f'test RMSE: {final_metrics['actual_rmse']}')
    print(f'test r2 Score: {final_metrics['actual_r2']}')

    return final_model, preprocessor, final_metrics, X_train_val

def save_artifacts(model, preprocessor, metrics, X_train: pd.DataFrame):

    # save model + preprocess as an sinlge pkl file
    full_pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('final_modle', model)
    ])
    joblib.dump(full_pipeline, MODELS_DIR / 'full_pipeline.pkl')
    print(f'Final Pipeline saved!')

    # save metrics
    final_metrics = {
        'test_mae': metrics['actual_mae'],
        'test_rmse': metrics['actual_rmse'],
        'test_r2': metrics['actual_r2'],
    }

    with open(MODELS_DIR / 'metrics.json', 'w') as f:
        json.dump(final_metrics, f, indent=2)
    print(f'Final Test Metrics saved!')

    # saving locality references for inputs
    locality_reference_num_features = X_train.groupby('locality')[NUM_REFRENCE_COL].median()
    locality_reference_binary_features = X_train.groupby('locality')[BINARY_REFERENCE_COL].agg(lambda X: X.mode().iloc[0])

    locality_reference = pd.concat([locality_reference_num_features, locality_reference_binary_features], axis=1)

    joblib.dump(locality_reference, MODELS_DIR / 'locality_reference.pkl')
    print(f'Locality reference!')


if __name__ == '__main__':

    model, preprocessor, metrics, X_train = train()
    save_artifacts(model, preprocessor, metrics, X_train)