"""
FastAPI Backend - Main Application Entry Point

Run locally:
  uvicorn backend.main:app --reload --port 8000

Or from the project root:
  uvicorn backend.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.routes import router
from database.db import create_tables

# ─────────────────────────────────────────────
# Create FastAPI app
# ─────────────────────────────────────────────
app = FastAPI(
    title="Smart City IoT API",
    description="API for Smart City IoT Simulation Platform",
    version="1.0.0"
)

# ─────────────────────────────────────────────
# Allow React dashboard to call this API
# ─────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, set to your Vercel URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routes
app.include_router(router)


# ─────────────────────────────────────────────
# Root endpoint
# ─────────────────────────────────────────────
@app.get("/")
def root():
    return {
        "message": "Smart City IoT API is running ✅",
        "endpoints": [
            "/traffic",
            "/pollution",
            "/weather",
            "/correlation",
            "/prediction?traffic=80&humidity=60&rainfall=0"
        ]
    }


# ─────────────────────────────────────────────
# Create tables on startup
# ─────────────────────────────────────────────
@app.on_event("startup")
def startup_event():
    try:
        create_tables()
        print("✅ Database tables ready.")
    except Exception as e:
        print(f"⚠️  Could not connect to database: {e}")
