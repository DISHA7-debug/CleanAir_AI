# BACKEND_SPEC.md — CleanAir AI Backend (v2, matches actual ML pipeline output)

This version replaces the original BACKEND_SPEC.md. It is written against the
**real files produced by the ML pipeline** (verified by inspecting the actual
CSVs/JSON on the `ml` branch on 2026-07-16), not an assumed schema. Build
against this document, not the original.

## 1. Tech choice (unchanged)

- FastAPI (Python), served via Uvicorn
- File-based storage — read directly from `data/processed/`, `outputs/`,
  and `models/`. No database.
- Swagger docs at `/docs`. Permissive CORS for local frontend dev.

## 2. Real source files and what they contain

### `data/processed/station_advanced_intelligence.csv`
The master station table — **one row per station**, ~77 columns. This is
the single source of truth for almost every station-level endpoint. Key
columns (not exhaustive — pass through what's needed per endpoint, don't
invent new column names):

- Identity: `station_id`, `station_name`, `city`, `state`, `lat`, `lon`, `timestamp`
- Raw pollutants: `PM2.5`, `PM10`, `NO2`, `SO2`, `CO`, `O3`, `NH3`
- Current AQI: `current_aqi`, `current_aqi_category`, `reported_aqi`,
  `reported_dominant_pollutant`
- Weather: `temperature_2m`, `relative_humidity_2m`, `rain`, `wind_speed_10m`,
  `cloud_cover`, `weather_trapping_score`, `weather_trapping_category`
- Land-use / geospatial proxy: `landuse_type_proxy`, `landuse_data_source`,
  `urban_pressure_score`, `road_density_proxy`, `environmental_risk_score`
- Source attribution: `primary_pollution_source`, `primary_source_score`,
  `secondary_source_score`, `source_score_gap`,
  `source_attribution_confidence`, `source_attribution_confidence_category`,
  `source_evidence`, `landuse_source_alignment`, `recommended_intervention`
- Forecast: `forecast_aqi_next`, `forecast_aqi_p10`, `forecast_aqi_p50`,
  `forecast_aqi_p90`, `forecast_category`, `forecast_aqi_category`,
  `forecast_aqi_change`, `forecast_trend`
- Satellite/aerosol proxy: `satellite_aerosol_proxy_score`,
  `satellite_aerosol_proxy_category`, `satellite_data_source`
- Dispersion/health: `dispersion_index`, `dispersion_category`,
  `health_exposure_risk_score`, `health_exposure_risk_category`
- Hotspot flags: `is_current_hotspot`, `is_forecast_hotspot`,
  `is_emerging_hotspot`, `hotspot_status`
- Priority: `advanced_priority_score`, `advanced_priority_category`,
  `advanced_priority_rank`, `advanced_data_quality_flag`, `advanced_layer_note`

**Do not rename these columns in the API response.** Serve them under their
real names. Renaming introduces exactly the kind of drift that broke the
original spec — keep the API a thin, faithful pass-through of the pipeline's
actual field names, with light grouping/nesting for readability if useful.

### `data/processed/city_advanced_intelligence_summary.csv`
One row per city: `state`, `city`, `stations`, `mean_current_aqi`,
`max_current_aqi`, `mean_forecast_aqi`, `max_forecast_aqi`,
`mean_priority_score`, `max_priority_score`, `current_hotspot_stations`,
`forecast_hotspot_stations`, `emerging_hotspot_stations`,
`mean_health_exposure_risk`, `mean_dispersion_index`,
`mean_satellite_aerosol_proxy`, `city_priority_rank`.

### `outputs/top_priority_hotspots.csv`
Already-ranked priority queue (sorted by `advanced_priority_rank`). Columns:
`advanced_priority_rank`, `state`, `city`, `station_name`, `current_aqi`,
`current_aqi_category`, `forecast_aqi_next`, `forecast_aqi_category`,
`forecast_aqi_change`, `forecast_trend`, `hotspot_status`,
`advanced_priority_score`, `advanced_priority_category`,
`health_exposure_risk_score`, `dispersion_index`,
`satellite_aerosol_proxy_score`, `primary_pollution_source`,
`recommended_intervention`, `lat`, `lon`.

**Use this file directly for `/priority-queue`** — it's pre-sorted and
pre-selected, don't recompute ranking from the master table for this endpoint.

### `outputs/map_ready_advanced_hotspots.csv`
Lighter-weight version of the same data, intended for map rendering. Use for
any endpoint that feeds a map component (fewer columns = faster payload).

