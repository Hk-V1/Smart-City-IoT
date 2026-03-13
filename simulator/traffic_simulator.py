"""
Traffic Simulator
Generates realistic traffic density values based on time of day.
Peak hours (8-10 AM, 5-8 PM) have higher traffic density.
"""

import random
from datetime import datetime


def get_traffic_density(timestamp: datetime = None) -> float:
    """
    Returns a traffic density value (0-100) based on time of day.
    Peak hours: 8-10 AM and 5-8 PM → higher values (60-100)
    Non-peak hours → lower values (10-50)
    """
    if timestamp is None:
        timestamp = datetime.now()

    hour = timestamp.hour

    # Define peak hours
    is_morning_peak = 8 <= hour <= 10
    is_evening_peak = 17 <= hour <= 20

    if is_morning_peak or is_evening_peak:
        # Peak hour traffic: 60 to 100
        base = random.uniform(60, 100)
    elif 0 <= hour <= 5:
        # Late night: very low traffic
        base = random.uniform(5, 20)
    else:
        # Normal hours: 10 to 50
        base = random.uniform(10, 50)

    # Add small random variation (noise)
    noise = random.uniform(-5, 5)
    density = max(0, min(100, base + noise))  # Clamp between 0 and 100

    return round(density, 2)


def generate_traffic_reading(timestamp: datetime = None) -> dict:
    """
    Returns a full traffic sensor reading as a dictionary.
    """
    if timestamp is None:
        timestamp = datetime.now()

    return {
        "sensor_type": "traffic",
        "timestamp": timestamp.isoformat(),
        "traffic_density": get_traffic_density(timestamp)
    }
