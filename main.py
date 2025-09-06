import time

from src.utils.connect_db import conn
from src.ingestion.load_data import load_stations, create_tables, load_weather_data

def main():

    # Letrehozni Normals tablat és betölteni oda a normal értékeket stationokhoz

    start = time.time()

    cur = conn.cursor()

    create_tables()
    
    load_stations()

    load_weather_data()

    cur.close()
    conn.close()

    end = time.time()

    print(f"Elapsed time {end - start}")


if __name__ == "__main__":
    main()