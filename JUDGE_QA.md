# Judge & Viva Q&A — CleanAir AI

Prepared answers for the questions most likely to come up. Read this the
night before the demo. Answer honestly — the whole design of this project
is to have a true, specific answer for every question rather than an
impressive-sounding vague one.

## Data & Architecture

**Q: Is there a backend, or is Streamlit doing everything?**
A: For the prototype both exist: a FastAPI backend (`backend/main.py`) serves
a proper REST API (visible at `/docs`), and the Streamlit dashboard consumes
processed files directly for demo resilience. In production, the dashboard
would call the API exclusively; the file-based fallback is a hackathon
pragmatism, not the target architecture.

**Q: Does it fetch real-time data?**
A: Yes — CPCB via data.gov.in (station AQI + pollutants) and Open-Meteo
(weather) are both live API calls, not cached/mocked. The Refresh button
re-fetches and recomputes the AQI-dependent layers.

**Q: Is the satellite data real or simulated?**
A: Real Sentinel-5P tropospheric NO2, pulled via Google Earth Engine, for our
top-20 highest-AQI cities. We validated our satellite/aerosol proxy score
against this real data and report the Pearson correlation
(`outputs/satellite_proxy_validation.csv`). Remaining ~480 stations use the
disclosed proxy; the architecture supports full Sentinel-5P coverage in
production (rate-limited by Earth Engine's free-tier quota, not a technical
limitation).

**Q: Is the mobility/traffic layer real traffic data?**
A: No — it's a proxy built from NO2/CO pollutant ratios plus real OSM road
density within 500m of each station. We do not claim live traffic API
integration. This is disclosed in the dashboard itself, not just in this doc.

## Machine Learning

**Q: How did you split train/test? Could this be leaking future data?**
A: Time-based split — train on the earliest 80% of the timeline, test on the
most recent 20%. We deliberately did NOT use a random shuffle split, because
that would leak future values into training via the lag/rolling features and
artificially inflate every metric. This is stated in `final_aqi_model_metrics.json`
under `train_test_split`.

**Q: Your RMSE is around 90-100 on a 0-500 scale — is that actually good?**
A: Point RMSE alone understates operational usefulness on this scale, which
is why we also report category-level accuracy (did we predict the correct
AQI bucket — Good/Moderate/Poor/etc.) and hotspot F1 (did we correctly flag
stations crossing into Poor+ in the next 24h). Those are the numbers that map
to what a city administrator actually acts on. [Insert your run's actual
category accuracy and F1 numbers here before presenting.]

**Q: Does the model perform the same across all cities?**
A: No, and we don't hide that — see `outputs/per_city_error.csv`. High-AQI-
variance cities like Delhi in winter are harder to forecast than more stable
cities; we report per-city RMSE specifically so this isn't averaged away.

**Q: What's actually driving the forecast — is it just persistence in
disguise?**
A: We report the feature-importance share coming from lag/rolling features
vs weather/geospatial features (`lag_feature_importance_share` in the metrics
JSON). [State your actual number.] If it's high, that's an honest finding —
persistence is a strong signal for AQI, and our model still beats the pure
persistence baseline by [X]% RMSE, meaning the additional features are adding
real value on top of it.

**Q: How confident is any single forecast?**
A: We use Random Forest's per-tree prediction spread to generate p10/p50/p90
confidence bands, shown in the dashboard as a shaded region around the point
forecast rather than a bare number.

## Priority Score & Enforcement

**Q: Is your priority score actually better than just ranking by current AQI?**
A: See the ablation table (`outputs/ablation_naive_ranking.csv` vs
`ablation_advanced_ranking.csv`, also in the dashboard's Priority Queue tab).
We show concretely which stations the advanced score surfaces that a naive
AQI ranking misses — typically stations with moderate current AQI but high
weather-trapping risk and a rising forecast trend, i.e. compound risk that's
invisible in a same-day snapshot.

**Q: What are the weights in the priority score, and why those values?**
A: Explicit and documented in notebook 05/06: 30% current AQI, 20% forecast
trend, 15% weather trapping, 15% satellite proxy, 10% mobility, 10%
attribution confidence. These are a reasonable starting allocation, not
empirically fit — in production they'd be calibrated against historical
enforcement outcomes or domain-expert review, which is explicitly named as
an upgrade path.

## Source Attribution

**Q: How do you know your source attribution is correct?**
A: Two ways: (1) it's grounded in standard pollutant-ratio chemistry
(NO2+CO → traffic, SO2 → industrial, PM10/PM2.5 ratio → dust vs combustion —
this is not arbitrary, it's how air-quality source apportionment is done in
the literature), and (2) we cross-validate against real OSM land-use context
and report an explicit agreement rate. We don't claim certainty — we report
a confidence score per attribution and flag disagreements rather than
silently trusting one signal.

## Scope & Honesty

**Q: What would you do differently with more time/data?**
A: Full Sentinel-5P coverage for all 503 stations (currently rate-limited to
top-20 by Earth Engine free-tier quota), a live traffic API integration to
replace the mobility proxy, official municipal GIS zoning layers instead of
OSM-derived land-use, and calibrating priority-score weights against real
historical enforcement outcomes instead of a reasoned initial allocation.
All of this is on the documented upgrade path (`docs/PROJECT_CONTEXT.md`,
section 9) — we scoped the prototype specifically around what could be built
on real (not fabricated) data in the hackathon window.

**Q: Why should a city trust this over what they already have?**
A: Most city dashboards show current AQI. We forecast it with quantified
uncertainty, attribute likely causes with a validated confidence score, and
rank where to intervene with an approach that's demonstrably better than
sorting by AQI alone — turning monitoring into a decision-support workflow.
