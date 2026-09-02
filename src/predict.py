from pathlib import Path
import numpy as np
import pandas as pd
import joblib

PROJECT_ROOT  = Path(__file__).resolve().parents[1]
PIPELINE_PATH = PROJECT_ROOT / "models" / "xgb_pipeline.pkl"

# load pipeline
def load_pipeline(path: Path = PIPELINE_PATH):
    if not path.exists():
        raise FileNotFoundError(
            f"Pipeline not found at {path}. Run train.py first."
        )
    return joblib.load(path)


# load once at module level
# so FastAPI doesn't reload it on every request
_pipeline = load_pipeline()