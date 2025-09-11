"""
Data Cleaning and Validation for Weather Data

This module provides functions to clean and validate hourly, daily, and monthly weather data.
It ensures that datetime values are properly parsed, removes rows with all missing or zero values,
and validates temperature columns against defined realistic bounds.
"""

import pandas as pd
from src.utils.utils import rename_index_to_time

# --- Constants: temperature limits in Celsius ---
MIN_TEMP = -60
MAX_TEMP = 90

def clean_and_validate_hours(df_hourly: pd.DataFrame, temp_col: str = "temp") -> pd.DataFrame:
    """
    Clean and validate hourly weather data.

    Steps:
    - Convert index to 'time' column if necessary.
    - Ensure 'time' column is datetime, replace invalid values with None.
    - Remove rows where all non-time columns are NaN or 0.
    - Replace pandas NA values with Python None.
    - Filter rows where temperature is within realistic bounds.

    """
    df_hourly = rename_index_to_time(df_hourly)
    df_hourly["time"] = pd.to_datetime(df_hourly["time"], format="%Y-%m-%d %H:%M:%S", errors="coerce")
    df_hourly["time"] = df_hourly["time"].where(df_hourly["time"].notna(), None)

    # Identify non-time columns
    cols_to_check = df_hourly.columns.difference(["time"])

    # Create mask: True if value is NaN or 0
    mask = (df_hourly[cols_to_check].isna()) | (df_hourly[cols_to_check] == 0)

    # Keep rows where not all values are NaN or 0
    df_hourly = df_hourly[~mask.all(axis=1)]

    # Replace pandas NA with Python None
    df_hourly.replace({pd.NA: None}, inplace=True)

    # Filter temperature column if exists
    if temp_col in df_hourly.columns:
        df_hourly = df_hourly[(df_hourly[temp_col] >= MIN_TEMP) & (df_hourly[temp_col] <= MAX_TEMP)]

    return df_hourly

def clean_and_validate_days(df: pd.DataFrame, temp_col: str = "tavg") -> pd.DataFrame:
    """
    Clean and validate daily weather data.

    Steps:
    - Convert index to 'time' column if necessary.
    - Ensure 'time' column is a date object, replace NaN/NaT with None.
    - Remove rows where all non-time columns are NaN or 0.
    - Replace pandas NA values with Python None.
    - Filter rows where temperature is within realistic bounds.
    """
    df = rename_index_to_time(df)
    # Ensure 'time' column is date
    df["time"] = pd.to_datetime(df["time"]).dt.date

    # Replace all NaN/NaT with Python None
    df = df.where(pd.notna(df), None) 
    df = df.astype(object)              

    # Identify non-time columns
    cols_to_check = df.columns.difference(["time"])

    # Create mask: True if value is NaN or 0
    mask = (df[cols_to_check].isna()) | (df[cols_to_check] == 0)

    # Keep rows where not all values are NaN or 0
    df = df[~mask.all(axis=1)]

    # Replace pandas NA with Python None
    df.replace({pd.NA: None}, inplace=True)

    if temp_col in df.columns:
        df = df[(df[temp_col] >= MIN_TEMP) & (df[temp_col] <= MAX_TEMP)]

    return df



