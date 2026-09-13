import { useMemo, useRef, useState } from "react";
import { ChartRenderer } from "./components/charts/ChartRenderer";
import type { VisualizationChart } from "./types/visualization";
import "./App.css";

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000").replace(/\/$/, "");

const ALLOWED_EXTENSIONS = [
  ".csv",
  ".xlsx",
  ".json",
  ".zip",
  ".gz",
  ".parquet",
];

const MAX_FILE_SIZE = 100 * 1024 * 1024;

const ANALYSIS_OPTIONS = [
  { id: "missing_values", label: "Missing Values", description: "Identify where data is missing and which columns are most affected." },
  { id: "statistics", label: "Descriptive Statistics", description: "Summarize central values and variability in numeric columns." },
  { id: "correlation", label: "Correlation", description: "Measure relationships between numeric variables." },
  { id: "outliers", label: "Outliers", description: "Flag values that deviate sharply from the normal range." },
];

type DatasetResponse = {
  id: string;
  filename: string;
  file_type: string;
  file_size: number;
  row_count: number;
  profile: Record<string, unknown>;
  rows: Array<Record<string, unknown>>;
};

type AnalysisResult = {
  analysis: string;
  result: {
    status?: string;
    results?: Record<string, unknown>;
    chart?: VisualizationChart;
    findings?: string[];
  };
};

