import os
import logging
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

from backend.models import (
    HealthCheckResponse,
    StationResponse,
    StationsListResponse,
    CitySummaryResponse,
    PriorityQueueEntry,
    PriorityQueueAblationResponse,
    AblationRankingRow,
    StationForecastResponse,
    ModelMetricsResponse,
    ModelComparisonRow,
    PerCityErrorRow,
    FeatureImportanceRow,
    ConfusionMatrixResponse,
    TestPredictionResponse,
    HotspotSummaryResponse,
    MapDataRow,
    AdvisoryResponse,
    RefreshResponse
)
from backend.services import data_loader, advisory_service, model_resolver

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("cleanair_backend")

app = FastAPI(
    title="CleanAir AI Backend",
    description="AI-Powered Urban Air Quality Intelligence Platform API for ET AI Hackathon 2026",
    version="1.0.0"
)

# Enable Permissive CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Try resolving the best model on startup (gracefully log failure)
@app.on_event("startup")
def startup_event():
    logger.info("Initializing CleanAir AI Backend...")
    try:
        model, name, path = model_resolver.resolve_and_load_best_model()
        logger.info(f"Successfully resolved and preloaded best model '{name}' from '{path}'")
    except Exception as e:
        logger.warning(
            f"Best model could not be resolved/loaded on startup: {str(e)}. "
            "Server will still run, serving endpoints with graceful degradation."
        )

@app.get("/", response_model=HealthCheckResponse, tags=["Health"])
def health_check():
    """
    Health check endpoint returning api status and available endpoints.
    """
    routes = []
    for route in app.routes:
        if hasattr(route, "methods"):
            routes.append(f"{list(route.methods)} {route.path}")
    return {
        "status": "healthy",
        "message": "CleanAir AI Backend is running.",
        "endpoints": sorted(routes)
    }

@app.get("/stations", response_model=StationsListResponse, tags=["Stations"])
def get_stations(
    city: Optional[str] = Query(None, description="Filter stations by city (case-insensitive)"),
    state: Optional[str] = Query(None, description="Filter stations by state (case-insensitive)"),
    limit: int = Query(100, ge=1, le=1000, description="Max number of stations to return")
):
    """
    Retrieve stations with optional filters for city and state.
    Source: data/processed/station_advanced_intelligence.csv
    """
    df = data_loader.load_csv("data/processed/station_advanced_intelligence.csv")
    
    # Filter operations
    if city:
        df = df[df["city"].str.lower() == city.strip().lower()]
    if state:
        df = df[df["state"].str.lower() == state.strip().lower()]
        
    total_count = len(df)
    df_limited = df.head(limit)
    
    cleaned = data_loader.clean_records(df_limited)
    return {
        "total": total_count,
        "limit": limit,
        "stations": cleaned
    }

@app.get("/stations/{station_id}", response_model=Dict[str, Any], tags=["Stations"])
def get_station_by_id(
    station_id: str = Path(..., description="Unique ID of the station to look up")
):
    """
    Retrieve a single station by its unique station_id.
    Source: data/processed/station_advanced_intelligence.csv
    """
    df = data_loader.load_csv("data/processed/station_advanced_intelligence.csv")
    
    # Filter where station_id matches
    station_row = df[df["station_id"] == station_id]
    if station_row.empty:
        raise HTTPException(
            status_code=404, 
            detail=f"Station with station_id '{station_id}' not found in station_advanced_intelligence.csv"
        )
        
    records = data_loader.clean_records(station_row)
    return records[0]

@app.get("/cities", response_model=List[CitySummaryResponse], tags=["Cities"])
def get_cities():
    """
    Retrieve city summaries list.
    Source: data/processed/city_advanced_intelligence_summary.csv
    """
    df = data_loader.load_csv("data/processed/city_advanced_intelligence_summary.csv")
    return data_loader.clean_records(df)

@app.get("/cities/{city}", response_model=CitySummaryResponse, tags=["Cities"])
def get_city_by_name(
    city: str = Path(..., description="Name of the city (case-insensitive)")
):
    """
    Retrieve individual city details summary. Case-insensitive.
    Source: data/processed/city_advanced_intelligence_summary.csv
    """
    df = data_loader.load_csv("data/processed/city_advanced_intelligence_summary.csv")
    city_row = df[df["city"].str.lower() == city.strip().lower()]
    
    if city_row.empty:
        raise HTTPException(
            status_code=404,
            detail=f"City '{city}' not found in city_advanced_intelligence_summary.csv"
        )
        
    records = data_loader.clean_records(city_row)
    return records[0]

