# BACKEND_SPEC.md — CleanAir AI Backend

For the implementing agent: build a FastAPI backend matching this spec exactly.
Do not invent additional endpoints beyond what's listed unless something here
is genuinely ambiguous — flag ambiguity rather than guessing silently.

## 1. Tech choice

- **Framework:** FastAPI (Python), served via Uvicorn
- **Storage (prototype):** flat files — CSV/Parquet in `data/processed/`, JSON
  in `outputs/`, produced by the ML notebooks (see `ML_PIPELINE_SPEC.md`).
  No database required for the hackathon build.
- **Storage (if time allows / stretch):** SQLite or PostgreSQL, with the
  notebooks writing to tables instead of files. Not required for MVP.
- Auto-generated Swagger docs must be reachable at `/docs`.
- Enable permissive CORS for local dashboard/frontend development.

## 2. Data contracts (what files the backend reads)

The backend does NOT compute intelligence itself — it only reads the output
of the ML/data pipeline (see ML_PIPELINE_SPEC.md) and serves it. Expected
input files (all in `data/processed/` unless noted):

| File | Produced by | Contains |
|---|---|---|
| `final_intervention_priority_queue.csv` | pipeline stage 6 | one row per station: aqi, category, source, priority score, all layers |
| `city_risk_summary.csv` | pipeline stage 6 | one row per city: avg/max AQI, dominant source, avg priority |
| `test_predictions_with_uncertainty.csv` | pipeline stage 4 | station-level 24h forecast + p10/p50/p90 |
| `outputs/final_aqi_model_metrics.json` | pipeline stage 4 | full ML evaluation report |
| `outputs/per_city_error.csv` | pipeline stage 4 | per-city RMSE/MAE breakdown |
| `outputs/ablation_naive_ranking.csv` / `ablation_advanced_ranking.csv` | pipeline stage 5 | naive-vs-advanced ranking comparison |
| `outputs/satellite_proxy_validation.csv` | pipeline stage 5 | real-vs-proxy satellite correlation data |

If a file is missing, the corresponding endpoint should return a clear 404
with a message telling the caller which pipeline notebook to run — not a
silent empty response.

## 3. Endpoints

### `GET /`
Health check. Returns service name, status, and list of available endpoints.

### `GET /stations`
List stations with current intelligence.
- Query params: `city` (optional, case-insensitive filter), `state` (optional),
  `limit` (default 100, max 1000)
- Returns: `{ count, stations: [ {station_name, city, state, lat, lon, aqi,
  aqi_category, dominant_pollutant, attributed_source, attribution_confidence,
  weather_trapping_score, satellite_aerosol_proxy, mobility_pressure_proxy,
  final_priority_score} ] }`

### `GET /stations/{station_name}`
Single station detail (full row from priority queue file). 404 if not found.

### `GET /cities`
List all cities with summary stats (from `city_risk_summary.csv`).

### `GET /cities/{city}`
Single city detail. 404 if not found.

### `GET /forecast/{station_name}`
24h-ahead AQI forecast with confidence band.
- Returns: `{ station_name, current_aqi, forecast_24h_p10, forecast_24h_p50,
  forecast_24h_p90, forecast_category }`
- 404 if no forecast data exists for the station.

### `GET /model/metrics`
Full ML evaluation report — passthrough of `final_aqi_model_metrics.json`.
Must include: best_model name, pooled RMSE/MAE/R², category_accuracy,
hotspot_f1, top_10_worst_cities_by_rmse, top_15_feature_importance,
lag_feature_importance_share, train_test_split description.

### `GET /priority-queue`
Ranked enforcement priority list.
- Query param: `top_n` (default 20, max 500)
- Returns: `{ count, queue: [...] }` sorted by `final_priority_score` descending.

### `GET /priority-queue/ablation`
Returns naive-AQI-only ranking vs advanced-priority ranking, plus the diff:
`{ naive_ranking, advanced_ranking, newly_surfaced_by_advanced_score,
dropped_by_advanced_score }`. This is judge-facing evidence — must not be
dropped or simplified.

### `GET /advisory/{aqi_category}`
- Query param: `lang` — one of `en, hi, ta, kn, bn, mr, te`
- Returns: `{ aqi_category, language, advisory }`
- 404 for unrecognized category. Unrecognized language should fall back to `en`
  rather than erroring.

### `POST /refresh-live-aqi`
Triggers a live re-fetch from the CPCB API for current station AQI values +
recomputes AQI category and priority score. Does NOT re-run the full pipeline
(satellite/OSM layers stay as last-computed) — document this limitation in
the endpoint's docstring so it surfaces in `/docs`, and the frontend should
show this caveat too (see FRONTEND_SPEC.md).
- Returns: `{ status: "refreshed", stations_updated: <int> }`

## 4. Advisory content requirements

The advisory service must ship complete text (not placeholders) for all 6 AQI
categories (Good / Satisfactory / Moderate / Poor / Very Poor / Severe) in
English and Hindi at minimum. The remaining 5 languages (Tamil, Kannada,
Bengali, Marathi, Telugu) should be included but may be machine-translated —
mark this clearly in code comments as "needs native-speaker review before
demo," don't silently present them as equally vetted.

## 5. Error handling requirements

- Missing data files → 404 with actionable message (which notebook to run)
- Malformed query params → 422 (FastAPI default is fine)
- Any endpoint that depends on a live external API (refresh) → catch and
  return 500 with the underlying error message, don't crash the server

## 6. Non-goals for this backend (explicitly out of scope)

- No authentication/authorization — not needed for a hackathon demo
- No write/edit endpoints beyond the refresh trigger
- No database migrations — file-based storage is intentional for MVP
- No websocket/streaming — polling via the refresh button is sufficient
