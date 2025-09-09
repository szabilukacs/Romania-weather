import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime

from utils.utils import load_data
from utils.queries import SELECT_NAME_WMO_STATIONS

BLUE = "#1f77b4"
ORANGE = "#ff7f0e"

def show_temperatures():
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
    st.altair_chart(temp_chart, use_container_width=True)

def show_prcp():
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
    st.altair_chart(prcp_chart, use_container_width=True)

def show_statistics():
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


st.title("📊 Éves összehasonlítás – Idén vs Tavaly")

# Stations dropdown
stations = load_data(SELECT_NAME_WMO_STATIONS)
station_name = st.selectbox("Choose a station:", stations["name"])
station_id = stations.loc[stations["name"] == station_name, "wmo"].values[0]

# Select month
month = st.selectbox(
    "Válassz egy hónapot az összehasonlításhoz:",
    list(range(1, int(datetime.today().month))),
    format_func=lambda x: pd.to_datetime(str(x), format="%m").strftime("%B")
)

# Load daily data for the last 2 year
query = f"""
SELECT time, tavg, tmin, tmax, prcp
FROM weather_data_daily
WHERE station_id = {station_id}
  AND time >= NOW() - INTERVAL '2 years'
ORDER BY time ASC;
"""
df = load_data(query)

df["time"] = pd.to_datetime(df["time"])

# Select the selected month
df_month = df[df["time"].dt.month == month]

# Separete the years
current_year = pd.Timestamp.now().year
df_month["year"] = df_month["time"].dt.year
df_month["day"] = df_month["time"].dt.day

df_current = df_month[df_month["year"] == current_year]
df_last = df_month[df_month["year"] == (current_year - 1)]

# Label column
df_current["label"] = f"{current_year}"
df_last["label"] = f"{current_year - 1}"
df_compare = pd.concat([df_current, df_last])

colors = [BLUE, ORANGE]

show_statistics()

show_temperatures()

show_prcp()

