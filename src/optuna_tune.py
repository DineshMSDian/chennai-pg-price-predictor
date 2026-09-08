import optuna
import mlflow

import numpy as np
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from xgboost import XGBRegressor
from preprocess import preprocess

mlflow.set_tracking_uri('http://localhost:5000')
mlflow.set_experiment('XGB-optuna-trials')

def evaluate(y_true, y_pred):

    log_mae = mean_absolute_error(y_true, y_pred)
    log_rmse = root_mean_squared_error(y_true, y_pred)
    log_r2 = r2_score(y_true, y_pred)

    actual_y_true = np.expm1(y_true)
    actual_y_pred = np.expm1(y_pred)

    actual_mae = mean_absolute_error(actual_y_true, actual_y_pred)
    actual_rmse = root_mean_squared_error(actual_y_true, actual_y_pred)
    actual_r2 = r2_score(actual_y_true, actual_y_pred)

    return {
        'log_mae': log_mae,
        'log_rmse': log_rmse,
        'log_r2': log_r2,

        'actual_mae': actual_mae,
        'actual_rmse': actual_rmse,
        'actual_r2': actual_r2,
    }

def objective(trial: optuna.Trial, X_train, X_val, y_train, y_val):
    params = {
        'n_estimators': trial.suggest_int('n_estimators', 200, 500),
        'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.1, log=True),
        'max_depth': trial.suggest_int('max_depth', 3, 8),
        'subsample': trial.suggest_float('subsample', 0.5, 1.0),
        'colsample_bytree': trial.suggest_float('colsample_bytree', 0.5, 1.0),
        'reg_alpha': trial.suggest_float('reg_alpha', 1e-8, 10.0, log=True),
        'reg_lambda': trial.suggest_float('reg_lambda', 1e-8, 10.0, log=True),
    }

    with mlflow.start_run(nested=True, run_name=f'trail_{trial.number}') as child_run:
        mlflow.log_params(params)

        model = XGBRegressor(random_state=42, n_jobs=-1, **params)
        model.fit(X_train, y_train)
        prediction = model.predict(X_val)

        metrics = evaluate(y_val, prediction)

        mlflow.log_metrics((metrics))

    return metrics['actual_mae']

def run_tuning(X_train, X_val, y_train, y_val, n_trials = 50):

    with mlflow.start_run(run_name='xgb-optuna-trail') as parent_run:    
        study = optuna.create_study(direction='minimize')
        study.optimize(
            lambda trial: objective(trial, X_train, X_val, y_train, y_val),
            n_trials=n_trials
        )

        best_params = study.best_trial.params
        best_score = study.best_trial.value
        assert best_score is not None # fixes mlflow exception that best-score as None, optuna defauls it float | None

        mlflow.log_params(best_params)
        mlflow.log_metric('best_mae', round(best_score), 4)

        print(f'\nBest Trial is: {study.best_trial}')
        print(f"\nBest MAE: {best_score:.4f}")
        print(f"\nBest Params: {best_params}")

    return best_params

if __name__ == '__main__':
    from preprocess import preprocess

    X_train, X_val, X_test, y_train, y_val, y_test, preprocessor = preprocess()

    X_train_processed = preprocessor.fit_transform(X_train, y_train)
    X_val_processed = preprocessor.transform(X_val)
    best = run_tuning(X_train_processed, X_val_processed, y_train, y_val, 100)