# AI Productivity Framework

A PoC framework for measuring AI productivity. Implemented as part of my Master's thesis.

## Overview

This framework provides a system for collecting, storing, and analyzing productivity metrics related to AI-assisted development. It includes:

- SQLite database for storing observations organized by projects
- Data ingestion pipeline for CSV data
- REST API built with FastAPI for querying metrics
- React frontend with project selection

## Metrics Tracked

- **SATISFACTION**: Developer satisfaction scores (1-5 scale)
- **RETENTION**: Team retention rate (0-1 scale)
- **DEPLOYMENT_FREQUENCY**: Number of deployments per day
- **LINES_OF_CODE**: Lines of code written per day
- **AMOUNT_OF_COMMITS**: Number of commits per day
- **AI_ACCEPTANCE_RATE**: Rate of AI suggestions accepted (0-1 scale)

## Project Structure

```
productivity_framework/
├── init_database.py      # Database initialization script
├── data_ingestor.py      # Data ingestion script
├── main.py               # FastAPI application
├── data_projects.csv     # Project data
├── data_observations.csv # Observation data
├── requirements.txt      # Python dependencies
├── frontend/             # React frontend
└── README.md            # This file
```

## Setup Instructions

### 1. Create a Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install fastapi uvicorn
```

Or if you want to use the requirements.txt (note: versions may need adjustment for Python 3.14+):
```bash
pip install -r requirements.txt
```

### 3. Initialize the Database

```bash
python init_database.py
```

This will create `productivity_framework.db` with the Projects and Observations tables.

### 4. Ingest Sample Data

```bash
python data_ingestor.py
```

This will load the project and observation data from `data_projects.csv` and `data_observations.csv` into the database.

### 5. Run the API Server

```bash
python main.py
```

The API will be available at `http://localhost:8000`

Alternatively, you can use uvicorn as a Python module:
```bash
python -m uvicorn main:app --reload
```

## API Endpoints

### GET /
Root endpoint providing API information.

### GET /projects
Retrieve all projects from the database.

### GET /observations
Retrieve all observations from the database for a specific project.

**Query Parameters:**
- `project_id` (required): Filter by specific project ID
- `type` (optional): Filter by specific observation type
- `limit` (optional): Limit the number of results

**Example:**
```bash
# Get all projects
curl http://localhost:8000/projects

# Get all observations for project 1
curl http://localhost:8000/observations?project_id=1

# Get only SATISFACTION metrics for project 1
curl "http://localhost:8000/observations?project_id=1&type=SATISFACTION"

# Get latest 10 observations for project 1
curl "http://localhost:8000/observations?project_id=1&limit=10"
```

### GET /metrics
Calculate metrics for a given time period and project.

**Query Parameters:**
- `project_id` (required): Project ID to filter observations
- `metric_types` (required): Comma-separated list of metric types
- `start_time` (required): Start time in ISO format
- `end_time` (required): End time in ISO format
- `intervals` (optional): Number of intervals (default: 1)

**Example:**
```bash
curl "http://localhost:8000/metrics?project_id=1&metric_types=DEPLOYMENT_FREQUENCY&start_time=2025-01-01T00:00:00&end_time=2025-12-31T23:59:59"
```

## Interactive API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Usage Example

1. Start the server: `python main.py`
2. Open your browser and go to `http://localhost:8000/docs`
3. Use the interactive interface to test the API endpoints
4. Query observations with different filters

## Adding New Data

To add new observations:

1. Create a CSV file with columns: `metric_type`, `timestamp`, `value`
2. Run the data ingestor:
   ```bash
   python data_ingestor.py
   ```

Or modify the script to accept a custom CSV file path.

## Database Schema

**Projects Table:**
- `id`: INTEGER PRIMARY KEY (auto-increment)
- `name`: TEXT (project name, unique)

**Observations Table:**
- `id`: INTEGER PRIMARY KEY (auto-increment)
- `project_id`: INTEGER (foreign key to projects)
- `type`: TEXT (observation type)
- `timestamp`: TIMESTAMP (when the observation was recorded)
- `value`: REAL (observation value)
- `commit_hash`: TEXT (optional commit reference)
- `deployment_id`: INTEGER (optional deployment reference)
- `deployment_failure_id`: INTEGER (optional failure reference)
- `ai_rework_commit`: INTEGER (optional AI rework flag)

## Requirements

- Python 3.8+
- FastAPI
- Uvicorn
- Pydantic

## Future Enhancements

- Add authentication and authorization
- Implement aggregation endpoints (averages, trends)
- Add data validation for metric types
- Support for bulk data imports
- Time-series analysis capabilities
- Dashboard for visualization

## License

See LICENSE file for details.
