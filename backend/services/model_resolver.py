import os
import json
import pickle
import joblib
import logging

logger = logging.getLogger(__name__)

# Project root path (assumed to be parent of backend folder, or configured via env)
WORKSPACE_ROOT = os.environ.get("WORKSPACE_ROOT", os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def resolve_and_load_best_model():
    """
    Dynamically resolves the best forecasting model:
    1. Read 'best_model' from outputs/final_aqi_model_metrics.json
    2. Lowercase and replace spaces with underscores to get filename stem (e.g., "Random Forest" -> "random_forest")
    3. Load models/trained_forecasting_models/{stem}.pkl
    
    If any file is missing, raises FileNotFoundError with clear messages.
    """
    metrics_json_path = os.path.join(WORKSPACE_ROOT, "outputs", "final_aqi_model_metrics.json")
    
    # Graceful check for metrics json
    if not os.path.exists(metrics_json_path):
        # Check fallback to sample data or raise
        sample_metrics_path = os.path.join(WORKSPACE_ROOT, "backend", "sample_data", "final_aqi_model_metrics.json")
        if os.path.exists(sample_metrics_path):
            metrics_json_path = sample_metrics_path
        else:
            raise FileNotFoundError(
                f"Required model metrics file missing: '{metrics_json_path}'. "
                "This file is produced by notebook 04_ml_forecasting_models.ipynb."
            )
            
    with open(metrics_json_path, "r") as f:
        metrics = json.load(f)
        
    best_model_name = metrics.get("best_model")
    if not best_model_name:
        raise ValueError("Could not find 'best_model' in metrics JSON.")
        
    # Convert "Random Forest" to "random_forest"
    model_stem = best_model_name.lower().replace(" ", "_")
    model_file_name = f"{model_stem}.pkl"
    
    # Path to check
    model_path = os.path.join(WORKSPACE_ROOT, "models", "trained_forecasting_models", model_file_name)
    
    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"Expected best model file missing: '{model_path}'. "
            f"The best model resolved was '{best_model_name}' which maps to '{model_file_name}'."
        )
        
    logger.info(f"Dynamically resolved and loading best model from {model_path}")
    model = joblib.load(model_path)
        
    return model, best_model_name, model_path
