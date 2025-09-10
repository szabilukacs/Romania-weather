import os
import requests
from datetime import datetime

from src.utils.connect_db import conn

from dotenv import load_dotenv

# --- Load env variables ---
load_dotenv()

# --- API Key ---
API_KEY = os.getenv("API_KEY")

# Példa koordináták (Székelyudvarhelyhez közelebb pl. 46.305, 25.295) # szarhegy
LAT = 46.740406
LON = 25.537289


# --- API request ---
url = f"https://api.openweathermap.org/data/3.0/onecall?lat={LAT}&lon={LON}&exclude=hourly,daily&appid={API_KEY}&units=metric"
response = requests.get(url)
data = response.json()

if response.status_code == 200:

    # --- Extract current weather ---
    current = data.get("current", {})
    weather = current.get("weather", [{}])[0]  # first element in weather list
    station_id = 15004

    record = {
        "station_id": station_id,  
        "lat": data["lat"],
        "lon": data["lon"],
        "timezone": data["timezone"],
        "timezone_offset": data["timezone_offset"],
        "dt": datetime.fromtimestamp(current["dt"]),
        "sunrise": datetime.fromtimestamp(current["sunrise"]),
        "sunset": datetime.fromtimestamp(current["sunset"]),
        "temp": current.get("temp"),
        "feels_like": current.get("feels_like"),
        "pressure": current.get("pressure"),
        "humidity": current.get("humidity"),
        "dew_point": current.get("dew_point"),
        "uvi": current.get("uvi"),
        "clouds": current.get("clouds"),
        "visibility": current.get("visibility"),
        "wind_speed": current.get("wind_speed"),
        "wind_deg": current.get("wind_deg"),
        "wind_gust": current.get("wind_gust"),
        "weather_id": weather.get("id"),
        "weather_main": weather.get("main"),
        "weather_description": weather.get("description"),
        "weather_icon": weather.get("icon"),
    }

    # --- Insert into PostgreSQL ---
    cur = conn.cursor()

    insert_query = """
    INSERT INTO weather_live (
        station_id, lat, lon, timezone, timezone_offset,
        dt, sunrise, sunset, temp, feels_like, pressure,
        humidity, dew_point, uvi, clouds, visibility,
        wind_speed, wind_deg, wind_gust,
        weather_id, weather_main, weather_description, weather_icon
    )
    VALUES (
        %(station_id)s,
        %(lat)s, %(lon)s, %(timezone)s, %(timezone_offset)s,
        %(dt)s, %(sunrise)s, %(sunset)s, %(temp)s, %(feels_like)s, %(pressure)s,
        %(humidity)s, %(dew_point)s, %(uvi)s, %(clouds)s, %(visibility)s,
        %(wind_speed)s, %(wind_deg)s, %(wind_gust)s,
        %(weather_id)s, %(weather_main)s, %(weather_description)s, %(weather_icon)s
    );
    """

    cur.execute(insert_query, record)
    conn.commit()

    cur.close()
    conn.close()

    print("✅ Record inserted successfully.")
else:
    print(f"❌ Hiba: {response.status_code} - {response.text}")

