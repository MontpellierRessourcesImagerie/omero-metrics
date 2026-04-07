import traceback

import dash
import dash_mantine_components as dmc
from dash import html
from django_plotly_dash import DjangoDash
from microscopemetrics import SaturationError
from microscopemetrics_schema import datamodel as mm_schema

import omero_metrics.dash_apps.dash_utils.omero_metrics_components as my_components
from omero_metrics.styles import (
    CONTAINER_STYLE,
    MANTINE_THEME,
    THEME,
)
from omero_metrics.tools import dash_forms_tools as dft
from omero_metrics.views import run_analysis_view

active = 0
min_step = 0
max_step = 2


dashboard_name = "omero_dataset_form"
dash_form_dataset = DjangoDash(
    name=dashboard_name,
    serve_locally=True,
    external_stylesheets=[
        "/static/omero_metrics/css/style_app.css",
    ],
)

dash_form_dataset.layout = dmc.MantineProvider(
    theme=MANTINE_THEME,
    children=[
        # Header Section
        my_components.header_component(
            "Analysis Dashboard",
            "Configure and run your analysis",
            "Analysis Form",
            load_buttons=False,
        ),
        dmc.Container(
            [
                dmc.LoadingOverlay(
                    id="loading-overlay",
                    overlayProps={
                        "radius": "sm",
                        "blur": 1,
                    },
                ),
                # Main content
                dmc.Paper(
                    id="main-content",
                    shadow="xs",
                    p="md",
                    radius="md",
                    children=[
                        # Progress indicator
                        dmc.Progress(
                            id="analysis-progress",
                            value=0,
                            color=THEME["primary"],
                            radius="xl",
                            size="sm",
                            mb="xl",
                        ),
                        # Stepper
                        dmc.Stepper(
                            id="stepper-basic-usage",
                            active=0,
                            color=THEME["primary"],
                            size="sm",
                            iconSize=32,
                            children=[
                                dmc.StepperStep(
                                    id="step_sample",
                                    label="Sample Configuration",
                                    description="Define sample parameters",
                                    icon=my_components.get_icon(
                                        icon="material-symbols:science-outline",
                                    ),
                                    children=[
                                        dmc.Paper(
                                            p="md",
                                            radius="md",
                                            withBorder=True,
                                            children=[
                                                dmc.Text(
                                                    "Sample Configuration",
                                                    size="lg",
                                                    fw=500,
                                                    mb="md",
                                                ),
                                                html.Div(id="sample_container"),
                                            ],
                                        )
                                    ],
                                ),
                                dmc.StepperStep(
                                    id="step_input_data",
                                    label="Data Selection",
                                    description="Choose input images",
                                    icon=my_components.get_icon(
                                        icon="material-symbols:image-search",
                                    ),
                                    children=[
                                        dmc.Paper(
                                            p="md",
                                            radius="md",
                                            withBorder=True,
                                            children=[
                                                dmc.Grid(
                                                    [
                                                        dmc.GridCol(
                                                            [
                                                                dmc.Stack(
                                                                    [
                                                                        dmc.MultiSelect(
                                                                            label="Select Images",
                                                                            placeholder="Choose images to process",
                                                                            id="framework-multi-select",
                                                                            clearable=True,
                                                                            searchable=True,
                                                                            leftSection=my_components.get_icon(
                                                                                icon="material-symbols-light:image",
                                                                            ),
                                                                            styles={
                                                                                "input": {
                                                                                    "borderColor": THEME[
                                                                                        "border"
                                                                                    ]
                                                                                }
                                                                            },
                                                                        ),
                                                                        dmc.Textarea(
                                                                            id="comment",
                                                                            label="Analysis Notes",
                                                                            placeholder="Add analysis comments or notes...",
                                                                            autosize=True,
                                                                            minRows=3,
                                                                            styles={
                                                                                "input": {
                                                                                    "borderColor": THEME[
                                                                                        "border"
                                                                                    ]
                                                                                }
                                                                            },
                                                                        ),
                                                                    ],
                                                                    gap="md",
                                                                ),
                                                            ],
                                                            span=6,
                                                        ),
                                                        dmc.GridCol(
                                                            [
                                                                dmc.Paper(
                                                                    withBorder=True,
                                                                    p="md",
                                                                    radius="md",
                                                                    children=[
                                                                        dmc.Text(
                                                                            "Configuration Preview",
                                                                            fw=500,
                                                                            mb="md",
                                                                        ),
                                                                        html.Div(
                                                                            id="setup-text"
                                                                        ),
                                                                    ],
                                                                ),
                                                            ],
                                                            span=6,
                                                        ),
                                                    ],
                                                ),
                                            ],
                                        ),
                                    ],
                                ),
                                dmc.StepperCompleted(
                                    children=dmc.Paper(
                                        p="md",
                                        radius="md",
                                        withBorder=True,
                                        children=[
                                            dmc.Stack(
                                                [
                                                    dmc.Text(
                                                        "Review Configuration",
                                                        size="lg",
                                                        fw=500,
                                                    ),
                                                    dmc.Grid(
                                                        [
                                                            dmc.GridCol(
                                                                id="sample_col",
                                                                span=4,
                                                            ),
                                                            dmc.GridCol(
                                                                id="config_col",
                                                                span=4,
                                                            ),
                                                            dmc.GridCol(
                                                                id="image_id",
                                                                span=4,
                                                            ),
                                                        ],
                                                    ),
                                                ],
                                                gap="xl",
                                            ),
                                        ],
                                    ),
                                ),
                            ],
                        ),
                        # Navigation buttons
                        dmc.Group(
                            [
                                dmc.Button(
                                    "Back",
                                    id="back-basic-usage",
                                    variant="outline",
                                    leftSection=my_components.get_icon(
                                        icon="material-symbols:arrow-back",
                                    ),
                                    color=THEME["secondary"],
                                ),
                                dmc.Button(
                                    "Next",
                                    id="next-basic-usage",
                                    rightSection=my_components.get_icon(
                                        icon="material-symbols:arrow-forward",
                                    ),
                                    color=THEME["primary"],
                                ),
                            ],
                            justify="space-between",
                            mt="xl",
                        ),
                    ],
                ),
                html.Div(id="analysis-results"),
                html.Div(id="blank"),
            ],
            size="xl",
            p="md",
            style=CONTAINER_STYLE,
        ),
    ],
)


