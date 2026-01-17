# AI Productivity Framework

A PoC framework for measuring AI productivity. Implemented as part of my Master's thesis.

## Overview

This framework provides a system for collecting, storing, and analyzing productivity metrics related to AI-assisted development. It includes:

- SQLite database for storing observations
- Data ingestion pipeline for CSV data
- REST API built with FastAPI for querying metrics

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
├── sample_data.csv       # Sample data for testing
├── requirements.txt      # Python dependencies
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

This will create `productivity_framework.db` with the Observations table.

### 4. Ingest Sample Data

```bash
python data_ingestor.py
```

This will load the sample data from `sample_data.csv` into the database.

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

### GET /observations
Retrieve all observations from the database.

**Query Parameters:**
- `metric_type` (optional): Filter by specific metric type
- `limit` (optional): Limit the number of results

**Example:**
```bash
# Get all observations
curl http://localhost:8000/observations

# Get only SATISFACTION metrics
curl http://localhost:8000/observations?metric_type=SATISFACTION

# Get latest 10 observations
curl http://localhost:8000/observations?limit=10
```

### GET /metrics
Get a list of all available metric types.

**Example:**
```bash
curl http://localhost:8000/metrics
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

**Observations Table:**
- `id`: INTEGER PRIMARY KEY (auto-increment)
- `metric_type`: TEXT (metric category)
- `timestamp`: TIMESTAMP (when the observation was recorded)
- `value`: REAL (metric value)

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
