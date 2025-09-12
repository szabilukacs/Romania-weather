select * from stations where name = 'Buzau';

select * from stations;

select * from weather_data_hourly;

select * from weather_data_hourly where time > '2010-06-15' and snow > 1;

select * from weather_data_daily where station_id = '15004' and time > '2005-01-01';

select * from weather_data_daily;

Select min(temp) from weather_data_hourly;

SELECT time, temp, dwpt, rhum, prcp, coco
FROM weather_data_hourly
WHERE station_id = 15004
  AND DATE(time) >= '1999-01-08'
ORDER BY time ASC;

CREATE TABLE weather_live (
    id SERIAL PRIMARY KEY,              -- egyedi azonosító
	station_id INTEGER NOT NULL REFERENCES stations(wmo),  -- foreign key to stations table
    lat DECIMAL(8,5) NOT NULL,          -- szélesség
    lon DECIMAL(8,5) NOT NULL,          -- hosszúság
    timezone VARCHAR(50),               -- pl. "America/Chicago"
    timezone_offset INT,                -- offset másodpercben
    dt TIMESTAMP NOT NULL,              -- UNIX timestamp -> datetime
    sunrise TIMESTAMP,                  -- napkelte
    sunset TIMESTAMP,                   -- napnyugta
    temp DECIMAL(5,2),                  -- hőmérséklet (°C)
    feels_like DECIMAL(5,2),            -- hőérzet (°C)
    pressure INT,                       -- légnyomás (hPa)
    humidity INT,                       -- páratartalom (%)
    dew_point DECIMAL(5,2),             -- harmatpont (°C)
    uvi DECIMAL(4,2),                   -- UV index
    clouds INT,                         -- felhőzet (%)
    visibility INT,                     -- látótávolság (m)
    wind_speed DECIMAL(5,2),            -- szélsebesség (m/s)
    wind_deg INT,                       -- szélirány (°)
    wind_gust DECIMAL(5,2),             -- széllökés (m/s)
    weather_id INT,                     -- OpenWeather "id"
    weather_main VARCHAR(50),           -- rövid (pl. Clouds)
    weather_description VARCHAR(100),   -- leírás (pl. broken clouds)
    weather_icon VARCHAR(10),           -- ikon kód (pl. 04d)
    created_at TIMESTAMP DEFAULT NOW()  -- mikor írtuk DB-be
);

select * from weather_live;
