from pathlib import Path
import joblib
import numpy as np
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error
from sklearn.pipeline import Pipeline
from xgboost import XGBRegressor

from preprocess import preprocess
from configs import(
    DATA_PATH, MODELS_DIR, 
    BEST_PARAMS,
)

def evaluate(name: str, model, X, y_true_log):
    """
    evaluate model performance on a split, metrics reported in both log and actual rupee
    """

    y_pred_log = model.predict(X)

    # log metrics
    log_r2 = r2_score(y_true_log, y_pred_log)
    log_mae = mean_absolute_error(y_true_log, y_pred_log)
    log_rmse = root_mean_squared_error(y_true_log, y_pred_log)

    # actual metrics
    y_pred_actual = np.expm1(y_pred_log)
    y_true_actual = np.expm1(y_true_log)

    actual_mae  = mean_absolute_error(y_true_actual, y_pred_actual)
    actual_rmse = root_mean_squared_error(y_true_actual, y_pred_actual)

    print(f"\n{name} Results")
    print(f"  R²        {log_r2:.4f}")
    print(f"  Log MAE   {log_mae:.4f}")
    print(f"  Log RMSE  {log_rmse:.4f}")
    print(f"  MAE       ₹{actual_mae:,.2f}")
    print(f"  RMSE      ₹{actual_rmse:,.2f}")

    return {
        "r2"          : log_r2,
        "log_mae"     : log_mae,
        "log_rmse"    : log_rmse,
        "actual_mae"  : actual_mae,
        "actual_rmse" : actual_rmse,
    }

def train():
    # preprocessing
    print('Preprocessing started!!')

    X_train, X_val, X_test, y_train, y_val, y_test, preprocessor = preprocess()

    # fit on train

    X_train_processed = preprocessor.fit_transform(X_train, y_train)
    X_val_processed = preprocessor.transform(X_val)
    X_test_processed = preprocessor.transform(X_test)

    # building model with best params
    print(f'Training model (XGboost)')
    model = XGBRegressor(**BEST_PARAMS)
    model.fit(X_train_processed, y_train)

    # evaluate on train/val/test
    train_metrics = evaluate('Train', model, X_train_processed, y_train)
    val_metrics = evaluate('Validation', model, X_val_processed, y_val)
    test_metrics = evaluate('Test', model, X_test_processed, y_test)

    # same logic as in the notebook check_fitting()
    gap = train_metrics["r2"] - val_metrics["r2"]
    print(f"\nTrain/Val gap  {gap:.4f}")
    if gap > 0.15:
        print("  WARNING: possible overfitting")
    else:
        print("  OK: gap within acceptable range")

    full_pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('model', model)
    ])

    return full_pipeline, val_metrics, test_metrics

def save_pipeline(pipeline):
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    path = MODELS_DIR / 'xgb_pipeline.pkl'
    joblib.dump(pipeline, path)
    print(f'\nPipeline Saved to {path}')

if __name__ == '__main__':
    pipeline, val_metrics, test_metrics  = train()
    save_pipeline(pipeline)

    print('\nFinal val  R2_score  ', round(val_metrics['r2'], 4))
    print('Final test R2_score  ', round(test_metrics['r2'], 4))
    print('\nDone.')