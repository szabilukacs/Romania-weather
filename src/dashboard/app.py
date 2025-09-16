"""
Weather Dashboard Visualization

This script creates an interactive weather dashboard
using Streamlit and Altair. Users can select a weather station
and a date range to visualize daily average temperatures
and precipitation. Statistical metrics are displayed as
cards above the charts.
"""

import sys
import streamlit as st
import pandas as pd
import altair as alt
sys.path.append("../")
from utils.utils import load_data_into_df  # noqa: E402
from utils.queries import SELECT_STATIONS_DROPDOWN  # noqa: E402


# sys.path.insert(1, '/src/dashboard/')


def show_temp():
    """
    Display a line chart of daily average temperatures using Altair.
    """
    temp_chart = (
        alt.Chart(df)
        .mark_line(color="#FF4B4B")
        .encode(
            x=alt.X("time:T", title="Idő"),
            y=alt.Y("tavg:Q", title="Hőmérséklet (°C)"),
            tooltip=[
                alt.Tooltip("time:T", title="Dátum"),
                alt.Tooltip("tavg:Q", title="Hőmérséklet °C"),
            ],
        )
        .properties(width=700, height=300, title="📈 Napi átlaghőmérséklet")
    )
    st.altair_chart(temp_chart, use_container_width=True)


def show_prcp():
    """
    Display a bar chart of daily precipitation using Altair.
    """
    prcp_chart = (
        alt.Chart(df)
        .mark_bar(color="#1F77B4")
        .encode(
            x=alt.X("time:T", title="Idő"),
            y=alt.Y("prcp:Q", title="Csapadék (mm)"),
            tooltip=[
                alt.Tooltip("time:T", title="Dátum"),
                alt.Tooltip("prcp:Q", title="Csapadék mm"),
            ],
        )
        .properties(
            width=700,
            height=200,
            title="🌧 Napi csapadék",
            padding={"top": 30, "bottom": 10, "left": 10, "right": 10},
        )
    )
    st.altair_chart(prcp_chart, use_container_width=True)


st.title("🌦 Weather Dashboard")

# --- Dropdown to select station ---
stations = load_data_into_df(SELECT_STATIONS_DROPDOWN)
station_name = st.selectbox("Choose a station:", stations["name"])
station_id = stations.loc[stations["name"] == station_name, "wmo"].values[0]

# --- Date range picker ---
today = pd.Timestamp.today().date()
start_date = st.date_input(
    "Start date:", value=today - pd.Timedelta(days=37), max_value=today
)
end_date = st.date_input(
    "End date:", value=today - pd.Timedelta(days=7), max_value=today
)

if start_date > end_date:
    st.error("Start date must be before end date!")
else:
    # --- Query weather data for the selected date range ---
    query = f"""
    SELECT time, tavg, tmin, tmax, prcp
    FROM weather_data_daily
    WHERE station_id = {station_id}
      AND time >= '{start_date}' AND time <= '{end_date}'
    ORDER BY time ASC;
    """
    df = load_data_into_df(query)
    df["time"] = pd.to_datetime(df["time"])

    # --- Statistical metric cards ---
    col1, col2, col3, col4 = st.columns(4)

    avg_temp = df["tavg"].mean()
    min_temp = df["tavg"].min()
    max_temp = df["tavg"].max()
    total_precip = df["prcp"].sum()

    with col1:
        st.metric("🌡 Átlaghőmérséklet", f"{avg_temp:.1f} °C")
    with col2:
        st.metric("🥶 Minimum hőmérséklet", f"{min_temp:.1f} °C")
    with col3:
        st.metric("🥵 Maximum hőmérséklet", f"{max_temp:.1f} °C")
    with col4:
        st.metric("🌧 Teljes csapadék", f"{total_precip:.1f} mm")

    show_temp()

    show_prcp()
