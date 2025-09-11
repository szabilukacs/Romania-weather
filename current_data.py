import os
from dotenv import load_dotenv

from src.utils.connect_db import connect_to_db
from src.ingestion.get_current_data import fetch_weather_nearby
from src.utils.constants import REGIONS

# --- Load env variables ---
load_dotenv()

# --- API Key ---
API_KEY = os.getenv("API_KEY")

conn = connect_to_db()

fetch_weather_nearby(API_KEY, conn, REGIONS)

