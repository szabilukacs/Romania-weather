import pandas as pd
from datetime import datetime
from meteostat import Stations, Daily, Hourly, Monthly
from psycopg2.extras import execute_values

from src.queries import INSERT_STATIONS,SELEC_STATION_START_VALUES, INSERT_WEATHER_HOURLY, INSERT_WEATHER_DAILY
from src.connect_db import conn

def create_tables(cur):
    with open("postgresql/create_tables.sql", "r") as f:
        cur.execute(f.read())

def load_stations(cur):

    Stations.cache_dir = 'meteostat/cache'

    stations = Stations()

    stations = stations.region('RO','HA') # eloszor csak Hargita megye kiserleti alapon

    print('Stations in Romania:', stations.fetch(2))

    df_stations = stations.fetch(2)

    # Convert date strings to datetime
    date_cols = ["hourly_start", "hourly_end", "daily_start", "daily_end", "monthly_start", "monthly_end"]
    
    for col in date_cols:
        df_stations[col] = pd.to_datetime(df_stations[col]).dt.date

    # Replace all Pandas NA types with Python None
    df_stations.replace({pd.NA: None}, inplace=True)

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
    
    execute_values(cur, INSERT_STATIONS, records)


def proba(cur):

    Stations.cache_dir = 'meteostat/cache'

    stations = Stations()

    stations = stations.region('RO','HA') # eloszor csak Hargita megye kiserleti alapon

    print(type(stations))

    # Select data start dates
    df_station_data = pd.read_sql_query(SELEC_STATION_START_VALUES, conn)

    print(df_station_data)

    for index, row in df_station_data.iterrows():
        station_id = int(row["wmo"])
        hourly_start = datetime.strptime(str(row["hourly_start"]),'%Y-%m-%d')
        daily_start = datetime.strptime(str(row["daily_start"]),'%Y-%m-%d')
        monthly_start = datetime.strptime(str(row["monthly_start"]),'%Y-%m-%d')

        start_date = min(hourly_start,daily_start,monthly_start)
        end_date = datetime(2025,9,1) # to do mai datumra 
        print(daily_start)
        print(station_id)
        print(start_date)
        
        data_hourly = Hourly(station_id, start=start_date, end=end_date)
        data_daily = Daily(station_id, start=start_date, end=end_date)
        data_monthly = Monthly(station_id, start=start_date, end=end_date)

        df_hourly = data_hourly.fetch()
        df_daily = data_daily.fetch()

        # print(df_hourly)
        print(df_hourly.columns)

        df_hourly = df_hourly.reset_index().rename(columns={"index": "time"})
        df_daily = df_daily.reset_index().rename(columns={"index": "time"})

        #TODO itt rendet rakni

        df_hourly["time"] = pd.to_datetime(df_hourly["time"])
        print(df_hourly)
        # Csak a time oszlop alapján nézzük a duplikátumokat, megtartjuk az első előfordulást
        df_hourly = df_hourly.drop_duplicates(subset=["time"], keep="first")


        # Convert to datetime, invalid parsing -> NaT
        df_hourly["time"] = pd.to_datetime(df_hourly["time"], errors="coerce")

        # Drop rows where time is NaT
        df_hourly = df_hourly.dropna(subset=["time"])

        # Feltételezzük, hogy df_hourly["time"] már datetime és nincs NaT
        cols_to_check = df_hourly.columns.difference(["time"])  # minden oszlop, kivéve 'time'

        # Drop rows where all columns_to_check are NULL (NaN) or 0
        df_hourly = df_hourly[~df_hourly[cols_to_check].apply(lambda row: all((pd.isna(x) or x == 0) for x in row), axis=1)]

        # Ellenőrzés
        print(df_hourly)


        # Ellenőrzés
        print(df_hourly["time"].isna().sum())  # 0-nak kell lennie

        print(df_hourly.iloc[50:56])



        df_daily["time"] = pd.to_datetime(df_daily["time"]).dt.date

        # Replace all Pandas NA types with Python None
        df_hourly.replace({pd.NA: None}, inplace=True)
        df_daily.replace({pd.NA: None}, inplace=True)

       # Convert DataFrame rows to list of tuples in the correct order
        records = [
            (
                station_id,
                row['time'],
                row['temp'],
                row['dwpt'],
                row['rhum'],
                row['prcp'],
                row['snow'],
                row['wdir'],
                row['wspd'],
                row['wpgt'],
                row['pres'],
                row['tsun'],
                row['coco']
            )
            for _, row in df_hourly.iterrows()
        ]

        execute_values(cur, INSERT_WEATHER_HOURLY, records)

              # Convert DataFrame rows to list of tuples in the correct order
        records = [
            (
                station_id,
                row['time'],
                row['tavg'],
                row['tmin'],
                row['tmax'],
                row['prcp'],
                row['snow'],
                row['wdir'],
                row['wspd'],
                row['wpgt'],
                row['pres'],
                row['tsun']
            )
            for _, row in df_daily.iterrows()
        ]

        execute_values(cur, INSERT_WEATHER_DAILY, records)

        coverage = data_hourly.coverage()  # visszaadja, hogy mennyire teljes az adat
        count = data_hourly.count()        # hány adatpont van

        print(f"Coverage: {coverage}, Count: {count}")


def main():

    cur = conn.cursor()

    create_tables(cur)
    
    load_stations(cur)

    proba(cur)

    cur.close()
    conn.close()



if __name__ == "__main__":
    main()