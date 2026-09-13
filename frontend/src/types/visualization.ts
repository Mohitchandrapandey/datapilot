export type ChartType = "bar" | "line" | "scatter" | "histogram" | "boxplot" | "pie" | "heatmap";

export type ChartValue = string | number | null;
export type ChartRow = Record<string, ChartValue>;

export type VisualizationMetadata = {
  source_rows?: number;
  displayed_points?: number;
  aggregated?: boolean;
  aggregation?: string;
  columns?: string[];
  histograms?: Record<string, ChartRow[]>;
  [key: string]: unknown;
};

export type VisualizationChart = {
  type: ChartType;
  title: string;
  description?: string;
  x_axis?: string;
  y_axis?: string;
  data: ChartRow[] | Record<string, Record<string, number>>;
  metadata?: VisualizationMetadata;
};
