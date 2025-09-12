import sys
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import io

from src.utils.connect_db import connect_to_db

sys.path.append("../../")


def get_start_date(row, cols=("hourly_start", "daily_start")):
    """
    Return the earliest start date from hourly and daily columns.
    """
    hourly_start = pd.to_datetime(row["hourly_start"], errors="coerce").to_pydatetime()
    daily_start = pd.to_datetime(row["daily_start"], errors="coerce").to_pydatetime()

    return min(hourly_start, daily_start)


def rename_index_to_time(df, new_name="time"):
    """
    Reset DataFrame index and rename it to 'time' (or specified name).
    """
    return df.reset_index().rename(columns={"index": new_name})


def prepare_to_records(df: pd.DataFrame, station_id: int, cols: list):
    """
    Prepare DataFrame for database insertion:
      - Add station_id
      - Keep specified columns and convert NaN to None
      - Convert rows to list of tuples for execute_values
    """
    # Add station_id column
    df["station_id"] = station_id

    # Keep only these columns and convert NaN -> None for SQL
    df = df[cols].where(pd.notna(df[cols]), None)
    df = df[cols].astype(object)  # force object dtype so None marad

    # Convert DataFrame rows to list of tuples, NaN -> None
    records = [
        tuple(getattr(row, col) if pd.notna(getattr(row, col)) else None for col in cols)
        for row in df.itertuples(index=False)
    ]

    return records, df


def copy_to_db(
    df_hourly: pd.DataFrame,
    conn: psycopg2.extensions.connection,
    station_id: int,
    cols: list,
):
    """
    Insert hourly data into the database using COPY for fast performance.
    """
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
            file=buffer,
        )
    conn.commit()


def insert_into_db(
    df: pd.DataFrame,
    conn: psycopg2.extensions.connection,
    station_id: int,
    insert_sql: str,
    cols: list,
):
    """
    Insert data into the database using execute_values.
    """
    records, df = prepare_to_records(df, station_id, cols)

    with conn.cursor() as cur:
        execute_values(cur, insert_sql, records)

    conn.commit()


def calc_days_of_year(year: int):
    """
    Calculate the number of days in a given year.
    For the current year, return days elapsed so far.
    """
    today = pd.Timestamp.today()
    # Days calculation
    if year == today.year:
        # Ongoing year → days elapsed
        days_in_year = today.day_of_year
    else:
        # Completed year → 365 or 366
        days_in_year = 366 if pd.Timestamp(year=year, month=12, day=31).is_leap_year else 365
    return days_in_year


def load_data_into_df(query):
    """
    Execute SQL query and return the result as a pandas DataFrame.
    """
    conn = connect_to_db()
    df = pd.read_sql(query, conn)
    conn.close()
    return df
