select * from stations;

select * from weather_data_hourly;

select * from weather_data_daily where station_id = '15004' and time > '2025-01-01';

select * from weather_data_monthly;

Select min(temp) from weather_data_hourly;