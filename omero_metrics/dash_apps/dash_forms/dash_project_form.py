import traceback

import dash
import dash_mantine_components as dmc
from dash import html
from django_plotly_dash import DjangoDash
from microscopemetrics.analyses.mappings import MAPPINGS
from microscopemetrics_schema import datamodel as mm_schema

import omero_metrics.dash_apps.dash_utils.omero_metrics_components as my_components
import omero_metrics.views as views
from omero_metrics.styles import (
    CONTAINER_STYLE,
    MANTINE_THEME,
    THEME,
)
from omero_metrics.tools import dash_forms_tools as dft

# TODO: change the styles import


DATASET_TO_INPUT = {
    "FieldIlluminationDataset": mm_schema.FieldIlluminationInputParameters,
    "PSFBeadsDataset": mm_schema.PSFBeadsInputParameters,
}

sample_types = [x[0] for x in MAPPINGS if x[0]]
sample_types_dp = [
    {
        "label": dft.add_space_between_capitals(x.__name__),
        "value": f"{i}",
        "description": f"Configure analysis for {x.__name__}",  # Added descriptions
    }
    for i, x in enumerate(sample_types)
]


dashboard_name = "omero_project_config_form"
dash_form_project = DjangoDash(
    name=dashboard_name,
    serve_locally=True,
    external_stylesheets=[
        "/static/omero_metrics/css/style_app.css",
    ],
)

dash_form_project.layout = dmc.MantineProvider(
    theme=MANTINE_THEME,
    children=[
        my_components.header_component(
            "Configuration Setup",
            "Configure your sample type and input parameters",
            "Analysis Form",
            load_buttons=False,
        ),
        dmc.Container(
            [
                dmc.Paper(
                    id="main-content",
                    children=[
                        dmc.LoadingOverlay(
                            id="loading-overlay",
                            overlayProps={
                                "radius": "sm",
                                "blur": 1,
                            },
                        ),
                        # Progress Indicator
                        dmc.Progress(
                            id="progress-bar",
                            value=0,
                            color=THEME["primary"],
                            size="sm",
                            mb="md",
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
                                    description="Define your sample parameters",
                                    icon=my_components.get_icon(
                                        icon="mdi:microscope"
                                    ),
                                    children=[
                                        dmc.Paper(
                                            children=[
                                                dmc.Title(
                                                    "Sample Configuration",
                                                    order=3,
                                                ),
                                                dmc.Text(
                                                    "Select your sample type and configure its parameters",
                                                    c="dimmed",
                                                    size="sm",
                                                ),
                                                dmc.Select(
                                                    id="sample_type_selector",
                                                    data=sample_types_dp,
                                                    searchable=True,
                                                    placeholder="Select Sample Type",
                                                    leftSection=my_components.get_icon(
                                                        icon="mdi:database-search"
                                                    ),
                                                    allowDeselect=False,
                                                    size="md",
                                                    mb=10,
                                                    styles={
                                                        "input": {
                                                            "border": f"1px solid {THEME['border']}"
                                                        }
                                                    },
                                                ),
                                                html.Div(id="sample_container"),
                                            ],
                                            p="md",
                                            radius="md",
                                            withBorder=True,
                                        )
                                    ],
                                ),
                                dmc.StepperStep(
                                    id="step_input_data",
                                    label="Analysis Parameters",
                                    description="Set analysis configuration",
                                    icon=my_components.get_icon(
                                        icon="mdi:tune-vertical"
                                    ),
                                    children=[
                                        dmc.Paper(
                                            children=[
                                                dmc.Title(
                                                    "Analysis Parameters",
                                                    order=3,
                                                ),
                                                dmc.Text(
                                                    "Configure the input parameters for your analysis",
                                                    c="dimmed",
                                                    size="sm",
                                                    mb=10,
                                                ),
                                                html.Div(
                                                    id="input_parameters_container"
                                                ),
                                            ],
                                            p="md",
                                            radius="md",
                                            withBorder=True,
                                        )
                                    ],
                                ),
                                dmc.StepperCompleted(
                                    children=[
                                        dmc.Paper(
                                            children=[
                                                dmc.Title(
                                                    "Review Configuration",
                                                    order=3,
                                                ),
                                                dmc.Text(
                                                    "Review your configuration before saving",
                                                    c="dimmed",
                                                    size="sm",
                                                ),
                                                dmc.Grid(
                                                    children=[
                                                        dmc.GridCol(
                                                            dmc.Paper(
                                                                children=[
                                                                    dmc.Title(
                                                                        "Sample Details",
                                                                        order=4,
                                                                    ),
                                                                    html.Div(
                                                                        id="sample_col"
                                                                    ),
                                                                ],
                                                                p="md",
                                                                withBorder=True,
                                                                radius="md",
                                                            ),
                                                            span=6,
                                                        ),
                                                        dmc.GridCol(
                                                            dmc.Paper(
                                                                children=[
                                                                    dmc.Title(
                                                                        "Input Parameters",
                                                                        order=4,
                                                                    ),
                                                                    html.Div(
                                                                        id="input_col"
                                                                    ),
                                                                ],
                                                                p="md",
                                                                withBorder=True,
                                                                radius="md",
                                                            ),
                                                            span=6,
                                                        ),
                                                    ],
                                                    gutter="xl",
                                                ),
                                            ],
                                            p="md",
                                            radius="md",
                                            withBorder=True,
                                        ),
                                    ]
                                ),
                            ],
                        ),
                        dmc.Group(
                            children=[
                                dmc.Button(
                                    "Back",
                                    id="back-basic-usage",
                                    variant="outline",
                                    leftSection=my_components.get_icon(
                                        icon="mdi:arrow-left"
                                    ),
                                ),
                                dmc.Button(
                                    "Next",
                                    id="next-basic-usage",
                                    color=THEME["primary"],
                                    rightSection=my_components.get_icon(
                                        icon="mdi:arrow-right"
                                    ),
                                ),
                            ],
                            justify="space-between",
                            mt="xl",
                        ),
                    ],
                    shadow="xs",
                    p="md",
                    radius="md",
                ),
            ],
            size="xl",
            p="md",
            style=CONTAINER_STYLE,
        ),
    ],
)


