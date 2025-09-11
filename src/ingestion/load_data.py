import pandas as pd
from datetime import datetime
from meteostat import Stations, Daily, Hourly, Monthly
from psycopg2.extras import execute_values

from src.utils.utils import get_start_date, copy_to_db, insert_into_db
from src.utils.queries import INSERT_STATIONS,SELEC_STATION_START_VALUES, INSERT_WEATHER_DAILY, INSERT_WEATHER_MONTHLY
from src.celan_and_validate.clean_and_validate import clean_and_validate_hours, clean_and_validate_days
from src.utils.constants import REGIONS

COLS_HOURLY = ["station_id","time", "temp", "dwpt", "rhum", "prcp", "snow",
        "wdir", "wspd", "wpgt", "pres", "tsun", "coco"]
COLS_DAILY = ["station_id","time", "tavg", "tmin", "tmax", "prcp", "snow",
               "wdir", "wspd", "wpgt", "pres", "tsun"]

def create_tables(conn):
    cur = conn.cursor()
    with open("postgresql/create_tables.sql", "r") as f:
        cur.execute(f.read())
    cur.close()


def is_valid_wmo(wmo) -> bool:
    """
    Return True if `wmo` is a valid numeric WMO identifier that can be used as int.
    This filters out None, pd.NA, NaN, the literal "<NA>" string, empty strings,
    and any non-numeric values (except float-like integers like "123.0").
    """
    # explicit None / pandas NA / numpy.nan check
    if wmo is None:
        return False
    if pd.isna(wmo):  # covers np.nan, pd.NA, None-like
        return False

    s = str(wmo).strip()
    if s == "":
        return False

    # Common textual null representations
    if s.upper() in {"<NA>", "NA", "N/A", "NONE", "NAN"}:
        return False

    # If string is all digits -> ok
    if s.isdigit():
        return True

    # If it's a float string like "123.0", allow it (but not "123.4")
    try:
        f = float(s)
        if f.is_integer():
            return True
        return False
    except Exception:
        return False


def load_stations(conn):

    cur = conn.cursor()

    Stations.cache_dir = 'meteostat/cache'

    stations = Stations()

    stations = stations.region('RO') # eloszor csak Hargita megye kiserleti alapon

    print('Stations in Romania:', stations.count())

    # Example list of region codes

    # If a list of specific regions is provided, filter them
    if REGIONS:
        dfs = []
        for region_code in REGIONS:
            region_stations = stations.region('RO',region_code).fetch()
            print(region_stations)
            dfs.append(region_stations)
        filtered_stations = pd.concat(dfs, ignore_index=True)
    else:
        # Fetch all stations
        filtered_stations = stations.fetch()

    print("Filtered stations:", len(filtered_stations))

    df_stations = filtered_stations

    # Convert date strings to datetime
    date_cols = ["hourly_start", "hourly_end", "daily_start", "daily_end", "monthly_start", "monthly_end"]
    
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
            print(wmo_value)
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
            row.monthly_start,
            row.monthly_end
        ))

    # Only insert when we have records
    if records:
        execute_values(cur, INSERT_STATIONS, records)
    else:
        print("No valid station records to insert.")


    conn.commit()
    cur.close()

def load_weather_data(conn):

    cur = conn.cursor()
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

        # Clean data
        df_hourly = clean_and_validate_hours(df_hourly)
        df_daily = clean_and_validate_days(df_daily)
        df_monthly = clean_and_validate_days(df_monthly)

        # Insert hourly datas
        copy_to_db(df_hourly, conn, station_id, COLS_HOURLY)

        # Insert Daily datas
        insert_into_db(df_daily, conn, station_id, INSERT_WEATHER_DAILY, COLS_DAILY)

        # Insert Monthly datas
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

    cur.close()