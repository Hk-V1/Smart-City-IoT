"""
Correlation Analysis
Performs data analysis experiments on the stored sensor data.

Experiments:
  1. Peak vs Non-Peak Traffic comparison
  2. Pollution Spike Detection (PM2.5 > threshold)
  3. Traffic vs Pollution correlation
  4. Weather impact on pollution

Run:
  python analysis/correlation_analysis.py
"""

import sys
import os
import pandas as pd
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import fetch_traffic, fetch_pollution, fetch_weather, fetch_joined_data


def load_data_as_dataframe():
    """
    Load all sensor data from the database and merge into one DataFrame.
    """
    traffic = fetch_traffic(limit=5000)
    pollution = fetch_pollution(limit=5000)
    weather = fetch_weather(limit=5000)

    # Convert to DataFrames
    df_t = pd.DataFrame(traffic)
    df_p = pd.DataFrame(pollution)
    df_w = pd.DataFrame(weather)

    if df_t.empty or df_p.empty or df_w.empty:
        print("⚠️  No data found. Run the data generator first:")
        print("   python simulator/generate_data.py")
        return None

    # Convert timestamps to datetime
    for df in [df_t, df_p, df_w]:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        # Round to nearest 5 minutes for merging
        df["timestamp_rounded"] = df["timestamp"].dt.round("5min")

    # Merge all three on rounded timestamp
    df = df_t[["timestamp_rounded", "traffic_density"]].merge(
        df_p[["timestamp_rounded", "pm25", "co_level"]], on="timestamp_rounded", how="inner"
    ).merge(
        df_w[["timestamp_rounded", "temperature", "humidity", "rainfall"]], on="timestamp_rounded", how="inner"
    )

    # Add hour column for time-based analysis
    df["hour"] = df["timestamp_rounded"].dt.hour
    df["is_peak"] = df["hour"].apply(
        lambda h: True if (8 <= h <= 10 or 17 <= h <= 20) else False
    )

    print(f"✅ Loaded {len(df)} merged records for analysis.\n")
    return df


# ─────────────────────────────────────────────
# Experiment 1: Peak vs Non-Peak Traffic
# ─────────────────────────────────────────────
def analyze_peak_vs_nonpeak(df: pd.DataFrame) -> dict:
    """Compare average traffic density during peak vs non-peak hours."""
    peak = df[df["is_peak"] == True]["traffic_density"]
    nonpeak = df[df["is_peak"] == False]["traffic_density"]

    result = {
        "peak_avg": round(peak.mean(), 2),
        "nonpeak_avg": round(nonpeak.mean(), 2),
        "peak_max": round(peak.max(), 2),
        "nonpeak_max": round(nonpeak.max(), 2),
        "peak_count": int(len(peak)),
        "nonpeak_count": int(len(nonpeak))
    }

    print("📊 Experiment 1: Peak vs Non-Peak Traffic")
    print(f"   Peak hours avg density:     {result['peak_avg']}")
    print(f"   Non-peak hours avg density: {result['nonpeak_avg']}")
    print()

    return result


# ─────────────────────────────────────────────
# Experiment 2: Pollution Spike Detection
# ─────────────────────────────────────────────
def detect_pollution_spikes(df: pd.DataFrame, threshold: float = 50.0) -> dict:
    """
    Detect records where PM2.5 is unusually high.
    Default threshold: 50 μg/m³ (WHO unhealthy level)
    """
    spikes = df[df["pm25"] > threshold]

    result = {
        "threshold": threshold,
        "total_records": int(len(df)),
        "spike_count": int(len(spikes)),
        "spike_percentage": round(len(spikes) / len(df) * 100, 2) if len(df) > 0 else 0,
        "max_pm25": round(df["pm25"].max(), 2),
        "avg_pm25": round(df["pm25"].mean(), 2),
        "spikes": spikes[["timestamp_rounded", "pm25", "traffic_density"]].head(10).to_dict(orient="records")
    }

    print("📊 Experiment 2: Pollution Spike Detection")
    print(f"   PM2.5 threshold: {threshold} μg/m³")
    print(f"   Spikes detected: {result['spike_count']} ({result['spike_percentage']}% of data)")
    print(f"   Max PM2.5: {result['max_pm25']} μg/m³")
    print()

    return result


# ─────────────────────────────────────────────
# Experiment 3: Traffic vs Pollution Correlation
# ─────────────────────────────────────────────
def calculate_traffic_pollution_correlation(df: pd.DataFrame) -> dict:
    """
    Calculate Pearson correlation between traffic_density and PM2.5.
    Value ranges from -1 (inverse) to 1 (direct correlation).
    """
    corr_pm25 = df["traffic_density"].corr(df["pm25"])
    corr_co = df["traffic_density"].corr(df["co_level"])

    result = {
        "traffic_vs_pm25": round(corr_pm25, 4),
        "traffic_vs_co": round(corr_co, 4),
        "interpretation": (
            "Strong positive correlation" if corr_pm25 > 0.7
            else "Moderate positive correlation" if corr_pm25 > 0.4
            else "Weak correlation"
        )
    }

    print("📊 Experiment 3: Traffic vs Pollution Correlation")
    print(f"   Traffic ↔ PM2.5 correlation: {result['traffic_vs_pm25']}")
    print(f"   Traffic ↔ CO correlation:    {result['traffic_vs_co']}")
    print(f"   Interpretation: {result['interpretation']}")
    print()

    return result


# ─────────────────────────────────────────────
# Experiment 4: Weather Impact on Pollution
# ─────────────────────────────────────────────
def analyze_weather_impact(df: pd.DataFrame) -> dict:
    """
    Analyze how rainfall and humidity affect PM2.5.
    """
    corr_rainfall = df["rainfall"].corr(df["pm25"])
    corr_humidity = df["humidity"].corr(df["pm25"])

    # Average PM2.5 with and without rain
    rainy = df[df["rainfall"] > 0]["pm25"]
    dry = df[df["rainfall"] == 0]["pm25"]

    result = {
        "rainfall_vs_pm25_corr": round(corr_rainfall, 4),
        "humidity_vs_pm25_corr": round(corr_humidity, 4),
        "avg_pm25_rainy": round(rainy.mean(), 2) if len(rainy) > 0 else None,
        "avg_pm25_dry": round(dry.mean(), 2) if len(dry) > 0 else None,
    }

    print("📊 Experiment 4: Weather Impact on Pollution")
    print(f"   Rainfall ↔ PM2.5 correlation: {result['rainfall_vs_pm25_corr']}")
    print(f"   Humidity ↔ PM2.5 correlation: {result['humidity_vs_pm25_corr']}")
    print(f"   Avg PM2.5 on rainy days:  {result['avg_pm25_rainy']} μg/m³")
    print(f"   Avg PM2.5 on dry days:    {result['avg_pm25_dry']} μg/m³")
    print()

    return result


def run_all_analysis() -> dict:
    """Run all four analysis experiments and return results."""
    df = load_data_as_dataframe()
    if df is None:
        return {}

    results = {
        "peak_vs_nonpeak": analyze_peak_vs_nonpeak(df),
        "pollution_spikes": detect_pollution_spikes(df),
        "traffic_pollution_correlation": calculate_traffic_pollution_correlation(df),
        "weather_impact": analyze_weather_impact(df)
    }

    return results


if __name__ == "__main__":
    run_all_analysis()
