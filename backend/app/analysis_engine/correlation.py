from __future__ import annotations

from typing import Any

import pandas as pd

from app.analysis_engine.base import Analysis, AnalysisResultMixin


class CorrelationAnalysis(Analysis, AnalysisResultMixin):
    name = "correlation"
    description = "Measure relationships between numeric variables using Pearson correlation."

    def run(self, context: dict[str, Any]) -> dict[str, Any]:
        data = context.get("data", [])
        if not data:
            return self.make_result(self.name, {"matrix": {}}, findings=["No data available."])
        df = pd.DataFrame(data)
        numeric_columns = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])]
        if len(numeric_columns) < 2:
            return self.make_result(self.name, {"matrix": {}}, findings=["At least two numeric columns are required for correlation analysis."])
        corr = df[numeric_columns].corr(method="pearson").fillna(0)
        for column in numeric_columns:
            corr.loc[column, column] = 1.0
        matrix = corr.round(4).to_dict()
        strongest = []
        for col_a in numeric_columns:
            for col_b in numeric_columns:
                if col_a >= col_b:
                    continue
                value = float(corr.loc[col_a, col_b])
                strongest.append({"column_a": col_a, "column_b": col_b, "correlation": round(value, 4)})
        strongest = sorted(strongest, key=lambda item: abs(item["correlation"]), reverse=True)[:5]
        findings = []
        if strongest:
            top = strongest[0]
            direction = "positive" if top["correlation"] > 0 else "negative"
            findings.append(f"{top['column_a']} and {top['column_b']} show a {direction} relationship with a correlation of {top['correlation']}.")
        else:
            findings.append("No strong relationships were identified in the selected numeric columns.")
        chart = {
            "type": "heatmap",
            "title": "Correlation Matrix",
            "description": "Pearson correlation across numeric columns.",
            "data": matrix,
            "metadata": {
                "source_rows": int(context.get("source_rows", len(df))),
                "displayed_points": len(numeric_columns) ** 2,
                "aggregated": True,
                "columns": [str(column) for column in numeric_columns],
            },
        }
        return self.make_result(self.name, {"matrix": matrix, "strongest_relationships": strongest}, chart=chart, findings=findings)
