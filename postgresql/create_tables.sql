
-- DROP TABLE IF EXISTS stations CASCADE;
-- DROP TABLE IF EXISTS weather_data_hourly CASCADE;
-- DROP TABLE IF EXISTS weather_data_daily CASCADE;
-- DROP TABLE IF EXISTS weather_live CASCADE;

CREATE TABLE IF NOT EXISTS stations (
    name TEXT NOT NULL,              -- station name
    country CHAR(2) NOT NULL,        -- ISO country code (e.g. HU, RO)
    region TEXT,                     -- region, state, or province
    wmo INTEGER PRIMARY KEY,         -- WMO station code
    icao CHAR(4),                    -- ICAO station code
    latitude DOUBLE PRECISION,       -- latitude in decimal degrees
    longitude DOUBLE PRECISION,      -- longitude in decimal degrees
    elevation DOUBLE PRECISION,      -- elevation above sea level (meters)
    timezone TEXT NOT NULL,          -- timezone identifier (e.g. Europe/Bucharest)
    hourly_start DATE,               -- first available hourly record
    hourly_end DATE,                 -- last available hourly record
    daily_start DATE,                -- first available daily record
    daily_end DATE,                  -- last available daily record
    last_update TIMESTAMP                 -- last updated by me
);

CREATE TABLE IF NOT EXISTS weather_data_hourly (
    id SERIAL PRIMARY KEY,             -- internal unique ID
    station_id INT NOT NULL REFERENCES stations(wmo),  -- foreign key to stations table
    time TIMESTAMP NOT NULL,           -- timestamp of the measurement
    temp REAL,                         -- temperature in Celsius
    dwpt REAL,                         -- dew point in Celsius
    rhum REAL,                         -- relative humidity (%)
    prcp REAL,                         -- precipitation (mm)
    snow REAL,                         -- snow (mm)
    wdir REAL,                         -- wind direction (degrees)
    wspd REAL,                         -- wind speed (km/h or m/s)
    wpgt REAL,                         -- wind gust (km/h or m/s)
    pres REAL,                         -- atmospheric pressure (hPa)
    tsun REAL,                         -- sunshine duration (hours)
    coco INT                           -- weather condition code or description
);

CREATE TABLE IF NOT EXISTS weather_data_daily (
    id SERIAL PRIMARY KEY,                     -- internal unique ID
    station_id INT NOT NULL REFERENCES stations(wmo),  -- foreign key to stations table
    time DATE NOT NULL,                        -- date of the measurement
    tavg REAL,                                 -- average temperature (°C)
    tmin REAL,                                 -- minimum temperature (°C)
    tmax REAL,                                 -- maximum temperature (°C)
    prcp REAL,                                 -- precipitation (mm)
    snow REAL,                                 -- snow (mm)
    wdir REAL,                                 -- wind direction (degrees)
    wspd REAL,                                 -- wind speed (km/h or m/s)
    wpgt REAL,                                 -- wind gust (km/h or m/s)
    pres REAL,                                 -- atmospheric pressure (hPa)
    tsun REAL                                  -- sunshine duration (hours)
);

CREATE TABLE IF NOT EXISTS weather_live (
    id SERIAL PRIMARY KEY,              -- unique identifier
	station_id INTEGER NOT NULL REFERENCES stations(wmo),  -- foreign key to stations table
    lat DECIMAL(8,5) NOT NULL,          -- latitude
    lon DECIMAL(8,5) NOT NULL,          -- longitude
    timezone VARCHAR(50),               -- e.g. "America/Chicago"
    timezone_offset INT,                -- offset in seconds
    dt TIMESTAMP NOT NULL,              -- UNIX timestamp -> datetime
    sunrise TIMESTAMP,                  -- sunrise
    sunset TIMESTAMP,                   -- sunset
    temp DECIMAL(5,2),                  -- temperature (°C)
    feels_like DECIMAL(5,2),            -- feels like (°C)
    pressure INT,                       -- pressure (hPa)
    humidity INT,                       -- humidity (%)
    dew_point DECIMAL(5,2),             -- dew point (°C)
    uvi DECIMAL(4,2),                   -- UV index
    clouds INT,                         -- cloudiness (%)
    visibility INT,                     -- visibility (m)
    wind_speed DECIMAL(5,2),            -- wind speed (m/s)
    wind_deg INT,                       -- wind direction (°)
    wind_gust DECIMAL(5,2),             -- wind gust (m/s)
    weather_id INT,                     -- OpenWeather "id"
    weather_main VARCHAR(50),           -- short description (e.g. Clouds)
    weather_description VARCHAR(50),    -- full description (e.g. broken clouds)
    weather_icon VARCHAR(10)           -- icon code (e.g. 04d)
);



