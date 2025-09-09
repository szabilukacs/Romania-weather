INSERT_STATIONS = """
        INSERT INTO stations (
            name, country, region, wmo, icao, latitude, longitude, elevation,
            timezone, hourly_start, hourly_end, daily_start, daily_end,
            monthly_start, monthly_end
        ) VALUES %s
        ON CONFLICT DO NOTHING;  -- prevents crash if duplicates exist
    """
SELEC_STATION_START_VALUES = """ SELECT wmo, hourly_start, daily_start, monthly_start FROM stations; """

INSERT_WEATHER_DAILY = """
INSERT INTO weather_data_daily (
    station_id, time, tavg, tmin, tmax, prcp, snow, wdir, wspd, wpgt, pres, tsun
) VALUES %s
ON CONFLICT DO NOTHING;  -- prevents crash if duplicates exist
"""

INSERT_WEATHER_MONTHLY = """
INSERT INTO weather_data_monthly (
    station_id, time, tavg, tmin, tmax, prcp, wspd, pres, tsun
) VALUES %s
ON CONFLICT DO NOTHING;  -- prevents crash if duplicates exist
"""

SELECT_STATION_DATA = "SELECT wmo,daily_start, hourly_start, elevation, name FROM stations;"

SELECT_NAME_WMO_STATIONS = "SELECT wmo, name FROM stations;"