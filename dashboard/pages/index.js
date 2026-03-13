/**
 * Smart City IoT Dashboard - Main Page
 *
 * Shows:
 *  - Traffic density over time (line chart)
 *  - Pollution levels over time (line chart)
 *  - Weather (temperature & humidity) over time (line chart)
 *  - Traffic vs PM2.5 scatter plot
 *  - Correlation analysis summary
 *  - PM2.5 prediction panel
 *
 * Data refreshes every 30 seconds.
 */

import { useState, useEffect } from "react";
import {
  TrafficChart,
  PollutionChart,
  WeatherChart,
  CorrelationScatter,
} from "../components/charts";

// ── Change this to your Render backend URL when deployed ──────────────────────
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
// ─────────────────────────────────────────────────────────────────────────────

export default function Dashboard() {
  // Sensor data
  const [traffic, setTraffic] = useState([]);
  const [pollution, setPollution] = useState([]);
  const [weather, setWeather] = useState([]);
  const [correlation, setCorrelation] = useState(null);

  // Prediction panel
  const [trafficInput, setTrafficInput] = useState(60);
  const [humidityInput, setHumidityInput] = useState(55);
  const [rainfallInput, setRainfallInput] = useState(0);
  const [prediction, setPrediction] = useState(null);
  const [predicting, setPredicting] = useState(false);

  // Loading/error state
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  // ─────────────────────────────────────────────
  // Fetch all data from backend
  // ─────────────────────────────────────────────
  async function fetchAllData() {
    try {
      setError(null);

      const [trafficRes, pollutionRes, weatherRes, corrRes] = await Promise.all([
        fetch(`${API_BASE}/traffic?limit=100`),
        fetch(`${API_BASE}/pollution?limit=100`),
        fetch(`${API_BASE}/weather?limit=100`),
        fetch(`${API_BASE}/correlation`),
      ]);

      const trafficJson = await trafficRes.json();
      const pollutionJson = await pollutionRes.json();
      const weatherJson = await weatherRes.json();
      const corrJson = await corrRes.json();

      setTraffic(trafficJson.data || []);
      setPollution(pollutionJson.data || []);
      setWeather(weatherJson.data || []);
      setCorrelation(corrJson.data || null);
      setLastUpdated(new Date().toLocaleTimeString());
    } catch (err) {
      setError("Could not connect to backend. Make sure FastAPI is running on port 8000.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  // Fetch on mount, then every 30 seconds
  useEffect(() => {
    fetchAllData();
    const interval = setInterval(fetchAllData, 30000);
    return () => clearInterval(interval);
  }, []);

  // ─────────────────────────────────────────────
  // Run PM2.5 prediction
  // ─────────────────────────────────────────────
  async function handlePredict() {
    setPredicting(true);
    try {
      const res = await fetch(
        `${API_BASE}/prediction?traffic=${trafficInput}&humidity=${humidityInput}&rainfall=${rainfallInput}`
      );
      const json = await res.json();
      setPrediction(json);
    } catch (err) {
      setPrediction({ error: "Prediction failed. Make sure the backend is running." });
    } finally {
      setPredicting(false);
    }
  }

  // ─────────────────────────────────────────────
  // Render
  // ─────────────────────────────────────────────
  return (
    <div style={styles.page}>
      {/* Header */}
      <div style={styles.header}>
        <h1 style={styles.title}>🏙️ Smart City IoT Dashboard</h1>
        <p style={styles.subtitle}>
          Live sensor data: traffic, pollution, and weather
          {lastUpdated && ` · Last updated: ${lastUpdated}`}
        </p>
        <button onClick={fetchAllData} style={styles.refreshBtn}>
          🔄 Refresh Now
        </button>
      </div>

      {/* Error message */}
      {error && (
        <div style={styles.errorBox}>
          ⚠️ {error}
        </div>
      )}

      {loading ? (
        <div style={styles.loading}>Loading sensor data...</div>
      ) : (
        <>
          {/* ── Charts Row 1: Traffic & Pollution ── */}
          <div style={styles.chartsRow}>
            <div style={styles.chartCard}>
              <TrafficChart data={traffic} />
            </div>
            <div style={styles.chartCard}>
              <PollutionChart data={pollution} />
            </div>
          </div>

          {/* ── Charts Row 2: Weather & Scatter ── */}
          <div style={styles.chartsRow}>
            <div style={styles.chartCard}>
              <WeatherChart data={weather} />
            </div>
            <div style={styles.chartCard}>
              <CorrelationScatter trafficData={traffic} pollutionData={pollution} />
            </div>
          </div>

          {/* ── Stats Summary Row ── */}
          {traffic.length > 0 && (
            <div style={styles.statsRow}>
              <StatCard
                label="Latest Traffic"
                value={`${traffic[0]?.traffic_density?.toFixed(1)} / 100`}
                color="#4f46e5"
              />
              <StatCard
                label="Latest PM2.5"
                value={`${pollution[0]?.pm25?.toFixed(1)} μg/m³`}
                color="#ef4444"
              />
              <StatCard
                label="Temperature"
                value={`${weather[0]?.temperature?.toFixed(1)} °C`}
                color="#f59e0b"
              />
              <StatCard
                label="Humidity"
                value={`${weather[0]?.humidity?.toFixed(1)} %`}
                color="#06b6d4"
              />
            </div>
          )}

          {/* ── Correlation Analysis ── */}
          {correlation && (
            <div style={styles.section}>
              <h2 style={styles.sectionTitle}>📊 Correlation Analysis</h2>
              <div style={styles.statsRow}>
                <StatCard
                  label="Peak Traffic Avg"
                  value={correlation.peak_vs_nonpeak?.peak_avg}
                  color="#6366f1"
                />
                <StatCard
                  label="Non-Peak Avg"
                  value={correlation.peak_vs_nonpeak?.nonpeak_avg}
                  color="#8b5cf6"
                />
                <StatCard
                  label="Traffic↔PM2.5 Corr"
                  value={correlation.traffic_pollution_correlation?.traffic_vs_pm25}
                  color="#ec4899"
                />
                <StatCard
                  label="Pollution Spikes"
                  value={`${correlation.pollution_spikes?.spike_count} spikes`}
                  color="#f43f5e"
                />
              </div>
              <p style={styles.corrNote}>
                📌 {correlation.traffic_pollution_correlation?.interpretation}
              </p>
            </div>
          )}

          {/* ── Prediction Panel ── */}
          <div style={styles.section}>
            <h2 style={styles.sectionTitle}>🔮 Predict PM2.5 Pollution</h2>
            <p style={styles.sectionDesc}>
              Enter sensor values to predict future air pollution levels.
            </p>

            <div style={styles.predictionForm}>
              <label style={styles.label}>
                Traffic Density: <strong>{trafficInput}</strong>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={trafficInput}
                  onChange={(e) => setTrafficInput(Number(e.target.value))}
                  style={styles.slider}
                />
              </label>

              <label style={styles.label}>
                Humidity: <strong>{humidityInput}%</strong>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={humidityInput}
                  onChange={(e) => setHumidityInput(Number(e.target.value))}
                  style={styles.slider}
                />
              </label>

              <label style={styles.label}>
                Rainfall: <strong>{rainfallInput} mm</strong>
                <input
                  type="range"
                  min="0"
                  max="30"
                  step="0.5"
                  value={rainfallInput}
                  onChange={(e) => setRainfallInput(Number(e.target.value))}
                  style={styles.slider}
                />
              </label>

              <button
                onClick={handlePredict}
                disabled={predicting}
                style={styles.predictBtn}
              >
                {predicting ? "Predicting..." : "Predict PM2.5"}
              </button>
            </div>

            {prediction && (
              <div style={styles.predictionResult}>
                {prediction.error ? (
                  <p style={{ color: "#ef4444" }}>⚠️ {prediction.error}</p>
                ) : (
                  <>
                    <p style={styles.predValue}>
                      Predicted PM2.5: <strong>{prediction.predicted_pm25} μg/m³</strong>
                    </p>
                    <p style={styles.predInterp}>
                      {getAQIEmoji(prediction.predicted_pm25)} {prediction.interpretation}
                    </p>
                  </>
                )}
              </div>
            )}
          </div>
        </>
      )}

      {/* Footer */}
      <div style={styles.footer}>
        Smart City IoT Simulation Platform · Built with Python + FastAPI + React
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────
// Small stat card component
// ─────────────────────────────────────────────
function StatCard({ label, value, color }) {
  return (
    <div style={{ ...styles.statCard, borderTop: `4px solid ${color}` }}>
      <p style={styles.statLabel}>{label}</p>
      <p style={{ ...styles.statValue, color }}>{value}</p>
    </div>
  );
}

function getAQIEmoji(pm25) {
  if (pm25 < 12) return "🟢";
  if (pm25 < 35) return "🟡";
  if (pm25 < 55) return "🟠";
  if (pm25 < 150) return "🔴";
  return "🟣";
}

// ─────────────────────────────────────────────
// Inline styles (no CSS file needed)
// ─────────────────────────────────────────────
const styles = {
  page: {
    fontFamily: "'Segoe UI', sans-serif",
    maxWidth: 1200,
    margin: "0 auto",
    padding: "24px 16px",
    backgroundColor: "#f8fafc",
    minHeight: "100vh",
  },
  header: {
    textAlign: "center",
    marginBottom: 32,
  },
  title: {
    fontSize: 32,
    fontWeight: 700,
    color: "#1e293b",
    margin: 0,
  },
  subtitle: {
    color: "#64748b",
    marginTop: 8,
  },
  refreshBtn: {
    marginTop: 12,
    padding: "8px 20px",
    background: "#4f46e5",
    color: "#fff",
    border: "none",
    borderRadius: 8,
    cursor: "pointer",
    fontSize: 14,
  },
  errorBox: {
    background: "#fef2f2",
    border: "1px solid #fca5a5",
    color: "#b91c1c",
    padding: 16,
    borderRadius: 8,
    marginBottom: 24,
  },
  loading: {
    textAlign: "center",
    padding: 80,
    color: "#64748b",
    fontSize: 18,
  },
  chartsRow: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: 24,
    marginBottom: 24,
  },
  chartCard: {
    background: "#fff",
    borderRadius: 12,
    padding: 20,
    boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
  },
  statsRow: {
    display: "grid",
    gridTemplateColumns: "repeat(4, 1fr)",
    gap: 16,
    marginBottom: 24,
  },
  statCard: {
    background: "#fff",
    borderRadius: 12,
    padding: 16,
    boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
    textAlign: "center",
  },
  statLabel: {
    fontSize: 12,
    color: "#64748b",
    marginBottom: 4,
    textTransform: "uppercase",
    letterSpacing: 0.5,
  },
  statValue: {
    fontSize: 22,
    fontWeight: 700,
    margin: 0,
  },
  section: {
    background: "#fff",
    borderRadius: 12,
    padding: 24,
    marginBottom: 24,
    boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 700,
    color: "#1e293b",
    marginTop: 0,
    marginBottom: 8,
  },
  sectionDesc: {
    color: "#64748b",
    marginBottom: 20,
  },
  corrNote: {
    marginTop: 16,
    color: "#475569",
    fontStyle: "italic",
  },
  predictionForm: {
    display: "flex",
    flexDirection: "column",
    gap: 16,
    maxWidth: 480,
  },
  label: {
    display: "flex",
    flexDirection: "column",
    gap: 6,
    color: "#334155",
    fontWeight: 500,
  },
  slider: {
    width: "100%",
    accentColor: "#4f46e5",
  },
  predictBtn: {
    padding: "12px 24px",
    background: "#4f46e5",
    color: "#fff",
    border: "none",
    borderRadius: 8,
    cursor: "pointer",
    fontSize: 15,
    fontWeight: 600,
    marginTop: 8,
    width: "fit-content",
  },
  predictionResult: {
    marginTop: 20,
    padding: 20,
    background: "#f0f9ff",
    borderRadius: 8,
    border: "1px solid #bae6fd",
  },
  predValue: {
    fontSize: 20,
    margin: 0,
    color: "#0f172a",
  },
  predInterp: {
    marginTop: 8,
    fontSize: 16,
    color: "#0369a1",
  },
  footer: {
    textAlign: "center",
    padding: "24px 0",
    color: "#94a3b8",
    fontSize: 13,
  },
  "no-data": {
    color: "#94a3b8",
    textAlign: "center",
    padding: 20,
  },
};
