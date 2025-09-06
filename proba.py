from datetime import datetime
from meteostat import Stations, Daily, Hourly, Monthly
import matplotlib.pyplot as plt
from meteostat import Normals
# Just test

stations = Stations()

stations = stations.region('RO') 

# print('Station:', stations.fetch(40))

start_year = 2023
end_year = 2025
station_id = '15120'

data = Monthly('15120')
data = data.normalize()
data = data.fetch()

# print(f"Year: {year}, Coverage: {coverage}, Count: {count}")
print(data)

for year in range(start_year, end_year + 1):
    start = datetime(year, 1, 1)
    end = datetime(year, 12, 31)
   # data = Daily(station_id, start=start, end=end) # Change to Monthly to check months
   # coverage = data.coverage()
   # count = data.count() 


    