# 🏙️ Smart City IoT Simulation Platform

A complete simulation platform that generates smart city sensor data (traffic, pollution, weather), streams it through Kafka, stores it in PostgreSQL, analyzes correlations, trains a prediction model, and displays everything on a React dashboard.

---

## 📁 Project Structure

```
smart-city-iot/
├── simulator/
│   ├── traffic_simulator.py    # Generates traffic density values
│   ├── pollution_simulator.py  # Generates PM2.5 and CO levels
│   ├── weather_simulator.py    # Generates temperature, humidity, rainfall
│   ├── producer.py             # Kafka producer (sends data to topics)
│   └── generate_data.py        # ⚡ Populate DB directly (no Kafka needed)
│
├── streaming/
│   └── kafka_consumer.py       # Kafka consumer (saves to PostgreSQL)
│
├── database/
│   ├── db.py                   # DB connection + insert/fetch functions
│   └── schema.sql              # SQL table definitions
│
├── analysis/
│   ├── correlation_analysis.py # 4 data experiments
│   └── prediction_model.py     # Train Random Forest, predict PM2.5
│
├── backend/
│   ├── main.py                 # FastAPI app entry point
│   └── routes.py               # API endpoints
│
├── dashboard/
│   ├── package.json            # Node.js dependencies
│   ├── pages/index.js          # Main React dashboard page
│   └── components/charts.js    # Reusable chart components
│
├── deployment/
│   ├── render.yaml             # Render backend deployment config
│   └── vercel.json             # Vercel frontend deployment config
│
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

---

## 🚀 Quick Start (Local)

### Step 1 — Clone and enter the project

```bash
git clone https://github.com/your-username/smart-city-iot.git
cd smart-city-iot
```

### Step 2 — Set up Python environment

```bash
# Create a virtual environment
python -m venv venv

# Activate it
# On Mac/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3 — Set up PostgreSQL

You need a PostgreSQL database. Choose one:

**Option A: Local PostgreSQL**
```bash
# Install PostgreSQL (Mac)
brew install postgresql
brew services start postgresql

# Create the database
psql -U postgres -c "CREATE DATABASE smartcity;"
```

