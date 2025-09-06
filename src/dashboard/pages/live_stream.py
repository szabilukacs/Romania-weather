import streamlit as st
import pandas as pd
import pydeck as pdk
from utils.connect_db import connect_to_db

# --- Load stations and latest daily data ---
def load_data(query):
    conn = connect_to_db()
    df = pd.read_sql(query, conn)
    conn.close()
    return df



df_stations = load_data("SELECT name, latitude, longitude FROM stations;")

# TODO: API-bol lekert adatokat itt streamelni majd

# Pydeck Layer
layer = pdk.Layer(
    "ScatterplotLayer",
    df_stations,
    get_position='[longitude, latitude]',
    get_fill_color='[255, 0, 0, 160]',  # piros
    get_radius=5000,  # radius in meters
    pickable=True
)

# Tooltip
tooltip = {"html": "<b>Station:</b> {name}", "style": {"backgroundColor": "white", "color": "black"}}

# Map
r = pdk.Deck(
    layers=[layer],
    initial_view_state=pdk.ViewState(
        latitude=45.9432,  # Romania középpont
        longitude=24.9668,
        zoom=6,
        pitch=0,
    ),
    tooltip=tooltip
)

st.pydeck_chart(r)

st.title("Live weather")
