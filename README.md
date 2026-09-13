# DataPilot

Upload. Choose. Analyze. Report.

DataPilot is an analysis-first data analytics platform. Upload a structured dataset, inspect its quality, run focused analyses, view real visualizations, and build a report from the calculated results.

## Features

- CSV, XLSX, JSON, ZIP, GZIP, and Parquet uploads
- Dataset profiling with schema, missing values, duplicates, and column summaries
- Missing-value analysis
- Descriptive statistics for numeric columns
- Correlation analysis with a correlation heatmap
- IQR-based outlier detection with box-plot summaries
- Backend-generated histograms and chart-ready metadata
- Responsive Recharts visualizations
- Findings tied to the same calculated analysis results
- Report builder with retained visualizations and findings
- CSV and PDF export API endpoints

The current implementation does not yet include trend, growth, grouping, top/bottom, or duplicate-specific analysis modules. Those should not be treated as completed features.

## Architecture

```text
Browser
	-> Upload
	-> FastAPI backend
	-> Dataset processing and profiling
	-> Analysis engine
	-> Numerical results and chart-ready data
	-> React visualizations and report builder
```

Uploaded files are processed on the server. The frontend receives a bounded preview and aggregated chart data rather than the complete source file.

## Technology

- Frontend: React, TypeScript, Vite, Recharts
- Backend: Python, FastAPI, Uvicorn
- Data processing: Pandas, NumPy
- Supported readers: openpyxl and PyArrow
- Tests: pytest and FastAPI TestClient

## Project Structure

```text
DataPilot/
├── backend/
│   └── app/
│       ├── analysis_engine/
│       ├── api/
│       ├── core/
│       ├── services/
│       └── main.py
├── frontend/
│   ├── src/
│   │   ├── components/charts/
│   │   ├── types/
│   │   └── utils/
│   ├── package.json
│   └── package-lock.json
├── tests/
│   ├── data/sales.csv
│   └── test_backend.py
├── docs/
├── .env.example
├── .gitignore
└── README.md
```

## Windows Setup

### Backend

From the repository root:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Backend URL: `http://127.0.0.1:8000`

API docs: `http://127.0.0.1:8000/docs`

### Frontend

In a second PowerShell window:

```powershell
cd frontend
npm install
npm run dev
```

Frontend URL: `http://localhost:5173`

## Configuration

Copy `.env.example` to `.env` when local overrides are needed. The backend currently supports:

| Variable | Description | Default |
| --- | --- | --- |
| `UPLOAD_DIR` | Directory for locally uploaded files | `backend/uploads` |
| `MAX_FILE_SIZE` | Maximum upload size in bytes | `104857600` |

Keep `.env` local. It is ignored by Git.

## Testing

From the repository root:

```powershell
python -m pip install -r backend/requirements.txt
$env:PYTHONPATH = "backend"
python -m pytest -q
```

Frontend checks:

```powershell
cd frontend
npm run build
npm run lint
```

## Data and Security

Uploaded files are local runtime data and are ignored by Git. Do not place confidential, regulated, or production datasets in the repository. The committed `tests/data/sales.csv` is a small fixture used by backend tests.

Before publishing, review `.env`, upload directories, dependency folders, build output, logs, and generated caches.

## Roadmap

- Background processing for very large uploads
- Persistent storage and PostgreSQL support
- Object storage integration
- Authentication and team collaboration
- Trend, growth, grouping, and top/bottom analyses
- Forecasting, regression, clustering, and advanced analytics
- Richer PDF and Excel report generation

## License

No license has been selected yet. Until a license is added, all rights are reserved.
