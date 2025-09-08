import streamlit as st
import pandas as pd
import altair as alt
from meteostat import Hourly
from datetime import datetime
from utils.connect_db import connect_to_db
from utils.queries import SELECT_STATION_DATA


st.title("📅 Daily Weather Data")

# TODO: coco kód alapján ki is irni óránként hogy mi volt a helyzet.
# TODO: tobbi adatot is itt feldolgozni valahogy érdekesen
# TODO: ellenorizni az adatokn'l h'ny null van az oras adatoknal

# --- Állomás kiválasztás (ha több van) ---
# Állomás kiválasztása
def load_data(query):
    conn = connect_to_db()
    df = pd.read_sql(query, conn)
    conn.close()
    return df

stations = load_data(SELECT_STATION_DATA)
station_name = st.selectbox("Choose a station:", stations["name"])
station_id = stations.loc[stations["name"] == station_name, "wmo"].values[0]
hourly_start = stations.loc[stations["name"] == station_name, "hourly_start"].values[0]
elevation = stations.loc[stations["name"] == station_name, "elevation"].values[0]

# --- Dátum kiválasztás ---
selected_date = st.date_input("Válassz egy napot:", pd.to_datetime("today").date(), min_value=hourly_start)


def load_data(query):
    conn = connect_to_db()
    df = pd.read_sql(query, conn)
    conn.close()
    return df

customy1 = datetime(selected_date.year,1,1)
customy2 = datetime(selected_date.year,12,31)
data = Hourly(station_id,start = customy1,end = customy2)
print(data.coverage())

# --- Adatok lekérdezése ---
query = f"""
SELECT time, temp, dwpt, rhum, prcp, pres, tsun, coco
FROM weather_data_hourly
WHERE station_id = {station_id}
  AND DATE(time) = '{selected_date}'
ORDER BY time ASC;
"""
print(station_id)
print(selected_date)
df = load_data(query)

if df.empty:
    st.warning("❌ Nincs adat a kiválasztott napra.")
else:
    
    st.subheader(f"🌍 Állomás: {station_name} – {elevation} m - {selected_date}")

    # --- Hőmérséklet vonaldiagram ---
    temp_chart = (
        alt.Chart(df)
        .mark_line(point=True, color="red")
        .encode(
            x=alt.X("time:T", title="Idő"),
            y=alt.Y("temp:Q", title="Átlaghőmérséklet (°C)"),
            tooltip=["time", "temp"]
        )
        .properties(title="🌡 Napi hőmérséklet alakulása", width=700, height=300)
    )

    # --- Csapadék oszlopdiagram ---
    prcp_chart = (
        alt.Chart(df)
        .mark_bar(color="blue", opacity=0.7)
        .encode(
            x=alt.X("time:T", title="Idő"),
            y=alt.Y("prcp:Q", title="Csapadék (mm)"),
            tooltip=["time", "prcp"]
        )
        .properties(title="🌧 Napi csapadék", width=700, height=200)
    )

    st.altair_chart(temp_chart, use_container_width=True)
    st.altair_chart(prcp_chart, use_container_width=True)

    # Mutatjuk a táblázatot
    st.dataframe(df)
