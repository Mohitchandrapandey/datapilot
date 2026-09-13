import { CartesianGrid, Scatter, ScatterChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { ChartRow } from "../../types/visualization";
import { formatNumber } from "../../utils/chartUtils";

export function ScatterChartView({ data, xAxis = "x", yAxis = "y" }: { data: ChartRow[]; xAxis?: string; yAxis?: string }) {
  return <ResponsiveContainer width="100%" height="100%"><ScatterChart margin={{ top: 8, right: 18, left: 8, bottom: 20 }}>
    <CartesianGrid /><XAxis type="number" dataKey={xAxis} name={xAxis} tickFormatter={formatNumber} /><YAxis type="number" dataKey={yAxis} name={yAxis} tickFormatter={formatNumber} /><Tooltip cursor={{ strokeDasharray: "3 3" }} formatter={(value) => formatNumber(value)} /><Scatter data={data} fill="#0f766e" />
  </ScatterChart></ResponsiveContainer>;
}
