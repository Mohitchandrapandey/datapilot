import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { ChartRow } from "../../types/visualization";
import { formatNumber } from "../../utils/chartUtils";

export function BarChartView({ data, xAxis = "name", yAxis = "value", horizontal = false }: { data: ChartRow[]; xAxis?: string; yAxis?: string; horizontal?: boolean }) {
  return <ResponsiveContainer width="100%" height="100%"><BarChart data={data} layout={horizontal ? "vertical" : "horizontal"} margin={{ top: 8, right: 18, left: 8, bottom: 28 }}>
    <CartesianGrid strokeDasharray="3 3" vertical={false} />
    {horizontal ? <><XAxis type="number" tickFormatter={formatNumber} /><YAxis type="category" dataKey={xAxis} width={96} tick={{ fontSize: 11 }} /></> : <><XAxis dataKey={xAxis} tick={{ fontSize: 11 }} interval={0} angle={data.length > 6 ? -28 : 0} textAnchor={data.length > 6 ? "end" : "middle"} /><YAxis tickFormatter={formatNumber} /></>}
    <Tooltip formatter={(value) => formatNumber(value)} />
    <Bar dataKey={yAxis} fill="#0f766e" radius={[4, 4, 0, 0]} />
  </BarChart></ResponsiveContainer>;
}
