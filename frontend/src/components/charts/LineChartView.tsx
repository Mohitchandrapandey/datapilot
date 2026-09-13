import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { ChartRow } from "../../types/visualization";
import { formatNumber } from "../../utils/chartUtils";

export function LineChartView({ data, xAxis = "name", yAxis = "value" }: { data: ChartRow[]; xAxis?: string; yAxis?: string }) {
  return <ResponsiveContainer width="100%" height="100%"><LineChart data={data} margin={{ top: 8, right: 18, left: 8, bottom: 20 }}>
    <CartesianGrid strokeDasharray="3 3" vertical={false} /><XAxis dataKey={xAxis} /><YAxis tickFormatter={formatNumber} /><Tooltip formatter={(value) => formatNumber(value)} /><Line type="monotone" dataKey={yAxis} stroke="#0f766e" strokeWidth={2.5} dot={{ r: 3 }} />
  </LineChart></ResponsiveContainer>;
}
