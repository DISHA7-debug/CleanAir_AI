import os
import json
import logging
import pandas as pd
from fastapi import HTTPException

logger = logging.getLogger(__name__)

WORKSPACE_ROOT = os.environ.get("WORKSPACE_ROOT", os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Mapping of expected relative paths to the producing notebooks
FILE_NOTEBOOK_MAPPING = {
    "data/processed/station_advanced_intelligence.csv": "05_advanced_intelligence_layers.ipynb / 06_evaluation_ablation_packaging.ipynb",
    "data/processed/city_advanced_intelligence_summary.csv": "06_evaluation_ablation_packaging.ipynb",
    "outputs/top_priority_hotspots.csv": "06_evaluation_ablation_packaging.ipynb",
    "outputs/map_ready_advanced_hotspots.csv": "06_evaluation_ablation_packaging.ipynb",
    "data/processed/test_predictions_with_uncertainty.csv": "04_ml_forecasting_models.ipynb",
    "outputs/final_aqi_model_metrics.json": "04_ml_forecasting_models.ipynb",
    "outputs/aqi_model_comparison.csv": "04_ml_forecasting_models.ipynb",
    "outputs/per_city_error.csv": "04_ml_forecasting_models.ipynb",
    "outputs/feature_importance.csv": "04_ml_forecasting_models.ipynb",
    "outputs/category_confusion_matrix.csv": "04_ml_forecasting_models.ipynb",
    "outputs/priority_ranking_ablation.csv": "05_advanced_intelligence_layers.ipynb",
    "outputs/hotspot_summary.json": "06_evaluation_ablation_packaging.ipynb"
}

# Cache dictionary to store dataframes/json data for fast serving
_data_cache = {}

def get_file_path(relative_path: str) -> str:
    """
    Returns the resolved path of a file, preferring the root path
    and falling back to backend/sample_data/ if missing.
    """
    # Main path
    main_path = os.path.join(WORKSPACE_ROOT, relative_path)
    if os.path.exists(main_path):
        return main_path
        
    # Fallback sample path
    # If relative_path contains data/processed/ or outputs/, strip to filename for sample_data
    file_name = os.path.basename(relative_path)
    sample_path = os.path.join(WORKSPACE_ROOT, "backend", "sample_data", file_name)
    if os.path.exists(sample_path):
        logger.warning(f"File '{main_path}' not found. Falling back to sample file '{sample_path}'.")
        return sample_path
        
    # Raise error naming the expected file path and producing notebook
    notebook = FILE_NOTEBOOK_MAPPING.get(relative_path, "Unknown Notebook")
    error_msg = (
        f"Required data file is missing: '{relative_path}'. "
        f"This file is expected to be produced by the ML pipeline notebook: '{notebook}'."
    )
    raise HTTPException(status_code=404, detail=error_msg)

def load_csv(relative_path: str, use_cache: bool = True) -> pd.DataFrame:
    """
    Loads a CSV file into a Pandas DataFrame.
    """
    cache_key = f"csv:{relative_path}"
    if use_cache and cache_key in _data_cache:
        return _data_cache[cache_key]
        
    file_path = get_file_path(relative_path)
    try:
        # Load CSV, keep empty fields as empty string/NaN appropriately
        df = pd.read_csv(file_path)
        if use_cache:
            _data_cache[cache_key] = df
        return df
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error reading CSV '{relative_path}': {str(e)}"
        )

def load_json(relative_path: str, use_cache: bool = True) -> dict:
    """
    Loads a JSON file into a Python dictionary.
    """
    cache_key = f"json:{relative_path}"
    if use_cache and cache_key in _data_cache:
        return _data_cache[cache_key]
        
    file_path = get_file_path(relative_path)
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
        if use_cache:
            _data_cache[cache_key] = data
        return data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error reading JSON '{relative_path}': {str(e)}"
        )

def clear_cache():
    """
    Clears the internal memory cache. Called during refresh endpoint.
    """
    _data_cache.clear()
    logger.info("Internal dataset cache cleared.")

def clean_records(df: pd.DataFrame) -> list:
    """
    Converts a Pandas DataFrame to a list of dicts and replaces any NaN/NaT/Null with None.
    """
    records = df.to_dict(orient="records")
    return [{k: (None if pd.isna(v) else v) for k, v in r.items()} for r in records]

