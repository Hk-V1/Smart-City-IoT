-- ═══════════════════════════════════════════════════════════
-- Smart City IoT Platform - PostgreSQL Schema
-- ═══════════════════════════════════════════════════════════
-- Run this file against your PostgreSQL database to create tables.
--
-- Using psql:
--   psql -U postgres -d smartcity -f schema.sql
--
-- Or paste this into your cloud database console (Supabase, Neon, etc.)
-- ═══════════════════════════════════════════════════════════


-- Create the database (skip if it already exists)
-- CREATE DATABASE smartcity;


-- ── Traffic Data ─────────────────────────────────────────────
-- Stores traffic density readings from the traffic sensor.
CREATE TABLE IF NOT EXISTS traffic_data (
    id              SERIAL PRIMARY KEY,
    timestamp       TIMESTAMP NOT NULL,
    traffic_density FLOAT NOT NULL       -- Range: 0 (empty) to 100 (gridlock)
);

-- Index for fast time-based queries
CREATE INDEX IF NOT EXISTS idx_traffic_timestamp ON traffic_data(timestamp);


-- ── Pollution Data ────────────────────────────────────────────
-- Stores PM2.5 and CO pollution measurements.
CREATE TABLE IF NOT EXISTS pollution_data (
    id          SERIAL PRIMARY KEY,
    timestamp   TIMESTAMP NOT NULL,
    pm25        FLOAT NOT NULL,    -- PM2.5 in μg/m³ (WHO safe: < 12)
    co_level    FLOAT NOT NULL     -- Carbon monoxide in ppm
);

CREATE INDEX IF NOT EXISTS idx_pollution_timestamp ON pollution_data(timestamp);


-- ── Weather Data ──────────────────────────────────────────────
-- Stores temperature, humidity, and rainfall readings.
CREATE TABLE IF NOT EXISTS weather_data (
    id          SERIAL PRIMARY KEY,
    timestamp   TIMESTAMP NOT NULL,
    temperature FLOAT NOT NULL,    -- Degrees Celsius
    humidity    FLOAT NOT NULL,    -- Percentage (0-100)
    rainfall    FLOAT NOT NULL     -- Millimeters (0 = no rain)
);

CREATE INDEX IF NOT EXISTS idx_weather_timestamp ON weather_data(timestamp);


-- ── Example Queries ───────────────────────────────────────────

-- Get last 10 traffic readings:
-- SELECT * FROM traffic_data ORDER BY timestamp DESC LIMIT 10;

-- Average PM2.5 per hour:
-- SELECT DATE_TRUNC('hour', timestamp) AS hour, AVG(pm25) AS avg_pm25
-- FROM pollution_data
-- GROUP BY hour
-- ORDER BY hour DESC;

-- Peak hour traffic (8-10 AM, 5-8 PM):
-- SELECT AVG(traffic_density) AS peak_avg
-- FROM traffic_data
-- WHERE EXTRACT(HOUR FROM timestamp) BETWEEN 8 AND 10
--    OR EXTRACT(HOUR FROM timestamp) BETWEEN 17 AND 20;