@dash_form_dataset.expanded_callback(
    dash.dependencies.Output("setup-text", "children"),
    [dash.dependencies.Input("blank", "children")],
)
def update_setup(_, **kwargs):
    input_parameters = kwargs["session_state"]["context"]["input_parameters"][
        "input_parameters"
    ]
    input_parameters_object = getattr(mm_schema, input_parameters["type"])
    input_parameters_mm = input_parameters_object(**input_parameters["fields"])

    return dft.get_form(
        input_parameters_mm, disabled=True, form_id="input_parameters_form"
    )


@dash_form_dataset.expanded_callback(
    dash.dependencies.Output("sample_container", "children"),
    [dash.dependencies.Input("blank", "children")],
)
def update_sample(_, **kwargs):
    sample = kwargs["session_state"]["context"]["input_parameters"]["sample"]
    mm_sample = getattr(mm_schema, sample["type"])
    mm_sample = mm_sample(**sample["fields"])

    return dft.get_form(mm_sample, disabled=True, form_id="sample_form")


@dash_form_dataset.expanded_callback(
    dash.dependencies.Output("framework-multi-select", "data"),
    dash.dependencies.Output("framework-multi-select", "value"),
    [dash.dependencies.Input("blank", "children")],
)
def list_images_multi_selector(_, **kwargs):
    list_images = kwargs["session_state"]["context"]["list_images"]
    return list_images, [list_images[i]["value"] for i, _ in enumerate(list_images)]


@dash_form_dataset.expanded_callback(
    dash.dependencies.Output("framework-multi-select", "error"),
    [dash.dependencies.Input("framework-multi-select", "value")],
)
def multi_selector_callback(value, **kwargs):
    return "Select at least 1." if len(value) < 1 else ""


