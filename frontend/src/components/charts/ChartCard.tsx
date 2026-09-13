import type { ReactNode } from "react";
import type { VisualizationMetadata } from "../../types/visualization";
import { formatNumber } from "../../utils/chartUtils";

export type ChartCardProps = {
  title: string;
  description?: string;
  metadata?: VisualizationMetadata;
  finding?: string;
  children: ReactNode;
};

export function ChartCard({ title, description, metadata, finding, children }: ChartCardProps) {
  return (
    <section className="chart-card" aria-label={title}>
      <div className="chart-card-heading">
        <div>
          <h5>{title}</h5>
          {description && <p>{description}</p>}
        </div>
        {metadata?.displayed_points !== undefined && (
          <span className="chart-meta">{formatNumber(metadata.displayed_points)} points</span>
        )}
      </div>
      <div className="chart-stage">{children}</div>
      {metadata?.aggregated && <p className="chart-footnote">Aggregated from {formatNumber(metadata.source_rows)} rows{metadata.aggregation ? ` using ${metadata.aggregation}` : ""}.</p>}
      {finding && <p className="chart-finding"><strong>Finding:</strong> {finding}</p>}
    </section>
  );
}