function App() {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [dataset, setDataset] = useState<DatasetResponse | null>(null);
  const [selectedAnalyses, setSelectedAnalyses] = useState<string[]>(["missing_values", "statistics", "correlation"]);
  const [analysisResults, setAnalysisResults] = useState<AnalysisResult[]>([]);
  const [reportData, setReportData] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState("");
  const [uploading, setUploading] = useState(false);
  const [runningAnalysis, setRunningAnalysis] = useState(false);

  const overviewCards = useMemo(() => {
    if (!dataset) return [];
    const profile = dataset.profile as Record<string, any>;
    return [
      { label: "Rows", value: dataset.row_count ?? profile.row_count ?? 0 },
      { label: "Columns", value: profile.column_count ?? (dataset.rows[0] ? Object.keys(dataset.rows[0]).length : 0) },
      { label: "Missing Values", value: profile.missing_values ?? 0 },
      { label: "Duplicates", value: profile.duplicate_rows ?? 0 },
    ];
  }, [dataset]);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    setError("");
    setSelectedFile(null);
    if (!file) return;

    const fileName = file.name.toLowerCase();
    const isAllowed = ALLOWED_EXTENSIONS.some((extension) => fileName.endsWith(extension));

    if (!isAllowed) {
      setError("Unsupported file format. Please upload CSV, XLSX, JSON, ZIP, GZIP or Parquet.");
      return;
    }

    if (file.size > MAX_FILE_SIZE) {
      setError("File is too large. V1 currently supports files up to 100 MB.");
      return;
    }

    setSelectedFile(file);
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    setUploading(true);
    setError("");

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const response = await fetch(`${API_BASE_URL}/api/upload`, {
        method: "POST",
        body: formData,
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Upload failed.");
      setDataset(data.dataset as DatasetResponse);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed.");
    } finally {
      setUploading(false);
    }
  };

  const toggleAnalysis = (analysisId: string) => {
    setSelectedAnalyses((previous) =>
      previous.includes(analysisId)
        ? previous.filter((item) => item !== analysisId)
        : [...previous, analysisId]
    );
  };

  const runSelectedAnalyses = async () => {
    if (!dataset || selectedAnalyses.length === 0) {
      setError("Select at least one analysis to continue.");
      return;
    }

    setRunningAnalysis(true);
    setError("");

    try {
      const response = await fetch(`${API_BASE_URL}/api/analyses/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ dataset_id: dataset.id, analyses: selectedAnalyses }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Analysis failed.");
      setAnalysisResults(data.results as AnalysisResult[]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Analysis failed.");
    } finally {
      setRunningAnalysis(false);
    }
  };

  const generateReport = async () => {
    if (!dataset || analysisResults.length === 0) return;

    const reportPayload = {
      title: `${dataset.filename} analysis report`,
      dataset_name: dataset.filename,
      dataset_id: dataset.id,
      findings: analysisResults.flatMap((entry) => entry.result.findings ?? []),
      sections: analysisResults.map((entry) => ({ id: entry.analysis, title: entry.analysis })),
      analyses: analysisResults,
      overview: (dataset.profile as Record<string, any>) ?? {},
    };

    const response = await fetch(`${API_BASE_URL}/api/reports`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(reportPayload),
    });

    const data = await response.json();
    if (response.ok) {
      setReportData(data.report as Record<string, unknown>);
    }
  };

  const renderStatisticsTable = (summary: Record<string, unknown>) => {
    const rows = Object.entries(summary).map(([column, value]) => ({ column, ...(value as Record<string, number>) })) as Array<Record<string, string | number>>;
    if (!rows.length) return <div className="empty-state">No numeric statistics available.</div>;
    return <div className="table-wrap"><table><thead><tr><th>Column</th><th>Count</th><th>Mean</th><th>Median</th><th>Std Dev</th><th>Min</th><th>25%</th><th>75%</th><th>Max</th></tr></thead><tbody>{rows.map((row) => <tr key={row.column}><td>{row.column}</td>{["count", "mean", "median", "std", "min", "q1", "q3", "max"].map((key) => <td key={key}>{Number(row[key] ?? 0).toLocaleString(undefined, { maximumFractionDigits: 2 })}</td>)}</tr>)}</tbody></table></div>;
  };

  const renderCorrelationTable = (relationships: unknown) => {
    const rows = Array.isArray(relationships) ? relationships as Array<Record<string, unknown>> : [];
    if (!rows.length) return null;
    return <div className="relationship-table"><h5>Strongest Relationships</h5><table><thead><tr><th>Variables</th><th>Correlation</th></tr></thead><tbody>{rows.map((row, index) => <tr key={index}><td>{String(row.column_a)} ↔ {String(row.column_b)}</td><td>{Number(row.correlation).toFixed(2)}</td></tr>)}</tbody></table></div>;
  };

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand-wrap">
          <div className="brand">DataPilot</div>
          <span className="tagline">Upload. Choose. Analyze. Report.</span>
        </div>
        <div className="status-pill">{uploading ? "Uploading..." : runningAnalysis ? "Running analysis..." : "Ready"}</div>
      </header>

      <main className="page">
        <section className="hero-panel">
          <div>
            <p className="eyebrow">Data analysis that moves at your pace</p>
            <h1>Analyze your data.</h1>
            <p className="hero-copy">Upload your dataset, choose exactly the analysis you need, and get clear results without writing code.</p>
          </div>

          <div className="upload-card">
            <div className="upload-box">
              <div className="upload-icon">↑</div>
              <h2>Upload your data</h2>
              <p>CSV · XLSX · JSON · ZIP · GZIP · Parquet</p>
              <input ref={fileInputRef} type="file" accept=".csv,.xlsx,.json,.zip,.gz,.parquet" onChange={handleFileSelect} hidden />
              {!selectedFile ? (
                <button className="primary-button" onClick={() => fileInputRef.current?.click()}>Choose File</button>
              ) : (
                <div className="selected-file-box">
                  <strong>{selectedFile.name}</strong>
                  <span>{(selectedFile.size / (1024 * 1024)).toFixed(2)} MB</span>
                  <div className="selection-actions">
                    <button className="secondary-button" onClick={() => fileInputRef.current?.click()}>Change File</button>
                    <button className="primary-button" onClick={handleUpload} disabled={uploading}>{uploading ? "Uploading..." : "Upload & Continue"}</button>
                  </div>
                </div>
              )}
              {error && <div className="error-box">{error}</div>}
              <small>Large files are processed on the server to keep the browser light.</small>
            </div>
          </div>
        </section>

        {dataset && (
          <>
            <section className="overview-panel">
              {overviewCards.map((card) => (
                <div key={card.label} className="metric-card">
                  <span>{card.label}</span>
                  <strong>{card.value}</strong>
                </div>
              ))}
            </section>

            <section className="content-grid">
              <div className="panel">
                <h3>Dataset Overview</h3>
                <div className="table-wrap">
                  <table>
                    <thead>
                      <tr>
                        <th>Column</th>
                        <th>Type</th>
                        <th>Missing</th>
                        <th>Unique</th>
                        <th>Example</th>
                      </tr>
                    </thead>
                    <tbody>
                      {((dataset.profile as Record<string, any>).columns ?? []).map((column: any, index: number) => (
                        <tr key={`${column.name}-${index}`}>
                          <td>{column.name}</td>
                          <td>{column.dtype}</td>
                          <td>{column.missing_values}</td>
                          <td>{column.unique_values}</td>
                          <td>{String(column.example ?? "-")}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              <div className="panel">
                <h3>Analysis Selection</h3>
                <div className="analysis-list">
                  {ANALYSIS_OPTIONS.map((analysis) => (
                    <label key={analysis.id} className={`analysis-option ${selectedAnalyses.includes(analysis.id) ? "selected" : ""}`}>
                      <input type="checkbox" checked={selectedAnalyses.includes(analysis.id)} onChange={() => toggleAnalysis(analysis.id)} />
                      <div>
                        <strong>{analysis.label}</strong>
                        <span>{analysis.description}</span>
                      </div>
                    </label>
                  ))}
                </div>
                <button className="primary-button wide" onClick={runSelectedAnalyses} disabled={runningAnalysis || selectedAnalyses.length === 0}>
                  {runningAnalysis ? "Running Analysis..." : "Run Selected Analysis"}
                </button>
              </div>
            </section>

            {analysisResults.length > 0 && (
              <section className="panel results-panel">
                <h3>Analysis Results</h3>
                <div className="results-grid">
                  {analysisResults.map((entry) => (
                    <div key={entry.analysis} className="result-card">
                      <div className="result-header">
                        <h4>{entry.analysis}</h4>
                        <span className="badge">Success</span>
                      </div>

                      {entry.analysis === "statistics" && renderStatisticsTable((entry.result.results?.summary as Record<string, unknown>) ?? {})}
                      {entry.analysis === "missing_values" && <div className="result-metrics"><strong>{String(entry.result.results?.total_missing_cells ?? 0)}</strong><span>Total missing cells</span><strong>{String(((entry.result.results?.columns_with_highest_missing_rate as Array<Record<string, unknown>> | undefined)?.[0]?.column) ?? "None")}</strong><span>Highest missing column</span></div>}
                      {entry.analysis === "correlation" && renderCorrelationTable(entry.result.results?.strongest_relationships)}
                      <ChartRenderer chart={entry.result.chart} finding={entry.result.findings?.[0]} />

                      <ul className="finding-list">
                        {(entry.result.findings ?? []).map((finding, index) => (
                          <li key={`${entry.analysis}-${index}`}>{finding}</li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
                <div className="report-actions">
                  <button className="primary-button" onClick={generateReport}>Create Report</button>
                </div>
              </section>
            )}

            {reportData && (
              <section className="panel report-panel">
                <h3>Report Builder</h3>
                <div className="report-card">
                  <h4>{String(reportData.title || "DataPilot report")}</h4>
                  <p>{String(reportData.dataset_name || "Dataset")}</p>
                  <ul>
                    {(reportData.findings as string[] | undefined ?? []).map((finding, index) => <li key={index}>{finding}</li>)}
                  </ul>
                  <div className="results-grid">
                    {(reportData.visualizations as Array<{ analysis: string; chart: VisualizationChart }> | undefined ?? []).map((visualization) => (
                      <ChartRenderer key={visualization.analysis} chart={visualization.chart} />
                    ))}
                  </div>
                </div>
              </section>
            )}
          </>
        )}
      </main>
    </div>
  );
}

export default App;

