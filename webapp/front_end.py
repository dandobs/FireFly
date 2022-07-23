import io
import os
import base64

import requests
from dash import html
from PIL import Image
import random
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

class app_frontEnd():

    def __init__(self):

        self.data = {}
        self.waypoints = {}
        self.fire_coords = {}
        self.dbUrl = "http://127.0.0.1:5000/getAllImages"

    def refresh_map(self):
        token = open(".mapbox_token").read()
        us_cities = pd.read_csv(
            "https://raw.githubusercontent.com/plotly/datasets/master/us-cities-top-1k.csv"
        )
        self.update_sensor_data()
        print(self.waypoints)

        # Plot dataframes of fire and waypoints separately based on the value of the
        # fire flag that has been set in its columns
        fig = px.scatter_mapbox(
            self.waypoints,
            lat="lat",
            lon="lon",
            hover_name="fire",
            hover_data=["fire"],
            custom_data=["locID"],
            color_discrete_sequence=["fuchsia"],
            zoom=15,
            center=dict(lat=self.waypoints["lat"][0], lon=self.waypoints["lon"][0]),
            height=300,
        )

        # Add fire coordinates to be a different marker
        fig.add_trace(
            go.Scattermapbox(
                lat = self.fire_coords["lat"],
                lon = self.fire_coords["lon"],
                customdata = self.fire_coords["locID"],
                mode="markers",
                marker=go.scattermapbox.Marker(
                    size=15, color="rgb(255, 0, 0)", opacity=0.7
                ),
                # text=locations_name,
                hoverinfo="all",
            )
        )

        fig.update_layout(
            # mapbox_style="white-bg",
            autosize=True,
            hovermode="closest",
            showlegend=False,
            mapbox_style="dark",
            mapbox_accesstoken=token,
        )
        fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
        return fig


    # Connect to database and get latest sensor data
    def update_sensor_data(self):
        # Connect to db and get curr data
        res = requests.get(self.dbUrl)
        allimgs = res.json()["Data"]
        df = pd.DataFrame.from_dict(allimgs)
        df['fire'] = np.where(df['size'] > -1, True, False)
        coords = df.iloc[:, [0,5,6,8]]
        self.fire_coords = coords[coords["fire"] == True]
        self.waypoints = coords

        for curr_img in allimgs:
            curr_id = curr_img['locID']
            del curr_img['locID']
            self.data[curr_id] = curr_img         
    
    def get_point_data(self, locID) -> str:
        """genImgURI Open image file at provided path with PIL and encode to
        img_uri string.

        Args:
            image_path (str): Path to image file.

        Returns:
            img_uri (str): str containing image bytes viewable by html.Img
        """
        camera_data = self.data[locID]['rgbImagePath']
        ir_data = self.data[locID]['irImagePath']
        size = self.data[locID]['size']
        lat = self.data[locID]['lat']
        lon = self.data[locID]['lon']
        date_time = self.data[locID]['date_time']

        metadata_string = f"Metadata: Lat:{lat}, Lon:{lon}, Size of fire:{size}, Date & Time of Image: {date_time}"

        ir_bytes = base64.b64decode(ir_data)
        camera_bytes = base64.b64decode(camera_data.encode("utf8"))

        ir_url = f"data:image/png;base64,{bytearray(ir_bytes)}"
        camera_url = f"data:image/png;base64, {bytearray(camera_bytes)}"

        return camera_url, ir_url, metadata_string
        

    def empty_contained_img(self, id: str):
        component = html.Div(
            [
                html.Img(
                    id=id,
                    style={
                        "width": "100%",
                        "height": "100%",
                        "min-height": "30vh",
                        "max-height": "30vh",
                        "object-fit": "contain",
                    },
                )
            ]
        )
        return component
    
    