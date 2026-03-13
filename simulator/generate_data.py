"""
Data Generator (No Kafka Required)
Generates 7 days of simulated sensor data and stores directly in PostgreSQL.
Use this to quickly populate the database for testing/demo purposes.

Run:
  python simulator/generate_data.py
"""

import sys
import os
import random
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulator.traffic_simulator import get_traffic_density
from simulator.weather_simulator import get_weather_conditions
from simulator.pollution_simulator import get_pollution_levels
from database.db import create_tables, insert_traffic, insert_pollution, insert_weather


def generate_historical_data(days: int = 7, interval_minutes: int = 5):
    """
    Generate sensor readings every `interval_minutes` for the past `days` days.
    Stores all data directly into PostgreSQL.
    """
    create_tables()

    start_time = datetime.now() - timedelta(days=days)
    current_time = start_time
    end_time = datetime.now()

    count = 0

    print(f"📊 Generating {days} days of data (every {interval_minutes} min)...")
    print(f"   From: {start_time.strftime('%Y-%m-%d %H:%M')}")
    print(f"   To:   {end_time.strftime('%Y-%m-%d %H:%M')}\n")

    while current_time <= end_time:
        # Generate readings
        traffic_density = get_traffic_density(current_time)
        weather = get_weather_conditions(current_time)
        pollution = get_pollution_levels(traffic_density, weather["rainfall"])

        # Save to database
        insert_traffic(current_time, traffic_density)
        insert_weather(current_time, weather["temperature"], weather["humidity"], weather["rainfall"])
        insert_pollution(current_time, pollution["pm25"], pollution["co_level"])

        count += 1
        if count % 100 == 0:
            print(f"   ✅ {count} records inserted... ({current_time.strftime('%Y-%m-%d %H:%M')})")

        current_time += timedelta(minutes=interval_minutes)

    print(f"\n🎉 Done! Inserted {count} records for each sensor type.")
    print(f"   Total rows: ~{count * 3} across all tables.")


if __name__ == "__main__":
    generate_historical_data(days=7, interval_minutes=5)
