import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { ChartRow } from "../../types/visualization";
import { formatNumber } from "../../utils/chartUtils";

export function HistogramView({ data }: { data: ChartRow[] }) {
  const displayData = data.map((row) => ({ ...row, label: `${formatNumber(row.bin_start)}-${formatNumber(row.bin_end)}` }));
  return <ResponsiveContainer width="100%" height="100%"><BarChart data={displayData} margin={{ top: 8, right: 18, left: 8, bottom: 28 }}>
    <CartesianGrid strokeDasharray="3 3" vertical={false} /><XAxis dataKey="label" tick={{ fontSize: 10 }} angle={-28} textAnchor="end" /><YAxis allowDecimals={false} /><Tooltip formatter={(value) => formatNumber(value)} /><Bar dataKey="count" fill="#f59e0b" />
  </BarChart></ResponsiveContainer>;
}
