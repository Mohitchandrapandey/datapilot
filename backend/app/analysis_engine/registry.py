from __future__ import annotations

from app.analysis_engine.correlation import CorrelationAnalysis
from app.analysis_engine.missing_values import MissingValuesAnalysis
from app.analysis_engine.outliers import OutlierAnalysis
from app.analysis_engine.statistics import StatisticsAnalysis

ANALYSIS_REGISTRY = {
    "missing_values": MissingValuesAnalysis,
    "statistics": StatisticsAnalysis,
    "correlation": CorrelationAnalysis,
    "outliers": OutlierAnalysis,
}


def get_analysis(name: str):
    analysis_class = ANALYSIS_REGISTRY.get(name)
    if not analysis_class:
        raise ValueError(f"Unsupported analysis: {name}")
    return analysis_class()
