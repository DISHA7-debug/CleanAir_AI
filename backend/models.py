from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

# Health check response model
class HealthCheckResponse(BaseModel):
    status: str
    message: str
    endpoints: List[str]

# General station details response model
class StationResponse(BaseModel):
    station_id: str
    station_name: str
    city: str
    state: str
    lat: Optional[float] = None
    lon: Optional[float] = None
    timestamp: Optional[str] = None
    current_aqi: Optional[float] = None
    current_aqi_category: Optional[str] = None
    reported_aqi: Optional[float] = None
    reported_dominant_pollutant: Optional[str] = None
    primary_pollution_source: Optional[str] = None
    recommended_intervention: Optional[str] = None
    is_current_hotspot: Optional[int] = None
    is_forecast_hotspot: Optional[int] = None
    is_emerging_hotspot: Optional[int] = None
    hotspot_status: Optional[str] = None
    advanced_priority_score: Optional[float] = None
    advanced_priority_category: Optional[str] = None
    advanced_priority_rank: Optional[int] = None
    class Config:
        extra = "allow"

# List of stations
class StationsListResponse(BaseModel):
    total: int
    limit: int
    stations: List[Dict[str, Any]]

# City details summary
class CitySummaryResponse(BaseModel):
    state: str
    city: str
    stations: Optional[int] = None
    mean_current_aqi: Optional[float] = None
    max_current_aqi: Optional[float] = None
    mean_forecast_aqi: Optional[float] = None
    max_forecast_aqi: Optional[float] = None
    mean_priority_score: Optional[float] = None
    max_priority_score: Optional[float] = None
    current_hotspot_stations: Optional[int] = None
    forecast_hotspot_stations: Optional[int] = None
    emerging_hotspot_stations: Optional[int] = None
    mean_health_exposure_risk: Optional[float] = None
    mean_dispersion_index: Optional[float] = None
    mean_satellite_aerosol_proxy: Optional[float] = None
    city_priority_rank: Optional[int] = None

# Priority queue response entry
class PriorityQueueEntry(BaseModel):
    advanced_priority_rank: Optional[int] = None
    state: Optional[str] = None
    city: Optional[str] = None
    station_name: Optional[str] = None
    current_aqi: Optional[float] = None
    current_aqi_category: Optional[str] = None
    forecast_aqi_next: Optional[float] = None
    forecast_aqi_category: Optional[str] = None
    forecast_aqi_change: Optional[float] = None
    forecast_trend: Optional[str] = None
    hotspot_status: Optional[str] = None
    advanced_priority_score: Optional[float] = None
    advanced_priority_category: Optional[str] = None
    health_exposure_risk_score: Optional[float] = None
    dispersion_index: Optional[float] = None
    satellite_aerosol_proxy_score: Optional[float] = None
    primary_pollution_source: Optional[str] = None
    recommended_intervention: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None

# Priority queue ablation ranking row
class AblationRankingRow(BaseModel):
    ranking_method: Optional[str] = None
    rank_position: Optional[int] = None
    advanced_only_station: Optional[bool] = None
    appears_in_naive_top10: Optional[bool] = None
    appears_in_advanced_top10: Optional[bool] = None
    advanced_priority_rank: Optional[int] = None
    station_id: Optional[str] = None
    station_name: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    current_aqi: Optional[float] = None
    advanced_priority_score: Optional[float] = None
    hotspot_status: Optional[str] = None
    primary_pollution_source: Optional[str] = None
    recommended_intervention: Optional[str] = None

class PriorityQueueAblationResponse(BaseModel):
    naive_ranking: List[AblationRankingRow]
    advanced_ranking: List[AblationRankingRow]
    newly_surfaced_by_advanced_score: List[AblationRankingRow]

