import dash
import flask
from dash import html, dcc, no_update
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

from figure_gen import blankFig, example_map
from component_builder import gen_img_uri, empty_contained_img

################################################################################
""" Initialize Flask Server and Dash App: """
################################################################################

app = flask.Flask(__name__)


# Define dash app
dash_app = dash.Dash(
    __name__,
    server=app,
    external_stylesheets=[dbc.themes.CYBORG],
)

################################################################################
""" Dash Components: """
################################################################################

horz_line = html.Hr()

titles_color = "#acdcf2"

# title of the dash
title = dbc.Card(
    [
        html.H5(
            "FireFly Dashboard",
            style={
                "color": titles_color,
                "text-align": "center",
                "padding": "15px",
            },
        )
    ]
)

# Map
graph_with_loading_animation = dcc.Graph(
    id="main_map",
    clear_on_unhover=True,
    figure=example_map(),
    loading_state={"is_loading": False},
    style={"height": "70vh"},
)

optical_preview = empty_contained_img(id="optical_preview")
ir_preview = empty_contained_img(id="ir_preview")


################################################################################
""" Dash UI Layout: """
################################################################################
def serve_layout():
    return dbc.Container(
        [
            # horz_line,
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.Row(
                                    children=[
                                        title,
                                    ],
                                    justify="center",
                                    align="center",
                                ),
                                dbc.Row(
                                    [optical_preview],
                                    justify="center",
                                    align="center",
                                ),
                                dbc.Row(
                                    [ir_preview],
                                    justify="center",
                                    align="center",
                                ),
                            ],
                            body=True,
                            style={"height": "70vh"},
                        ),
                        md=5,
                        align="start",
                        style={"padding-top": "1vh"},
                    ),
                    dbc.Col(
                        [
                            # 3D Graph and its components
                            dbc.Row(
                                children=[
                                    graph_with_loading_animation,
                                ],
                                style={"height": "70vh"},
                            ),
                            # horz_line,
                        ],
                        md=7,
                        style={"padding-top": "1vh"},
                    ),
                ],
                justify="center",
                align="start",
            ),
            dbc.Row(
                dbc.Card(
                    [
                        dbc.Row(
                            children=[
                                "Metadata",
                            ],
                            justify="left",
                            align="center",
                        ),
                    ],
                    body=True,
                ),
                style={"height": "29vh", "padding": "1vh"},
            ),
        ],
        fluid=True,
    )


# Dynamically serve layout for each user that connects
dash_app.layout = serve_layout


"""
TODO: 
    - Generate testing coordinates for fires/waypoints + paths to fire dataset
        - Select random points on map closeby and write them down
    - Set default map zoom upon website load to be around ontario/fire coordinates
    - add refresh button

Current bugs:

############### Callbacks needed (based on chronolgical flow) ###############:
[DB QUERYING]:
    - Upon website load the DB is queried for:
        - Fire coordinates + metadata
        - Waypoint coordinates
        
[MAPPING]:    
    - Coordinates of fires are plotted on the map
    - Different colored coordinates of the waypoints are plotted on the map
    
[INTERACTIVE MAP]:
    - Fire Marker or Waypoint Marker Clicked
    [PREVIEW]:
        [DB QUERYING]:
        -> Images and Metadata of the clicked fire are queried from the DB
        -> IR and Optical Images are displayed on the left side of the screen
        -> Metadata of this fire is displayed in the bottom right of the screen
        -> Metadata includes:
            - Date and Time
            - Latitude and Longitude
            - Fire Size
            - Opened/Not Opened

    -> If marker is for a fire: 
        - Show dismiss button (if not already dismissed)
        - When clicked
        - Issue command to DB for updating metadata of the fire coordinate to be dismissed
- """

########################################################################
""" [CALLBACK]: Click To Preview Fire: """
########################################################################
@dash_app.callback(
    Output("optical_preview", "src"),
    Input("main_map", "clickData"),
    prevent_initial_call=True,
)
def func(clickData):
    # print("hi")
    if clickData:
        clicked_point = clickData["points"][0]
        # clickData format depends on which trace it came from
        if type(clicked_point["customdata"]) == list:
            clicked_point_customdata = clicked_point["customdata"][0]
        else:
            clicked_point_customdata = clicked_point["customdata"]
        path_idx = (clicked_point_customdata % 10) + 1
        print(f"Index: {clicked_point_customdata}")
        # generate Optical file path using clicked point index and uri
        optical_img_path = f"../data/match_data/picture{path_idx}.png"
        optical_img_uri = gen_img_uri(clicked_point_customdata, optical_img_path)
        # generate IR file path using clicked point index and uri
        ir_img_path = f"../data/match_data/data{path_idx}.csv"

        return optical_img_uri
    else:
        return no_update


########################################################################
""" Run server """
########################################################################
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=80)
