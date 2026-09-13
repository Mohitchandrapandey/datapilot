import type { ChartRow } from "../../types/visualization";
import { formatNumber, numberValue } from "../../utils/chartUtils";

export function BoxPlotView({ data }: { data: ChartRow[] }) {
  const selected = data[0];
  if (!selected) return <div className="empty-state">No numeric values available for a box plot.</div>;
  const min = numberValue(selected.min); const max = numberValue(selected.max); const span = max - min || 1;
  const position = (value: unknown) => `${Math.max(0, Math.min(100, ((numberValue(value) - min) / span) * 100))}%`;
  return <div className="boxplot-wrap"><div className="boxplot-labels"><span>{String(selected.column ?? "Column")}</span><span>Potential outliers: {formatNumber(selected.outlier_count)}</span></div><div className="boxplot-track"><span className="boxplot-whisker" style={{ left: position(selected.lower_bound), width: `calc(${position(selected.upper_bound)} - ${position(selected.lower_bound)})` }} /><span className="boxplot-box" style={{ left: position(selected.q1), width: `calc(${position(selected.q3)} - ${position(selected.q1)})` }} /><span className="boxplot-median" style={{ left: position(selected.median) }} /></div><div className="boxplot-scale"><span>{formatNumber(min)}</span><span>Q1 {formatNumber(selected.q1)}</span><span>Median {formatNumber(selected.median)}</span><span>Q3 {formatNumber(selected.q3)}</span><span>{formatNumber(max)}</span></div><p className="boxplot-bounds">IQR bounds: {formatNumber(selected.lower_bound)} to {formatNumber(selected.upper_bound)}</p></div>;
}
