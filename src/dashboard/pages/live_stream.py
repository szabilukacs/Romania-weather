import streamlit as st
import pandas as pd
import pydeck as pdk
from utils.connect_db import connect_to_db

# --- Load stations and latest daily data ---
def load_data_into_df(query):
    conn = connect_to_db()
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# --- Query: stations + latest live weather data ---
query = """
SELECT s.name, s.latitude, s.longitude,
       w.temp, w.humidity, w.wind_speed, w.weather_description,
        w.dt, w.feels_like, w.clouds, w.visibility, w.wind_deg, w.wind_gust, 
        w.pressure, w.uvi, w.dew_point, w.weather_main, w.weather_description
FROM stations s
JOIN (
    SELECT DISTINCT ON (station_id) *
    FROM weather_live
    ORDER BY station_id, dt DESC
) w ON s.wmo = w.station_id;
"""


df_stations = load_data_into_df(query)

print(df_stations)

# Feltételezzük, hogy a df_stations-ben van egy 'time' oszlop
df_stations["dt"] = pd.to_datetime(df_stations["dt"], errors="coerce")

# Formázzuk emberi olvashatóra (pl. 2025-09-09 15:00)
df_stations["time_str"] = df_stations["dt"].dt.strftime("%Y-%m-%d %H:%M")

# Pydeck Layer
layer = pdk.Layer(
    "ScatterplotLayer",
    df_stations,
    get_position='[longitude, latitude]',
    get_fill_color='[255, 0, 0, 160]',  # piros
    get_radius=5000,  # radius in meters
    pickable=True
)

# Készítünk egy oszlopot a címkének, 1 tizedesjegy
df_stations["label"] = df_stations["temp"].map(lambda x: f"{x:.1f}°C")

# Text layer for temperature labels
text_layer = pdk.Layer(
    "TextLayer",
    df_stations,
    get_position='[longitude, latitude]',
    get_text="label",
    get_size=16,
    get_color=[0, 0, 0],   # fekete szöveg
    get_alignment_baseline="'bottom'",
    get_pixel_offset=[0, -5]  # 20 pixelrel felfelé toljuk a címkét
)

# Tooltip
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


# Map
r = pdk.Deck(
    layers=[layer, text_layer],
    initial_view_state=pdk.ViewState(
        latitude=45.9432,  # Romania középpont
        longitude=24.9668,
        zoom=5.5,
        pitch=0,
    ),
    tooltip=tooltip,
    map_style="mapbox://styles/mapbox/light-v11"  # világos térkép
)

st.pydeck_chart(r)

st.title("Live weather")