@dash_form_project.expanded_callback(
    [
        dash.dependencies.Output("stepper-basic-usage", "active"),
        dash.dependencies.Output("next-basic-usage", "children"),
        dash.dependencies.Output("next-basic-usage", "color"),
        dash.dependencies.Output("progress-bar", "value"),
        dash.dependencies.Output("next-basic-usage", "rightSection"),
    ],
    [
        dash.dependencies.Input("back-basic-usage", "n_clicks"),
        dash.dependencies.Input("next-basic-usage", "n_clicks"),
        dash.dependencies.State("stepper-basic-usage", "active"),
        dash.dependencies.State("sample_content", "children"),
        dash.dependencies.State("input_content", "children"),
    ],
    prevent_initial_call=True,
)
def stepper_callback(*args, **kwargs):
    current = args[2]
    button_id = kwargs["callback_context"].triggered[0]["prop_id"]
    step = current if current is not None else 0

    progress = (step / 2) * 100

    if button_id == "back-basic-usage.n_clicks":
        step = max(0, step - 1)
        next_text = ["Next"]
        next_icon = my_components.get_icon(icon="mdi:arrow-right")
        next_color = THEME["primary"]
    else:
        sample = args[3]
        input_parameters = args[4]

        if step == 0 and not dft.validate_form(sample):
            return dash.no_update, dash.no_update, dash.no_update, progress
        elif step == 1 and not dft.validate_form(input_parameters):
            return dash.no_update, dash.no_update, dash.no_update, progress

        step = min(2, step + 1)

        if step == 2:
            next_text = ["Save Configuration"]
            next_icon = my_components.get_icon(icon="mdi:check")
            next_color = THEME["primary"]
        else:
            next_text = ["Next"]
            next_color = THEME["primary"]
            next_icon = my_components.get_icon(icon="mdi:arrow-right")

    progress = (step / 2) * 100
    return step, next_text, next_color, progress, next_icon


