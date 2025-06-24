import os
import uuid
import requests

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware 
from pydantic import BaseModel 
from typing import Dict, Any, Optional
import uvicorn 

app = FastAPI(title="Weather Data System", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for weather data
weather_storage: Dict[str, Dict[str, Any]] = {}

class WeatherRequest(BaseModel):
    date: str
    location: str
    notes: Optional[str] = ""

class WeatherResponse(BaseModel):
    id: str

@app.post("/weather", response_model=WeatherResponse)
async def create_weather_request(request: WeatherRequest):
    """
    You need to implement this endpoint to handle the following:
    1. Receive form data (date, location, notes)
    2. Calls WeatherStack API for the location
    3. Stores combined data with unique ID in memory
    4. Returns the ID to frontend
    """
    # 1. Recieve data
    api_key = os.getenv("WEATHERSTACK_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Weather API key not configured")

    # 2. Calls WeatherStack API for the location
    params = {
        "access_key": api_key,
        "query": request.location,
        "historical_date": request.date
    }
    resp = requests.get("http://api.weatherstack.com/historical", params=params)
    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail="Error fetching data from WeatherStack")

    data = resp.json()
    if "error" in data:
        # propagate WeatherStack error info
        detail = data["error"].get("info", "Unknown WeatherStack error")
        raise HTTPException(status_code=400, detail=detail)

    # 3. Stores combined data with unique ID in memory
    weather_id = str(uuid.uuid4())
    record = {
        "id": weather_id,
        "date": request.date,
        "location": request.location,
        "notes": request.notes,
        "weather": data
    }
    weather_storage[weather_id] = record

    # 4. Returns the ID to frontend
    return {"id": weather_id}

@app.get("/weather/{weather_id}")
async def get_weather_data(weather_id: str):
    """
    Retrieve stored weather data by ID.
    This endpoint is already implemented for the assessment.
    """
    if weather_id not in weather_storage:
        raise HTTPException(status_code=404, detail="Weather data not found")
    
    return weather_storage[weather_id]


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)