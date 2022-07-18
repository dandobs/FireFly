import dash
import flask
from dash import html, dcc, no_update
import dash_bootstrap_components as dbc

from figure_gen import blankFig, example_map

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
graph_with_loading_animation = dcc.Loading(
    children=[
        dcc.Graph(
            id="main_graph",
            clear_on_unhover=True,
            figure=example_map(),
            loading_state={"is_loading": False},
            style={"height": "70vh"},
        )
    ],
    type="graph",
)
################################################################################
""" Dash UI Layout: """
################################################################################
def serve_layout():
    return dbc.Container(
        [
            horz_line,
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.Row(
                                    children=[
                                        dbc.Row(title),
                                        # dbc.Row(horz_line),
                                        # dbc.Row(file_info),
                                        # dbc.Row(data_info),
                                        dbc.Row(
                                            [
                                                # This component is verbosely placed in layout as it
                                                # requires session_id to be dynamically generated
                                                dbc.Col([]),
                                            ]
                                        ),
                                        dbc.Col(
                                            [
                                                # controls_title,
                                                # dbc.Row(n_neighbors_slider),
                                                # dbc.Row(min_dist_slider),
                                                # horz_line,
                                                # dbc.Row(min_cluster_size_slider),
                                                # dbc.Row(min_samples_slider),
                                            ]
                                        ),
                                        horz_line,
                                        dbc.Row(
                                            # [card_3D_buttons],
                                            # justify="center",
                                            # align="center",
                                        ),
                                    ],
                                    justify="center",
                                    align="center",
                                ),
                            ],
                            body=True,
                            style={"height": "124vh"},
                        ),
                        md=5,
                        align="center",
                    ),
                    dbc.Col(
                        [
                            # 3D Graph and its components
                            dbc.Row(
                                children=[
                                    graph_with_loading_animation,
                                    dcc.Tooltip(
                                        id="main_graph_tooltip", direction="right"
                                    ),
                                    dcc.Download(id="main_graph_download"),
                                ],
                                style={"height": "70vh"},
                            ),
                            horz_line,
                            dbc.Row(
                                [
                                    # 2D Graph and its components
                                    dbc.Col(
                                        # children=[
                                        #     graph_2D,
                                        #     dcc.Tooltip(
                                        #         id="graph_2D_tooltip",
                                        #         direction="right",
                                        #     ),
                                        #     dcc.Download(id="graph_2D_download"),
                                        #     horz_line,
                                        #     # Tabbed card for preview and search here
                                        #     dbc.Row(
                                        #         children=(
                                        #             dbc.Col(
                                        #                 children=[
                                        #                     preview_and_search_card
                                        #                 ],
                                        #                 width="auto",
                                        #                 md=12,
                                        #             ),
                                        #         ),
                                        #         justify="center",
                                        #         align="center",
                                        #     ),
                                        #     horz_line,
                                        #     # content will be rendered in this element
                                        #     html.Div(id="page-content"),
                                        # ],
                                    ),
                                ],
                                style={"height": "50vh"},
                                justify="center",
                                align="start",
                            ),
                        ],
                        md=7,
                    ),
                ],
                justify="center",
                align="center",
            ),
        ],
        fluid=True,
    )


# Dynamically serve layout for each user that connects
dash_app.layout = serve_layout


"""
TODO: 
    - Set default map zoom upon website load to be around ontario/fire coordinates

Callbacks needed:
- coordinates of fires are plotted on the map
- different colored coordinates of the waypoints are plotted on the map
- marker_clicked -> IR and Optical Images are displayed on the left side of the screen
    - Metadata of this fire is displayed in the bottom right of the screen
    - Metadata includes:
        - Date and Time
        - Latitude and Longitude
        - Fire Size
        - Opened/Not Opened
- Dismiss button, when clicked, update metadata, and issue update to DB
- """


########################################################################
""" Run server """
########################################################################
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=80)