@dash_form_project.expanded_callback(
    dash.dependencies.Output("sample_container", "children"),
    [
        dash.dependencies.Input("sample_type_selector", "value"),
    ],
    prevent_initial_call=True,
)
def update_sample_container(sample_type_selector, **kwargs):
    mm_sample = MAPPINGS[int(sample_type_selector)][0]
    sample_form = dft.get_form(mm_sample, disabled=False, form_id="sample_content")
    return [sample_form]


@dash_form_project.expanded_callback(
    dash.dependencies.Output("input_parameters_container", "children"),
    [
        dash.dependencies.Input("sample_type_selector", "value"),
    ],
    prevent_initial_call=True,
)
def update_input_parameters(sample_type_selector, **kwargs):
    analysis_type = MAPPINGS[int(sample_type_selector)][2].__name__
    mm_input_parameters = DATASET_TO_INPUT[analysis_type]
    mm_input_parameters = dft.get_form(
        mm_input_parameters, disabled=False, form_id="input_content"
    )
    return [mm_input_parameters]


@dash_form_project.expanded_callback(
    dash.dependencies.Output("sample_col", "children"),
    dash.dependencies.Output("input_col", "children"),
    [
        dash.dependencies.Input("next-basic-usage", "n_clicks"),
        dash.dependencies.State("sample_content", "children"),
        dash.dependencies.State("input_content", "children"),
        dash.dependencies.State("stepper-basic-usage", "active"),
    ],
    prevent_initial_call=True,
)
def review_configuration(_, sample_form, input_parameters_form, current, **kwargs):
    sample = dft.disable_all_fields_dash_form(sample_form)
    input_parameters = dft.disable_all_fields_dash_form(input_parameters_form)
    if current == 1:
        return sample, input_parameters
    else:
        return dash.no_update


dash_form_project.clientside_callback(
    """
    function updateLoadingState(n_clicks, current) {
    if (current == 2) {
        return true}
    else {
        return false}
    }
    """,
    dash.dependencies.Output("loading-overlay", "visible", allow_duplicate=True),
    dash.dependencies.Input("next-basic-usage", "n_clicks"),
    dash.dependencies.State("stepper-basic-usage", "active"),
    prevent_initial_call=True,
)


@dash_form_project.expanded_callback(
    dash.dependencies.Output("main-content", "children"),
    dash.dependencies.Output("loading-overlay", "visible"),
    [
        dash.dependencies.Input("next-basic-usage", "n_clicks"),
        dash.dependencies.State("sample_content", "children"),
        dash.dependencies.State("input_content", "children"),
        dash.dependencies.State("stepper-basic-usage", "active"),
        dash.dependencies.State("sample_type_selector", "value"),
    ],
    prevent_initial_call=True,
)
def save_config_dash(
    clicked_data,
    sample_form,
    input_form,
    current,
    sample_type_selector,
    **kwargs,
):
    if not sample_type_selector:  # No sample type selected
        return dash.no_update, False

    analysis_type = MAPPINGS[int(sample_type_selector)][2].__name__
    mm_sample = MAPPINGS[int(sample_type_selector)][0]
    mm_input_parameters = DATASET_TO_INPUT[analysis_type]
    project_id = int(kwargs["session_state"]["context"]["project_id"])
    request = kwargs["request"]
    if clicked_data > 0 and current == 2:
        if dft.validate_form(sample_form) and dft.validate_form(input_form):
            try:
                input_parameters = dft.extract_form_data(input_form)
                mm_input_parameters = mm_input_parameters(**input_parameters)
                sample = dft.extract_form_data(sample_form)
                mm_sample = mm_sample(**sample)
                response_type, response_msg = views.save_config(
                    request=request,
                    project_id=project_id,
                    input_parameters=mm_input_parameters,
                    sample=mm_sample,
                )

                return my_components.alert_handler(response_type, response_msg)
            except Exception as e:
                return my_components.alert_handler(
                    "unidentified_error", str(e), traceback.format_exc()
                )

    return dash.no_update, False
