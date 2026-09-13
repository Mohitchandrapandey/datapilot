from __future__ import annotations

from typing import Any

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.analysis_engine.registry import get_analysis
from app.services.file_service import DATASETS, get_dataset, save_uploaded_file
from app.services.report_service import generate_report, get_report, list_reports

router = APIRouter()


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/api/upload")
async def upload_file(file: UploadFile = File(...)) -> dict[str, Any]:
    try:
        dataset = save_uploaded_file(file)
        return {"status": "success", "dataset": dataset}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - safety net
        raise HTTPException(status_code=500, detail=f"Unable to process this dataset: {exc}") from exc


@router.get("/api/datasets/{dataset_id}")
def fetch_dataset(dataset_id: str) -> dict[str, Any]:
    try:
        return {"status": "success", "dataset": get_dataset(dataset_id)}
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/api/datasets/{dataset_id}/profile")
def fetch_profile(dataset_id: str) -> dict[str, Any]:
    try:
        dataset = get_dataset(dataset_id)
        return {"status": "success", "profile": dataset["profile"]}
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/api/analyses/run")
def run_analysis(payload: dict[str, Any]) -> dict[str, Any]:
    analyses = payload.get("analyses") or payload.get("analysis")
    dataset_id = payload.get("dataset_id")
    if not analyses or not dataset_id:
        raise HTTPException(status_code=400, detail="analyses and dataset_id are required.")
    try:
        dataset = get_dataset(dataset_id)
        rows = dataset.get("rows", [])
        results = []
        for analysis_name in analyses if isinstance(analyses, list) else [analyses]:
            analysis = get_analysis(analysis_name)
            output = analysis.run({"data": rows, "context": payload, "dataset_id": dataset_id, "source_rows": dataset.get("row_count", len(rows))})
            results.append({"analysis": analysis_name, "result": output})
        return {"status": "success", "results": results, "dataset": dataset}
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"Analysis failed: {exc}") from exc


@router.post("/api/reports")
def create_report(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        report = generate_report(payload)
        return {"status": "success", "report": report}
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"Report generation failed: {exc}") from exc


@router.get("/api/reports")
def get_reports() -> dict[str, Any]:
    return {"status": "success", "reports": list_reports()}


@router.get("/api/reports/{report_id}")
def get_report_by_id(report_id: str) -> dict[str, Any]:
    try:
        return {"status": "success", "report": get_report(report_id)}
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/api/reports/{report_id}/export/csv")
def export_csv(report_id: str):
    try:
        report = get_report(report_id)
        csv_text = report.get("csv", "")
        return {"status": "success", "csv": csv_text, "report_id": report_id}
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/api/reports/{report_id}/export/pdf")
def export_pdf(report_id: str):
    try:
        report = get_report(report_id)
        return {"status": "success", "pdf_url": f"/api/reports/{report_id}/pdf", "report": report}
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
