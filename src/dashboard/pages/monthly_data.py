import streamlit as st
import pandas as pd
import altair as alt

from datetime import datetime
from utils.connect_db import connect_to_db

# Lekérdezés futtatása
def load_data(query):
    conn = connect_to_db()
    df = pd.read_sql(query, conn)
    conn.close()
    return df

st.title("📊 Éves összehasonlítás – Idén vs Tavaly")

# Állomások dropdown
stations = load_data("SELECT wmo, name FROM stations;")
station_name = st.selectbox("Choose a station:", stations["name"])
station_id = stations.loc[stations["name"] == station_name, "wmo"].values[0]

# Hónap kiválasztása
month = st.selectbox(
    "Válassz egy hónapot az összehasonlításhoz:",
    list(range(1, int(datetime.today().month))),
    format_func=lambda x: pd.to_datetime(str(x), format="%m").strftime("%B")
)

# Adatok lekérdezése az elmúlt 2 évre
query = f"""
SELECT time, tavg, tmin, tmax, prcp
FROM weather_data_daily
WHERE station_id = {station_id}
  AND time >= NOW() - INTERVAL '2 years'
ORDER BY time ASC;
"""
df = load_data(query)

df["time"] = pd.to_datetime(df["time"])

# Csak az adott hónap
df_month = df[df["time"].dt.month == month]

# Év szétválasztás
current_year = pd.Timestamp.now().year
df_month["year"] = df_month["time"].dt.year
df_month["day"] = df_month["time"].dt.day  # nap szerinti összehasonlítás

df_current = df_month[df_month["year"] == current_year]
df_last = df_month[df_month["year"] == (current_year - 1)]

# Label oszlop
df_current["label"] = f"{current_year}"
df_last["label"] = f"{current_year - 1}"
df_compare = pd.concat([df_current, df_last])

# --- 📈 Hőmérséklet chart ---
colors = ["#1f77b4", "#ff7f0e"]  # kék és narancs

temp_chart = (
    alt.Chart(df_compare)
    .mark_line()
    .encode(
        x=alt.X("day:O", title="Nap"),
        y=alt.Y("tavg:Q", title="Hőmérséklet (°C)"),
        color=alt.Color(
            "label:N",
            scale=alt.Scale(domain=df_compare["label"].unique(), range=colors),
            legend=alt.Legend(title="Év")
        ),
        tooltip=["time", "tavg", "label"]
    )
    .properties(
        title=f"Átlaghőmérséklet összehasonlítás – {pd.to_datetime(str(month), format='%m').strftime('%B')}",
        width=700,
        height=300
    )
)
# --- 🌧 Csapadék chart ---
prcp_chart = (
    alt.Chart(df_compare)
    .mark_bar(opacity=0.6)
    .encode(
        x=alt.X("day:O", title="Nap"),
        y=alt.Y("prcp:Q", title="Csapadék (mm)"),
        color=alt.Color(
            "label:N",
            scale=alt.Scale(domain=df_compare["label"].unique(), range=colors),
            legend=alt.Legend(title="Év")
        ),
        tooltip=["time", "prcp", "label"]
    )
    .properties(
        title=f"Csapadék összehasonlítás – {pd.to_datetime(str(month), format='%m').strftime('%B')}",
        width=700,
        height=300
    )
)

# --- 📊 Statisztikai kártyák ---
col1, col2 = st.columns(2)

# Átlaghőmérséklet különbség
avg_temp_current = df_current["tavg"].mean()
avg_temp_last = df_last["tavg"].mean()
temp_diff = avg_temp_current - avg_temp_last

col1.metric(
    label="🌡 Átlaghőmérséklet különbség",
    value=f"{avg_temp_current:.1f} °C",
    delta=f"{temp_diff:+.1f} °C vs {current_year - 1}"
)

# Teljes havi csapadék különbség
prcp_sum_current = df_current["prcp"].sum()
prcp_sum_last = df_last["prcp"].sum()
prcp_diff = prcp_sum_current - prcp_sum_last

col2.metric(
    label="🌧 Teljes havi csapadék",
    value=f"{prcp_sum_current:.1f} mm",
    delta=f"{prcp_diff:+.1f} mm vs {current_year - 1}"
)

# Megjelenítés
st.altair_chart(temp_chart, use_container_width=True)
st.altair_chart(prcp_chart, use_container_width=True)
