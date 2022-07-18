import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from data_gen import get_coordinates


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
    waypoints, fire_coords = get_coordinates()

    # Plot dataframes of fire and waypoints separately based on the value of the
    # fire flag that has been set in its columns
    fig = px.scatter_mapbox(
        waypoints,
        lat="lat",
        lon="lon",
        hover_name="fire",
        hover_data=["fire"],
        color_discrete_sequence=["fuchsia"],
        zoom=3,
        height=300,
    )

    fig.add_trace(
        go.Scattermapbox(
            lat=fire_coords["lat"],
            lon=fire_coords["lon"],
            mode="markers",
            marker=go.scattermapbox.Marker(
                size=15, color="rgb(255, 0, 0)", opacity=0.7
            ),
            # text=locations_name,
            hoverinfo="text",
        )
    )

    fig.update_layout(
        # mapbox_style="white-bg",
        autosize=True,
        hovermode="closest",
        showlegend=False,
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


def gen_map(fire_coordinates, waypoint_coordinates):
    pass
