#!/bin/bash
# 1. Run the seed script to populate the DB
echo "🌱 Seeding Solapur Health Data..."
python3 seed_data.py

# 2. Start the FastAPI server
echo "🚀 Starting CityHealth 360 API..."
uvicorn main:app --host 0.0.0.0 --port 8000