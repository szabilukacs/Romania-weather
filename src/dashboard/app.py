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

# Adatok lekérdezése
query = f"""
SELECT time, tavg, prcp
FROM weather_data_daily
WHERE station_id = {station_id}
  AND time >= NOW() - INTERVAL '1 year'
ORDER BY time ASC;
"""
df = load_data(query)

# Tábla
st.dataframe(df.head(10))

temp_chart = (
    alt.Chart(df)
    .mark_line(color="red")
    .encode(
        x=alt.X("time:T", title="Idő"),
        y=alt.Y("tavg:Q", title="Hőmérséklet (°C)"),
        tooltip=["time", "tavg"]
    )
    .properties(title="Napi átlaghőmérséklet alakulása az elmúlt 1 évben", width=700, height=300)
)

# Vonaldiagram (pl. hőmérséklet)
st.altair_chart(temp_chart, use_container_width=True)
