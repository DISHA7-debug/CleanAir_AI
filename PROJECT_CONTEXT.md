# CleanAir AI — Master Project Context
### AI-Powered Urban Air Quality Intelligence for Smart City Intervention
**ET AI Hackathon 2026 — Problem Statement 5**

---

## 1. One-Line Pitch

CleanAir AI moves cities from passive AQI monitoring to proactive pollution **forecasting, source attribution, and enforcement intervention** — with every number traceable to real public data and every claim defensible under judge questioning.

## 2. Why This Version Is Different From v1

The previous prototype (RMSE 100.3, R² 0.73, pooled across 503 stations) was solid but had five defensible weaknesses. This rebuild fixes all five as first-class features, not afterthoughts:

| Weakness in v1 | Fix in v2 |
|---|---|
| Pooled RMSE hides per-city variance | Per-city AND per-AQI-category error reporting built into the pipeline from day 1 |
| No feature importance / explainability | SHAP + native feature importance on every trained model, surfaced in dashboard |
| Proxy layers had no validation | Satellite proxy validated against real Sentinel-5P AOD for top hotspot cities; correlation reported |
| No uncertainty on forecasts | Quantile Random Forest / tree-variance confidence intervals on every prediction |
| Priority score not benchmarked | Ablation study: naive AQI-only ranking vs. advanced multi-factor ranking, with concrete "what changed and why" cities |

## 3. Problem Statement Requirement Mapping

| PS5 Requirement | Our Implementation | Data Source (Real) |
|---|---|---|
| Monitoring station data | Live ingestion, cleaning, aggregation | data.gov.in CPCB real-time AQI API |
| Satellite imagery | Real Sentinel-5P NO2/AOD for top-20 hotspot cities; proxy fallback for remainder | Google Earth Engine (Copernicus S5P), free tier |
| Mobility feeds | NO2/CO-derived traffic pressure proxy, validated against OSM road density | OpenStreetMap Overpass API (road density) + pollutant ratios |
| Meteorological forecasts | Wind, humidity, temp, precip, boundary-layer proxy | Open-Meteo API (free, no key) |
| Geospatial land-use layers | OSM land-use tags (industrial/residential/commercial) within 1km buffer of each station | OpenStreetMap Overpass API |
| Source attribution | Dominant-pollutant-signature classifier + land-use cross-validation | Derived from CPCB pollutant breakdown |
| Hyperlocal AQI forecasting | 24h and 72h ahead, per-station, with confidence intervals | Trained on historical CPCB time series |
| Enforcement intelligence | Multi-factor priority score + ablation-validated ranking | Derived |
| Citizen advisory | Multilingual (7 languages), AQI-category-triggered, health-vulnerability-aware | Rule-based + LLM-polished copy |

