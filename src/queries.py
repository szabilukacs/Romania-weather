INSERT_STATIONS = """
        INSERT INTO stations (
            name, country, region, wmo, icao, latitude, longitude, elevation,
            timezone, hourly_start, hourly_end, daily_start, daily_end,
            monthly_start, monthly_end
        ) VALUES %s
        ON CONFLICT DO NOTHING;  -- prevents crash if duplicates exist
    """