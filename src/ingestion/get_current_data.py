import requests
import pandas as pd
from datetime import datetime
from meteostat import Stations

def fetch_and_store_weather(lat: float, lon: float, station_id: int, conn, api_key: str) -> None:
    """
    Fetch current weather from OpenWeather API and store it in PostgreSQL.
    
    Args:
        lat (float): Latitude of the station
        lon (float): Longitude of the station
        station_id (int): ID of the station in database
        conn (psycopg2 connection): Active PostgreSQL connection
        api_key (str): OpenWeather API key
    """
    url = (
        f"https://api.openweathermap.org/data/3.0/onecall"
        f"?lat={lat}&lon={lon}&exclude=hourly,daily&appid={api_key}&units=metric"
    )

    response = requests.get(url)

    if response.status_code != 200:
        print(f"❌ Error: {response.status_code} - {response.text}")
        return

    data = response.json()
    current = data.get("current", {})
    weather = current.get("weather", [{}])[0]  # first element in weather list

    # --- Prepare record for DB ---
    record = {
        "station_id": station_id,
        "lat": data["lat"],
        "lon": data["lon"],
        "timezone": data["timezone"],
        "timezone_offset": data["timezone_offset"],
        "dt": datetime.fromtimestamp(current["dt"]),
        "sunrise": datetime.fromtimestamp(current["sunrise"]),
        "sunset": datetime.fromtimestamp(current["sunset"]),
        "temp": current.get("temp"),
        "feels_like": current.get("feels_like"),
        "pressure": current.get("pressure"),
        "humidity": current.get("humidity"),
        "dew_point": current.get("dew_point"),
        "uvi": current.get("uvi"),
        "clouds": current.get("clouds"),
        "visibility": current.get("visibility"),
        "wind_speed": current.get("wind_speed"),
        "wind_deg": current.get("wind_deg"),
        "wind_gust": current.get("wind_gust"),
        "weather_id": weather.get("id"),
        "weather_main": weather.get("main"),
        "weather_description": weather.get("description"),
        "weather_icon": weather.get("icon"),
    }

    insert_query = """
    INSERT INTO weather_live (
        station_id, lat, lon, timezone, timezone_offset,
        dt, sunrise, sunset, temp, feels_like, pressure,
        humidity, dew_point, uvi, clouds, visibility,
        wind_speed, wind_deg, wind_gust,
        weather_id, weather_main, weather_description, weather_icon
    )
    VALUES (
        %(station_id)s,
        %(lat)s, %(lon)s, %(timezone)s, %(timezone_offset)s,
        %(dt)s, %(sunrise)s, %(sunset)s, %(temp)s, %(feels_like)s, %(pressure)s,
        %(humidity)s, %(dew_point)s, %(uvi)s, %(clouds)s, %(visibility)s,
        %(wind_speed)s, %(wind_deg)s, %(wind_gust)s,
        %(weather_id)s, %(weather_main)s, %(weather_description)s, %(weather_icon)s
    );
    """

    cur = conn.cursor()
    cur.execute(insert_query, record)
    conn.commit()
    cur.close()

    print(f"✅ Weather record inserted for station_id={station_id}")

def is_valid_wmo(wmo) -> bool:
    """
    Return True if `wmo` is a valid numeric WMO identifier that can be used as int.
    This filters out None, pd.NA, NaN, the literal "<NA>" string, empty strings,
    and any non-numeric values (except float-like integers like "123.0").
    """
    # explicit None / pandas NA / numpy.nan check
    if wmo is None:
        return False
    if pd.isna(wmo):  # covers np.nan, pd.NA, None-like
        return False

    s = str(wmo).strip()
    if s == "":
        return False

    # Common textual null representations
    if s.upper() in {"<NA>", "NA", "N/A", "NONE", "NAN"}:
        return False

    # If string is all digits -> ok
    if s.isdigit():
        return True

    # If it's a float string like "123.0", allow it (but not "123.4")
    try:
        f = float(s)
        if f.is_integer():
            return True
        return False
    except Exception:
        return False


def fetch_weather_nearby(api_key, conn, lat, lon, n_stations=5, regions: list[str] = None):
    """
    Fetch the nearest `n_stations` to the given coordinates (lat, lon) and store their current weather data.
    If a list of regions is provided, only stations from those regions will be processed.

    Args:
        lat (float): Latitude of the location.
        lon (float): Longitude of the location.
        conn: Database connection object.
        api_key (str): API key for fetching weather data.
        n_stations (int, optional): Number of nearest stations to fetch. Defaults to 5.
        regions (list[str], optional): List of region codes to filter stations. Defaults to None.
    """
    try:
        Stations.cache_dir = 'meteostat/cache'
        stations_obj = Stations().nearby(lat, lon)

        # If regions list is provided, filter stations by each region
        if regions:
            dfs = []
            for region_code in regions:
                region_stations = stations_obj.region('RO',region_code).fetch(n_stations)
                dfs.append(region_stations)
            stations = pd.concat(dfs, ignore_index=True)
        else:
            stations = stations_obj.fetch(n_stations) # ezt az opciot kivenni

        # --- Filter out invalid WMOs ---
        valid_mask = stations['wmo'].apply(is_valid_wmo)
        n_total, n_kept = len(stations), int(valid_mask.sum())
        print(f"Stations total: {n_total}, kept valid WMO: {n_kept}, dropped: {n_total - n_kept}")

        stations = stations.loc[valid_mask]

        for idx, row in stations.iterrows():
            station_id = int(float(str(row["wmo"]).strip()))  # now guaranteed safe
            station_lat = row["latitude"]
            station_lon = row["longitude"]
            name = row["name"]

            print(f"🌍 Fetching: {name} (ID={station_id}, lat={station_lat}, lon={station_lon})")

            try:
                fetch_and_store_weather(
                    lat=station_lat,
                    lon=station_lon,
                    station_id=station_id,
                    conn=conn,
                    api_key=api_key
                )
            except Exception as e:
                print(f"❌ Error at station {name}: {e}")

    finally:
        conn.close()
