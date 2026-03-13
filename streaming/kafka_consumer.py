"""
Kafka Consumer
Reads messages from Kafka topics and stores them in PostgreSQL.

Topics consumed:
  - traffic_topic
  - pollution_topic
  - weather_topic

Run this after starting the producer:
  python streaming/kafka_consumer.py
"""

import json
import sys
import os
from datetime import datetime

# Add parent folder to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import insert_traffic, insert_pollution, insert_weather, create_tables

# ─────────────────────────────────────────────
# Try to import Kafka
# ─────────────────────────────────────────────
try:
    from kafka import KafkaConsumer
    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False
    print("⚠️  kafka-python not installed. Cannot consume from Kafka.")

KAFKA_SERVER = os.getenv("KAFKA_SERVER", "localhost:9092")
TOPICS = ["traffic_topic", "pollution_topic", "weather_topic"]


def process_message(topic: str, data: dict):
    """
    Route a Kafka message to the correct database insert function.
    """
    timestamp_str = data.get("timestamp", datetime.now().isoformat())
    # Parse timestamp string to datetime object
    try:
        timestamp = datetime.fromisoformat(timestamp_str)
    except Exception:
        timestamp = datetime.now()

    if topic == "traffic_topic":
        insert_traffic(
            timestamp=timestamp,
            traffic_density=data["traffic_density"]
        )
        print(f"✅ Saved traffic: density={data['traffic_density']}")

    elif topic == "pollution_topic":
        insert_pollution(
            timestamp=timestamp,
            pm25=data["pm25"],
            co_level=data["co_level"]
        )
        print(f"✅ Saved pollution: PM2.5={data['pm25']}, CO={data['co_level']}")

    elif topic == "weather_topic":
        insert_weather(
            timestamp=timestamp,
            temperature=data["temperature"],
            humidity=data["humidity"],
            rainfall=data["rainfall"]
        )
        print(f"✅ Saved weather: temp={data['temperature']}, humidity={data['humidity']}")


def run_consumer():
    """
    Main consumer loop: read from Kafka and save to database.
    """
    if not KAFKA_AVAILABLE:
        print("❌ Kafka not available. Exiting consumer.")
        return

    # Make sure tables exist before consuming
    create_tables()

    consumer = KafkaConsumer(
        *TOPICS,
        bootstrap_servers=[KAFKA_SERVER],
        # Deserialize JSON bytes → Python dict
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        # Start from the beginning if no offset saved
        auto_offset_reset="earliest",
        group_id="smartcity-consumer-group"
    )

    print(f"🎧 Listening on topics: {TOPICS}")
    print("Press Ctrl+C to stop.\n")

    try:
        for message in consumer:
            topic = message.topic
            data = message.value
            print(f"\n📨 Received from [{topic}]:")
            process_message(topic, data)

    except KeyboardInterrupt:
        print("\n⛔ Consumer stopped by user.")
        consumer.close()


if __name__ == "__main__":
    run_consumer()