### `data/processed/test_predictions_with_uncertainty.csv`
Per-station forecast evaluation rows (this is model *test set* output, used
both for the `/forecast/{station}` endpoint and for feeding ML metrics
displays). Columns: `station_id`, `station_name`, `city`, `state`,
`timestamp`, `reported_aqi`, `target_aqi_next`, `best_model`,
`predicted_aqi_next`, `residual`, `absolute_error`, `predicted_aqi_p10`,
`predicted_aqi_p50`, `predicted_aqi_p90`, `actual_category`,
`predicted_category`.

Note: field names here (`predicted_aqi_p10/p50/p90`) differ from the
forecast fields in `station_advanced_intelligence.csv`
(`forecast_aqi_p10/p50/p90`) — these are two different things. The
`station_advanced_intelligence.csv` forecast is the live/current forecast per
station; `test_predictions_with_uncertainty.csv` is the held-out test-set
evaluation data used to prove model accuracy. Use the right one for the right
purpose — don't conflate them.

### `outputs/final_aqi_model_metrics.json`
Full run report. Real structure (confirmed from actual file):
```json
{
  "notebook": "04_ml_forecasting_models.ipynb",
  "run_time": "...",
  "training_mode": "real_time_series_history",
  "history_rows": 0, "model_rows": 0, "train_rows": 0, "test_rows": 0,
  "unique_stations": 0, "unique_timestamps": 0,
  "models_tested": ["..."],
  "best_model": "Random Forest",
  "best_metrics": {"model": "", "mae": 0, "rmse": 0, "r2": 0, "improvement_over_persistence_percent": 0},
  "category_accuracy": 0,
  "high_aqi_threshold": 200,
  "high_aqi_precision": 0, "high_aqi_recall": 0, "high_aqi_f1": 0,
  "lag_feature_importance_share_percent": 0,
  "model_comparison_file": "ABSOLUTE_WINDOWS_PATH_STRIP_THIS",
  "predictions_file": "ABSOLUTE_WINDOWS_PATH_STRIP_THIS",
  "feature_importance_file": "ABSOLUTE_WINDOWS_PATH_STRIP_THIS",
  "per_city_error_file": "ABSOLUTE_WINDOWS_PATH_STRIP_THIS",
  "feature_columns_file": "ABSOLUTE_WINDOWS_PATH_STRIP_THIS",
  "best_model_file": "ABSOLUTE_WINDOWS_PATH_STRIP_AND_ALSO_WRONG_SEE_NOTE",
  "all_saved_models": {"MODEL_NAME": "ABSOLUTE_WINDOWS_PATH_STRIP_THIS"}
}
```

**MANDATORY:** the backend must strip every `*_file` key and the entire
`all_saved_models` object before returning this JSON from `/model/metrics`.
These are machine-specific absolute paths from the ML lead's Windows machine
(`C:\Users\Lenovo\...`) and are both useless and wrong once files move
branches/machines. Return only the numeric/categorical fields.

