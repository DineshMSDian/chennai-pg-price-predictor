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

    """
    1. this func() will called by train()
    2. and getting the X_train, X_val, y_train, y_val and preprocessor
    3. using preprocessor it preprocess the train and val datas, used for optuna_tuning.run_tune()
    4. then it calls the run_tune from optuna_tune.py and send the processed train and val datasets
    5. then it will return the best_params to train()
    """

    X_train_processed = preprocessor.fit_transform(X_train, y_train)
    X_val_processed = preprocessor.transform(X_val)

    best_params = run_tuning(X_train_processed, X_val_processed, y_train, y_val, 100)

    return best_params

def save_artifacts(model, preprocessor, metrics, X_train: pd.DataFrame):

    """
    1. save model + preprocess as an sinlge pkl file
    2. save metrics
    3. saving locality references for inputs
    """

    full_pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('final_modle', model)
    ])
    joblib.dump(full_pipeline, MODELS_DIR / 'full_pipeline.pkl')
    print(f'Final Pipeline saved!')

    final_metrics = {
        'test_mae': metrics['actual_mae'],
        'test_rmse': metrics['actual_rmse'],
        'test_r2': metrics['actual_r2'],
    }

    with open(MODELS_DIR / 'metrics.json', 'w') as f:
        json.dump(final_metrics, f, indent=2)
    print(f'Final Test Metrics saved!')

    locality_reference_num_features = X_train.groupby('locality')[NUM_REFRENCE_COL].median()
    locality_reference_binary_features = X_train.groupby('locality')[BINARY_REFERENCE_COL].agg(lambda X: X.mode().iloc[0])

    locality_reference = pd.concat([locality_reference_num_features, locality_reference_binary_features], axis=1)

    joblib.dump(locality_reference, MODELS_DIR / 'locality_reference.pkl')
    print(f'Locality reference!')

def train():

    """ main() function
    1. initializeing preprocessing
    2. here i send the old train/val sets to run_optuna(), that calls the run_tuning from optuna_tune.py and returns the best_params
    3. and after getting best_params, i combine my old train/val into new train_val (combined) to retrain the model with the new test_val datast with best_pramas that optuna returns, 
        so for hyper-parameter-tuning 70% train, 15& val, for retraing the model with new train dataset with best_params, i combined the old test and val inro single test_val 85% for traing and testing with already existing test 15% dataset
    4. retrain the model with combined dataset
    5. Make prediction and evaluate the performance of the newly trained model with best_params tested on untouched test_set
    6. calls the save_artifact() and sends the final_model, preprocessor, final_metrics and newly created X_train_val train set for extracting locality reference from on it
    """

    X_train, X_val, X_test, y_train, y_val, y_test, preprocessor = preprocess()
    final_params = run_optuna(X_train, X_val, y_train, y_val, preprocessor)

    X_train_val = pd.concat([X_train, X_val], axis=0, ignore_index=True)
    y_train_val = pd.concat([y_train, y_val], axis=0, ignore_index=True)

    X_train_val_processed = preprocessor.fit_transform(X_train_val, y_train_val)
    X_test_processed = preprocessor.transform(X_test)

    final_model = XGBRegressor(random_state=42, n_jobs=-1, **final_params)
    final_model.fit(X_train_val_processed, y_train_val)

    prediction = final_model.predict(X_test_processed)
    final_metrics = evaluate(y_test, prediction)

    print(f'final test results...')
    print(f'\ntest MAE: {final_metrics['actual_mae']}')
    print(f'test RMSE: {final_metrics['actual_rmse']}')
    print(f'test r2 Score: {final_metrics['actual_r2']}')

    save_artifacts(final_model, preprocessor, final_metrics, X_train_val)

    return f'Training process Completed and the results are presented! :)'


if __name__ == '__main__':
    train()