import pandas as pd
from datetime import datetime
from meteostat import Stations, Daily, Hourly, Monthly
from psycopg2.extras import execute_values
import time
import io

from src.queries import INSERT_STATIONS,SELEC_STATION_START_VALUES, INSERT_WEATHER_HOURLY, INSERT_WEATHER_DAILY, INSERT_WEATHER_MONTHLY
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

    conn.commit()


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
        df_monthly = data_monthly.fetch()

        print(df_hourly)
        print(df_hourly.columns)

        df_hourly = df_hourly.reset_index().rename(columns={"index": "time"})
        df_daily = df_daily.reset_index().rename(columns={"index": "time"})
        df_monthly = df_monthly.reset_index().rename(columns={"index": "time"})

        #TODO itt rendet rakni

        df_hourly["time"] = pd.to_datetime(df_hourly["time"], format="%Y-%m-%d %H:%M:%S", errors="coerce")

        # A NaT értékek cseréje None-ra
        df_hourly["time"] = df_hourly["time"].where(df_hourly["time"].notna(), None)
        

        # Feltételezzük, hogy df_hourly["time"] már datetime és nincs NaT
        cols_to_check = df_hourly.columns.difference(["time"])  # minden oszlop, kivéve 'time'

        # Igaz/hamis mátrix: True ha NaN vagy 0
        mask = (df_hourly[cols_to_check].isna()) | (df_hourly[cols_to_check] == 0)

        # Olyan sor kell, ahol NEM mind igaz (tehát van legalább egy nem-null és nem-0 érték)
        df_hourly = df_hourly[~mask.all(axis=1)]

        print(df_hourly.columns)


        # Ellenőrzés
        print(df_hourly["time"].isna().sum())  # 0-nak kell lennie

        df_daily["time"] = pd.to_datetime(df_daily["time"]).dt.date

        df_monthly["time"] = pd.to_datetime(df_monthly["time"]).dt.date

        print("ITT")

        # Replace all Pandas NA types with Python None
        df_hourly.replace({pd.NA: None}, inplace=True)
        df_daily.replace({pd.NA: None}, inplace=True)
        df_monthly.replace({pd.NA: None}, inplace=True)

        print("ITT2")

       # Convert DataFrame rows to list of tuples in the correct order
        records = [
            (
                station_id,
                row.time,
                row.temp,
                row.dwpt,
                row.rhum,
                row.prcp,
                row.snow,
                row.wdir,
                row.wspd,
                row.wpgt,
                row.pres,
                row.tsun,
                row.coco
            )
            for row in df_hourly.itertuples(index=False)
        ]
        batch_size = 100000

        print("ITT3")

      #  for i in range(0, len(records), batch_size):
       #     batch = records[i:i+batch_size]
        #    execute_values(cur, INSERT_WEATHER_HOURLY, batch)
         #   conn.commit()   # commit after each batch

        #cols = [
       #     "station_id", "time", "temp", "dwpt", "rhum", "prcp", "snow",
       #     "wdir", "wspd", "wpgt", "pres", "tsun", "coco"
      #  ]
       # df_hourly = df_hourly[cols].where(pd.notna(df_hourly[cols]), None)

        df_hourly["station_id"] = station_id

        cols = [
            "station_id", "time", "temp", "dwpt", "rhum", "prcp", "snow",
            "wdir", "wspd", "wpgt", "pres", "tsun", "coco"
        ]
        df_hourly = df_hourly[cols].where(pd.notna(df_hourly[cols]), None)

        
        buffer = io.StringIO()
        df_hourly.to_csv(buffer, index=False, header=False)  
        buffer.seek(0)

        with conn.cursor() as cur:
            cur.copy_expert(
                sql=f"""
                    COPY weather_data_hourly (
                        {", ".join(cols)}
                    )
                    FROM STDIN WITH (FORMAT CSV, NULL '');
                """,
                file=buffer
            )
        conn.commit()


        print("commit utan")

        # Convert DataFrame rows to list of tuples in the correct order
        records = [
            (
                station_id,
                row.time,
                row.tavg,
                row.tmin,
                row.tmax,
                row.prcp,
                row.snow,
                row.wdir,
                row.wspd,
                row.wpgt,
                row.pres,
                row.tsun
            )
            for row in df_daily.itertuples(index=False)
        ]

        with conn.cursor() as cur:
            execute_values(cur, INSERT_WEATHER_DAILY, records)

        conn.commit()

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
            for _, row in df_monthly.iterrows() # ez nem megy itertuples-el
        ]

        with conn.cursor() as cur:
            execute_values(cur, INSERT_WEATHER_MONTHLY, records)

        conn.commit()

        print(f"{data_hourly.count()} Elements inserted! ")
        print(f"Data coverage: {data_hourly.coverage():.2f} %")


def main():

    start = time.time()

    cur = conn.cursor()

    create_tables(cur)
    
    load_stations(cur)

    proba(cur)

    cur.close()
    conn.close()

    end = time.time()

    print(f"Elapsed time {end - start}")



if __name__ == "__main__":
    main()