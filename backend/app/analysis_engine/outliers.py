from __future__ import annotations

from typing import Any

import pandas as pd

from app.analysis_engine.base import Analysis, AnalysisResultMixin


class OutlierAnalysis(Analysis, AnalysisResultMixin):
    name = "outliers"
    description = "Detect potential outliers using the interquartile range method."

    def run(self, context: dict[str, Any]) -> dict[str, Any]:
        data = context.get("data", [])
        if not data:
            return self.make_result(self.name, {"results": {}, "outlier_count": 0}, findings=["No data available."])
        df = pd.DataFrame(data)
        numeric_columns = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])]
        if not numeric_columns:
            return self.make_result(self.name, {"results": {}, "outlier_count": 0}, findings=["No numeric columns were found for outlier analysis."])
        column_results = {}
        all_outliers = 0
        for column in numeric_columns:
            series = pd.to_numeric(df[column], errors="coerce").dropna()
            if series.empty:
                continue
            q1 = series.quantile(0.25)
            q3 = series.quantile(0.75)
            iqr = q3 - q1
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            outliers = series[(series < lower) | (series > upper)]
            outlier_count = int(len(outliers))
            column_results[str(column)] = {
                "outlier_count": outlier_count,
                "percentage": round((len(outliers) / len(series)) * 100, 2) if len(series) else 0.0,
                "lower_bound": float(lower),
                "upper_bound": float(upper),
                "min": float(series.min()),
                "q1": float(q1),
                "median": float(series.median()),
                "q3": float(q3),
                "max": float(series.max()),
            }
            all_outliers += outlier_count
        findings = [f"Potential outliers were identified in {sum(1 for value in column_results.values() if value['outlier_count'] > 0)} numeric columns."]
        if all_outliers == 0:
            findings = ["No obvious outliers were detected using the IQR method."]

        result = {
            "results": column_results,
            "outlier_count": all_outliers,
            "affected_columns": [column for column, value in column_results.items() if value["outlier_count"] > 0],
        }
        first_column = next(iter(column_results), None)
        chart = {
            "type": "boxplot",
            "title": f"Outliers in {first_column}" if first_column else "Outlier Analysis",
            "description": "Values outside the IQR lower and upper bounds are potential outliers.",
            "data": [
                {"column": column, **values}
                for column, values in column_results.items()
            ],
            "metadata": {
                "source_rows": int(context.get("source_rows", len(df))),
                "displayed_points": len(column_results),
                "columns": list(column_results),
            },
        }
        return self.make_result(self.name, result, chart=chart, findings=findings)
