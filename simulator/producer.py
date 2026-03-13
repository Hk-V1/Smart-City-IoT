"""
Kafka Producer
Sends simulated sensor data to Kafka topics every 2-5 seconds.

Topics:
  - traffic_topic
  - pollution_topic
  - weather_topic

Run this script to start streaming data:
  python simulator/producer.py
"""

import json
import time
import random
import sys
import os
from datetime import datetime

# Add parent folder to path so we can import simulators
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulator.traffic_simulator import generate_traffic_reading
from simulator.weather_simulator import generate_weather_reading
from simulator.pollution_simulator import generate_pollution_reading

# ─────────────────────────────────────────────
# Try to import Kafka. If not available, print a warning.
# ─────────────────────────────────────────────
try:
    from kafka import KafkaProducer
    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False
    print("⚠️  kafka-python not installed. Running in DEMO mode (data printed only).")

# Kafka server address — change this if your Kafka is on a different host
KAFKA_SERVER = os.getenv("KAFKA_SERVER", "localhost:9092")

# ─────────────────────────────────────────────
# Setup Kafka producer (if available)
# ─────────────────────────────────────────────
def create_producer():
    """Create and return a Kafka producer."""
    if not KAFKA_AVAILABLE:
        return None
    try:
        producer = KafkaProducer(
            bootstrap_servers=[KAFKA_SERVER],
            # Serialize Python dict → JSON bytes
            value_serializer=lambda v: json.dumps(v).encode("utf-8")
        )
        print(f"✅ Connected to Kafka at {KAFKA_SERVER}")
        return producer
    except Exception as e:
        print(f"❌ Could not connect to Kafka: {e}")
        return None


def send_message(producer, topic: str, message: dict):
    """Send a message to a Kafka topic."""
    if producer:
        producer.send(topic, value=message)
        producer.flush()
    # Always print so you can see data even without Kafka
    print(f"[{topic}] {json.dumps(message, indent=2)}")


def run_producer():
    """
    Main loop: generate sensor data and send to Kafka every 2-5 seconds.
    """
    producer = create_producer()
    print("\n🚀 Starting Smart City IoT Simulator...\n")

    try:
        while True:
            now = datetime.now()

            # --- Generate sensor readings ---
            traffic_data = generate_traffic_reading(now)
            weather_data = generate_weather_reading(now)

            # Pollution depends on traffic density and rainfall
            pollution_data = generate_pollution_reading(
                traffic_density=traffic_data["traffic_density"],
                rainfall=weather_data["rainfall"],
                timestamp=now
            )

            # --- Send to Kafka topics ---
            send_message(producer, "traffic_topic", traffic_data)
            send_message(producer, "weather_topic", weather_data)
            send_message(producer, "pollution_topic", pollution_data)

            print("─" * 40)

            # Wait 2-5 seconds before next reading
            sleep_time = random.uniform(2, 5)
            time.sleep(sleep_time)

    except KeyboardInterrupt:
        print("\n⛔ Simulator stopped by user.")
        if producer:
            producer.close()


if __name__ == "__main__":
    run_producer()