@app.get("/priority-queue", response_model=List[PriorityQueueEntry], tags=["Priority Queue"])
def get_priority_queue(
    top_n: int = Query(20, ge=1, le=500, description="Number of top priority stations to return")
):
    """
    Retrieve ranked priority hotspots queue directly.
    Source: outputs/top_priority_hotspots.csv
    """
    df = data_loader.load_csv("outputs/top_priority_hotspots.csv")
    # File is pre-sorted by advanced_priority_rank
    df_limited = df.head(top_n)
    return data_loader.clean_records(df_limited)

@app.get("/priority-queue/ablation", response_model=PriorityQueueAblationResponse, tags=["Priority Queue"])
def get_priority_queue_ablation():
    """
    Compare Naive AQI ranking against Advanced Multi-factor ranking.
    Source: outputs/priority_ranking_ablation.csv
    """
    df = data_loader.load_csv("outputs/priority_ranking_ablation.csv")
    
    # Split rows by ranking_method
    naive_df = df[df["ranking_method"].str.lower().str.contains("naive")]
    advanced_df = df[df["ranking_method"].str.lower().str.contains("advanced")]
    
    # advanced_only_station can be boolean or string representation of bool
    # We'll normalize it by comparing to True, 'True', 'true', 1, etc.
    advanced_only_df = df[
        (df["advanced_only_station"] == True) | 
        (df["advanced_only_station"].astype(str).str.lower() == "true") |
        (df["advanced_only_station"] == 1)
    ]
    
    return {
        "naive_ranking": data_loader.clean_records(naive_df),
        "advanced_ranking": data_loader.clean_records(advanced_df),
        "newly_surfaced_by_advanced_score": data_loader.clean_records(advanced_only_df)
    }

@app.get("/forecast/{station_id}", response_model=StationForecastResponse, tags=["Forecast"])
def get_forecast(
    station_id: str = Path(..., description="Unique ID of the station to retrieve forecast for")
):
    """
    Retrieve forecast parameters for a given station.
    Source: data/processed/station_advanced_intelligence.csv
    """
    df = data_loader.load_csv("data/processed/station_advanced_intelligence.csv")
    
    station_row = df[df["station_id"] == station_id]
    if station_row.empty:
        raise HTTPException(
            status_code=404,
            detail=f"Station '{station_id}' not found in station_advanced_intelligence.csv"
        )
        
    records = data_loader.clean_records(station_row)
    row = records[0]
    
    return {
        "station_id": row.get("station_id"),
        "station_name": row.get("station_name"),
        "city": row.get("city"),
        "state": row.get("state"),
        "forecast_aqi_next": row.get("forecast_aqi_next"),
        "forecast_aqi_p10": row.get("forecast_aqi_p10"),
        "forecast_aqi_p50": row.get("forecast_aqi_p50"),
        "forecast_aqi_p90": row.get("forecast_aqi_p90"),
        "forecast_category": row.get("forecast_category") or row.get("forecast_aqi_category"),
        "forecast_trend": row.get("forecast_trend")
    }

@app.get("/model/metrics", response_model=ModelMetricsResponse, tags=["Model Evaluation"])
def get_model_metrics():
    """
    Retrieve aggregate model evaluation metrics. Strips Windows paths and internal model references.
    Source: outputs/final_aqi_model_metrics.json
    """
    metrics = data_loader.load_json("outputs/final_aqi_model_metrics.json")
    
    # Strip paths per requirement 7
    cleaned_metrics = {k: v for k, v in metrics.items() if not k.endswith("_file")}
    cleaned_metrics.pop("all_saved_models", None)
    
    # Also strip default wrong path in best_model_file if any keys got missed
    cleaned_metrics.pop("best_model_file", None)
    
    return cleaned_metrics

@app.get("/model/comparison", response_model=List[ModelComparisonRow], tags=["Model Evaluation"])
def get_model_comparison():
    """
    Retrieve experimental results across different models/features.
    Source: outputs/aqi_model_comparison.csv
    """
    df = data_loader.load_csv("outputs/aqi_model_comparison.csv")
    return data_loader.clean_records(df)

