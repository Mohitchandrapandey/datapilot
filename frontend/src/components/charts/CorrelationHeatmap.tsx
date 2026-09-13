import type { VisualizationChart } from "../../types/visualization";
import { numberValue } from "../../utils/chartUtils";

export function CorrelationHeatmap({ chart }: { chart: VisualizationChart }) {
  const matrix = chart.data as Record<string, Record<string, number>>;
  const columns = chart.metadata?.columns ?? Object.keys(matrix);
  const color = (value: number) => value >= 0 ? `rgba(15, 118, 110, ${0.12 + Math.abs(value) * 0.72})` : `rgba(220, 38, 38, ${0.12 + Math.abs(value) * 0.72})`;
  return <div className="heatmap-wrap" role="table" aria-label={chart.title}><div className="heatmap-grid" style={{ gridTemplateColumns: `minmax(92px, 1.2fr) repeat(${columns.length}, minmax(58px, 1fr))` }}><div /><>{columns.map((column) => <strong key={column}>{column}</strong>)}</>{columns.map((row) => <><strong key={`${row}-label`}>{row}</strong>{columns.map((column) => { const value = numberValue(matrix[row]?.[column]); return <span key={`${row}-${column}`} className="heatmap-cell" style={{ background: color(value) }} title={`${row} and ${column}: ${value.toFixed(2)}`}>{value.toFixed(2)}</span>; })}</>)}</div></div>;
}
