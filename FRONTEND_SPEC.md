# FRONTEND_SPEC.md — CleanAir AI Dashboard

For the implementing agent: this defines what the demo-facing UI must show
and why. The framework choice is flexible (Streamlit is fastest to build and
is the recommended default for a 1-week hackathon; a React frontend is a
stretch goal if time allows — see section 6). Everything below describes
required content and behavior, not a specific tech stack.

## 1. Purpose

This is the primary judge-facing artifact. It must read as a **decision-support
tool for a city administrator**, not a raw AQI display. Every screen should
answer "so what should I do about this" not just "here's a number."

## 2. Global layout

- **Sidebar filters:** State → City → Station (cascading dropdowns), plus a
  language selector for advisories (en/hi/ta/kn/bn/mr/te).
  Also include a **"Refresh Live AQI"** button that calls the backend's
  `POST /refresh-live-aqi` and reloads the view.
- **Header metrics strip:** total monitoring stations, cities covered,
  states/UTs covered, current highest AQI station (name + value).
- **Data provenance footer/banner:** must be visible somewhere persistent —
  "Live CPCB (data.gov.in) · Open-Meteo · Sentinel-5P (top-20 cities) · OSM" —
  so judges see the pipeline is grounded in real sources without having to ask.

## 3. Required tabs/sections

### Tab 1 — Live Intelligence
For the filtered station(s), show a card per station with:
- Station name, city, state
- AQI value + colored category badge (Good=green, Satisfactory=yellow-green,
  Moderate=yellow, Poor=orange, Very Poor=red, Severe=purple)
- Dominant pollutant
- Attributed pollution source (with confidence indicator)
- Final priority score
- Citizen advisory text in the selected language, visually distinct (e.g. an
  info callout box)

### Tab 2 — Maps & Hotspots
- An interactive map (Folium/Leaflet or equivalent) with one marker per
  station, colored by AQI category, marker size scaled by priority score.
  Clicking/hovering shows station name + AQI + category in a popup.
- A bar chart of the top 15 stations nationally by current AQI.

### Tab 3 — Advanced Layers
- A clearly worded **data provenance disclosure** at the top of this tab
  specifically (not just the footer) — satellite is real for top-20 cities,
  proxy elsewhere; mobility and land-use are proxies. This disclosure text
  must not be watered down or removed — it is load-bearing for judge trust.
- Show the real-vs-proxy satellite correlation number (from
  `satellite_proxy_validation.csv`) as a headline metric.
- Three summary metrics: average satellite proxy, average mobility proxy,
  average weather trapping score (for the current filter).
- A land-use classification breakdown (pie or bar chart).

### Tab 4 — ML Forecasting
This tab exists specifically to survive judge scrutiny. It must show, not
just the flattering pooled number:
- Best model name, headline metrics (RMSE/MAE/R²)
- **Category accuracy** (% of 24h-ahead predictions in the correct AQI
  bucket) — displayed prominently, this is the operationally meaningful number
- **Hotspot detection F1** (AQI>200 in 24h)
- The train/test split methodology description (must say "time-based split,"
  this is non-negotiable — do not let an agent quietly implement random-split
  and describe it as time-based)
- Model comparison table (all models tried, including the persistence
  baseline, with % improvement over baseline)
- **Per-city error table** — do not average this away, must be a visible
  table or chart, not just a footnote
- Feature importance chart (bar chart, top ~15 features)
- The lag-feature-importance-share number, with a one-line explanation of
  why it matters ("how much of the forecast is essentially persistence")

### Tab 5 — Data Tables & Priority Queue
- Sortable/filterable table of the full intervention priority queue, with a
  CSV download button
- **Ablation display: naive AQI-only ranking vs advanced priority ranking,
  side by side.** This is required, not optional — it's the direct answer to
  "is your ranking actually better than sorting by AQI." Include a caption
  identifying which stations only appear in the advanced ranking and a
  one-line reason category (e.g. "high weather-trapping + rising trend").
- City-level risk summary table

## 4. Interaction requirements

- All filters (state/city/station/language) must actually filter every tab's
  content, not just Tab 1.
- The Refresh button must give visible feedback (spinner/toast) and reload
  data after completion, not fail silently.
- Numbers should never render as blank/NaN in the UI without a fallback —
  e.g. "Model metrics not available — run notebook 04 first" rather than a
  crash or empty chart.

## 5. Tone/content rules for anything user-facing

- Never state a claim more strongly than the underlying data supports (see
  JUDGE_QA.md and PROJECT_CONTEXT.md section 10 "what not to overclaim").
- Any proxy layer shown in the UI must be labeled as a proxy in the UI text
  itself, not only in developer docs.
- Advisory copy must be genuinely actionable per category (see
  BACKEND_SPEC.md section 4 for required content), not generic filler.

## 6. Optional stretch: React frontend

If time allows beyond the Streamlit build, a React app can replace the
dashboard for a more polished look, calling the same FastAPI backend
endpoints (see BACKEND_SPEC.md). All five tabs/sections above still apply as
content requirements — a React version is a visual upgrade, not a scope
change. Do not attempt this until the Streamlit version (or equivalent MVP)
is fully working end-to-end with real pipeline data.
