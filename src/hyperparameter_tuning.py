import optuna
import mlflow

import numpy as np
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score

from dotenv import load_dotenv

load_dotenv()
mlflow.set_tracking_uri('http://localhost:5000')
mlflow.set_experiment('XGB-optuna-trials')
def eval(y_val, y_pred):
    
    log_mae = mean_absolute_error(y_val, y_pred)
    log_rmse = root_mean_squared_error(y_val, y_pred)
    log_r2 = r2_score(y_val, y_pred)
    actual_y_val = np.expm1(y_val)
    actual_y_pred = np.expm1(y_pred)

    actual_mae = mean_absolute_error(actual_y_pred, y_pred)
    actual_rmse = root_mean_squared_error(actual_y_val, actual_y_pred) 
    actual_r2 = r2_score(actual_y_val, actual_y_pred)
    

    return {
        'log_mae': log_mae,
        'log_rmse': log_rmse,
        'log_r2_score': log_r2,
        'actual_mae': actual_mae,
        'actual_rmse': actual_rmse,
        'actual_r2_score': actual_r2,
    }

def objective(trial, X_train, X_val, y_train, y_val):
    params = {
        'n_estimators': trial.suggest_int('n_estimators', 200, 500),
        'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.1),
        'max_depth': trial.suggest_int('max_depth', 3, 8),
        'subsample': trial.suggest_float('subsample', 0.1, 1.0),
        'colsample_bytree': trial.suggest_float('colsample_bytree',0.1, 1.0),
        'reg_alpha': trial.suggest_float('reg_alpha',1e-8, 1.0, log=True),
        'reg_lambda': trial.suggest_float('reg_lambda',1e-3, 10.0, log=True),
    }

    with mlflow.start_run(nested=True, run_name=f'trail_{trial.number}') as child_run:

        model = XGBRegressor(random_state=42, n_jobs=-1, **params)
        model.fit(X_train, y_train)
        metrics = eval(y_val, model.predict(X_val))

        mlflow.log_params(params)
        mlflow.log_metrics({'log_mae': metrics['log_mae'], 'log_rmse': metrics['log_rmse'], 'log_r2': metrics['log_r2_score'], 'actual_mae': metrics['actual_mae'], 'actual_rmse': metrics['actual_rmse'], 'actual_r2': metrics['actual_r2_score']})

        trial.set_user_attr('run_id', child_run.info.run_id)

        return metrics['actual_mae']

def tune(X_train, X_val, y_train, y_val):
    with mlflow.start_run(run_name='Study'):
        n_trails = 1000
        mlflow.log_param('n_trails', n_trails)

        study = optuna.create_study(direction='minimize', sampler=)
        study.optimize(lambda trial: objective(trial, X_train, X_val, y_train, y_val), n_trials=n_trails)

        mlflow.log_metric('Best Validation MAE Score', study.best_value)
        mlflow.log_params({
            f"best_{key}": value
            for key, value in study.best_params.items()
        })

        if best_run_id := study.best_trial.user_attrs.get('run_id'):
            mlflow.log_param('best_child_run_id', best_run_id)

        return study


if __name__ == '__main__':
    from preprocess import preprocess

    X_train, X_val, X_test, y_train, y_val, y_test, preprocessor = preprocess()

    X_train_processsed = preprocessor.fit_transform(X_train, y_train)
    X_val_processed = preprocessor.transform(X_val)
    X_test_processsed = preprocessor.transform(X_test)

    study = tune(X_train_processsed, X_val_processed, y_train, y_val)

    print(f'Best_params: {study.best_params}')
    print(f'\nBest Score: {study.best_value}')
    