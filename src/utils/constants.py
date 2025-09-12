# Weather condition mapping
COCO_CODES = {
    1: "Clear",
    2: "Fair",
    3: "Cloudy",
    4: "Overcast",
    5: "Fog",
    6: "Freezing Fog",
    7: "Light Rain",
    8: "Rain",
    9: "Heavy Rain",
    10: "Freezing Rain",
    11: "Heavy Freezing Rain",
    12: "Sleet",
    13: "Heavy Sleet",
    14: "Light Snowfall",
    15: "Snowfall",
    16: "Heavy Snowfall",
    17: "Rain Shower",
    18: "Heavy Rain Shower",
    19: "Sleet Shower",
    20: "Heavy Sleet Shower",
    21: "Snow Shower",
    22: "Heavy Snow Shower",
    23: "Lightning",
    24: "Hail",
    25: "Thunderstorm",
    26: "Heavy Thunderstorm",
    27: "Storm",
}

DAILY_DAYS_SHIFT = 14
BLUE = "#1f77b4"
ORANGE = "#ff7f0e"

ROMANIA_LAT = 45.9432
ROMANIA_LONG = 24.9668
MAP_ZOOM = 5.5

COLS_HOURLY = [
    "station_id",
    "time",
    "temp",
    "dwpt",
    "rhum",
    "prcp",
    "snow",
    "wdir",
    "wspd",
    "wpgt",
    "pres",
    "tsun",
    "coco",
]
COLS_DAILY = [
    "station_id",
    "time",
    "tavg",
    "tmin",
    "tmax",
    "prcp",
    "snow",
    "wdir",
    "wspd",
    "wpgt",
    "pres",
    "tsun",
]

NR_OF_RETRIES = 3
DELAY_TIME_S = 5

# test
REGIONS = ["HA"]

# Transylvani region
# TODO: felosztani 2 percre majd DAG-ban limit miatt
# REGIONS = ['HA', 'SM','MA','BH','SJ','CJ','BN','MU','AD','SI','HU','CV','BS']
