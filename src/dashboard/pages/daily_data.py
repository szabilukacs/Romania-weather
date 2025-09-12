"""
Daily Weather Data Dashboard with Streamlit

This app visualizes hourly weather data for a selected station and day.
It includes:
- Key statistics (sunshine duration, snowfall)
- Temperature and precipitation charts
- Weather condition timeline
"""

import streamlit as st
import pandas as pd
import altair as alt
from meteostat import Hourly
from datetime import datetime

from src.utils.utils import load_data_into_df
from src.utils.queries import SELECT_STATION_DATA
from src.utils.constants import COCO_CODES, DAILY_DAYS_SHIFT


def show_temperature():
    """Display daily temperature as a line chart."""
    temp_chart = (
        alt.Chart(df)
        .mark_line(point=True, color="red")
        .encode(
            x=alt.X("time:T", title="Idő"),
            y=alt.Y("temp:Q", title="Átlaghőmérséklet (°C)"),
            tooltip=["time", "temp"],
        )
        .properties(
            title="🌡 Napi hőmérséklet alakulása",
            width=700,
            height=300,
            padding={"top": 30, "bottom": 10, "left": 10, "right": 10},
        )
    )
    st.altair_chart(temp_chart, use_container_width=True)


def show_prcp():
    """Display daily precipitation as a bar chart."""
    prcp_chart = (
        alt.Chart(df)
        .mark_bar(color="blue", opacity=0.7)
        .encode(
            x=alt.X("time:T", title="Idő"),
            y=alt.Y("prcp:Q", title="Csapadék (mm)"),
            tooltip=["time", "prcp"],
        )
        .properties(
            title="🌧 Napi csapadék",
            width=700,
            height=200,
            padding={"top": 30, "bottom": 10, "left": 10, "right": 10},
        )
    )

    st.altair_chart(prcp_chart, use_container_width=True)


def show_statistics():
    """Display summary statistics: sunshine duration and snowfall."""
    total_sun_minutes = df["tsun"].sum()
    hours = total_sun_minutes // 60
    minutes = total_sun_minutes % 60

    total_snow = df["snow"].sum()  # mm

    col1, col2 = st.columns(2)

    col1.metric(label="🌞 Összes napsütés aznap", value=f"{hours}h {minutes}m")

    col2.metric(label="❄️ Hullott hó mennyiség", value=f"{total_snow:.1f} mm")


def show_coco():
    """Display timeline of weather condition codes (coco)."""
    df_coco = df[["time", "coco"]].dropna().reset_index(drop=True)

    # Convert coco codes to integers
    df_coco["coco"] = df_coco["coco"].astype(float).round().astype(int)

    # Map codes to human-readable condition labels
    df_coco["condition"] = df_coco["coco"].map(COCO_CODES)

    # Define condition duration
    df_coco["end_time"] = df_coco["time"].shift(-1)
    df_coco = df_coco.dropna(subset=["end_time"])

    # Build Altair timeline chart
    timeline_chart = (
        alt.Chart(df_coco)
        .mark_bar()
        .encode(
            x=alt.X("time:T", title="Time"),
            x2="end_time:T",
            y=alt.Y("condition:N", title="Weather Condition"),
            color=alt.Color(
                "condition:N",
                legend=alt.Legend(title="Condition"),
            ),
            tooltip=["time:T", "end_time:T", "condition"],
        )
        .properties(
            title="🌦 Weather Condition Timeline",
            width=700,
            height=200,
            padding={"top": 30, "bottom": 10, "left": 10, "right": 10},
        )
    )
    st.altair_chart(timeline_chart, use_container_width=True)


st.title("📅 Daily Weather Data")

stations = load_data_into_df(SELECT_STATION_DATA)
# Load station list
stations = load_data_into_df(SELECT_STATION_DATA)
station_name = st.selectbox("Choose a station:", stations["name"])
station_id = stations.loc[stations["name"] == station_name, "wmo"].values[0]
hourly_start = stations.loc[stations["name"] == station_name, "hourly_start"].values[0]
elevation = stations.loc[stations["name"] == station_name, "elevation"].values[0]

# Select date
today = pd.to_datetime("today").date()
selected_date = st.date_input(
    "Válassz egy napot:",
    today - pd.Timedelta(days=DAILY_DAYS_SHIFT),
    min_value=hourly_start,
)

data = Hourly(
    station_id,
    start=datetime(selected_date.year, 1, 1),
    end=datetime(selected_date.year, 12, 31),
)

# Select datas from database
query = f"""
SELECT time, temp, dwpt, rhum, prcp, snow, wdir, wspd, wpgt, pres, tsun, coco
FROM weather_data_hourly
WHERE station_id = {station_id}
AND DATE(time) = '{selected_date}'
ORDER BY time ASC;
"""

df = load_data_into_df(query)

if df.empty:
    st.warning("❌ Nincs adat a kiválasztott napra.")
else:
    st.subheader(f"🌍 Állomás: {station_name} – {elevation} m - {selected_date}")

    show_statistics()

    show_temperature()

    show_prcp()

    show_coco()

    # Show Raw data table
    st.dataframe(df)
