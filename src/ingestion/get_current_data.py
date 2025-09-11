import requests
from datetime import datetime


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