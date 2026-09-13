from __future__ import annotations

from typing import Any

import pandas as pd

from app.analysis_engine.base import Analysis, AnalysisResultMixin


class MissingValuesAnalysis(Analysis, AnalysisResultMixin):
    name = "missing_values"
    description = "Find missing values and identify the columns with the highest missing rates."

    def run(self, context: dict[str, Any]) -> dict[str, Any]:
        data = context.get("data", [])
        if not data:
            return self.make_result(self.name, {"total_missing_cells": 0, "by_column": {}, "missing_percentage": {}}, findings=["No data available."])
        df = pd.DataFrame(data)
        by_column = {str(col): int(df[col].isna().sum()) for col in df.columns}
        missing_percentage = {str(col): round((df[col].isna().mean() * 100), 2) for col in df.columns}
        highest_missing = sorted(missing_percentage.items(), key=lambda item: item[1], reverse=True)[:5]
        results = {
            "total_missing_cells": int(df.isna().sum().sum()),
            "by_column": by_column,
            "missing_percentage": missing_percentage,
            "columns_with_highest_missing_rate": [{"column": column, "missing_percentage": percentage} for column, percentage in highest_missing],
        }
        chart_data = [
            {"column": column, "missing_percentage": percentage, "missing_count": by_column[column]}
            for column, percentage in sorted(missing_percentage.items(), key=lambda item: item[1], reverse=True)
        ]
        findings = []
        if results["total_missing_cells"]:
            findings.append(f"{results['total_missing_cells']} missing values were detected across the dataset.")
        else:
            findings.append("No missing values were found in the selected dataset.")
        chart = {
            "type": "bar",
            "title": "Missing Values by Column",
            "description": "Percentage of missing values in each column.",
            "x_axis": "column",
            "y_axis": "missing_percentage",
            "data": chart_data,
            "metadata": {
                "source_rows": int(context.get("source_rows", len(df))),
                "displayed_points": len(chart_data),
                "aggregated": True,
                "aggregation": "missing percentage",
            },
        }
        return self.make_result(self.name, results, chart=chart, findings=findings)