@dash_form_dataset.expanded_callback(
    dash.dependencies.Output("image_id", "children"),
    dash.dependencies.Output("sample_col", "children"),
    dash.dependencies.Output("config_col", "children"),
    [
        dash.dependencies.Input("next-basic-usage", "n_clicks"),
        dash.dependencies.State("sample_form", "children"),
        dash.dependencies.State("framework-multi-select", "value"),
        dash.dependencies.State("input_parameters_form", "children"),
        dash.dependencies.State("stepper-basic-usage", "active"),
    ],
)
def update_review_form(
    _, form_content, multi_selector, input_parameters, current, **kwargs
):

    selectors = dmc.MultiSelect(
        label="Images selected",
        data=[f"Image ID: {i}" for i in multi_selector],
        value=multi_selector,
        clearable=False,
        w="auto",
        disabled=True,
        leftSection=my_components.get_icon(icon="material-symbols-light:image"),
        rightSection=my_components.get_icon(icon="radix-icons:chevron-down"),
    )
    if current == 1:
        return (
            selectors,
            dft.disable_all_fields_dash_form(form_content),
            input_parameters,
        )
    else:
        return dash.no_update


@dash_form_dataset.expanded_callback(
    dash.dependencies.Output("stepper-basic-usage", "active"),
    dash.dependencies.Output("next-basic-usage", "children"),
    dash.dependencies.Output("next-basic-usage", "color"),
    [
        dash.dependencies.Input("back-basic-usage", "n_clicks"),
        dash.dependencies.Input("next-basic-usage", "n_clicks"),
        dash.dependencies.State("framework-multi-select", "value"),
        dash.dependencies.State("stepper-basic-usage", "active"),
        dash.dependencies.State("sample_form", "children"),
    ],
    prevent_initial_call=True,
)
def stepper_callback(*args, **kwargs):
    current = args[3]
    multi_selector = args[2]
    button_id = kwargs["callback_context"].triggered[0]["prop_id"]
    step = current if current is not None else active
    next_text = "Next"
    next_color = THEME["primary"]
    if button_id == "back-basic-usage.n_clicks":
        step = step - 1 if step > min_step else step
    else:
        if step == 0 and not dft.validate_form(args[4]):
            step = 0
        elif step == 1 and len(multi_selector) < 1:
            step = 1
        else:
            if step >= 1:
                next_text = "Run Analysis"
                next_color = THEME["primary"]
            step = step + 1 if step < max_step else step
    return step, next_text, next_color


dash_form_dataset.clientside_callback(
    """
    function updateLoadingState(n_clicks, current) {
        if (current == 2) {
            return true
        } else {
            return false
        }
    }
    """,
    dash.dependencies.Output("loading-overlay", "visible", allow_duplicate=True),
    dash.dependencies.Input("next-basic-usage", "n_clicks"),
    dash.dependencies.State("stepper-basic-usage", "active"),
    prevent_initial_call=True,
)


@dash_form_dataset.expanded_callback(
    dash.dependencies.Output("main-content", "children"),
    dash.dependencies.Output("loading-overlay", "visible"),
    [
        dash.dependencies.Input("next-basic-usage", "n_clicks"),
        dash.dependencies.State("framework-multi-select", "value"),
        dash.dependencies.State("stepper-basic-usage", "active"),
        dash.dependencies.State("comment", "value"),
    ],
    prevent_initial_call=True,
)
def run_analysis(_, list_images, current, comment, **kwargs):
    dataset_id = kwargs["session_state"]["context"]["dataset_id"]
    if current == 2:
        input_parameters = kwargs["session_state"]["context"]["input_parameters"][
            "input_parameters"
        ]
        sample = kwargs["session_state"]["context"]["input_parameters"]["sample"]
        try:
            input_parameters_object = getattr(mm_schema, input_parameters["type"])
            mm_input_parameters = input_parameters_object(
                **input_parameters["fields"]
            )
            sample_object = getattr(mm_schema, sample["type"])
            mm_sample = sample_object(**sample["fields"])

            response_type, response_msg, response_details = run_analysis_view(
                request=kwargs["request"],
                dataset_id=dataset_id,
                mm_sample=mm_sample,
                list_images=list_images,
                mm_input_parameters=mm_input_parameters,
                comment=comment,
            )

            return my_components.alert_handler(
                response_type, response_msg, response_details
            )

        except Exception as e:
            return my_components.alert_handler(
                "unidentified_error", f"{e}", traceback.format_exc()
            )[:1]
    return dash.no_update, False


dash_form_dataset.clientside_callback(
    """
    function updateProgress(active) {
        return active * 50;
    }
    """,
    dash.dependencies.Output("analysis-progress", "value"),
    dash.dependencies.Input("stepper-basic-usage", "active"),
)
