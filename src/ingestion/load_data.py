import pandas as pd
from datetime import datetime
from meteostat import Stations, Daily, Hourly, Monthly
from psycopg2.extras import execute_values

from src.utils.utils import get_start_date,rename_index_to_time, clean_hourly_data, copy_to_db, insert_into_db
from src.queries import INSERT_STATIONS,SELEC_STATION_START_VALUES, INSERT_WEATHER_DAILY, INSERT_WEATHER_MONTHLY
from src.connect_db import conn

COLS_HOURLY = ["station_id","time", "temp", "dwpt", "rhum", "prcp", "snow",
        "wdir", "wspd", "wpgt", "pres", "tsun", "coco"]
COLS_DAILY = ["station_id","time", "tavg", "tmin", "tmax", "prcp", "snow",
               "wdir", "wspd", "wpgt", "pres", "tsun"]

def create_tables(cur):
    with open("postgresql/create_tables.sql", "r") as f:
        cur.execute(f.read())

def load_stations(cur):

    Stations.cache_dir = 'meteostat/cache'

    stations = Stations()

    stations = stations.region('RO') # eloszor csak Hargita megye kiserleti alapon

    print('Stations in Romania:', stations.count())

    df_stations = stations.fetch(1)

    # Convert date strings to datetime
    date_cols = ["hourly_start", "hourly_end", "daily_start", "daily_end", "monthly_start", "monthly_end"]
    
    for col in date_cols:
        df_stations[col] = pd.to_datetime(df_stations[col]).dt.date

    # Replace all Pandas NA types with Python None
    df_stations.replace({pd.NA: None}, inplace=True)

    # Convert DataFrame rows to list of tuples in the same column order as the table
    records = [
        (
            row.name,
            row.country,
            row.region,
            row.wmo,
            row.icao,
            row.latitude,
            row.longitude,
            row.elevation,
            row.timezone,
            row.hourly_start,
            row.hourly_end,
            row.daily_start,
            row.daily_end,
            row.monthly_start,
            row.monthly_end
        )
        for row in df_stations.itertuples(index=False)
    ]
    
    execute_values(cur, INSERT_STATIONS, records)

    conn.commit()

def load_weather_data(cur):

    # Select data start dates from database
    df_station_data = pd.read_sql_query(SELEC_STATION_START_VALUES, conn)

    end_date = datetime.today()

    for index, row in df_station_data.iterrows():
        
        station_id = int(row["wmo"])

        start_date = get_start_date(row=row)
        
        # Get the hourly, daily, monthly datas then fetch the data
        df_hourly = Hourly(station_id, start=start_date, end=end_date).fetch()
        df_daily = Daily(station_id, start=start_date, end=end_date).fetch()
        df_monthly = Monthly(station_id, start=start_date, end=end_date).fetch()

        # Rename the index timestamp to time
        df_hourly = rename_index_to_time(df_hourly)
        df_daily = rename_index_to_time(df_daily)
        df_monthly = rename_index_to_time(df_monthly)

        df_hourly["time"] = pd.to_datetime(df_hourly["time"], format="%Y-%m-%d %H:%M:%S", errors="coerce")
        df_hourly = clean_hourly_data(df_hourly)
        df_daily["time"] = pd.to_datetime(df_daily["time"]).dt.date # TODO: kesobb tisztiani ezeket is
        df_monthly["time"] = pd.to_datetime(df_monthly["time"]).dt.date

        # Replace all Pandas NA types with Python None Clean-be berakni ezeket is
        df_hourly.replace({pd.NA: None}, inplace=True)
        df_daily.replace({pd.NA: None}, inplace=True)
        df_monthly.replace({pd.NA: None}, inplace=True)

        copy_to_db(df_hourly, conn, station_id, COLS_HOURLY)

        # Same with Daily
        insert_into_db(df_daily, conn, station_id, INSERT_WEATHER_DAILY, COLS_DAILY)

        # Same with Monthly
        records = [
            (
                station_id,
                row['time'],
                row['tavg'],
                row['tmin'],
                row['tmax'],
                row['prcp'],
                row['wspd'],
                row['pres'],
                row['tsun']
            )
            for _, row in df_monthly.iterrows() # TODO: change it to itertuples, it is working only with iterrows
        ]

        with conn.cursor() as cur:
            execute_values(cur, INSERT_WEATHER_MONTHLY, records)

        conn.commit()