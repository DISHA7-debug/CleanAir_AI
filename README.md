# CleanAir AI  
## AI-Powered Urban Air Quality Intelligence for Smart City Intervention

CleanAir AI is an end-to-end urban air-quality intelligence platform that moves beyond simple AQI dashboards. It collects real AQI data, enriches it with weather and geospatial proxy features, performs pollution source attribution, forecasts short-term AQI, ranks pollution hotspots, and recommends smart-city interventions.

The goal is to help city authorities answer:

- Where is pollution increasing?
- Which locations need immediate intervention?
- What is the likely source of pollution?
- Where should enforcement teams be deployed first?
- Which areas pose higher public-health risk?

---

## Problem Statement

India’s air pollution crisis is no longer limited to a few major cities. Many Tier 1 and Tier 2 cities now experience dangerous AQI levels due to vehicle emissions, construction activity, industrial pollution, biomass burning, and weather-based pollutant trapping.

Most AQI dashboards only answer:

> What is the AQI right now?

But city administrators need actionable intelligence. They need a system that converts raw AQI readings into decisions, priorities, and intervention plans.

CleanAir AI fills this gap by creating an AI-powered intelligence layer for smart city air-quality management.

---

## Proposed Solution

CleanAir AI transforms air-quality monitoring data into a complete decision-support system for urban authorities.

The platform performs:

- Live AQI data collection from CPCB/data.gov.in
- Weather and geospatial enrichment
- Pollution source attribution
- Short-term AQI forecasting
- Hotspot detection and ranking
- Health-risk and intervention-priority scoring
- Evidence-backed intervention recommendations
- Interactive hotspot map generation

Core idea:

> Instead of only showing pollution levels, CleanAir AI helps decide where to act, why to act, and what action to take.

---

## Key Features

### 1. Live AQI Data Fetching

- Fetches real AQI data from CPCB/data.gov.in
- Collects station, pollutant, location, city, state, and timestamp details
- Builds hourly station-wise AQI history
- Prevents duplicate timestamp entries

### 2. AQI Data Cleaning and Validation

- Cleans and standardizes pollutant records
- Handles missing and invalid AQI values
- Converts pollutant-level records into station-level AQI intelligence
- Adds AQI validity and quality flags

### 3. Weather and Geospatial Enrichment

- Integrates weather features using Open-Meteo API
- Adds temperature, humidity, rainfall, wind speed, cloud cover, and weather trapping features
- Creates geospatial proxy features such as:
  - Urban pressure score
  - Road density proxy
  - Environmental risk score

### 4. Pollution Source Attribution

The system estimates likely pollution source categories such as:

- Vehicular traffic
- Industrial combustion
- Construction / road dust
- Biomass / fine-particle combustion
- Photochemical smog
- Insufficient pollutant signal

It also generates confidence levels and intervention recommendations based on the likely source.

### 5. Multi-Model AQI Forecasting

CleanAir AI compares multiple machine-learning models:

- Persistence Baseline
- Linear Regression
- Ridge Regression
- Random Forest
- Extra Trees
- Gradient Boosting
- HistGradientBoosting
- XGBoost

Best model selected:

```text
Random Forest