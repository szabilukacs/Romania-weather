
DROP TABLE IF EXISTS stations CASCADE;

CREATE TABLE IF NOT EXISTS stations (
    id SERIAL PRIMARY KEY,           -- internal unique ID
    name TEXT NOT NULL,              -- station name
    country CHAR(2) NOT NULL,        -- ISO country code (e.g. HU, RO)
    region TEXT,                     -- region, state, or province
    wmo INTEGER,                     -- WMO station code
    icao CHAR(4),                    -- ICAO station code
    latitude DOUBLE PRECISION,       -- latitude in decimal degrees
    longitude DOUBLE PRECISION,      -- longitude in decimal degrees
    elevation DOUBLE PRECISION,      -- elevation above sea level (meters)
    timezone TEXT NOT NULL,          -- timezone identifier (e.g. Europe/Bucharest)
    hourly_start DATE,               -- first available hourly record
    hourly_end DATE,                 -- last available hourly record
    daily_start DATE,                -- first available daily record
    daily_end DATE,                  -- last available daily record
    monthly_start DATE,              -- first available monthly record
    monthly_end DATE                 -- last available monthly record
);

select * from stations;