# CleanAir AI — Build Spec Package

**AI-Powered Urban Air Quality Intelligence for Smart City Intervention**
ET AI Hackathon 2026 — Problem Statement 5

This folder contains **context and specification documents only** — no
implementation code. Hand this whole folder to a coding agent (Claude Code,
Cursor, etc.) along with the instruction to build the project according to
these specs, in the order below.

## Read order

1. **PROJECT_CONTEXT.md** — master spec: pitch, requirement mapping,
   architecture overview, tech stack, repo structure, team/timeline
2. **ML_METHODOLOGY.md** — the reasoning behind every ML methodology choice
   (why time-based split, why per-city metrics, why uncertainty bands, etc.)
3. **ML_PIPELINE_SPEC.md** — concrete stage-by-stage build spec for the 6
   data/ML notebooks (inputs, steps, outputs for each)
4. **BACKEND_SPEC.md** — concrete API contract: endpoints, request/response
   shapes, data file dependencies, error handling
5. **FRONTEND_SPEC.md** — concrete UI spec: tabs, required content per tab,
   interaction rules, tone/disclosure rules
6. **ARCHITECTURE.md** — system diagram (prototype + production upgrade path)
7. **JUDGE_QA.md** — the "why" behind every design decision, framed as
   prepared answers to hackathon judge questions. Useful for the agent to
   understand *why* a spec requirement exists (e.g. why time-based split is
   non-negotiable) so it doesn't quietly simplify it away.

## One-sentence brief for the agent

Build a 6-stage data/ML pipeline (real CPCB + Open-Meteo + Sentinel-5P + OSM
data), a FastAPI backend serving its outputs, and a dashboard — all exactly
as specified in the docs above — optimizing throughout for **judge
defensibility**: every "real data" claim must be a genuine API call, every
proxy must be disclosed in the UI itself, ML evaluation must be time-split
with per-city/per-category breakdowns (not just pooled RMSE), and the
enforcement priority ranking must ship with an ablation table proving it beats
naive AQI sorting.

## Suggested build order for the agent

1. Data pipeline Stage 1 (`ML_PIPELINE_SPEC.md` Stage 1) — get real CPCB data
   flowing and cleaned first; everything else depends on this
2. Stages 2-3 — weather, geospatial, source attribution
3. Backend skeleton (`BACKEND_SPEC.md`) — can be built in parallel once Stage
   1 output schema is stable, using placeholder/partial data
4. Stage 4 — ML forecasting (the highest-scrutiny piece; needs accumulated
   history, see prerequisite note in ML_PIPELINE_SPEC.md)
5. Stages 5-6 — satellite validation, priority score, ablation, packaging
6. Frontend/dashboard (`FRONTEND_SPEC.md`) — wire up against the backend once
   real pipeline outputs exist, not against mocked data, so the demo is real
   end-to-end

## Non-negotiable constraints (do not let the agent simplify these away)

- Time-based train/test split for all ML evaluation (never random shuffle)
- Per-city AND per-AQI-category metrics reported, not only pooled RMSE
- Real Sentinel-5P satellite pull (via Google Earth Engine) for at least the
  top-20 hotspot cities — not a fully simulated satellite layer
- Every proxy/heuristic layer labeled as such in both code and UI
- Naive-vs-advanced priority ranking ablation table, saved as a real
  artifact, not just reasoned about in text
