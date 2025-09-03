import pandas as pd
from datetime import datetime
from meteostat import Stations, Daily, Hourly, Monthly
from psycopg2.extras import execute_values

from src.connect_db import conn

def create_tables(cur):
    with open("postgresql/create_tables.sql", "r") as f:
        cur.execute(f.read())

def load_stations(cur):

    Stations.cache_dir = 'meteostat/cache'

    stations = Stations()

    stations = stations.region('RO','HA') # eloszor csak Hargita megye kiserleti alapon

    print('Stations in Romania:', stations.fetch())

    df_stations = stations.fetch()

    print(type(df_stations))

    #df_stations = pd.DataFrame(stations)

    

    # Convert date strings to datetime
    date_cols = ["hourly_start", "hourly_end", "daily_start", "daily_end", "monthly_start", "monthly_end"]
    for col in date_cols:
        df_stations[col] = pd.to_datetime(df_stations[col]).dt.date

    # Convert Pandas missing values (NaN, NA) to Python None
    #df_stations = df_stations.where(pd.notnull(df_stations), None)

    #df_stations = df_stations.applymap(lambda x: None if pd.isna(x) else x)

    # Replace all Pandas NA types with Python None
    df_stations.replace({pd.NA: None}, inplace=True)

    # Ha van numpy NaN is, azt is érdemes
    import numpy as np
    df_stations.replace({np.nan: None}, inplace=True)



    print(df_stations)


    # Convert DataFrame rows to list of tuples in the same column order as the table
    records = [
        (
            row['name'],
            row['country'],
            row['region'],
            row['wmo'],
            row['icao'],
            row['latitude'],
            row['longitude'],
            row['elevation'],
            row['timezone'],
            row['hourly_start'],
            row['hourly_end'],
            row['daily_start'],
            row['daily_end'],
            row['monthly_start'],
            row['monthly_end']
        )
        for _, row in df_stations.iterrows()
    ]

    insert_query = """
        INSERT INTO stations (
            name, country, region, wmo, icao, latitude, longitude, elevation,
            timezone, hourly_start, hourly_end, daily_start, daily_end,
            monthly_start, monthly_end
        ) VALUES %s
        ON CONFLICT DO NOTHING;  -- prevents crash if duplicates exist
    """

    
    execute_values(cur, insert_query, records)



def load_stations_proba():

    Stations.cache_dir = 'meteostat/cache'

    stations = Stations()

    stations = stations.region('RO','HA') # eloszor csak Hargita megye kiserleti alapon

    print('Stations in Romania:', stations.fetch())

    print(type(stations))

    station_id = '15107'

    start_year = 1973
    end_year = 2025

    for year in range(start_year, end_year + 1):
        start = datetime(year, 1, 1)
        end = datetime(year, 12, 31)
        
        data = Daily(station_id, start=start, end=end)
        coverage = data.coverage()  # visszaadja, hogy mennyire teljes az adat
        count = data.count()        # hány adatpont van

        print(f"Year: {year}, Coverage: {coverage}, Count: {count}")


def main():

    cur = conn.cursor()

    create_tables(cur)
    
    load_stations(cur)

    load_stations_proba()

    cur.close()
    conn.close()



if __name__ == "__main__":
    main()