@app.get("/model/per-city-error", response_model=List[PerCityErrorRow], tags=["Model Evaluation"])
def get_model_per_city_error():
    """
    Retrieve model errors broken down per city.
    Source: outputs/per_city_error.csv
    """
    df = data_loader.load_csv("outputs/per_city_error.csv")
    return data_loader.clean_records(df)

@app.get("/model/feature-importance", response_model=List[FeatureImportanceRow], tags=["Model Evaluation"])
def get_model_feature_importance(
    top_n: int = Query(15, ge=1, le=100, description="Top N important features to return")
):
    """
    Retrieve feature importance scores.
    Source: outputs/feature_importance.csv
    """
    df = data_loader.load_csv("outputs/feature_importance.csv")
    
    # Sort descending by importance
    df_sorted = df.sort_values(by="importance", ascending=False)
    df_limited = df_sorted.head(top_n)
    
    return data_loader.clean_records(df_limited)

@app.get("/model/confusion-matrix", response_model=List[Dict[str, Any]], tags=["Model Evaluation"])
def get_model_confusion_matrix():
    """
    Retrieve AQI category true vs predicted confusion matrix.
    Source: outputs/category_confusion_matrix.csv
    """
    df = data_loader.load_csv("outputs/category_confusion_matrix.csv")
    return data_loader.clean_records(df)

@app.get("/model/test-predictions/{station_id}", response_model=List[TestPredictionResponse], tags=["Model Evaluation"])
def get_model_test_predictions(
    station_id: str = Path(..., description="Unique ID of the station to fetch test prediction rows for")
):
    """
    Retrieve held-out test predictions for a station.
    Source: data/processed/test_predictions_with_uncertainty.csv
    """
    df = data_loader.load_csv("data/processed/test_predictions_with_uncertainty.csv")
    
    station_rows = df[df["station_id"] == station_id]
    if station_rows.empty:
        raise HTTPException(
            status_code=404,
            detail=f"Station '{station_id}' has no rows in test_predictions_with_uncertainty.csv"
        )
        
    return data_loader.clean_records(station_rows)

@app.get("/hotspots/summary", response_model=HotspotSummaryResponse, tags=["Hotspots"])
def get_hotspots_summary():
    """
    Retrieve general hotspot statistics summary.
    Source: outputs/hotspot_summary.json
    """
    return data_loader.load_json("outputs/hotspot_summary.json")

@app.get("/map-data", response_model=List[Dict[str, Any]], tags=["Map Rendering"])
def get_map_data():
    """
    Retrieve lightweight coordinate rows for map visualization.
    Source: outputs/map_ready_advanced_hotspots.csv
    """
    df = data_loader.load_csv("outputs/map_ready_advanced_hotspots.csv")
    return data_loader.clean_records(df)

@app.get("/advisory/{aqi_category}", response_model=AdvisoryResponse, tags=["Citizen Advisories"])
def get_health_advisory(
    aqi_category: str = Path(..., description="Category: Good, Satisfactory, Moderate, Poor, Very Poor, Severe"),
    lang: str = Query("en", description="Language code: en, hi, ta, kn, bn, mr, te")
):
    """
    Retrieve multilingual health advisories for a given AQI category.
    """
    return advisory_service.get_advisory(aqi_category, lang)

@app.post("/refresh-live-aqi", response_model=RefreshResponse, tags=["System Cache"])
def refresh_live_aqi():
    """
    Clears the internal memory cache to force re-reading updated ML outputs from disk.
    This simulates real-time data ingestion for the hackathon demo.
    """
    data_loader.clear_cache()
    
    # Optionally try to reload the best model in case the winner changed
    best_model_status = "Skipped reloading model"
    try:
        model, name, path = model_resolver.resolve_and_load_best_model()
        best_model_status = f"Reloaded winning model: '{name}'"
    except Exception as e:
        logger.warning(f"Could not reload best model on refresh: {str(e)}")
        best_model_status = f"Model reload failed: {str(e)}"
        
    return {
        "status": "success",
        "message": f"Successfully reloaded data files from disk. {best_model_status}."
    }
