import streamlit as st
import pandas as pd
import altair as alt

import sys
sys.path.append('../')
# sys.path.insert(1, '/src/dashboard/')

from utils.connect_db import connect_to_db

# Lekérdezés futtatása
def load_data(query):
    conn = connect_to_db()
    df = pd.read_sql(query, conn)
    conn.close()
    return df

st.title("🌦 Weather Dashboard")

# Dropdown station választáshoz
stations = load_data("SELECT wmo, name FROM stations;")
station_name = st.selectbox("Choose a station:", stations["name"])
station_id = stations.loc[stations["name"] == station_name, "wmo"].values[0]

# Időszak választó
period = st.selectbox("Choose period:", ["1 month", "3 months", "6 months", "1 year"])
period_map = {
    "1 month": "1 month",
    "3 months": "3 months",
    "6 months": "6 months",
    "1 year": "1 year"
}
interval = period_map[period]

# Adatok lekérdezése
query = f"""
SELECT time, tavg, prcp
FROM weather_data_daily
WHERE station_id = {station_id}
  AND time >= NOW() - INTERVAL '{interval}'
ORDER BY time ASC;
"""

df = load_data(query)

# Statisztikai kártyák
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Avg Temp (°C)", f"{df['tavg'].mean():.1f}")
with col2:
    st.metric("Min Temp (°C)", f"{df['tavg'].min():.1f}")
with col3:
    st.metric("Max Temp (°C)", f"{df['tavg'].max():.1f}")
with col4:
    st.metric("Total Precip (mm)", f"{df['prcp'].sum():.1f}")


# Line chart
temp_chart = (
    alt.Chart(df)
    .mark_line(color="red")
    .encode(
        x=alt.X("time:T", title="Idő"),
        y=alt.Y("tavg:Q", title="Hőmérséklet (°C)"),
        tooltip=["time", "tavg"]
    )
    .properties(
        title=f"Napi átlaghőmérséklet - elmúlt {period}",
        width=700, 
        height=300
    )
)

st.altair_chart(temp_chart, use_container_width=True)

# Csapadék oszlopdiagram
prcp_chart = (
    alt.Chart(df)
    .mark_bar(color="blue")
    .encode(
        x=alt.X("time:T", title="Idő"),
        y=alt.Y("prcp:Q", title="Csapadék (mm)"),
        tooltip=["time", "prcp"]
    )
    .properties(title=f"Napi csapadék - elmúlt {period}", width=700, height=200)
)

st.altair_chart(prcp_chart, use_container_width=True)
