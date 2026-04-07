import dash
import dash_mantine_components as dmc
from dash import dcc, html
from django_plotly_dash import DjangoDash

import omero_metrics.dash_apps.dash_utils.omero_metrics_components as my_components

warning_app = DjangoDash("WarningApp")

warning_app.layout = dmc.MantineProvider(
    [
        my_components.header_component(
            "Omero Metrics Warning",
            "This is a warning message",
            "Feedback",
            load_buttons=False,
        ),
        dmc.Container(
            [
                html.Div(id="input_void"),
                dmc.Alert(
                    title="Warning!",
                    color="yellow",
                    icon=my_components.get_icon(icon="mdi:alert-circle"),
                    id="warning_msg",
                    style={"margin": "10px"},
                ),
            ]
        ),
    ]
)


@warning_app.expanded_callback(
    dash.dependencies.Output("warning_msg", "children"),
    [dash.dependencies.Input("input_void", "value")],
)
def callback_warning(*args, **kwargs):
    message = kwargs["session_state"]["context"]["message"]
    return [message]


error_app = DjangoDash("ErrorApp")

error_app.layout = dmc.MantineProvider(
    [
        my_components.header_component(
            "Omero Metrics Error",
            "An error occurred",
            "Feedback",
            load_buttons=False,
        ),
        dmc.Container(
            [
                html.Div(id="input_void_error"),
                dmc.Alert(
                    title="Error!",
                    color="red",
                    icon=my_components.get_icon(icon="mdi:alert-circle"),
                    id="error_msg",
                    style={"margin": "10px"},
                ),
                dmc.Accordion(
                    children=[
                        dmc.AccordionItem(
                            [
                                dmc.AccordionControl("Error Details"),
                                dmc.AccordionPanel(
                                    dmc.Code(
                                        id="error_traceback",
                                        block=True,
                                        style={
                                            "whiteSpace": "pre-wrap",
                                            "maxHeight": "400px",
                                            "overflow": "auto",
                                        },
                                    )
                                ),
                            ],
                            value="details",
                        )
                    ],
                    style={"margin": "10px"},
                ),
            ]
        ),
    ]
)


@error_app.expanded_callback(
    [
        dash.dependencies.Output("error_msg", "children"),
        dash.dependencies.Output("error_traceback", "children"),
    ],
    [dash.dependencies.Input("input_void_error", "value")],
)
def callback_error(*args, **kwargs):
    context = kwargs["session_state"]["context"]
    message = context.get("message", "An unknown error occurred")
    traceback = context.get("traceback", "No traceback available")
    return [message, traceback]
