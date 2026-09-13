import zipfile
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.services.profiling_service import profile_dataset
from app.analysis_engine.missing_values import MissingValuesAnalysis
from app.analysis_engine.statistics import StatisticsAnalysis
from app.analysis_engine.correlation import CorrelationAnalysis
from app.analysis_engine.outliers import OutlierAnalysis


BASE_DIR = Path(__file__).resolve().parent


def test_profile_dataset_basic_summary():
    path = BASE_DIR / "data" / "sales.csv"
    profile = profile_dataset(str(path))

    assert profile["row_count"] > 0
    assert profile["column_count"] >= 8
    assert profile["missing_values"] >= 1
    assert "date" in profile["column_names"]


def test_missing_values_analysis():
    analysis = MissingValuesAnalysis()
    result = analysis.run({"data": [{"revenue": 100, "region": "North"}, {"revenue": None, "region": "South"}]})

    assert result["status"] == "success"
    assert result["results"]["total_missing_cells"] == 1


def test_statistics_and_correlation():
    stats = StatisticsAnalysis().run({"data": [{"revenue": 100, "units": 10}, {"revenue": 200, "units": 20}, {"revenue": 300, "units": 30}]})
    corr = CorrelationAnalysis().run({"data": [{"revenue": 100, "units": 10}, {"revenue": 200, "units": 20}, {"revenue": 300, "units": 30}]})

    assert stats["status"] == "success"
    assert corr["status"] == "success"
    assert corr["results"]["matrix"]["revenue"]["units"] > 0.9


def test_outlier_detection():
    analysis = OutlierAnalysis()
    result = analysis.run({"data": [{"revenue": 100}, {"revenue": 110}, {"revenue": 120}, {"revenue": 115}, {"revenue": 1000}]})

    assert result["status"] == "success"
    assert result["results"]["outlier_count"] >= 1


def test_api_upload_and_profile_endpoint():
    client = TestClient(app)
    with open(BASE_DIR / "data" / "sales.csv", "rb") as payload:
        response = client.post("/api/upload", files={"file": ("sales.csv", payload, "text/csv")})

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["dataset"]["row_count"] > 0


def test_zip_upload_supported_dataset(tmp_path):
    zip_path = tmp_path / "zip_test.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("sales.csv", "date,region,revenue,units\n2024-01-01,North,1200,10\n2024-01-02,South,1500,12\n")

    client = TestClient(app)
    with open(zip_path, "rb") as payload:
        response = client.post("/api/upload", files={"file": ("zip_test.zip", payload, "application/zip")})

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["dataset"]["file_type"] == "zip"
