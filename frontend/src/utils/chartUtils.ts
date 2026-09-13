import type { ChartRow } from "../types/visualization";

export const numberValue = (value: unknown): number => {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
};

export const formatNumber = (value: unknown): string => {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) return "-";
  return new Intl.NumberFormat(undefined, { maximumFractionDigits: 2 }).format(parsed);
};

export const asRows = (value: unknown): ChartRow[] => (Array.isArray(value) ? value.filter((row): row is ChartRow => typeof row === "object" && row !== null) : []);
