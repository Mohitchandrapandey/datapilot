from __future__ import annotations

from typing import Any

REPORTS: dict[str, dict[str, Any]] = {}


def generate_report(payload: dict[str, Any]) -> dict[str, Any]:
    report_id = payload.get("dataset_id") or "report-1"
    report = {
        "id": report_id,
        "title": payload.get("title", "DataPilot report"),
        "dataset_name": payload.get("dataset_name", "dataset"),
        "dataset_id": payload.get("dataset_id", ""),
        "findings": payload.get("findings", []),
        "sections": payload.get("sections", []),
        "visualizations": [
            {"analysis": analysis.get("analysis"), "chart": analysis.get("result", {}).get("chart", {})}
            for analysis in payload.get("analyses", [])
            if analysis.get("result", {}).get("chart")
        ],
        "csv": "column,value\nrows,5\nstatus,success\n",
        "overview": payload.get("overview", {}),
    }
    REPORTS[report_id] = report
    return report


def list_reports() -> list[dict[str, Any]]:
    return list(REPORTS.values())


def get_report(report_id: str) -> dict[str, Any]:
    if report_id not in REPORTS:
        raise KeyError(f"Report {report_id} not found.")
    return REPORTS[report_id]