Note also: `best_metrics.improvement_over_persistence_percent` is the correct
field for "% RMSE improvement over baseline" — there is no separate
`hotspot_f1`; use `high_aqi_f1` instead (same concept, different name than
originally spec'd).

### `outputs/aqi_model_comparison.csv`
Model comparison table, one row per experiment/model. Columns: `experiment`,
`model_type`, `feature_count`, `train_rows`, `test_rows`, `mae`, `rmse`,
`r2`, `improvement_over_baseline_percent`.

**Note:** this is actually a *feature-set* ablation (Persistence Baseline vs
Lag-Features-Only vs fuller feature sets), not a full model-type comparison
in the original sense. Use it for the "does more features help" chart on the
ML Forecasting tab.

### `outputs/per_city_error.csv`
Columns: `state`, `city`, `test_rows`, `mean_absolute_error`,
`max_absolute_error`, `mean_actual_aqi`, `mean_predicted_aqi`.

### `outputs/feature_importance.csv`
Columns: `feature`, `importance`. Simple two-column table, sortable
descending for top-N display.

### `outputs/category_confusion_matrix.csv`
AQI-category confusion matrix (true vs predicted buckets).

### `outputs/hotspot_summary.json`
Real structure:
```json
{
  "total_stations": 0, "total_cities": 0, "total_states": 0,
  "current_hotspot_stations": 0, "forecast_hotspot_stations": 0,
  "emerging_hotspot_stations": 0,
  "top_priority_city": "", "top_priority_state": "",
  "hotspot_distribution": {"CATEGORY": 0},
  "priority_category_distribution": {"CATEGORY": 0},
  "source_distribution": {"SOURCE": 0}
}
```
Serve as-is — this is clean and ready for a summary-stats endpoint.

### `outputs/ablation_results.csv`
This is a *feature-ablation* study (does adding lag features / more features
improve the model) — use it for the "does more features help" chart on the
ML Forecasting tab. It is NOT the priority-ranking ablation (see next file).

### `outputs/priority_ranking_ablation.csv` (CONFIRMED REAL — v3 update)
This now exists as a real precomputed file (added by the ML lead after the
v2 review) and is the actual judge-defense evidence for "is your priority
ranking better than sorting by AQI alone." Columns: `ranking_method`
("Naive AQI ranking" or the advanced-ranking equivalent), `rank_position`,
`advanced_only_station` (bool), `appears_in_naive_top10` (bool),
`appears_in_advanced_top10` (bool), `advanced_priority_rank`, `station_id`,
`station_name`, `city`, `state`, `current_aqi`, `advanced_priority_score`,
`hotspot_status`, `primary_pollution_source`, `recommended_intervention`.

**Use this file directly for `/priority-queue/ablation` — do NOT compute it
live in the backend.** This supersedes the v2 instruction to compute the
ablation on the fly; a real, ML-lead-verified artifact exists now and should
be treated as the source of truth. Filter/group by `ranking_method` and
`advanced_only_station` to build the "newly surfaced by advanced ranking"
list for the API response.

### `models/trained_forecasting_models/*.pkl`
Per-model trained models: `linear_regression.pkl`, `ridge_regression.pkl`,
`random_forest.pkl`, `extra_trees.pkl`, `gradient_boosting.pkl`,
`histgradientboosting.pkl`, `xgboost.pkl`.

**CONFIRMED (v3, via `find models -name "*.pkl"`): there is still no
`models/best_aqi_forecast_model.pkl` at the models root**, even though
`final_aqi_model_metrics.json`'s `best_model_file` field references that
path. Treat this as a permanently stale reference — do not build a hard
dependency on that file existing. Instead, the backend MUST implement this
resolution logic at startup / on first request:
1. Read `best_model` from `final_aqi_model_metrics.json` (currently
   `"Random Forest"`).
2. Lowercase + replace spaces with underscores to get the filename stem
   (`"Random Forest"` -> `random_forest`).
3. Load `models/trained_forecasting_models/{stem}.pkl`.
4. If that file is also missing, return a clear 500/404 rather than crashing
   silently, naming which file was expected.
This makes the backend resilient to the ML lead changing the winning model
in a future run without needing him to remember to also save a duplicate
"best model" copy — which he has now missed twice.

### `models/feature_columns.json`
Flat JSON array of ~200+ feature column names used by the trained model
(includes lag features, rolling stats, and one-hot encoded state/city/
category dummies). Only needed if the backend ever needs to run live
inference with the model — not needed for serving precomputed outputs. Note
for later: if a `/predict` endpoint is ever added, the input must be
one-hot encoded to match this exact column list, in this exact order.

## 3. Endpoints (revised)

### `GET /`
Health check + endpoint list.

### `GET /stations`
- Query params: `city`, `state` (optional filters), `limit` (default 100, max 1000)
- Source: `data/processed/station_advanced_intelligence.csv`
- Returns real column names, not renamed ones (see section 2 note).

### `GET /stations/{station_id}`
Look up by `station_id` (not `station_name` — station_id is the real unique
key, station_name has commas/special characters that make URL routing
fragile). 404 if not found.

### `GET /cities`
Source: `city_advanced_intelligence_summary.csv`.

### `GET /cities/{city}`
Case-insensitive match on `city` column. 404 if not found.

### `GET /priority-queue`
- Query param: `top_n` (default 20, max 500)
- Source: `outputs/top_priority_hotspots.csv` directly (already ranked).

### `GET /priority-queue/ablation`
**Source (v3, confirmed real): `outputs/priority_ranking_ablation.csv`.**
Do not compute this live — a verified precomputed file exists. Load it,
split rows by `ranking_method` into `naive_ranking` and `advanced_ranking`
lists, and derive `newly_surfaced_by_advanced_score` from rows where
`advanced_only_station == True`. Response shape:
`{ naive_ranking: [...], advanced_ranking: [...],
newly_surfaced_by_advanced_score: [...] }`.

### `GET /forecast/{station_id}`
Source: `station_advanced_intelligence.csv` (the live forecast fields:
`forecast_aqi_next`, `forecast_aqi_p10`, `forecast_aqi_p50`,
`forecast_aqi_p90`, `forecast_category`, `forecast_trend`), NOT
`test_predictions_with_uncertainty.csv` (that's test-evaluation data for the
ML tab, described next).

### `GET /model/metrics`
Source: `outputs/final_aqi_model_metrics.json`, with all `*_file` /
`all_saved_models` path fields **stripped** before returning (see section 2
mandatory note). Must include `best_model`, `best_metrics`,
`category_accuracy`, `high_aqi_precision/recall/f1`,
`lag_feature_importance_share_percent`, `models_tested`.

### `GET /model/comparison`
Source: `outputs/aqi_model_comparison.csv` — full table, for the "does
adding features help" chart.

### `GET /model/per-city-error`
Source: `outputs/per_city_error.csv`.

### `GET /model/feature-importance`
- Query param: `top_n` (default 15)
- Source: `outputs/feature_importance.csv`, sorted descending, sliced to top_n.

### `GET /model/confusion-matrix`
Source: `outputs/category_confusion_matrix.csv`.

### `GET /model/test-predictions/{station_id}`
Source: `test_predictions_with_uncertainty.csv` — the held-out test-set
prediction for a station, if it exists in the test set (not every station
will be in the test split — 404 with a clear message if not found, this is
expected/normal, not an error state).

### `GET /hotspots/summary`
Source: `outputs/hotspot_summary.json`, served as-is.

### `GET /map-data`
Source: `outputs/map_ready_advanced_hotspots.csv` — lightweight columns for
map rendering.

### `GET /advisory/{aqi_category}`
Unchanged from original spec — this is backend-authored content, not from
the ML pipeline. Query param `lang`, one of `en, hi, ta, kn, bn, mr, te`.
Full text required for `en`/`hi`, others may be flagged as needing review.

### `POST /refresh-live-aqi`
Unchanged in concept from original spec, but now: since the real pipeline is
notebook-driven and produces the master `station_advanced_intelligence.csv`
in one pass, this endpoint should be honest about its actual scope for the
hackathon — most realistically it just reloads the current files from disk
(clears any in-memory cache) rather than triggering a live re-fetch+recompute,
unless the ML lead exposes a lightweight re-fetch script separately. Document
whichever behavior is actually implemented clearly in the endpoint docstring
so it's not oversold in the demo.

## 4. Error handling (unchanged principle)

Missing file → 404 with a message naming the exact expected file path and
which pipeline notebook produces it. Confirm the notebook-to-file mapping
directly with the ML lead since it may differ slightly from
ML_PIPELINE_SPEC.md's original assumptions (that doc predates this real
schema).

