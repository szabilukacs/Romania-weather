import time

from src.utils.connect_db import connect_to_db
from src.ingestion.load_data import load_stations, create_tables, load_weather_data

def main():

 
    # TODO: Init Airflow.
    # TODO: rewrite in pyspark
    # TODO: Cloud

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