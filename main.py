import time

from src.utils.connect_db import connect_to_db
from src.ingestion.load_data import load_stations, create_tables, load_weather_data

def main():

 
    # TODO: Docker ok, airflow folyamatban.
    # TODO: Normals, streamlit pagen abrazolni esetleg, de adatbazisba nem kell menteni
    # TODO: Meteostat adatokat is frissiteni, arra is DAG pl. 
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