**Option B: Free Cloud PostgreSQL (recommended for beginners)**
- Go to [https://supabase.com](https://supabase.com) or [https://neon.tech](https://neon.tech)
- Create a free project
- Copy the connection string (looks like: `postgresql://user:pass@host:5432/db`)

### Step 4 — Set environment variable

```bash
# Replace with your actual database URL
export DATABASE_URL="postgresql://postgres:password@localhost:5432/smartcity"
```

On Windows (Command Prompt):
```cmd
set DATABASE_URL=postgresql://postgres:password@localhost:5432/smartcity
```

### Step 5 — Create tables and generate data

```bash
# Create tables in the database
python database/db.py

# Generate 7 days of simulated sensor data
python simulator/generate_data.py
```

You should see output like:
```
📊 Generating 7 days of data (every 5 min)...
   ✅ 100 records inserted...
   ✅ 200 records inserted...
🎉 Done! Inserted 2016 records for each sensor type.
```

### Step 6 — Train the prediction model

```bash
python analysis/prediction_model.py
```

Output:
```
🤖 Model Training Complete!
   Model:  Random Forest (100 trees)
   MAE:    3.45 μg/m³
   R²:     0.9123
   Saved:  analysis/pm25_model.pkl

🔮 Sample Predictions:
   Traffic=80, Humidity=60%, Rainfall=0mm → PM2.5 ≈ 38.2 μg/m³
```

### Step 7 — Start the FastAPI backend

```bash
uvicorn backend.main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
✅ Database tables ready.
```

Open your browser: [http://localhost:8000](http://localhost:8000)

API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### Step 8 — Start the React dashboard

Open a new terminal:

```bash
cd dashboard
npm install
npm run dev
```

Open: [http://localhost:3000](http://localhost:3000)

---

## 🌊 Kafka Streaming (Optional)

Kafka is optional. Use `generate_data.py` if you just want to populate the database quickly.

### Install and start Kafka

```bash
# Download Kafka (Mac/Linux)
wget https://downloads.apache.org/kafka/3.7.0/kafka_2.13-3.7.0.tgz
tar -xzf kafka_2.13-3.7.0.tgz
cd kafka_2.13-3.7.0

# Start ZooKeeper (in terminal 1)
bin/zookeeper-server-start.sh config/zookeeper.properties

# Start Kafka (in terminal 2)
bin/kafka-server-start.sh config/server.properties

# Create topics (in terminal 3)
bin/kafka-topics.sh --create --topic traffic_topic --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
bin/kafka-topics.sh --create --topic pollution_topic --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
bin/kafka-topics.sh --create --topic weather_topic --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
```

### Run the producer and consumer

```bash
# Terminal A: Start consumer (reads Kafka, writes to PostgreSQL)
python streaming/kafka_consumer.py

# Terminal B: Start producer (generates and streams sensor data)
python simulator/producer.py
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/traffic?limit=100` | Latest traffic readings |
| GET | `/pollution?limit=100` | Latest pollution readings |
| GET | `/weather?limit=100` | Latest weather readings |
| GET | `/correlation` | Run all 4 analysis experiments |
| GET | `/prediction?traffic=80&humidity=60&rainfall=0` | Predict PM2.5 |

### Example API Responses

**GET /traffic**
```json
{
  "status": "ok",
  "count": 100,
  "data": [
    {
      "id": 2016,
      "timestamp": "2024-07-10T09:15:00",
      "traffic_density": 87.3
    }
  ]
}
```

**GET /prediction?traffic=80&humidity=60&rainfall=0**
```json
{
  "status": "ok",
  "predicted_pm25": 38.2,
  "inputs": {
    "traffic_density": 80,
    "humidity": 60,
    "rainfall": 0
  },
  "interpretation": "Unhealthy for sensitive groups"
}
```

**GET /correlation**
```json
{
  "status": "ok",
  "data": {
    "peak_vs_nonpeak": {
      "peak_avg": 79.4,
      "nonpeak_avg": 28.6
    },
    "pollution_spikes": {
      "threshold": 50.0,
      "spike_count": 143,
      "spike_percentage": 7.1
    },
    "traffic_pollution_correlation": {
      "traffic_vs_pm25": 0.9123,
      "interpretation": "Strong positive correlation"
    },
    "weather_impact": {
      "rainfall_vs_pm25_corr": -0.3412,
      "avg_pm25_rainy": 18.4,
      "avg_pm25_dry": 34.7
    }
  }
}
```

---

## 📊 Dashboard Features

| Chart | Data | Type |
|-------|------|------|
| Traffic Density Over Time | traffic_density | Line Chart |
| Pollution Levels Over Time | pm25, co_level | Line Chart |
| Temperature & Humidity | temperature, humidity | Line Chart |
| Traffic vs PM2.5 | scatter points | Scatter Plot |
| Correlation Summary | all experiments | Stat Cards |
| PM2.5 Prediction | sliders → API | Prediction Panel |

---

## ☁️ Deployment

### Backend → Render.com

1. Push code to GitHub
2. Go to [https://render.com](https://render.com) → New Web Service
3. Connect your GitHub repo
4. Set these environment variables in Render dashboard:
   - `DATABASE_URL` → your PostgreSQL connection string
   - `KAFKA_SERVER` → your Kafka host (or leave as localhost if not using)
5. Build command: `pip install -r requirements.txt`
6. Start command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

### Frontend → Vercel

1. Go to [https://vercel.com](https://vercel.com) → New Project
2. Import your GitHub repo
3. Set Root Directory to `dashboard`
4. Add environment variable:
   - `NEXT_PUBLIC_API_URL` → your Render backend URL (e.g. `https://smart-city-api.onrender.com`)
5. Click Deploy

---

## 🧪 Run Analysis Manually

```bash
python analysis/correlation_analysis.py
```

Output:
```
✅ Loaded 1980 merged records for analysis.

📊 Experiment 1: Peak vs Non-Peak Traffic
   Peak hours avg density:     79.4
   Non-peak hours avg density: 28.6

📊 Experiment 2: Pollution Spike Detection
   PM2.5 threshold: 50 μg/m³
   Spikes detected: 143 (7.2% of data)

📊 Experiment 3: Traffic vs Pollution Correlation
   Traffic ↔ PM2.5 correlation: 0.9123
   Traffic ↔ CO correlation:    0.8876
   Interpretation: Strong positive correlation

📊 Experiment 4: Weather Impact on Pollution
   Rainfall ↔ PM2.5 correlation: -0.3412
   Avg PM2.5 on rainy days:  18.4 μg/m³
   Avg PM2.5 on dry days:    34.7 μg/m³
```

---

## 🔑 Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |
| `KAFKA_SERVER` | Kafka broker address | `localhost:9092` |
| `NEXT_PUBLIC_API_URL` | Backend URL (used in React) | `https://your-api.onrender.com` |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Simulation | Python (random, datetime) |
| Streaming | Apache Kafka + kafka-python |
| Database | PostgreSQL + psycopg2 |
| Analysis | pandas, numpy |
| Prediction | scikit-learn (Random Forest) |
| Backend API | FastAPI + uvicorn |
| Frontend | Next.js + React + Chart.js |
| Backend Deploy | Render.com |
| Frontend Deploy | Vercel |

---

## 📦 PostgreSQL Schema

```sql
CREATE TABLE traffic_data (
    id              SERIAL PRIMARY KEY,
    timestamp       TIMESTAMP NOT NULL,
    traffic_density FLOAT NOT NULL
);

CREATE TABLE pollution_data (
    id          SERIAL PRIMARY KEY,
    timestamp   TIMESTAMP NOT NULL,
    pm25        FLOAT NOT NULL,
    co_level    FLOAT NOT NULL
);

CREATE TABLE weather_data (
    id          SERIAL PRIMARY KEY,
    timestamp   TIMESTAMP NOT NULL,
    temperature FLOAT NOT NULL,
    humidity    FLOAT NOT NULL,
    rainfall    FLOAT NOT NULL
);
```

---

## 🧑‍💻 For Beginners

**If you're new to this, follow this order:**

1. Install Python 3.10+
2. Set up a free PostgreSQL database at [neon.tech](https://neon.tech)
3. Run `pip install -r requirements.txt`
4. Set your `DATABASE_URL`
5. Run `python database/db.py` to create tables
6. Run `python simulator/generate_data.py` to fill with data
7. Run `python analysis/prediction_model.py` to train the model
8. Run `uvicorn backend.main:app --reload` to start the API
9. In a new terminal: `cd dashboard && npm install && npm run dev`
10. Open http://localhost:3000 — your dashboard is live! 🎉
