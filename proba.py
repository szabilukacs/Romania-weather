import os

from src.utils.connect_db import connect_to_db

from dotenv import load_dotenv
from src.ingestion.get_current_data import fetch_and_store_weather

# --- Load env variables ---
load_dotenv()

# --- API Key ---
API_KEY = os.getenv("API_KEY")

# Példa koordináták (Székelyudvarhelyhez közelebb pl. 46.305, 25.295) # szarhegy
LAT = 46.740406
LON = 25.537289

# ezt beraki ingestionbe, fuggvenybe, bemente lan long, station_id
from meteostat import Stations

conn = connect_to_db()

# --- Legközelebbi 30 állomás lekérése ---
stations = Stations().nearby(LAT, LON).fetch(5)

# --- Iterálás az állomásokon ---
for idx, row in stations.iterrows():
    station_id = row["wmo"] or row["icao"] or idx  # fallback azonosító, ha WMO nincs
    lat = row["latitude"]
    lon = row["longitude"]
    name = row["name"]

    print(f"🌍 Lekérés: {name} (ID={station_id}, lat={lat}, lon={lon})")

    try:
        fetch_and_store_weather(
            lat=lat,
            lon=lon,
            station_id=station_id,
            conn=conn,
            api_key=API_KEY
        )
    except Exception as e:
        print(f"❌ Hiba {name} állomásnál: {e}")


conn.close()

