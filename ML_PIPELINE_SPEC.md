# ML_PIPELINE_SPEC.md — CleanAir AI Data & ML Pipeline

For the implementing agent: build this as a sequence of 6 Jupyter notebooks
(or equivalent scripts), each with a single clear responsibility, each
reading the previous stage's output and writing its own output file(s) to
`data/processed/` or `outputs/`. Order matters — later notebooks depend on
earlier ones. See ML_METHODOLOGY.md for the underlying methodology reasoning;
this file is the concrete build spec.

## Stage 1 — `01_live_aqi_data_fetching`

**Input:** data.gov.in CPCB "Real Time Air Quality Index" API (needs free
API key, env var `CPCB_API_KEY`).

**Steps:**
1. Paginated fetch of all available station records.
2. Clean: coerce numeric fields, parse timestamps, drop rows with missing
   station/pollutant/value/timestamp, drop negative values.
3. Pivot from one-row-per-(station,pollutant) to one-row-per-(station,timestamp)
   with pollutant values as columns (PM2.5, PM10, NO2, SO2, CO, O3, NH3).
4. Compute CPCB-standard sub-index AQI per pollutant using official CPCB
   breakpoint tables, take the max sub-index as the station AQI, and record
   the dominant pollutant.
5. Bucket AQI into category: Good (0-50) / Satisfactory (51-100) / Moderate
   (101-200) / Poor (201-300) / Very Poor (301-400) / Severe (401+).
6. Include an offline-dev fallback path: if no API key is set, load a cached
   raw file if one exists, otherwise fail loudly with an instruction to set
   the key — never silently fabricate data.

**Output:** `data/processed/station_intelligence_latest.csv`
(station_name, city, state, lat, lon, timestamp, pollutant columns, aqi,
dominant_pollutant, aqi_category)

## Stage 2 — `02_weather_geospatial_integration`

**Input:** Stage 1 output + Open-Meteo API (free, no key) + OSM Overpass API
(free, rate-limited).

**Steps:**
1. Fetch current weather (temp, humidity, wind speed/direction, precipitation,
   pressure) per unique station lat/lon from Open-Meteo.
2. Compute `weather_trapping_score` (0-100): higher when wind is low, humidity
   is high, and temperature is low (Indian winter inversion pattern); lower
   with recent rainfall (washout effect). Document the exact formula used.
3. Convert wind direction to sin/cos components for later use as ML features.
4. Query OSM Overpass for road density and landuse tags within a buffer
   (e.g. 500m) of each station — for a manageable sample if the full station
   set would exceed Overpass's fair-use rate limits (batch/cache for full
   coverage before the actual hackathon).
5. Classify each station's landuse into: industrial / construction_dust /
   commercial / residential / mixed / unclassified, from real OSM tags where
   available.
6. For stations without real OSM coverage, apply a disclosed proxy fallback
   classification based on dominant pollutant (e.g. NO2/CO-dominant →
   "traffic_corridor_proxy"). The column name must make clear which stations
   used real vs proxy classification.

**Output:** `data/processed/station_weather_geospatial.csv`

## Stage 3 — `03_source_attribution_landuse`

**Input:** Stage 2 output.

**Steps:**
1. Attribute a likely pollution source per station using pollutant-ratio
   chemistry heuristics:
   - High NO2 + CO → Vehicular/Traffic
   - High SO2 → Industrial Combustion
   - High PM10 relative to PM2.5 (coarse) → Construction/Road Dust
   - High PM2.5 relative to PM10 (fine) → Combustion/Biomass
   - High O3 with low primaries → Photochemical Smog
   Compute a normalized confidence score for the winning attribution, not
   just a label.
2. Cross-validate the attribution against the land-use classification from
   Stage 2 — if they agree, mark "Confirmed by land-use"; if they disagree,
   mark "Disagreement — flagged for review" rather than silently trusting one
   signal. Compute and log the overall agreement rate — this number is
   required for judge defense (see JUDGE_QA.md).
3. Generate citizen health advisories per AQI category in at least English
   and Hindi (full text, all 6 categories) — see BACKEND_SPEC.md section 4
   for the complete language/content requirements.

**Output:** `data/processed/station_source_attributed.csv`

## Stage 4 — `04_ml_forecasting_models` (core notebook — highest scrutiny)

**Input:** Accumulated history of Stage 1-3 output over time (see note below)

**Critical prerequisite:** A single API snapshot cannot train a real
forecaster. This notebook must accumulate a rolling history file
(`station_aqi_history.csv`) that grows every time Stage 1 is re-run — Stage 1
should append-and-deduplicate into this history file. Instruct the team to
run Stage 1 hourly for several days before the hackathon to build real
history.

**Steps:**
1. Build lag features per station: AQI at t-1h, t-3h, t-6h, t-24h, t-48h;
   rolling mean/std over 6h and 24h windows; hour-of-day, day-of-week,
   is_weekend, month.
2. Define the target: AQI at t+24h per station (shift-based). Optionally
   also target t+72h as a stretch goal — only claim this publicly if it is
   actually evaluated with its own metrics, not just mentioned.
3. **Train/test split must be time-based**, not random shuffle: train on the
   earliest ~80% of the timeline, test on the most recent ~20%. This is
   mandatory — a random split leaks future values into training via lag
   features and invalidates every downstream metric.
