"""
Database Module
Handles PostgreSQL connection and data insertion.

Tables:
  - traffic_data
  - pollution_data
  - weather_data

Set your DATABASE_URL environment variable:
  export DATABASE_URL="postgresql://user:password@host:5432/dbname"
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor

# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/smartcity")


def get_connection():
    """Create and return a PostgreSQL connection."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        raise


def create_tables():
    """
    Create all required tables if they don't exist.
    Run this once when setting up the database.
    """
    sql = """
    -- Traffic data table
    CREATE TABLE IF NOT EXISTS traffic_data (
        id          SERIAL PRIMARY KEY,
        timestamp   TIMESTAMP NOT NULL,
        traffic_density FLOAT NOT NULL
    );

    -- Pollution data table
    CREATE TABLE IF NOT EXISTS pollution_data (
        id          SERIAL PRIMARY KEY,
        timestamp   TIMESTAMP NOT NULL,
        pm25        FLOAT NOT NULL,
        co_level    FLOAT NOT NULL
    );

    -- Weather data table
    CREATE TABLE IF NOT EXISTS weather_data (
        id          SERIAL PRIMARY KEY,
        timestamp   TIMESTAMP NOT NULL,
        temperature FLOAT NOT NULL,
        humidity    FLOAT NOT NULL,
        rainfall    FLOAT NOT NULL
    );
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()
        print("✅ Tables created (or already exist).")
    finally:
        conn.close()


# ─────────────────────────────────────────────
# Insert functions
# ─────────────────────────────────────────────

def insert_traffic(timestamp, traffic_density: float):
    """Insert one traffic record."""
    sql = "INSERT INTO traffic_data (timestamp, traffic_density) VALUES (%s, %s)"
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (timestamp, traffic_density))
        conn.commit()
    finally:
        conn.close()


def insert_pollution(timestamp, pm25: float, co_level: float):
    """Insert one pollution record."""
    sql = "INSERT INTO pollution_data (timestamp, pm25, co_level) VALUES (%s, %s, %s)"
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (timestamp, pm25, co_level))
        conn.commit()
    finally:
        conn.close()


def insert_weather(timestamp, temperature: float, humidity: float, rainfall: float):
    """Insert one weather record."""
    sql = "INSERT INTO weather_data (timestamp, temperature, humidity, rainfall) VALUES (%s, %s, %s, %s)"
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (timestamp, temperature, humidity, rainfall))
        conn.commit()
    finally:
        conn.close()


# ─────────────────────────────────────────────
# Fetch functions (used by FastAPI routes)
# ─────────────────────────────────────────────

def fetch_traffic(limit: int = 100) -> list:
    """Fetch the latest traffic records."""
    sql = "SELECT * FROM traffic_data ORDER BY timestamp DESC LIMIT %s"
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, (limit,))
            rows = cur.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def fetch_pollution(limit: int = 100) -> list:
    """Fetch the latest pollution records."""
    sql = "SELECT * FROM pollution_data ORDER BY timestamp DESC LIMIT %s"
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, (limit,))
            rows = cur.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def fetch_weather(limit: int = 100) -> list:
    """Fetch the latest weather records."""
    sql = "SELECT * FROM weather_data ORDER BY timestamp DESC LIMIT %s"
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, (limit,))
            rows = cur.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def fetch_joined_data(limit: int = 200) -> list:
    """
    Fetch traffic + pollution joined by closest timestamp.
    Used for correlation analysis.
    """
    sql = """
    SELECT
        t.timestamp,
        t.traffic_density,
        p.pm25,
        p.co_level,
        w.temperature,
        w.humidity,
        w.rainfall
    FROM traffic_data t
    JOIN pollution_data p
        ON DATE_TRUNC('minute', t.timestamp) = DATE_TRUNC('minute', p.timestamp)
    JOIN weather_data w
        ON DATE_TRUNC('minute', t.timestamp) = DATE_TRUNC('minute', w.timestamp)
    ORDER BY t.timestamp DESC
    LIMIT %s
    """
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, (limit,))
            rows = cur.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


if __name__ == "__main__":
    print("Setting up database tables...")
    create_tables()
