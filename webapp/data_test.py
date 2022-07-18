import random
import pandas as pd


waypoints = pd.read_csv(
    "../path_planning/path_test.waypoints",
    skiprows=1,
    delim_whitespace=True,
)
waypoints = waypoints.iloc[:, 8:10]
waypoints.columns.values[0] = "lat"
waypoints.columns.values[1] = "lon"

num_rows = len(waypoints.index)

fire_flags = [False for i in range(num_rows)]

num_fires = 3
for i in range(num_fires):
    index = random.randrange(num_rows)
    fire_flags[index] = True

waypoints["fire"] = fire_flags

print(waypoints)
