import pandas as pd


waypoints = pd.read_csv(
    "../path_planning/path_test.waypoints",
    skiprows=1,
    delim_whitespace=True,
)
waypoints = waypoints.iloc[:, 8:10]
waypoints.columns.values[0] = "lat"
waypoints.columns.values[1] = "lon"
# waypoints = waypoints.rename(columns={waypoints.columns[0]: 'lat', waypoints.columns[1]: 'lon'})
print(waypoints)
