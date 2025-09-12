import streamlit as st
import pandas as pd
import math
import altair as alt

from utils.utils import calc_days_of_year, load_data_into_df
from utils.queries import SELECT_STATION_DATA


def styled_progress(label, value):
    """Színezett progress bar Streamlitben"""
    color = "green"
    if value < 50:
        color = "red"
    elif value < 80:
        color = "orange"

    st.markdown(
        f"""
        <div style="margin-bottom:10px">
            <b>{label}: {value:.1f}%</b>
            <div style="background-color:#ddd; border-radius:10px; height:20px; width:100%">
                <div style="background-color:{color}; width:{value}%; height:100%; border-radius:10px"></div>
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )


def show_statistics():
    col1, col2, col3 = st.columns(3)
    if not math.isnan(avg_tavg):
        delta_temp = f"{avg_tavg - avg_tavg_curr:+.1f} °C vs {current_year}" if avg_tavg_curr is not None else None
        col1.metric("🌡 Átlaghőmérséklet", f"{avg_tavg:.1f} °C", delta=delta_temp)

    if not int(total_precip) == 0:
        col2.metric(
            "🌧 Teljes csapadék",
            f"{total_precip:.1f} mm",
            delta=(f"{total_precip - total_precip_curr:+.1f} mm vs {current_year}" if total_precip_curr else None),
        )

    if not int(rainy_days) == 0:
        col3.metric(
            "☔ Csapadékos napok",
            rainy_days,
            delta=(f"{rainy_days - rainy_days_curr:+d} vs {current_year}" if rainy_days_curr else None),
        )


def show_extrem_values():
    if coldest_day is not None or warmest_day is not None:
        st.markdown("### Szélsőértékek")
        c1, c2 = st.columns(2)

        if coldest_day is not None:
            c1.metric("❄️ Leghidegebb nap", f"{coldest_day['tmin']:.1f} °C")

        if warmest_day is not None:
            c2.metric("☀️ Legmelegebb nap", f"{warmest_day['tmax']:.1f} °C")


def show_coverage():
    st.subheader("📊 Adat lefedettség")
    col1, col2 = st.columns(2)
    with col1:
        styled_progress("🌡 Hőmérséklet lefedettség", tavg_coverage)
    with col2:
        styled_progress("🌧 Csapadék lefedettség", prcp_coverage)


def show_chart():
    if not df_tavg.empty:
        # Vonaldiagram
        daily_temp_chart = (
            alt.Chart(df_tavg)
            .mark_line(color="red")
            .encode(
                x=alt.X("time:O", title="Nap az évből"),
                y=alt.Y("tavg:Q", title="Átlaghőmérséklet (°C)"),
                tooltip=["time", "tavg"],
            )
            .properties(title=f"{year} napi átlaghőmérsékletei", width=700, height=300)
        )

        st.altair_chart(daily_temp_chart, use_container_width=True)


# Állomás kiválasztása
stations = load_data_into_df(SELECT_STATION_DATA)
station_name = st.selectbox("Choose a station:", stations["name"])
station_id = stations.loc[stations["name"] == station_name, "wmo"].values[0]
daily_start = stations.loc[stations["name"] == station_name, "daily_start"].values[0]

# Év kiválasztása
year = st.selectbox(
    "Válassz egy évet:",
    list(reversed(range(daily_start.year, pd.Timestamp.now().year + 1))),
)

current_year = pd.Timestamp.today().year

# Adatok lekérdezése az adott évre
query_select_days_data = f"""
SELECT time, tavg, tmin, tmax, prcp
FROM weather_data_daily
WHERE station_id = {station_id}
  AND EXTRACT(YEAR FROM time) = {year}
ORDER BY time ASC;
"""
df = load_data_into_df(query_select_days_data)

# --- Adatok tisztítása ---
df["time"] = pd.to_datetime(df["time"])
# Távolítsuk el a sorokat, ahol minden érték NaN
df = df.dropna(subset=["tavg", "tmin", "tmax", "prcp"], how="all")

days_in_year = calc_days_of_year(year)

tavg_coverage = df["tavg"].notna().sum() / days_in_year * 100
prcp_coverage = df["prcp"].notna().sum() / days_in_year * 100

# --- Éves összesítés ---
avg_tavg = df["tavg"].mean()
total_precip = df["prcp"].sum()

rainy_days = df[df["prcp"] > 0].shape[0]
coldest_day = df.loc[df["tmin"].idxmin()] if not df["tmin"].isna().all() else None
warmest_day = df.loc[df["tmax"].idxmax()] if not df["tmax"].isna().all() else None

df_tavg = df[["time", "tavg"]]
df_tavg["time"] = df_tavg["time"].dt.dayofyear

# --- Markdown összegzés ---

# --- Aktuális év statisztikái (pl. 2025) ---
query_select_days_data_last_year = f"""
SELECT time, tavg, tmin, tmax, prcp
FROM weather_data_daily
WHERE station_id = {station_id}
  AND EXTRACT(YEAR FROM time) = {current_year}
ORDER BY time ASC;
"""
df_current = load_data_into_df(query_select_days_data_last_year)

# Calc current year means
if not df_current.empty:
    avg_tavg_curr = df_current["tavg"].mean()
    total_precip_curr = df_current["prcp"].sum()
    rainy_days_curr = df_current[df_current["prcp"] > 0].shape[0]
else:
    avg_tavg_curr = total_precip_curr = rainy_days_curr = None

# --- 3 hasábban mutatjuk a fő statisztikákat ---
show_statistics()

# --- Szélsőértékek külön "dobozban" ---
show_extrem_values()

# --- Coverage mutatók progress bar-ral ---
show_coverage()

show_chart()
