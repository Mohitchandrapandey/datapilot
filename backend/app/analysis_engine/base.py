from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Analysis(ABC):
    name: str = "analysis"
    description: str = ""
    required_columns: list[str] | None = None

    @abstractmethod
    def run(self, context: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError


class AnalysisResultMixin:
    @staticmethod
    def make_result(analysis_name: str, results: dict[str, Any], chart: dict[str, Any] | None = None, findings: list[str] | None = None, status: str = "success") -> dict[str, Any]:
        return {
            "analysis": analysis_name,
            "status": status,
            "results": results,
            "chart": chart or {},
            "findings": findings or [],
        }
