"""
FastAPI Routes
All API endpoints for the Smart City dashboard.

Endpoints:
  GET /traffic              - Latest traffic data
  GET /pollution            - Latest pollution data
  GET /weather              - Latest weather data
  GET /correlation          - Correlation analysis results
  GET /prediction           - Predict PM2.5 given inputs
"""

from fastapi import APIRouter, Query, HTTPException
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import fetch_traffic, fetch_pollution, fetch_weather

router = APIRouter()


# ─────────────────────────────────────────────
# GET /traffic
# Returns the latest traffic density readings
# ─────────────────────────────────────────────
@router.get("/traffic")
def get_traffic(limit: int = Query(default=100, ge=1, le=1000)):
    """
    Returns the latest traffic density records.
    
    Example: GET /traffic?limit=50
    """
    try:
        data = fetch_traffic(limit=limit)
        # Convert datetime objects to strings for JSON serialization
        for row in data:
            if "timestamp" in row and hasattr(row["timestamp"], "isoformat"):
                row["timestamp"] = row["timestamp"].isoformat()
        return {"status": "ok", "count": len(data), "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────
# GET /pollution
# Returns the latest pollution readings (PM2.5, CO)
# ─────────────────────────────────────────────
@router.get("/pollution")
def get_pollution(limit: int = Query(default=100, ge=1, le=1000)):
    """
    Returns the latest pollution records.
    
    Example: GET /pollution?limit=50
    """
    try:
        data = fetch_pollution(limit=limit)
        for row in data:
            if "timestamp" in row and hasattr(row["timestamp"], "isoformat"):
                row["timestamp"] = row["timestamp"].isoformat()
        return {"status": "ok", "count": len(data), "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────
# GET /weather
# Returns the latest weather readings
# ─────────────────────────────────────────────
@router.get("/weather")
def get_weather(limit: int = Query(default=100, ge=1, le=1000)):
    """
    Returns the latest weather records.
    
    Example: GET /weather?limit=50
    """
    try:
        data = fetch_weather(limit=limit)
        for row in data:
            if "timestamp" in row and hasattr(row["timestamp"], "isoformat"):
                row["timestamp"] = row["timestamp"].isoformat()
        return {"status": "ok", "count": len(data), "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────
# GET /correlation
# Runs correlation analysis and returns results
# ─────────────────────────────────────────────
@router.get("/correlation")
def get_correlation():
    """
    Runs all 4 analysis experiments and returns results.
    
    Example: GET /correlation
    """
    try:
        from analysis.correlation_analysis import run_all_analysis
        results = run_all_analysis()
        if not results:
            return {
                "status": "no_data",
                "message": "No data found. Run the data generator first.",
                "data": {}
            }
        return {"status": "ok", "data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────
# GET /prediction
# Predicts PM2.5 given traffic, humidity, rainfall
# ─────────────────────────────────────────────
@router.get("/prediction")
def get_prediction(
    traffic: float = Query(..., description="Traffic density (0-100)", ge=0, le=100),
    humidity: float = Query(..., description="Humidity percentage (0-100)", ge=0, le=100),
    rainfall: float = Query(default=0.0, description="Rainfall in mm", ge=0)
):
    """
    Predicts PM2.5 pollution level.
    
    Example: GET /prediction?traffic=80&humidity=60&rainfall=0
    
    Returns:
    {
      "predicted_pm25": 42.5,
      "inputs": { "traffic": 80, "humidity": 60, "rainfall": 0 },
      "interpretation": "Moderate pollution"
    }
    """
    try:
        from analysis.prediction_model import predict_pm25
        predicted = predict_pm25(traffic, humidity, rainfall)

        # Interpret the PM2.5 value
        if predicted < 12:
            interpretation = "Good air quality"
        elif predicted < 35:
            interpretation = "Moderate air quality"
        elif predicted < 55:
            interpretation = "Unhealthy for sensitive groups"
        elif predicted < 150:
            interpretation = "Unhealthy"
        else:
            interpretation = "Very unhealthy"

        return {
            "status": "ok",
            "predicted_pm25": predicted,
            "inputs": {
                "traffic_density": traffic,
                "humidity": humidity,
                "rainfall": rainfall
            },
            "interpretation": interpretation
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
