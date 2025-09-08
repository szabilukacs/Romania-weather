select * from stations;

select * from weather_data_hourly where time > '2010-06-15' and station_id = '15014' and tsun is not null;

select * from weather_data_daily where station_id = '15004' and time > '2005-01-01';

select * from weather_data_monthly;

Select min(temp) from weather_data_hourly;

SELECT time, temp, dwpt, rhum, prcp, coco
FROM weather_data_hourly
WHERE station_id = 15004
  AND DATE(time) >= '1999-01-08'
ORDER BY time ASC;