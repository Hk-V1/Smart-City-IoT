"""
Weather Simulator
Simulates temperature, humidity, and rainfall.
Adds random daily fluctuations.
"""

import random
from datetime import datetime


def get_weather_conditions(timestamp: datetime = None) -> dict:
    """
    Returns temperature (°C), humidity (%), and rainfall (mm).
    Temperature varies by time of day.
    """
    if timestamp is None:
        timestamp = datetime.now()

    hour = timestamp.hour

    # Temperature: cooler at night, warmer during the day
    if 6 <= hour <= 14:
        base_temp = random.uniform(22, 35)   # Daytime
    elif 14 < hour <= 20:
        base_temp = random.uniform(18, 30)   # Evening
    else:
        base_temp = random.uniform(12, 22)   # Night

    # Add small random variation
    temperature = base_temp + random.uniform(-2, 2)

    # Humidity: higher in morning and evening
    if 5 <= hour <= 9 or 18 <= hour <= 22:
        humidity = random.uniform(60, 90)
    else:
        humidity = random.uniform(30, 65)

    # Rainfall: random chance of rain (20% chance)
    if random.random() < 0.2:
        rainfall = random.uniform(0.5, 15)  # mm
    else:
        rainfall = 0.0

    return {
        "temperature": round(temperature, 2),
        "humidity": round(humidity, 2),
        "rainfall": round(rainfall, 2)
    }


def generate_weather_reading(timestamp: datetime = None) -> dict:
    """
    Returns a full weather sensor reading as a dictionary.
    """
    if timestamp is None:
        timestamp = datetime.now()

    conditions = get_weather_conditions(timestamp)

    return {
        "sensor_type": "weather",
        "timestamp": timestamp.isoformat(),
        "temperature": conditions["temperature"],
        "humidity": conditions["humidity"],
        "rainfall": conditions["rainfall"]
    }