## 4. System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  DATA LAYER                                                   │
│  CPCB AQI API │ Open-Meteo │ Sentinel-5P (GEE) │ OSM Overpass │
└───────────────────────┬───────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  INGESTION & FEATURE PIPELINE  (notebooks 01–05)              │
│  Clean → Aggregate → Weather join → Geospatial join →         │
│  Lag/rolling features → Source attribution → Land-use proxy   │
└───────────────────────┬───────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  ML LAYER  (notebook 04, 06)                                  │
│  RandomForest / XGBoost / HistGB / Linear (baseline: persist) │
│  → per-city + per-category metrics → SHAP → quantile CI       │
└───────────────────────┬───────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  INTELLIGENCE LAYER                                            │
│  Priority scorer → Ablation validator → Advisory generator     │
└───────────────────────┬───────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  SERVING LAYER                                                 │
│  FastAPI backend (REST) ──► Streamlit dashboard (primary demo) │
│                          └─► React widgets (optional, judges)  │
└─────────────────────────────────────────────────────────────┘
```

### Prototype vs Production
- **Prototype (this build):** Streamlit + FastAPI, file-based (CSV/Parquet/pkl) storage, notebook-driven pipeline, runs locally or on Streamlit Cloud.
- **Production path:** FastAPI services split into microservices (ingestion / ML / geospatial / advisory), PostgreSQL + PostGIS, scheduled Airflow/Cron refresh, Docker + cloud deploy, real-time Sentinel-5P pipeline for all stations (not just top-20).

## 5. Tech Stack

| Layer | Tools |
|---|---|
| Language | Python 3.11 |
| Data processing | Pandas, NumPy, GeoPandas |
| ML | scikit-learn (RandomForest, quantile variant), XGBoost, HistGradientBoosting, SHAP |
| Geospatial | GeoPandas, Shapely, Folium, GEE Python API (earthengine-api) |
| Backend API | FastAPI, Uvicorn, Pydantic |
| Dashboard | Streamlit, Plotly, Folium/streamlit-folium |
| Storage | CSV/Parquet (prototype) → PostgreSQL/PostGIS (production) |
| Data sources | data.gov.in CPCB API, Open-Meteo, Sentinel-5P via Google Earth Engine, OSM Overpass |

## 6. Repository Structure

```
CleanAir_AI/
├── docs/
│   ├── PROJECT_CONTEXT.md          (this file)
│   ├── ML_METHODOLOGY.md
│   ├── ARCHITECTURE.md
│   └── JUDGE_QA.md
├── notebooks/
│   ├── 01_live_aqi_data_fetching.ipynb
│   ├── 02_weather_geospatial_integration.ipynb
│   ├── 03_source_attribution_landuse.ipynb
│   ├── 04_ml_forecasting_models.ipynb
│   ├── 05_advanced_intelligence_layers.ipynb
│   └── 06_evaluation_ablation_packaging.ipynb
├── backend/
│   ├── main.py                     (FastAPI app)
│   ├── models.py                   (Pydantic schemas)
│   ├── services/
│   │   ├── aqi_service.py
│   │   ├── forecast_service.py
│   │   ├── priority_service.py
│   │   └── advisory_service.py
│   └── requirements.txt
├── dashboard/
│   └── app.py                      (Streamlit dashboard)
├── data/{raw,processed}/
├── models/
├── outputs/
├── reports/
├── requirements.txt
└── README.md
```

## 7. Key Metrics to Present (targets, validated in notebook 06)

- **RMSE / MAE / R²** — pooled AND per-city AND per-AQI-category
- **Baseline improvement %** — vs. persistence model (must be clearly positive and stated honestly)
- **Category accuracy** — % of predictions in the correct AQI bucket (Good/Satisfactory/Moderate/Poor/Very Poor/Severe) — this is the operationally meaningful number
- **Hotspot detection F1** — precision/recall on "will this station cross into Poor+ in next 24h"
- **Feature importance** — top 10 features per model, SHAP summary plot
- **Satellite proxy validation** — Pearson correlation between proxy score and real Sentinel-5P AOD for validated cities
- **Priority score ablation** — table showing top-10 naive-AQI ranking vs top-10 advanced ranking, with the concrete reasoning for reordering

## 8. Team Division of Labor (suggested for 1-week build)

| Owner | Workstream | Notebooks/Files |
|---|---|---|
| ML lead | Data pipeline, feature engineering, model training, evaluation, SHAP | 01, 02, 04, 06 |
| Geospatial/backend lead | Satellite/OSM integration, source attribution, priority score, FastAPI | 03, 05, backend/ |
| Frontend/demo lead | Streamlit dashboard, maps, advisory UI, demo script, PPT | dashboard/, reports/ |

## 9. One-Week Build Timeline

- **Day 1–2:** Data ingestion (CPCB, Open-Meteo), cleaning, EDA, baseline persistence model
- **Day 2–3:** Feature engineering (lag/rolling/weather/geospatial), source attribution, land-use proxy
- **Day 3–4:** Train + compare ML models, per-city/per-category evaluation, SHAP
- **Day 4–5:** Satellite (GEE) integration for top hotspot cities, priority score + ablation, advisory generation
- **Day 5–6:** FastAPI backend, Streamlit dashboard wiring, end-to-end test
- **Day 6–7:** Polish, demo script, PPT, architecture diagram, rehearse judge Q&A

## 10. What NOT to overclaim (judge-safety)

- Say "24h and 72h forecast" only if both horizons are actually evaluated with metrics — don't just mention 72h in the pitch without a number behind it.
- Satellite: say "real Sentinel-5P data validated for our top-20 hotspot cities; proxy-extrapolated for remaining stations, architecture supports full-coverage in production."
- Mobility: say "OSM road-density + pollutant-ratio proxy, not live traffic API" unless you actually integrate a live traffic feed.
- Priority score: back every claim with the ablation table — never say "more accurate" without showing the naive-vs-advanced comparison.
