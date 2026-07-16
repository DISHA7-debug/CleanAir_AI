# CleanAir AI Backend API

This directory contains the Python FastAPI backend service for the CleanAir AI platform, built to satisfy **Problem Statement 5: Smart Cities / Air Quality** for the ET AI Hackathon 2026.

## Overview
The backend acts as a high-performance REST serving layer that reads precomputed outputs directly from the ML pipeline files. No database is used. It features:
- **Automatic API documentation** via `/docs` (Swagger).
- **Graceful degradation** if files are missing (falling back to sample mock datasets when real files aren't populated yet).
- **Dynamic best-model resolution** from run configuration metrics.
- **Permissive CORS** for frontend client development.

## Setup Instructions

### 1. Prerequisites
Ensure you have Python 3.10+ installed.

### 2. Install Dependencies
Create a virtual environment and install the required libraries:
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment (macOS/Linux)
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 3. Run the Server
Run the FastAPI application locally using Uvicorn:
```bash
uvicorn backend.main:app --reload --port 8000
```
Once started, the Swagger API docs will be available at:
[http://localhost:8000/docs](http://localhost:8000/docs)

## Key Endpoints

- `GET /` — Health check & route index.
- `GET /stations` — List of all stations with optional `city` and `state` filters.
- `GET /stations/{station_id}` — Details for a specific station (looks up by URL-safe station_id).
- `GET /cities` — Summary metrics per city.
- `GET /priority-queue` — Ranked hotspot queue sorted by Advanced Priority Score.
- `GET /priority-queue/ablation` — Comparison of naive AQI ranking vs. advanced ranking.
- `GET /forecast/{station_id}` — 24h forecast and uncertainty bounds (p10/p50/p90).
- `GET /model/metrics` — Aggregate training statistics (with absolute paths stripped).
- `GET /advisory/{aqi_category}` — Citizen health advisories in English, Hindi, and 5 regional languages.
- `POST /refresh-live-aqi` — System endpoint to clear in-memory cache and reload latest pipeline outputs from disk.

## Implementation Notes
- **Fallback Data:** If real pipeline files under `data/processed/`, `outputs/`, or `models/` are not generated yet, the backend automatically serves mock rows from `backend/sample_data/` to prevent crashes.
- **Null Safety:** All CSV rows containing missing/empty cells are scrubbed and replaced with `None` to prevent JSON serialization errors.
