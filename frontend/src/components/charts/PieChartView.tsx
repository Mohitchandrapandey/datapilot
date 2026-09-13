import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import type { ChartRow } from "../../types/visualization";
import { formatNumber } from "../../utils/chartUtils";

const colors = ["#0f766e", "#f59e0b", "#2563eb", "#dc2626", "#7c3aed", "#64748b"];

export function PieChartView({ data, nameKey = "name", valueKey = "value" }: { data: ChartRow[]; nameKey?: string; valueKey?: string }) {
  return <ResponsiveContainer width="100%" height="100%"><PieChart><Pie data={data} dataKey={valueKey} nameKey={nameKey} innerRadius="42%" outerRadius="72%" paddingAngle={2}>{data.map((row, index) => <Cell key={String(row[nameKey] ?? index)} fill={colors[index % colors.length]} />)}</Pie><Tooltip formatter={(value) => formatNumber(value)} /></PieChart></ResponsiveContainer>;
}
