import random
import pandas as pd


def get_coordinates():
    coords = pd.read_csv(
        "../path_planning/path_test.waypoints",
        skiprows=1,
        delim_whitespace=True,
    )
    coords = coords.iloc[:, 8:10]
    coords.columns.values[0] = "lat"
    coords.columns.values[1] = "lon"
    # add a column for fire/not fire
    num_rows = len(coords.index)

    fire_flags = [False for i in range(num_rows)]

    num_fires = 3
    for i in range(num_fires):
        index = random.randrange(num_rows)
        fire_flags[index] = True

    coords["fire"] = fire_flags

    fire_coords = coords[coords["fire"] == True]
    waypoints = coords[coords["fire"] == False]

    return waypoints, fire_coords