4. Train and compare: Persistence baseline (predicted = current AQI),
   Linear Regression, Random Forest, HistGradientBoosting, XGBoost.
5. Compute for every model: MAE, RMSE, R², and % RMSE improvement over the
   persistence baseline.
6. Select best model by lowest test RMSE among non-baseline models.
7. Compute **per-city RMSE/MAE** (not just pooled) — required output, must
   not be skipped or averaged away.
8. Compute **per-AQI-category accuracy**: bucket both true and predicted
   values into the 6 AQI categories, report the % where predicted category
   matches true category, plus a full confusion matrix.
9. Compute **hotspot detection F1**: binary target = "will AQI exceed 200 in
   24h," report precision/recall/F1 for the best model.
10. Compute feature importance (native `.feature_importances_` for tree
    models, or `|coef_|` for linear) and save a chart. Report the fraction of
    total importance coming from lag/rolling features specifically — this is
    the "is it just persistence in disguise" honesty check.
11. Compute uncertainty bands: for Random Forest, use per-tree prediction
    spread to derive p10/p50/p90 quantiles per forecast. If the best model
    isn't Random Forest, either also fit a quantile-loss gradient booster for
    the confidence band, or clearly note that uncertainty bands are unavailable
    for the chosen model.
12. Save: trained model (`.pkl`), feature column list, full metrics report as
    JSON (must include: best_model, pooled metrics, category_accuracy,
    hotspot_f1, top-10 worst cities by RMSE, top-15 feature importances,
    lag_feature_importance_share, and a plain-text description of the
    train/test split methodology).

**Output:** `models/best_aqi_forecast_model.pkl`,
`outputs/final_aqi_model_metrics.json`, `outputs/aqi_model_comparison.csv`,
`outputs/per_city_error.csv`, `outputs/category_confusion_matrix.csv`,
`outputs/feature_importance.png`,
`data/processed/test_predictions_with_uncertainty.csv`

## Stage 5 — `05_advanced_intelligence_layers`

**Input:** Stage 3 output + Google Earth Engine (Sentinel-5P) + Stage 4
forecast (for trend risk, may be partially deferred to Stage 6).

**Steps:**
1. Identify the top ~20 cities by average AQI. For these cities only, pull
   **real** Sentinel-5P tropospheric NO2 column density via Google Earth
   Engine. This must be a genuine API call, not synthesized data.
2. Build a rule-based satellite/aerosol proxy score (0-100) for all stations,
   using AQI intensity + dominant pollutant + humidity.
3. Validate the proxy: compute Pearson correlation between city-average proxy
   score and real Sentinel-5P NO2 for the top-20 cities where both exist.
   This correlation number is required judge-defense evidence — save it to
   its own output file, don't bury it in a log.
4. Build a mobility pressure proxy (0-100) from NO2/CO ratios + OSM road
   density.
5. Define the Advanced Priority Score as an explicit weighted sum (document
   the exact weights used) of: normalized AQI, forecast trend risk, weather
   trapping score, satellite proxy, mobility proxy, attribution confidence.
6. **Ablation (required):** produce a table of the top-10 stations ranked by
   AQI alone (naive) vs top-10 ranked by the Advanced Priority Score, and
   identify which stations appear only in the advanced ranking. This is
   direct evidence for "is your enforcement ranking actually better than
   sorting by AQI" — must be saved as its own output, not just computed
   in-memory and discarded.

**Output:** `outputs/satellite_proxy_validation.csv`,
`outputs/ablation_naive_ranking.csv`, `outputs/ablation_advanced_ranking.csv`,
`data/processed/station_advanced_intelligence.csv`

## Stage 6 — `06_evaluation_ablation_packaging`

**Input:** All prior stage outputs.

**Steps:**
1. Merge the Stage 4 forecast into the priority score to compute a genuine
   `trend_risk` factor (forecast AQI minus current AQI, normalized) —
   replacing any placeholder trend value used in Stage 5.
2. Recompute the final Advanced Priority Score with trend risk included, and
   produce the final sorted intervention queue.
3. Produce a city-level risk summary (avg/max AQI, avg priority score,
   dominant source per city).
4. Auto-generate a requirement-coverage matrix mapping every PS5 requirement
   (monitoring data, satellite, mobility, weather, land-use, source
   attribution, forecasting, enforcement, citizen advisory) to its
   implementation status (Real / Real-partial / Proxy) and evidence file —
   this must match what's actually true in the pipeline, not be aspirational.
5. Auto-generate a demo script text file referencing the actual computed
   metrics (best model name, category accuracy, hotspot F1) rather than
   hardcoded placeholder numbers.

**Output:** `data/processed/final_intervention_priority_queue.csv`,
`data/processed/city_risk_summary.csv`,
`reports/problem_statement_coverage_matrix.csv`, `reports/demo_script.txt`

## Cross-cutting requirements for every stage

- Every notebook must run standalone from a fresh kernel given its input
  files present — no hidden in-memory state carried between notebooks outside
  of saved files.
- Every claim of "real data" must correspond to an actual external API call
  in that stage's code, not a hardcoded/simulated value.
- Every proxy/fallback must be labeled as such in the output column names or
  a companion flag column, not indistinguishable from real-derived values.
