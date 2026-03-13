/**
 * Charts Component
 * Reusable chart components for the Smart City dashboard.
 * Uses Chart.js via react-chartjs-2.
 */

import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { Line, Scatter } from "react-chartjs-2";

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

// ─────────────────────────────────────────────
// Traffic Line Chart
// ─────────────────────────────────────────────
export function TrafficChart({ data }) {
  if (!data || data.length === 0) return <p className="no-data">No traffic data available.</p>;

  // Reverse so oldest is first (left to right)
  const sorted = [...data].reverse();

  const chartData = {
    labels: sorted.map((d) => {
      const date = new Date(d.timestamp);
      return date.toLocaleTimeString();
    }),
    datasets: [
      {
        label: "Traffic Density",
        data: sorted.map((d) => d.traffic_density),
        borderColor: "#4f46e5",
        backgroundColor: "rgba(79, 70, 229, 0.1)",
        tension: 0.3,
        pointRadius: 2,
        fill: true,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: { position: "top" },
      title: { display: true, text: "Traffic Density Over Time" },
    },
    scales: {
      y: { min: 0, max: 100, title: { display: true, text: "Density" } },
    },
  };

  return <Line data={chartData} options={options} />;
}

// ─────────────────────────────────────────────
// Pollution Line Chart (PM2.5 and CO)
// ─────────────────────────────────────────────
export function PollutionChart({ data }) {
  if (!data || data.length === 0) return <p className="no-data">No pollution data available.</p>;

  const sorted = [...data].reverse();

  const chartData = {
    labels: sorted.map((d) => new Date(d.timestamp).toLocaleTimeString()),
    datasets: [
      {
        label: "PM2.5 (μg/m³)",
        data: sorted.map((d) => d.pm25),
        borderColor: "#ef4444",
        backgroundColor: "rgba(239, 68, 68, 0.1)",
        tension: 0.3,
        pointRadius: 2,
        fill: true,
      },
      {
        label: "CO Level (ppm)",
        data: sorted.map((d) => d.co_level),
        borderColor: "#f97316",
        backgroundColor: "rgba(249, 115, 22, 0.1)",
        tension: 0.3,
        pointRadius: 2,
        fill: false,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: { position: "top" },
      title: { display: true, text: "Pollution Levels Over Time" },
    },
    scales: {
      y: { title: { display: true, text: "Value" } },
    },
  };

  return <Line data={chartData} options={options} />;
}

// ─────────────────────────────────────────────
// Weather Line Chart (Temperature & Humidity)
// ─────────────────────────────────────────────
export function WeatherChart({ data }) {
  if (!data || data.length === 0) return <p className="no-data">No weather data available.</p>;

  const sorted = [...data].reverse();

  const chartData = {
    labels: sorted.map((d) => new Date(d.timestamp).toLocaleTimeString()),
    datasets: [
      {
        label: "Temperature (°C)",
        data: sorted.map((d) => d.temperature),
        borderColor: "#f59e0b",
        backgroundColor: "rgba(245, 158, 11, 0.1)",
        tension: 0.3,
        pointRadius: 2,
        fill: false,
      },
      {
        label: "Humidity (%)",
        data: sorted.map((d) => d.humidity),
        borderColor: "#06b6d4",
        backgroundColor: "rgba(6, 182, 212, 0.1)",
        tension: 0.3,
        pointRadius: 2,
        fill: false,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: { position: "top" },
      title: { display: true, text: "Temperature & Humidity Over Time" },
    },
    scales: {
      y: { title: { display: true, text: "Value" } },
    },
  };

  return <Line data={chartData} options={options} />;
}

// ─────────────────────────────────────────────
// Traffic vs PM2.5 Scatter Plot
// ─────────────────────────────────────────────
export function CorrelationScatter({ trafficData, pollutionData }) {
  if (!trafficData || !pollutionData || trafficData.length === 0) {
    return <p className="no-data">Not enough data for correlation chart.</p>;
  }

  // Match by index (simplified — assumes data is aligned)
  const minLen = Math.min(trafficData.length, pollutionData.length);
  const points = [];
  for (let i = 0; i < minLen; i++) {
    points.push({
      x: trafficData[i].traffic_density,
      y: pollutionData[i].pm25,
    });
  }

  const chartData = {
    datasets: [
      {
        label: "Traffic vs PM2.5",
        data: points,
        backgroundColor: "rgba(99, 102, 241, 0.6)",
        pointRadius: 4,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: { position: "top" },
      title: { display: true, text: "Traffic Density vs PM2.5 (Scatter)" },
    },
    scales: {
      x: { title: { display: true, text: "Traffic Density" } },
      y: { title: { display: true, text: "PM2.5 (μg/m³)" } },
    },
  };

  return <Scatter data={chartData} options={options} />;
}
