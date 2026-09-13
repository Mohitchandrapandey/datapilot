import { useState } from "react";
import type { VisualizationChart } from "../../types/visualization";
import { asRows } from "../../utils/chartUtils";
import { BarChartView } from "./BarChartView";
import { BoxPlotView } from "./BoxPlotView";
import { ChartCard } from "./ChartCard";
import { CorrelationHeatmap } from "./CorrelationHeatmap";
import { HistogramView } from "./HistogramView";
import { LineChartView } from "./LineChartView";
import { PieChartView } from "./PieChartView";
import { ScatterChartView } from "./ScatterChartView";

export function ChartRenderer({ chart, finding }: { chart?: VisualizationChart; finding?: string }) {
  const [selectedColumn, setSelectedColumn] = useState(chart?.metadata?.columns?.[0] ?? "");
  if (!chart) return <div className="empty-state">Visualization unavailable.</div>;
  const rows = asRows(chart.data);
  const metadata = chart.metadata;
  const histogramRows = metadata?.histograms?.[selectedColumn ?? ""] ?? rows;
  return <ChartCard title={chart.title} description={chart.description} metadata={metadata} finding={finding}>
    {chart.type === "bar" && <BarChartView data={rows} xAxis={chart.x_axis} yAxis={chart.y_axis} />}
    {chart.type === "line" && <LineChartView data={rows} xAxis={chart.x_axis} yAxis={chart.y_axis} />}
    {chart.type === "scatter" && <ScatterChartView data={rows} xAxis={chart.x_axis} yAxis={chart.y_axis} />}
    {chart.type === "histogram" && <><div className="chart-control"><label htmlFor="histogram-column">Column</label><select id="histogram-column" value={selectedColumn} onChange={(event) => setSelectedColumn(event.target.value)}>{(metadata?.columns ?? []).map((column) => <option key={column}>{column}</option>)}</select></div><HistogramView data={histogramRows} /></>}
    {chart.type === "boxplot" && <BoxPlotView data={rows} />}
    {chart.type === "pie" && <PieChartView data={rows} />}
    {chart.type === "heatmap" && <CorrelationHeatmap chart={chart} />}
  </ChartCard>;
}
