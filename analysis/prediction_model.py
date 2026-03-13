"""
Prediction Model
Trains a model to predict PM2.5 pollution levels
based on traffic density, humidity, and rainfall.

Model: Random Forest Regressor (simple, accurate, no scaling needed)
Fallback: Linear Regression

Run:
  python analysis/prediction_model.py
"""

import sys
import os
import numpy as np
import pandas as pd
import pickle

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import fetch_traffic, fetch_pollution, fetch_weather

# Where to save the trained model
MODEL_PATH = os.path.join(os.path.dirname(__file__), "pm25_model.pkl")

try:
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.linear_model import LinearRegression
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_absolute_error, r2_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("⚠️  scikit-learn not installed. Run: pip install scikit-learn")


def load_training_data() -> pd.DataFrame:
    """
    Load and merge sensor data for model training.
    Features: traffic_density, humidity, rainfall
    Target: pm25
    """
    traffic = fetch_traffic(limit=5000)
    pollution = fetch_pollution(limit=5000)
    weather = fetch_weather(limit=5000)

    df_t = pd.DataFrame(traffic)
    df_p = pd.DataFrame(pollution)
    df_w = pd.DataFrame(weather)

    if df_t.empty or df_p.empty or df_w.empty:
        return None

    for df in [df_t, df_p, df_w]:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["timestamp_rounded"] = df["timestamp"].dt.round("5min")

    df = df_t[["timestamp_rounded", "traffic_density"]].merge(
        df_p[["timestamp_rounded", "pm25"]], on="timestamp_rounded", how="inner"
    ).merge(
        df_w[["timestamp_rounded", "humidity", "rainfall"]], on="timestamp_rounded", how="inner"
    )

    df = df.dropna()
    print(f"✅ Loaded {len(df)} rows for training.")
    return df


def train_model():
    """
    Train a Random Forest model to predict PM2.5.
    Saves the trained model to a .pkl file.
    """
    if not SKLEARN_AVAILABLE:
        print("❌ scikit-learn required.")
        return None

    df = load_training_data()
    if df is None or len(df) < 10:
        print("⚠️  Not enough data to train. Run data generator first.")
        return None

    # Features and target
    X = df[["traffic_density", "humidity", "rainfall"]]
    y = df["pm25"]

    # Split into training and test sets (80/20)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Train Random Forest
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print(f"\n🤖 Model Training Complete!")
    print(f"   Model:  Random Forest (100 trees)")
    print(f"   MAE:    {mae:.2f} μg/m³")
    print(f"   R²:     {r2:.4f}")

    # Save model to file
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
    print(f"   Saved:  {MODEL_PATH}")

    return model


def load_model():
    """Load a previously trained model from disk."""
    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, "rb") as f:
            return pickle.load(f)
    return None


def predict_pm25(traffic_density: float, humidity: float, rainfall: float) -> float:
    """
    Predict PM2.5 level given traffic, humidity, and rainfall.
    Returns predicted PM2.5 value in μg/m³.

    Example:
      predict_pm25(traffic_density=80, humidity=60, rainfall=0)
      → Returns something like 42.5
    """
    model = load_model()

    if model is None:
        print("⚠️  No trained model found. Training now...")
        model = train_model()

    if model is None:
        # Fallback: simple formula if model unavailable
        pm25 = traffic_density * 0.4 + (100 - humidity) * 0.1 - rainfall * 0.8
        return max(0, round(pm25, 2))

    features = np.array([[traffic_density, humidity, rainfall]])
    prediction = model.predict(features)[0]
    return round(float(prediction), 2)


if __name__ == "__main__":
    print("Training PM2.5 prediction model...\n")
    model = train_model()

    if model:
        print("\n🔮 Sample Predictions:")
        test_cases = [
            (80, 60, 0),    # Peak traffic, moderate humidity, no rain
            (20, 70, 5),    # Low traffic, high humidity, raining
            (100, 40, 0),   # Max traffic, dry conditions
            (50, 80, 10),   # Moderate traffic, heavy rain
        ]
        for traffic, humidity, rainfall in test_cases:
            pred = predict_pm25(traffic, humidity, rainfall)
            print(f"   Traffic={traffic}, Humidity={humidity}%, Rainfall={rainfall}mm → PM2.5 ≈ {pred} μg/m³")
