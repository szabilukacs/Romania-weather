"""
Live Weather Map Visualization

This script loads live weather data from weather stations and visualizes it on an interactive map using Streamlit and Pydeck. 
Each station is displayed as a scatterplot point with a temperature label. Additional weather details are shown in tooltips 
when hovering over a station.
"""
import streamlit as st
import pandas as pd
import pydeck as pdk

from utils.utils import load_data_into_df
from utils.queries import SELECT_STATIONS_AND_LATEST_DATA
from utils.constants import ROMANIA_LAT, ROMANIA_LONG, MAP_ZOOM

# --- Query: stations + latest live weather data ---
query = SELECT_STATIONS_AND_LATEST_DATA

# Load data into a DataFrame
df_stations = load_data_into_df(query)

# Convert 'dt' column to datetime, coercing errors
df_stations["dt"] = pd.to_datetime(df_stations["dt"], errors="coerce")

# Format datetime to human-readable string
df_stations["time_str"] = df_stations["dt"].dt.strftime("%Y-%m-%d %H:%M")

# Create a label column for temperature with 1 decimal place
df_stations["label"] = df_stations["temp"].map(lambda x: f"{x:.1f}°C")

# --- Pydeck Scatterplot Layer ---
layer = pdk.Layer(
    "ScatterplotLayer",
    df_stations,
    get_position='[longitude, latitude]',
    get_fill_color='[255, 0, 0, 160]',  # red color
    get_radius=5000,  # radius in meters
    pickable=True
)

# --- Pydeck Text Layer for temperature labels ---
text_layer = pdk.Layer(
    "TextLayer",
    df_stations,
    get_position='[longitude, latitude]',
    get_text="label",
    get_size=16,
    get_color=[0, 0, 0],  # black text
    get_alignment_baseline="'bottom'",
    get_pixel_offset=[0, -5]  # offset text slightly above the marker
)

# --- Tooltip configuration ---
tooltip = {
    "html": """
        <b>📍 Station:</b> {name}<br/>
        <b>🕒 Time:</b> {time_str}<br/>
        <b>🌡 Temperature:</b> {temp} °C (feels {feels_like} °C)<br/>
        <b>💧 Humidity:</b> {humidity}%<br/>
        <b>☁️ Clouds:</b> {clouds}%<br/>
        <b>📏 Visibility:</b> {visibility} m<br/>
        <b>🧭 Wind:</b> {wind_speed} m/s ({wind_deg}°)<br/>
        <b>🌬 Gust:</b> {wind_gust} m/s<br/>
        <b>📊 Pressure:</b> {pressure} hPa<br/>
        <b>🔆 UV Index:</b> {uvi}<br/>
        <b>🌡 Dew Point:</b> {dew_point} °C<br/>
        <b>🌦 Condition:</b> {weather_main} ({weather_description})
    """,
    "style": {"backgroundColor": "white", "color": "black"}
}

# --- Create Pydeck map ---
r = pdk.Deck(
    layers=[layer, text_layer],
    initial_view_state=pdk.ViewState(
        latitude=ROMANIA_LAT,  # center of Romania
        longitude=ROMANIA_LONG,
        zoom=MAP_ZOOM,
        pitch=0,
    ),
    tooltip=tooltip,
    map_style="mapbox://styles/mapbox/light-v11"  # light map style
)

# Display map in Streamlit
st.pydeck_chart(r)

# Display title
st.title("Live Weather")
