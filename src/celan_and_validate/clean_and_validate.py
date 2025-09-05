import pandas as pd
from src.utils.utils import rename_index_to_time

# In celsius
MIN_TEMP = -60
MAX_TEMP = 90

def clean_and_validate_hours(df_hourly: pd.DataFrame, temp_col = "temp"):

    df_hourly = rename_index_to_time(df_hourly)

    df_hourly["time"] = pd.to_datetime(df_hourly["time"], format="%Y-%m-%d %H:%M:%S", errors="coerce")

    # A NaT értékek cseréje None-ra
    df_hourly["time"] = df_hourly["time"].where(df_hourly["time"].notna(), None)

    # Feltételezzük, hogy df_hourly["time"] már datetime és nincs NaT
    cols_to_check = df_hourly.columns.difference(["time"])  # minden oszlop, kivéve 'time'

    # Igaz/hamis mátrix: True ha NaN vagy 0
    mask = (df_hourly[cols_to_check].isna()) | (df_hourly[cols_to_check] == 0)

    # Olyan sor kell, ahol NEM mind igaz (tehát van legalább egy nem-null és nem-0 érték)
    df_hourly = df_hourly[~mask.all(axis=1)]

    df_hourly.replace({pd.NA: None}, inplace=True)

    if temp_col in df_hourly.columns:
        df_hourly = df_hourly[(df_hourly[temp_col] >= MIN_TEMP) & (df_hourly[temp_col] <= MAX_TEMP)]

    return df_hourly

def clean_and_validate_day_month(df: pd.DataFrame, temp_col = "tavg"):

    df = rename_index_to_time(df)

    df["time"] = pd.to_datetime(df["time"]).dt.date

    # A NaT értékek cseréje None-ra
    df = df.where(pd.notna(df), None)   # minden NaN / NaT → None
    df = df.astype(object)              # biztosítja, hogy Python alap típusok legyenek

    # Feltételezzük, hogy df_hourly["time"] már datetime és nincs NaT
    cols_to_check = df.columns.difference(["time"])  # minden oszlop, kivéve 'time'

    # Igaz/hamis mátrix: True ha NaN vagy 0
    mask = (df[cols_to_check].isna()) | (df[cols_to_check] == 0)

    # Olyan sor kell, ahol NEM mind igaz (tehát van legalább egy nem-null és nem-0 érték)
    df = df[~mask.all(axis=1)]

    df.replace({pd.NA: None}, inplace=True)

    if temp_col in df.columns:
        df = df[(df[temp_col] >= MIN_TEMP) & (df[temp_col] <= MAX_TEMP)]

    return df



