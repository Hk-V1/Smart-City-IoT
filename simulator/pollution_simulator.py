"""
Pollution Simulator
Simulates PM2.5 and CO levels.
Pollution is correlated with traffic density — more traffic = more pollution.
Rainfall reduces pollution.
"""

import random


def get_pollution_levels(traffic_density: float, rainfall: float = 0.0) -> dict:
    """
    Returns PM2.5 and CO levels based on traffic density and rainfall.

    traffic_density: 0-100 (from traffic simulator)
    rainfall: mm of rain (from weather simulator) — reduces pollution
    """

    # PM2.5 is correlated with traffic
    # Formula: PM2.5 = traffic * random_factor + noise
    pm25_factor = random.uniform(0.3, 0.6)
    pm25_noise = random.uniform(-5, 10)
    pm25 = (traffic_density * pm25_factor) + pm25_noise

    # Rainfall washes away particles — reduce PM2.5
    rainfall_reduction = rainfall * random.uniform(0.5, 1.5)
    pm25 = max(0, pm25 - rainfall_reduction)

    # CO level also tied to traffic
    co_factor = random.uniform(0.01, 0.03)
    co_noise = random.uniform(-0.1, 0.2)
    co_level = (traffic_density * co_factor) + co_noise
    co_level = max(0, co_level)

    return {
        "pm25": round(pm25, 2),
        "co_level": round(co_level, 3)
    }


def generate_pollution_reading(traffic_density: float, rainfall: float = 0.0,
                                timestamp=None) -> dict:
    """
    Returns a full pollution sensor reading as a dictionary.
    """
    from datetime import datetime
    if timestamp is None:
        timestamp = datetime.now()

    levels = get_pollution_levels(traffic_density, rainfall)

    return {
        "sensor_type": "pollution",
        "timestamp": timestamp.isoformat(),
        "pm25": levels["pm25"],
        "co_level": levels["co_level"]
    }
