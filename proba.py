import os

from src.utils.connect_db import connect_to_db

from src.utils.constants import REGIONS
from dotenv import load_dotenv
from src.ingestion.get_current_data import fetch_weather_nearby

# --- Load env variables ---
load_dotenv()

# --- API Key ---
API_KEY = os.getenv("API_KEY")

# Példa koordináták (Székelyudvarhelyhez közelebb pl. 46.305, 25.295) # szarhegy
LAT = 46.740406
LON = 25.537289

conn = connect_to_db()

fetch_weather_nearby(API_KEY, conn, LAT, LON, 8, REGIONS)

