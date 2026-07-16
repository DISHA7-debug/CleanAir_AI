# ML Methodology — CleanAir AI

## 1. Problem Framing

**Task:** Given a station's historical AQI + pollutant + weather time series, predict AQI at t+24h (and t+72h as stretch) for that station.

**Type:** Supervised regression (point forecast) + quantile regression (uncertainty band) + derived classification (AQI category bucket, for operational accuracy reporting).

**Unit of prediction:** station-hour. Each row = one station at one timestamp, with lag/rolling features and a target `aqi_t+24h`.

## 2. Data Sources & Refresh

| Source | What | Frequency | Access |
|---|---|---|---|
| data.gov.in CPCB real-time AQI | Station AQI, PM2.5, PM10, NO2, SO2, CO, O3, NH3 | Hourly (station-dependent) | Free API key, resource ID for "Real Time Air Quality Index" |
| Open-Meteo | Temp, humidity, wind speed/direction, precipitation, boundary layer height | Hourly, historical + forecast | Free, no key |
| Sentinel-5P (via Google Earth Engine) | NO2 tropospheric column, aerosol index | Daily, ~7km resolution | Free GEE account, `earthengine-api` |
| OSM Overpass | Land-use polygons, road density within buffer | Static (refresh monthly) | Free, no key |

## 3. Feature Engineering

**Temporal features (per station):**
- Lag features: AQI at t-1h, t-3h, t-6h, t-24h, t-48h
- Rolling stats: 6h/24h/72h rolling mean, std, max of AQI and PM2.5
- Time features: hour-of-day, day-of-week, is_weekend, month (seasonal signal — critical for Indian AQI which has strong winter/Diwali spikes)

**Weather features:**
- Temperature, relative humidity, wind speed, wind direction (as sin/cos), precipitation, pressure
- Derived: `weather_trapping_score` = f(low wind, high humidity, temperature inversion proxy) — higher score means pollutants accumulate rather than disperse

**Geospatial features:**
- Land-use classification within 1km buffer (traffic corridor / industrial / residential / construction / mixed) from OSM tags
- Road density within 500m (proxy for traffic pressure)
- Distance to nearest industrial zone

**Satellite features (top-20 hotspot cities only, real data):**
- Sentinel-5P NO2 tropospheric column (daily)
- Aerosol index

**Pollutant signature features:**
- Ratio of PM2.5/PM10 (fine vs coarse — indicates combustion vs dust)
- NO2/CO ratio (traffic signature)
- SO2 presence (industrial signature)

## 4. Models Compared

| Model | Why included |
|---|---|
| Persistence baseline | Mandatory sanity check — "AQI in 24h ≈ AQI now." Any real model must beat this meaningfully. |
| Linear Regression | Interpretable floor |
| Random Forest | Handles nonlinearity, gives feature importance + variance-based uncertainty for free |
| XGBoost | Typically strongest on tabular time-series-with-lags data |
| HistGradientBoosting | Fast, handles missing values natively (CPCB data has gaps) |
| Quantile Random Forest (10th/50th/90th percentile) | Confidence intervals on every forecast |

## 5. Evaluation Protocol (this is the key upgrade over v1)

Do **not** report only pooled RMSE/R². Report:

1. **Pooled RMSE/MAE/R²** — headline number, but framed as "across all 503 stations, all conditions"
2. **Per-city RMSE** — table for top 10 highest-AQI-variance cities (Delhi, Mumbai, Kolkata, Lucknow, Patna, etc.) — expect meaningfully different numbers per city; explain why (seasonal patterns, station density, missing data rates)
3. **Per-AQI-category accuracy** — bucket both true and predicted AQI into (Good/Satisfactory/Moderate/Poor/Very Poor/Severe) and report confusion matrix + category accuracy. This is the number that maps to what a city administrator actually cares about.
4. **Hotspot F1** — binary target: "will AQI cross into Poor (>200) in next 24h?" — precision/recall/F1
5. **Baseline improvement %** — `(RMSE_persistence - RMSE_model) / RMSE_persistence * 100`
6. **Train/test split** — time-based split (train on first 80% of timeline, test on last 20%) — NEVER random-shuffle split for time series, that leaks future into past and inflates metrics artificially. This is a common judge trap question.

## 6. Explainability

- **Feature importance** (native, from RF/XGBoost `.feature_importances_`)
- **SHAP summary plot** — top 15 features, shown per model, exported to `outputs/shap_summary.png`
- Narrative: identify whether the model is "mostly persistence-driven" (lag features dominate — expected and fine, but must be disclosed) vs genuinely using weather/geospatial signal. State this honestly in the pitch — judges respect honesty about what's driving the number more than an inflated claim.

## 7. Uncertainty Quantification

Random Forest gives per-tree predictions — use the spread across trees (or `sklearn`'s `GradientBoostingRegressor` with quantile loss at q=0.1/0.5/0.9) to generate a confidence band around every forecast. Displayed in dashboard as a shaded region around the forecast line, not just a point estimate.

## 8. Priority Score & Ablation

**Advanced Priority Score** = weighted combination of:
- Current AQI (normalized)
- Forecasted 24h AQI trend (rising/falling)
- Weather trapping score
- Satellite/mobility/land-use risk proxies
- Population exposure proxy (city population × vulnerable population share, if available)

**Ablation validation (mandatory for judge defense):**
Build a table: Top-10 stations by naive AQI-only ranking vs Top-10 by advanced priority score. For every station that changes rank, write one sentence explaining why (e.g., "Station X has moderate AQI today but weather trapping + rising trend pushes it to #3 — naive ranking would miss this until it's already severe"). This directly answers the PS5 evaluation criterion: "enforcement recommendation quality rated by domain experts."

## 9. What Honest Judges Will Ask (and pre-built answers)

| Question | Answer to have ready |
|---|---|
| "Is this real satellite data or fake?" | "Real Sentinel-5P via Google Earth Engine for our top 20 hotspot cities — validated with Pearson correlation r=X against ground PM readings. Remaining stations use a proxy, disclosed openly, architecture supports full-coverage in production." |
| "How do you know it's not overfitting?" | "Time-based train/test split, not random — no future leakage. We report per-city and per-category metrics, not just pooled, specifically to avoid hiding overfitting behind an averaged number." |
| "Why RMSE ~90-100 when AQI range is 0-500?" | "That's why we also report category accuracy — X% of predictions land in the correct AQI bucket, which is what actually drives an intervention decision. Point RMSE alone understates operational usefulness." |
| "Is your priority score actually better than just sorting by AQI?" | Show the ablation table. |