# Forecast details per station
class StationForecastResponse(BaseModel):
    station_id: str
    station_name: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    forecast_aqi_next: Optional[float] = None
    forecast_aqi_p10: Optional[float] = None
    forecast_aqi_p50: Optional[float] = None
    forecast_aqi_p90: Optional[float] = None
    forecast_category: Optional[str] = None
    forecast_trend: Optional[str] = None

# Model metrics clean representation
class ModelMetricsResponse(BaseModel):
    notebook: Optional[str] = None
    run_time: Optional[str] = None
    training_mode: Optional[str] = None
    history_rows: Optional[int] = None
    model_rows: Optional[int] = None
    train_rows: Optional[int] = None
    test_rows: Optional[int] = None
    unique_stations: Optional[int] = None
    unique_timestamps: Optional[int] = None
    models_tested: Optional[List[str]] = None
    best_model: Optional[str] = None
    best_metrics: Optional[Dict[str, Any]] = None
    category_accuracy: Optional[float] = None
    high_aqi_threshold: Optional[float] = None
    high_aqi_precision: Optional[float] = None
    high_aqi_recall: Optional[float] = None
    high_aqi_f1: Optional[float] = None
    lag_feature_importance_share_percent: Optional[float] = None

# Model comparison table row
class ModelComparisonRow(BaseModel):
    experiment: Optional[str] = None
    model_type: Optional[str] = None
    feature_count: Optional[int] = None
    train_rows: Optional[int] = None
    test_rows: Optional[int] = None
    mae: Optional[float] = None
    rmse: Optional[float] = None
    r2: Optional[float] = None
    improvement_over_baseline_percent: Optional[float] = None

# Per-city error row
class PerCityErrorRow(BaseModel):
    state: Optional[str] = None
    city: Optional[str] = None
    test_rows: Optional[int] = None
    mean_absolute_error: Optional[float] = None
    max_absolute_error: Optional[float] = None
    mean_actual_aqi: Optional[float] = None
    mean_predicted_aqi: Optional[float] = None

# Feature importance row
class FeatureImportanceRow(BaseModel):
    feature: Optional[str] = None
    importance: Optional[float] = None

# Confusion Matrix
class ConfusionMatrixResponse(BaseModel):
    confusion_matrix: List[Dict[str, Any]]

# Test prediction evaluation per station
class TestPredictionResponse(BaseModel):
    station_id: str
    station_name: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    timestamp: Optional[str] = None
    reported_aqi: Optional[float] = None
    target_aqi_next: Optional[float] = None
    best_model: Optional[str] = None
    predicted_aqi_next: Optional[float] = None
    residual: Optional[float] = None
    absolute_error: Optional[float] = None
    predicted_aqi_p10: Optional[float] = None
    predicted_aqi_p50: Optional[float] = None
    predicted_aqi_p90: Optional[float] = None
    actual_category: Optional[str] = None
    predicted_category: Optional[str] = None

# Hotspot general summary statistics
class HotspotSummaryResponse(BaseModel):
    total_stations: Optional[int] = None
    total_cities: Optional[int] = None
    total_states: Optional[int] = None
    current_hotspot_stations: Optional[int] = None
    forecast_hotspot_stations: Optional[int] = None
    emerging_hotspot_stations: Optional[int] = None
    top_priority_city: Optional[str] = None
    top_priority_state: Optional[str] = None
    hotspot_distribution: Optional[Dict[str, int]] = None
    priority_category_distribution: Optional[Dict[str, int]] = None
    source_distribution: Optional[Dict[str, int]] = None

# Map coordinate item response
class MapDataRow(BaseModel):
    station_name: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    current_aqi: Optional[float] = None
    current_aqi_category: Optional[str] = None
    advanced_priority_score: Optional[float] = None
    advanced_priority_rank: Optional[int] = None
    primary_pollution_source: Optional[str] = None
    class Config:
        extra = "allow"

# Advisory item response
class AdvisoryResponse(BaseModel):
    aqi_category: str
    language: str
    advisory: str

# POST refresh live response
class RefreshResponse(BaseModel):
    status: str
    message: str
