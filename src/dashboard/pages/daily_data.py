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

st.title("📅 Daily Weather Data")

# TODO: coco kód alapján ki is irni óránként hogy mi volt a helyzet.
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

        # Csak ahol van adat
    # --- Adatok előfeldolgozása ---
    df = df.dropna(subset=["wdir", "wspd"]).reset_index(drop=True)

    angles = np.deg2rad(df["wdir"] + 180)  # meteorológiai szélirány
    speeds = df["wspd"].values
    u = speeds * np.cos(angles)
    v = speeds * np.sin(angles)

    st.title("Szélirány animáció")

    play_button = st.button("▶️ Play 24 órás animáció")

    if play_button:
        placeholder = st.empty()  # ide rajzoljuk minden lépésben
        for hour_idx in range(len(df)):
            fig, ax = plt.subplots(figsize=(6,6))
            ax.quiver(0, 0, u[hour_idx], v[hour_idx], angles='xy', scale_units='xy', scale=1, color="crimson", width=0.015)

            max_speed = max(speeds) + 5
            ax.set_xlim(-max_speed, max_speed)
            ax.set_ylim(-max_speed, max_speed)

            # Égtájak jelzése
            ax.text(0, max_speed, "É", ha="center", va="bottom", fontsize=12, fontweight="bold")
            ax.text(0, -max_speed, "D", ha="center", va="top", fontsize=12, fontweight="bold")
            ax.text(-max_speed, 0, "Ny", ha="right", va="center", fontsize=12, fontweight="bold")
            ax.text(max_speed, 0, "K", ha="left", va="center", fontsize=12, fontweight="bold")

            ax.plot(0,0,"ko")
            ax.set_title(
                f"Óra: {df.loc[hour_idx,'time'].hour}:00 | Szél: {speeds[hour_idx]:.1f} km/h | irány: {df.loc[hour_idx,'wdir']}°",
                fontsize=14
            )
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_aspect('equal')

            placeholder.pyplot(fig)
            time.sleep(0.3)  # fél másodpercenként vált

    # Streamlit slider
    hour_idx = st.slider(
        "Válassz órát:",
        min_value=0,
        max_value=len(df)-1,
        value=0,
        format="Óra %d"
    )

    # --- Matplotlib ábra ---
    fig, ax = plt.subplots(figsize=(6,6))

    # Nyíl rajzolása az adott órára
    ax.quiver(0, 0, u[hour_idx], v[hour_idx], angles='xy', scale_units='xy', scale=1, color="crimson", width=0.015)

    # Tengelyek és skála
    max_speed = max(speeds) + 5
    ax.set_xlim(-max_speed, max_speed)
    ax.set_ylim(-max_speed, max_speed)

    # Égtájak jelzése
    ax.text(0, max_speed, "É", ha="center", va="bottom", fontsize=12, fontweight="bold")
    ax.text(0, -max_speed, "D", ha="center", va="top", fontsize=12, fontweight="bold")
    ax.text(-max_speed, 0, "Ny", ha="right", va="center", fontsize=12, fontweight="bold")
    ax.text(max_speed, 0, "K", ha="left", va="center", fontsize=12, fontweight="bold")

    # Középső pont
    ax.plot(0,0,"ko")  # az origó jelzése

    # Cím és tooltip
    ax.set_title(
        f"Szél: {df.loc[hour_idx,'wspd']:.1f} km/h\nirány: {df.loc[hour_idx,'wdir']}° (0° = Észak)",
        fontsize=14
    )

    # Tengelyek eltüntetése
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_aspect('equal')

    st.pyplot(fig)

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

    


