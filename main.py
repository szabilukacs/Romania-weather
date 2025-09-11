import time

from src.utils.connect_db import connect_to_db
from src.ingestion.load_data import load_stations, create_tables, load_weather_data

def main():

    # TODO: Letrehozni Normals tablat és betölteni oda a normal értékeket stationokhoz
    # TODO: torolni monthly adatokat ha nem kellenek akar
    # TODO: Terv: kod tisztitas -> adatb'zis api-nak -> api lekeresek megcsinalasa proba a terkephez
    # pytestek futtatasa -> Gitlab actions -> Docker
    # DAG implementalsa, airflow ha megy
    # Release
    # Ezutan a cloudos cuccok

    start = time.time()

    conn = connect_to_db()

    cur = conn.cursor()

    create_tables(conn)
    
    load_stations(conn)
    
    load_weather_data(conn)

    cur.close()
    conn.close()

    end = time.time()

    print(f"Elapsed time {end - start}")


if __name__ == "__main__":
    main()