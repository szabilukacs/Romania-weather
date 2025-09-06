
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import io

def get_start_date(row, cols=("hourly_start", "daily_start", "monthly_start")):

    hourly_start = pd.to_datetime(row["hourly_start"], errors="coerce").to_pydatetime()
    daily_start = pd.to_datetime(row["daily_start"], errors="coerce").to_pydatetime()
    monthly_start = pd.to_datetime(row["monthly_start"], errors="coerce").to_pydatetime()

    return min(hourly_start,daily_start,monthly_start)

def rename_index_to_time(df, new_name="time"):
    return df.reset_index().rename(columns={"index": new_name})

def prepare_to_records(df: pd.DataFrame, station_id: int, cols: list):
    # Add station_id column
    df["station_id"] = station_id

    # Keep only these columns and convert NaN -> None for SQL
    df = df[cols].where(pd.notna(df[cols]), None)

    # Convert DataFrame rows to list of tuples for execute_values
    records = [
        tuple(getattr(row, col) for col in cols)
        for row in df.itertuples(index=False)
    ]

    return records, df

def copy_to_db(df_hourly: pd.DataFrame, conn: psycopg2.extensions.connection, station_id: int, cols: list):
    
    records, df_hourly = prepare_to_records(df_hourly, station_id, cols)

    # Write DataFrame to in-memory CSV buffer
    buffer = io.StringIO()
    df_hourly.to_csv(buffer, index=False, header=False)
    buffer.seek(0)

    # Use COPY for fast insertion
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

def insert_into_db(df: pd.DataFrame, conn: psycopg2.extensions.connection, station_id: int, insert_sql: str, cols: list): 

    records, df = prepare_to_records(df,station_id, cols)

    with conn.cursor() as cur:
            execute_values(cur, insert_sql, records)

    conn.commit()

def calc_days_of_year(year: int):
    # --- Data coverage ---
    today = pd.Timestamp.today()
     # napok számítása
    if year == today.year:
        # folyamatban lévő év → eddig eltelt napok
        days_in_year = today.day_of_year
    else:
        # lezárt év → 365 vagy 366 nap
        days_in_year = 366 if pd.Timestamp(year=year, month=12, day=31).is_leap_year else 365
    return days_in_year