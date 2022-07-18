import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def blankFig():
    fig = go.Figure(go.Scatter(x=[], y=[]))
    fig.update_layout(template="plotly_dark")
    fig.update_xaxes(showgrid=False, showticklabels=False, zeroline=False)
    fig.update_yaxes(showgrid=False, showticklabels=False, zeroline=False)

    return fig


def example_map():
    token = open(".mapbox_token").read()
    us_cities = pd.read_csv(
        "https://raw.githubusercontent.com/plotly/datasets/master/us-cities-top-1k.csv"
    )
    waypoints = pd.read_csv(
        "../path_planning/path_test.waypoints",
        skiprows=1,
        delim_whitespace=True,
    )
    waypoints = waypoints.iloc[:, 8:10]
    waypoints.columns.values[0] = "lat"
    waypoints.columns.values[1] = "lon"
    fig = px.scatter_mapbox(
        waypoints,
        lat="lat",
        lon="lon",
        # hover_name="City",
        # hover_data=["State", "Population"],
        color_discrete_sequence=["fuchsia"],
        zoom=3,
        height=300,
    )
    fig.update_layout(
        # mapbox_style="white-bg",
        mapbox_style="dark",
        mapbox_accesstoken=token,
        mapbox_layers=[
            {
                "below": "traces",
                "sourcetype": "raster",
                "sourceattribution": "United States Geological Survey",
                "source": [
                    "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}"
                ],
            },
            {
                "sourcetype": "raster",
                "sourceattribution": "Government of Canada",
                "source": [
                    """https://geo.weather.gc.ca/geomet/?
                    SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap&BBOX={bbox-epsg-3857}&CRS=EPSG:3857
                    &WIDTH=1000&HEIGHT=1000&LAYERS=RADAR_1KM_RDBR&TILED=true&FORMAT=image/png"""
                ],
            },
        ],
    )
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig
