# AI Productivity Framework - Copilot Instructions

## Project Overview
A Master's thesis PoC for measuring AI-assisted development productivity. Three-tier architecture: SQLite database → FastAPI backend → React frontend.

## Architecture

### Data Flow
```
CSV files (semicolon-delimited) → data_ingestor.py → SQLite DB → FastAPI API → React frontend
```

### Key Components
- **Database**: SQLite (`productivity_framework.db`) with `projects` and `observations` tables
- **Backend**: FastAPI app in [main.py](main.py), routes in [api/routes.py](api/routes.py)
- **Frontend**: React app in `frontend/` using Recharts for visualization
- **Services**: Metric calculations in [services/metrics_calculator.py](services/metrics_calculator.py), CPS in [services/cps_calculator.py](services/cps_calculator.py)

## Critical Patterns

### Observation Types vs Metric Types
Raw data uses `ObservationType` (e.g., `DEPLOYMENT`, `COMMIT`, `AI_SUGGESTION_RESULT`). Calculated metrics use `MetricType` (e.g., `DEPLOYMENT_FREQUENCY`, `AI_ACCEPTANCE_RATE`). Both enums are in [models/enums.py](models/enums.py).

### Z-Score Normalization
All metrics are normalized to z-scores for comparison. Some metrics are **inverted** (lower = better): `CHANGE_FAILURE_RATE`, `MEAN_TIME_TO_RECOVER`, `LEAD_TIME_FOR_CHANGES`, `AI_REWORK_RATE`. Check `MetricType.is_inverted_metric()` before adding new metrics.

### Composite Productivity Score (CPS)
Weighted sum of z-scores: `CPS = Σ(weight × z_score)`. Weights are user-specified (0-1). Implementation in [services/cps_calculator.py](services/cps_calculator.py).

### Adding New Metrics
1. Add observation type to `ObservationType` enum if needed
2. Add metric type to `MetricType` enum with description
3. Implement calculator function in `services/metrics_calculator.py`
4. Register in `calculators` dict in `calculate_metric()` function
5. Mark as inverted in `is_inverted_metric()` if lower is better

## Developer Workflow

### Setup (Windows)
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python init_database.py
python data_ingestor.py
```

### Running
```powershell
# Backend (from project root)
python -m uvicorn main:app --reload

# Frontend (separate terminal)
cd frontend
npm install
npm start
```
Backend: `http://localhost:8000`, Frontend: `http://localhost:3000`

## Data Format
CSV files use **semicolon delimiter** (European format). Timestamps: `YYYY-MM-DD HH:MM:SS` or ISO 8601.

### Simulated Data
All data is **simulated** for thesis purposes. The database is always generated fresh by running:
1. `python init_database.py` - Creates empty tables
2. `python data_ingestor.py` - Loads CSV data into database

Data in [data_projects.csv](data_projects.csv) and [data_observations.csv](data_observations.csv) mirrors what's in the database. When querying or testing, assume CSV contents are available in the DB.

### Data Story
- **Project 1 & 2**: Imaginary projects with 5 developers each, high DORA metrics performers
- **2025 data**: Identical for both projects (includes some late 2024 rows). Project 1 is complete; Project 2 is WIP
- **2026 AI adoption story (Project 1)**:
  - Team adopts AI tools from January 2026
  - `LINES_OF_CODE_AI` stays steady; ~60% of 2026 code is AI-generated
  - `AI_ACCEPTANCE_RATE` starts high but drops as team learns appropriate trust levels
  - `AI_REWORK_RATE` spikes early (over-trusting AI), then stabilizes
  - Overall productivity improves after finding the right human-AI balance

## API Conventions
- All endpoints accept `project_id` as required query parameter
- Timestamps normalized internally to SQLite format (`YYYY-MM-DD HH:MM:SS`)
- `/metrics` endpoint supports multiple metric types (comma-separated) and time intervals
- Correlations calculated automatically when multiple metrics and intervals > 1

## Frontend Notes
- Simple React app with hooks (no Redux, no client-side routing)
- API base URL hardcoded in [frontend/src/App.js](frontend/src/App.js) as `http://localhost:8000`
- Project selection persists via React state in `App.js`
- Charts use Recharts library

## Project Scope
This is a **PoC project** - no unit tests, local deployment only. Manual testing via Swagger UI at `http://localhost:8000/docs`.
