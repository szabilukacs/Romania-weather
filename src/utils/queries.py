INSERT_STATIONS = """
        INSERT INTO stations (
            name, country, region, wmo, icao, latitude, longitude, elevation,
            timezone, hourly_start, hourly_end, daily_start, daily_end
        ) VALUES %s
        ON CONFLICT DO NOTHING;  -- prevents crash if duplicates exist
    """
SELEC_STATION_START_VALUES = (
    """ SELECT wmo, hourly_start, daily_start FROM stations; """
)

INSERT_WEATHER_DAILY = """
INSERT INTO weather_data_daily (
    station_id, time, tavg, tmin, tmax, prcp, snow, wdir, wspd, wpgt, pres, tsun
) VALUES %s
ON CONFLICT DO NOTHING;  -- prevents crash if duplicates exist
"""

SELECT_STATION_DATA = (
    "SELECT wmo,daily_start, hourly_start, elevation, name FROM stations;"
)

SELECT_NAME_WMO_STATIONS = "SELECT wmo, name FROM stations;"

SELECT_STATIONS_AND_LATEST_DATA = """
SELECT s.name, s.latitude, s.longitude,
       w.temp, w.humidity, w.wind_speed, w.weather_description,
        w.dt, w.feels_like, w.clouds, w.visibility, w.wind_deg, w.wind_gust,
        w.pressure, w.uvi, w.dew_point, w.weather_main, w.weather_description
FROM stations s
JOIN (
    SELECT DISTINCT ON (station_id) *
    FROM weather_live
    ORDER BY station_id, dt DESC
) w ON s.wmo = w.station_id;
"""

SELECT_STATIONS_DROPDOWN = "SELECT wmo, name FROM stations;"
