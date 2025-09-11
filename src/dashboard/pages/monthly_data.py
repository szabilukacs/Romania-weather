import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime

from utils.utils import load_data_into_df
from utils.queries import SELECT_NAME_WMO_STATIONS
from utils.constants import BLUE, ORANGE

def show_temperatures(df_compare: pd.DataFrame, month: int, colors: list[str]) -> None:
    """
    Display a line chart comparing average daily temperatures 
    between the current year and the previous year for the selected month.

    The chart uses Altair and plots:
      - X-axis: Day of the month
      - Y-axis: Average temperature (°C)
      - Color: Year (current vs. last year)

    Data source:
        - Global `df_compare` DataFrame (merged dataset of current and last year)
        - Global `month` variable (selected month)
        - Global `colors` list for consistent color scheme
    """
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

def show_prcp(df_compare: pd.DataFrame, month: int, colors: list[str]) -> None:
    """
    Display a bar chart comparing daily precipitation (mm) 
    between the current year and the previous year for the selected month.

    The chart uses Altair and plots:
      - X-axis: Day of the month
      - Y-axis: Precipitation (mm)
      - Color: Year (current vs. last year)

    Data source:
        - Global `df_compare` DataFrame (merged dataset of current and last year)
        - Global `month` variable (selected month)
        - Global `colors` list for consistent color scheme
    """
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

def show_statistics(df_current: pd.DataFrame, df_last: pd.DataFrame, current_year: int) -> None:
    """
    Display statistical summary metrics comparing:
      - Average temperature (°C) between the current and previous year
      - Total precipitation (mm) between the current and previous year

    The function shows results using Streamlit `metric` widgets in two columns:
      - Left column: average temperature difference
      - Right column: total monthly precipitation difference

    Data source:
        - Global `df_current` DataFrame (current year)
        - Global `df_last` DataFrame (previous year)
        - Global `current_year` variable
    """
    col1, col2 = st.columns(2)

    # Average temperature difference
    avg_temp_current = df_current["tavg"].mean()
    avg_temp_last = df_last["tavg"].mean()
    temp_diff = avg_temp_current - avg_temp_last

    col1.metric(
        label="🌡 Átlaghőmérséklet különbség",
        value=f"{avg_temp_current:.1f} °C",
        delta=f"{temp_diff:+.1f} °C vs {current_year - 1}"
    )

    # Total precipitation difference
    prcp_sum_current = df_current["prcp"].sum()
    prcp_sum_last = df_last["prcp"].sum()
    prcp_diff = prcp_sum_current - prcp_sum_last

    col2.metric(
        label="🌧 Teljes havi csapadék",
        value=f"{prcp_sum_current:.1f} mm",
        delta=f"{prcp_diff:+.1f} mm vs {current_year - 1}"
    )


# --- Streamlit App Layout ---
st.title("📊 Éves összehasonlítás – Idén vs Tavaly")

# Stations dropdown
stations = load_data_into_df(SELECT_NAME_WMO_STATIONS)
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
df = load_data_into_df(query)

df["time"] = pd.to_datetime(df["time"])

# Filter for selected month
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

# --- Display sections ---
show_statistics(df_current, df_last, current_year)

show_temperatures(df_compare, month, colors)

show_prcp(df_compare, month, colors)