## 5. Non-goals (unchanged)

No auth, no DB, no live-inference `/predict` endpoint (feature_columns.json
exists for this future capability but it's not in scope for the hackathon
backend).

## 6. Change log

**v2 (vs original spec):**
- Replaced `final_intervention_priority_queue.csv` / `city_risk_summary.csv`
  with real files: `station_advanced_intelligence.csv`,
  `top_priority_hotspots.csv`, `city_advanced_intelligence_summary.csv`.
- Added endpoints for feature importance, per-city error, confusion matrix,
  model comparison, hotspot summary, and map-data, matching real output files
  that weren't anticipated in the original spec.
- Switched station lookup key from `station_name` to `station_id` for
  URL-safety.

**v3 (post ML-lead fix pass, confirmed 2026-07-16):**
- Confirmed `final_aqi_model_metrics.json`'s `*_file` fields are now relative
  paths (Windows absolute paths fixed) — still strip them from the API
  response since they're implementation detail, not user-facing data.
- Confirmed `outputs/priority_ranking_ablation.csv` now exists as a real,
  well-built precomputed file. `/priority-queue/ablation` now reads this
  file directly instead of computing the comparison live.
- Confirmed `models/best_aqi_forecast_model.pkl` still does NOT exist,
  despite the JSON referencing it — this reference should be treated as
  permanently unreliable. Backend must resolve the best model dynamically
  (read `best_model` from the metrics JSON, map to
  `trained_forecasting_models/{stem}.pkl`) rather than depending on a
  dedicated "best model" file ever being created.
- Confirmed `station_id` is unique across all 500 rows with zero duplicates
  — safe to use as the primary lookup key.