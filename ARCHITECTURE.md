# CleanAir AI — Architecture Document
(For the "Architecture Diagram" expected deliverable — recreate this as a
visual slide in the pitch deck; this file is the source content.)

## Prototype Architecture (what we built for the hackathon)

```
DATA SOURCES
 ├─ data.gov.in CPCB Real-Time AQI API  (live, hourly)
 ├─ Open-Meteo API                       (live, no key required)
 ├─ Sentinel-5P via Google Earth Engine  (real, top-20 hotspot cities)
 └─ OpenStreetMap Overpass API           (land-use, road density)
        │
        ▼
INGESTION & FEATURE NOTEBOOKS (01–03)
 ├─ 01: fetch, clean, pivot, compute CPCB-standard AQI
 ├─ 02: weather join, weather-trapping score, OSM land-use/road join
 └─ 03: pollutant-signature source attribution, land-use cross-validation,
        multilingual advisory generation
        │
        ▼
PROCESSED DATA LAYER  (data/processed/*.csv)
        │
        ▼
ML LAYER (notebook 04)
 ├─ Time-based train/test split
 ├─ Persistence / Linear / RandomForest / HistGB / XGBoost
 ├─ Per-city + per-category evaluation, hotspot F1
 ├─ SHAP / native feature importance
 └─ RF-quantile confidence intervals
        │
        ▼
INTELLIGENCE LAYER (notebooks 05–06)
 ├─ Satellite proxy validation (real vs proxy correlation)
 ├─ Advanced Priority Score (weighted, explicit weights)
 └─ Naive-vs-advanced ranking ablation
        │
        ▼
SERVING LAYER
 ├─ FastAPI backend (backend/main.py)      — REST API, /docs Swagger
 └─ Streamlit dashboard (dashboard/app.py) — primary demo UI, 5 tabs
```

## Production Architecture (upgrade path, presented as "what's next")

```
React/Next.js Frontend  +  Streamlit (internal ops view)
        │
        ▼
FastAPI Gateway (auth, rate limiting)
        │
   ┌────┼─────────────┬─────────────┬──────────────┐
   ▼    ▼             ▼             ▼              ▼
AQI     Weather   ML Forecasting  Geospatial   Advisory &
Ingestion Service  Service         Intelligence  Intervention
Service (Airflow    (scheduled      Service       Service
(hourly  scheduled   retrain)       (full-coverage
cron)    pulls)                     Sentinel-5P +
                                     live traffic API)
   │    │             │             │              │
   └────┴─────────────┴─────────────┴──────────────┘
                        │
                        ▼
        PostgreSQL + PostGIS  +  Object Storage (S3/GCS)
                        │
                        ▼
              Docker + Kubernetes deployment
              Grafana/Prometheus monitoring
```

## Data Flow Summary (one paragraph, for the pitch deck)

Live AQI and weather data are ingested hourly, fused with real satellite and
geospatial signal for our highest-priority cities, and fed into a
time-series-safe ML pipeline that forecasts 24h-ahead AQI per station with
confidence intervals. A multi-factor priority score — validated against a
naive-AQI-only baseline — ranks stations for enforcement action, and
citizen-facing advisories are generated automatically in 7 languages. The
entire pipeline is served through a FastAPI backend and a Streamlit
dashboard built for city administrators, not just AQI display.
