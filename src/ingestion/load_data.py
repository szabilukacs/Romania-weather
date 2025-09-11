import pandas as pd
from datetime import datetime
from meteostat import Stations, Daily, Hourly
from psycopg2.extras import execute_values

from src.utils.utils import get_start_date, copy_to_db, insert_into_db
from src.utils.queries import INSERT_STATIONS,SELEC_STATION_START_VALUES, INSERT_WEATHER_DAILY
from src.celan_and_validate.clean_and_validate import clean_and_validate_hours, clean_and_validate_days, is_valid_wmo
from src.utils.constants import REGIONS, COLS_HOURLY, COLS_DAILY

def create_tables(conn):
    """
    Create all database tables using the SQL file located at 
    `postgresql/create_tables.sql`.

    Args:
        conn: Open PostgreSQL database connection object.
    """
    cur = conn.cursor()
    with open("postgresql/create_tables.sql", "r") as f:
        cur.execute(f.read())
    cur.close()

def load_stations(conn):
    """
    Load Romanian weather stations from the Meteostat API, filter invalid ones,
    and insert valid stations into the database.

    Steps:
        - Fetch all Romanian stations (filtered by REGIONS if specified).
        - Convert date columns to datetime format.
        - Drop stations with invalid WMO codes.
        - Insert valid station records into the database.

    Args:
        conn: Open PostgreSQL database connection object.
    """
    cur = conn.cursor()

    Stations.cache_dir = 'meteostat/cache'

    stations = Stations()

    stations = stations.region('RO')

    print('Stations in Romania:', stations.count())

    # Fetch once and filter locally if REGIONS are provided
    df_stations = stations.fetch()
    if REGIONS:
        df_stations = df_stations[df_stations["region"].isin(REGIONS)]
    else:
        print("Invalid data!")
        return

    print("Filtered stations:", len(df_stations))

    print(df_stations)

    # Convert date strings to datetime
    date_cols = ["hourly_start", "hourly_end", "daily_start", "daily_end"]
    
    for col in date_cols:
        df_stations[col] = pd.to_datetime(df_stations[col]).dt.date

    # Replace all Pandas NA types with Python None
    df_stations.replace({pd.NA: None}, inplace=True)

    # --- Filter DataFrame first ---
    valid_mask = df_stations['wmo'].apply(is_valid_wmo)
    n_total = len(df_stations)
    n_kept = int(valid_mask.sum())
    n_dropped = n_total - n_kept

    print(f"Stations total: {n_total}, kept (valid wmo): {n_kept}, dropped: {n_dropped}")

    if n_dropped:
        # show a few example offending values for debugging
        bad_examples = df_stations.loc[~valid_mask, 'wmo'].astype(str).unique()[:20]
        print("Examples of dropped wmo values:", bad_examples)

    # Convert DataFrame rows to list of tuples in the same column order as the table
    records = []
    for i, row in enumerate(df_stations.loc[valid_mask].itertuples(index=False), start=1):
        # row.wmo is now safe to convert
        try:
            # convert robustly (handles "123", 123.0, "123.0", etc.)
            wmo_value = int(float(str(row.wmo).strip()))
        except Exception:
            # should not happen due to prior filter, but be defensive
            print(f"Skipping row due to wmo conversion error: {row}")
            continue

        records.append((
            row.name,
            row.country,
            row.region,
            wmo_value,
            row.icao,
            row.latitude,
            row.longitude,
            row.elevation,
            row.timezone,
            row.hourly_start,
            row.hourly_end,
            row.daily_start,
            row.daily_end,
        ))

    # Only insert when we have records
    if records:
        execute_values(cur, INSERT_STATIONS, records)
    else:
        print("No valid station records to insert.")

    conn.commit()
    cur.close()

def load_weather_data(conn):
    """
    Fetch and store weather data (hourly and daily) from Meteostat API
    for all stations in the database.

    Steps:
        - Retrieve start dates for each station from the database.
        - Fetch hourly and daily data from Meteostat API.
        - Clean and validate the data.
        - Insert hourly data using COPY for efficiency.
        - Insert daily data using parameterized INSERT.

    Args:
        conn: Open PostgreSQL database connection object.
    """
    cur = conn.cursor()
    # Select data start dates from database
    df_station_data = pd.read_sql_query(SELEC_STATION_START_VALUES, conn)

    end_date = datetime.today()

    for index, row in df_station_data.iterrows():
        
        station_id = int(row["wmo"])

        start_date = get_start_date(row=row)
        
        # Get the hourly, daily datas then fetch the data
        df_hourly = Hourly(station_id, start=start_date, end=end_date).fetch()
        df_daily = Daily(station_id, start=start_date, end=end_date).fetch()

        # Clean data
        df_hourly = clean_and_validate_hours(df_hourly)
        df_daily = clean_and_validate_days(df_daily)

        # Insert hourly datas
        copy_to_db(df_hourly, conn, station_id, COLS_HOURLY)

        # Insert Daily datas
        insert_into_db(df_daily, conn, station_id, INSERT_WEATHER_DAILY, COLS_DAILY)

    cur.close()