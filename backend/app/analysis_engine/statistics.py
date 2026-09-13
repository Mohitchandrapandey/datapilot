from __future__ import annotations

from typing import Any

import pandas as pd

from app.analysis_engine.base import Analysis, AnalysisResultMixin


class StatisticsAnalysis(Analysis, AnalysisResultMixin):
    name = "statistics"
    description = "Compute descriptive statistics for numeric columns."

    def run(self, context: dict[str, Any]) -> dict[str, Any]:
        data = context.get("data", [])
        if not data:
            return self.make_result(self.name, {"summary": {}}, findings=["No data available."])
        df = pd.DataFrame(data)
        numeric_columns = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])]
        if not numeric_columns:
            return self.make_result(self.name, {"summary": {}}, findings=["No numeric columns were found for descriptive statistics."])
        summary = {}
        histograms = {}
        for column in numeric_columns:
            series = pd.to_numeric(df[column], errors="coerce")
            stats = series.describe(percentiles=[0.25, 0.5, 0.75])
            clean_series = series.dropna()
            summary[str(column)] = {
                "count": int(stats.get("count", 0)),
                "mean": float(stats.get("mean", 0.0)) if pd.notna(stats.get("mean", 0.0)) else 0.0,
                "median": float(stats.get("50%", 0.0)) if pd.notna(stats.get("50%", 0.0)) else 0.0,
                "std": float(stats.get("std", 0.0)) if pd.notna(stats.get("std", 0.0)) else 0.0,
                "min": float(stats.get("min", 0.0)) if pd.notna(stats.get("min", 0.0)) else 0.0,
                "max": float(stats.get("max", 0.0)) if pd.notna(stats.get("max", 0.0)) else 0.0,
                "q1": float(stats.get("25%", 0.0)) if pd.notna(stats.get("25%", 0.0)) else 0.0,
                "q3": float(stats.get("75%", 0.0)) if pd.notna(stats.get("75%", 0.0)) else 0.0,
            }
            if not clean_series.empty:
                bin_count = min(20, max(5, int(clean_series.nunique())))
                if clean_series.nunique() == 1:
                    value = float(clean_series.iloc[0])
                    histograms[str(column)] = [{"bin_start": value, "bin_end": value, "count": int(len(clean_series))}]
                else:
                    counts, edges = pd.cut(clean_series, bins=bin_count, include_lowest=True, retbins=True)
                    histogram_counts = clean_series.groupby(counts, observed=False).size()
                    histograms[str(column)] = [
                        {"bin_start": float(edges[index]), "bin_end": float(edges[index + 1]), "count": int(histogram_counts.iloc[index])}
                        for index in range(len(edges) - 1)
                    ]
        findings = [f"Calculated descriptive statistics for {len(summary)} numeric columns."]
        first_column = next(iter(summary), None)
        chart = {
            "type": "histogram",
            "title": f"Distribution of {first_column}" if first_column else "Numeric Distribution",
            "description": "Frequency distribution calculated from the selected numeric values.",
            "x_axis": "bin_start",
            "y_axis": "count",
            "data": histograms.get(first_column, []) if first_column else [],
            "metadata": {
                "source_rows": int(context.get("source_rows", len(df))),
                "displayed_points": len(histograms.get(first_column, [])) if first_column else 0,
                "aggregated": True,
                "aggregation": "histogram bins",
                "columns": list(histograms),
                "histograms": histograms,
            },
        }
        return self.make_result(self.name, {"summary": summary, "histograms": histograms}, chart=chart, findings=findings)
