import streamlit as st
import pandas as pd
import altair as alt
from meteostat import Hourly
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import time

from utils.connect_db import connect_to_db
from utils.queries import SELECT_STATION_DATA
from utils.constants import COCO_CODES

st.title("📅 Daily Weather Data")

# TODO: coco kód alapján ki is irni óránként hogy mi volt a helyzet.
# TODO: ellenorizni az adatokn'l h'ny null van-e az oras adatoknal

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
today = pd.to_datetime("today").date()
selected_date = st.date_input("Válassz egy napot:", today - pd.Timedelta(days=14), min_value=hourly_start)

customy1 = datetime(selected_date.year,1,1)
customy2 = datetime(selected_date.year,12,31)
data = Hourly(station_id,start = customy1,end = customy2)
print(data.coverage())

# --- Adatok lekérdezése ---
query = f"""
SELECT time, temp, dwpt, rhum, prcp, snow, wdir, wspd, wpgt, pres, tsun, coco
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
    
    # Csak a szükséges oszlopok
    
            # Feltételezzük, hogy df tartalmazza: time, coco
     # Biztonságos konverzió számra
    df_coco = df[["time", "coco"]].dropna().reset_index(drop=True)
    df_coco["coco"] = df_coco["coco"].astype(float).round().astype(int)

        # Feltérképezés condition szövegre
    df_coco["condition"] = df_coco["coco"].map(COCO_CODES)
    # 1️⃣ időszakok kiszámítása: meddig tartott egy adott állapot
    df_coco["end_time"] = df_coco["time"].shift(-1)  # következő váltás az adott sor vége
    df_coco = df_coco.dropna(subset=["end_time"])    # utolsó sorban nincs end_time

    # 2️⃣ Altair sávdiagram (timeline)
    timeline = (
        alt.Chart(df_coco)
        .mark_bar()
        .encode(
            x=alt.X("time:T", title="Idő"),
            x2="end_time:T",  # időszak vége
            y=alt.Y("condition:N", title="Időjárási állapot"),
            color=alt.Color("condition:N", legend=alt.Legend(title="Állapot")),
            tooltip=["time:T", "end_time:T", "condition"]
        )
        .properties(
            title="🌦 Időjárási állapotok idővonala",
            width=700,
            height=200
        )
    )

    st.altair_chart(timeline, use_container_width=True)


    total_sun_minutes = df['tsun'].sum()
    hours = total_sun_minutes // 60
    minutes = total_sun_minutes % 60

    st.metric(
        label="🌞 Összes napsütés aznap",
        value=f"{hours}h {minutes}m"
    )

    # --- Hó összesítése ---
    total_snow = df['snow'].sum()  # mm

    # Óra és perc konverzió nem kell, mert mm-ben mérjük
    st.metric(
        label="❄️ Hullott hó mennyiség",
        value=f"{total_snow:.1f} mm"
    )



    # Mutatjuk a táblázatot
    st.dataframe(df)

    


