import math
from datetime import datetime

import dash
import dash_mantine_components as dmc
import pandas as pd
from dash import html
from django_plotly_dash import DjangoDash
from linkml_runtime.dumpers import JSONDumper, YAMLDumper
from microscopemetrics_schema import datamodel as mm_schema

import omero_metrics.dash_apps.dash_utils.omero_metrics_components as my_components
from omero_metrics import views
from omero_metrics.styles import (
    BUTTON_STYLE,
    CARD_STYLE_ELEVATED,
    COLORS_CHANNELS,
    CONTAINER_STYLE,
    DATEPICKER_STYLES,
    MANTINE_THEME,
    SELECT_STYLES,
    TAB_ITEM_STYLE,
    TAB_STYLES,
    TABLE_MANTINE_STYLE,
    THEME,
)
from omero_metrics.tools import dash_forms_tools as dft
from omero_metrics.tools.serializers import deserialize

# Initialize the Dash app
dashboard_name = "omero_project_dash"
omero_project_dash = DjangoDash(
    name=dashboard_name,
    serve_locally=True,
)


# Define the layout
omero_project_dash.layout = dmc.MantineProvider(
    theme=MANTINE_THEME,
    children=[
        dmc.NotificationProvider(position="top-center"),
        html.Div(id="delete-notifications-container"),
        dmc.Modal(
            title="Confirm Delete",
            id="delete-confirm_delete",
            children=[
                dmc.Text("Are you sure you want to delete this project outputs?"),
                dmc.Space(h=20),
                dmc.Group(
                    [
                        dmc.Button(
                            "Submit",
                            id="delete-modal-submit-button",
                            color="red",
                        ),
                        dmc.Button(
                            "Close",
                            color="gray",
                            variant="outline",
                            id="delete-modal-close-button",
                        ),
                    ],
                    justify="flex-end",
                ),
            ],
        ),
        html.Div(id="blank-input"),
        html.Div(id="save_config_result"),
        my_components.header_component(
            "Project Dashboard",
            "Microscopy Image Analysis Dashboard",
            "Project Analysis",
        ),
        dmc.Tabs(
            value="dashboard",
            styles=TAB_STYLES,
            children=[
                dmc.TabsList(
                    children=[
                        dmc.TabsTab(
                            "Dashboard",
                            value="dashboard",
                            leftSection=my_components.get_icon(
                                icon="ph:chart-line-bold"
                            ),
                            color=THEME["primary"],
                            style=TAB_ITEM_STYLE,
                        ),
                        dmc.TabsTab(
                            "Settings",
                            value="settings",
                            leftSection=my_components.get_icon(icon="ph:gear-bold"),
                            color=THEME["primary"],
                            style=TAB_ITEM_STYLE,
                        ),
                        dmc.TabsTab(
                            "Thresholds",
                            value="thresholds",
                            leftSection=my_components.get_icon(icon="ph:ruler-bold"),
                            color=THEME["primary"],
                            style=TAB_ITEM_STYLE,
                        ),
                    ],
                    grow=True,
                    justify="space-around",
                    variant="light",
                    style={"backgroundColor": THEME["surface"]},
                ),
                # Dashboard Panel
                dmc.TabsPanel(
                    value="dashboard",
                    children=dmc.Container(
                        children=[
                            # Chart Section
                            dmc.Paper(
                                style={**CARD_STYLE_ELEVATED, "marginTop": "12px"},
                                children=[
                                    dmc.Title(
                                        "Measurement Trends",
                                        order=3,
                                        style={
                                            "marginBottom": "12px",
                                        },
                                    ),
                                    dmc.Grid(
                                        children=[
                                            dmc.GridCol(
                                                span=6,
                                                children=[
                                                    dmc.Select(
                                                        id="key-measurement-dropdown",
                                                        label="Select Measurement",
                                                        placeholder="Choose a measurement",
                                                        leftSection=my_components.get_icon(
                                                            icon="ph:magnifying-glass"
                                                        ),
                                                        disabled=True,
                                                        rightSection=my_components.get_icon(
                                                            icon="ph:caret-down"
                                                        ),
                                                        allowDeselect=False,
                                                        styles=SELECT_STYLES,
                                                    ),
                                                ],
                                            ),
                                            dmc.GridCol(
                                                span=6,
                                                children=[
                                                    dmc.DatePickerInput(
                                                        id="date-picker",
                                                        label="Date Range",
                                                        type="range",
                                                        valueFormat="DD-MM-YYYY",
                                                        placeholder="Select date range",
                                                        leftSection=my_components.get_icon(
                                                            icon="ph:calendar"
                                                        ),
                                                        miw=150,
                                                        disabled=True,
                                                        styles=DATEPICKER_STYLES,
                                                    ),
                                                ],
                                            ),
                                        ],
                                        align="flex-end",
                                        style={
                                            "marginBottom": "12px",
                                        },
                                    ),
                                    html.Div(
                                        id="graph-project",
                                        style={"height": "250px"},
                                        children=[
                                            dmc.LineChart(
                                                id="line-chart",
                                                h=300,
                                                data=[],
                                                dataKey="date",
                                                withLegend=True,
                                                legendProps={
                                                    "horizontalAlign": "top",
                                                    "left": 50,
                                                },
                                                series=[],
                                                curveType="linear",
                                                style={"padding": 20},
                                                xAxisLabel="Acquisition Date",
                                                connectNulls=True,
                                            ),
                                            html.Div(id="feedback_message"),
                                        ],
                                    ),
                                ],
                            ),
                            # Data Table Section
                            dmc.Paper(
                                id="clicked_data_paper",
                                hiddenFrom={"visible": False, "display": None},
                                style={**CARD_STYLE_ELEVATED, "marginTop": "12px"},
                                children=[
                                    dmc.Text(
                                        id="text_km",
                                        c=THEME["primary"],
                                        mt=10,
                                        ml=10,
                                        mr=10,
                                        fw="bold",
                                    ),
                                    dmc.ScrollArea(
                                        [
                                            dmc.Table(
                                                id="kkm_table",
                                                striped=True,
                                                data={},  # data will be updated by the callback
                                                highlightOnHover=True,
                                                style=TABLE_MANTINE_STYLE,
                                            ),
                                            dmc.Group(
                                                mt="md",
                                                children=[
                                                    dmc.Pagination(
                                                        id="pagination",
                                                        total=0,
                                                        value=1,
                                                        withEdges=True,
                                                    )
                                                ],
                                                justify="center",
                                            ),
                                        ]
                                    ),
                                ],
                            ),
                        ],
                        fluid=True,
                        style=CONTAINER_STYLE,
                    ),
                ),
                # Settings Panel
                dmc.TabsPanel(
                    value="settings",
                    children=dmc.Container(
                        children=[
                            dmc.LoadingOverlay(
                                id="loading-overlay",
                                overlayProps={
                                    "radius": "sm",
                                    "blur": 1,
                                },
                            ),
                            dmc.Paper(
                                style={**CARD_STYLE_ELEVATED, "marginTop": "12px"},
                                children=[
                                    dmc.Grid(
                                        children=[
                                            dmc.GridCol(
                                                id="input_parameters_container",
                                                span="6",
                                            ),
                                            dmc.GridCol(
                                                id="sample_container",
                                                span="6",
                                            ),
                                        ],
                                        justify="space-between",
                                    ),
                                    dmc.Group(
                                        justify="flex-end",
                                        mt="xl",
                                        children=[
                                            dmc.Button(
                                                "Update",
                                                id="submit_config",
                                                style=BUTTON_STYLE,
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                        fluid=True,
                        style=CONTAINER_STYLE,
                    ),
                ),
                # Thresholds Panel
                dmc.TabsPanel(
                    value="thresholds",
                    children=dmc.Container(
                        children=[
                            dmc.LoadingOverlay(
                                id="loading-overlay-threshold",
                                overlayProps={
                                    "radius": "sm",
                                    "blur": 1,
                                },
                            ),
                            dmc.Paper(
                                style={**CARD_STYLE_ELEVATED, "marginTop": "12px"},
                                children=[
                                    dmc.Accordion(
                                        id="accordion-compose-controls",
                                        chevron=my_components.get_icon(
                                            icon="ant-design:plus-outlined"
                                        ),
                                        disableChevronRotation=True,
                                        children=[],
                                    ),
                                    dmc.Group(
                                        justify="flex-end",
                                        mt="xl",
                                        id="thresholds-button-container",
                                        children=[],
                                    ),
                                    html.Div(id="notifications-container"),
                                ],
                            ),
                        ],
                        fluid=True,
                        style=CONTAINER_STYLE,
                    ),
                ),
            ],
        ),
    ],
)


@omero_project_dash.expanded_callback(
    dash.dependencies.Output("key-measurement-dropdown", "data"),
    dash.dependencies.Output("key-measurement-dropdown", "value"),
    dash.dependencies.Output("date-picker", "minDate"),
    dash.dependencies.Output("date-picker", "maxDate"),
    dash.dependencies.Output("date-picker", "value"),
    dash.dependencies.Output("date-picker", "disabled"),
    dash.dependencies.Output("key-measurement-dropdown", "disabled"),
    dash.dependencies.Output("activate_download", "disabled"),
    dash.dependencies.Output("delete_data", "disabled"),
    [dash.dependencies.Input("blank-input", "children")],
)
def update_dropdown(*args, **kwargs):
    try:
        context = kwargs["session_state"]["context"]
        kkm = context["kkm"]
        kkm = [k.replace("_", " ").title() for k in kkm]

        # Parse datetime strings and get min/max
        datetimes = context["dates"]
        min_date = context["min_date"]
        max_date = context["max_date"]

        kkm_options = [{"value": f"{i}", "label": f"{k}"} for i, k in enumerate(kkm)]
        value_date = [min_date, max_date]
        return (
            kkm_options,
            "0",
            min_date,
            max_date,
            value_date,
            False,
            False,
            False,
            False,
        )
    except Exception as e:
        return (
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
            True,
            True,
            True,
            True,
        )


@omero_project_dash.expanded_callback(
    dash.dependencies.Output("graph-project", "children"),
    [dash.dependencies.Input("blank-input", "children")],
)
def check_data(*args, **kwargs):
    try:
        data = kwargs["session_state"]["context"]["key_measurements_by_kkm"]
        # FIXME: This expression is odd in any case this returns no update
        if not data:
            return dash.no_update
        return dash.no_update
    except Exception as e:
        return [
            my_components.empty_state(
                icon="material-symbols:bar-chart-off",
                title="No data available for this project",
            )
        ]


@omero_project_dash.expanded_callback(
    dash.dependencies.Output("line-chart", "data"),
    dash.dependencies.Output("line-chart", "series"),
    dash.dependencies.Output("line-chart", "referenceLines"),
    [
        dash.dependencies.Input("key-measurement-dropdown", "value"),
        dash.dependencies.Input("date-picker", "value"),
    ],
    prevent_initial_call=True,
)
def update_table(measurement, dates_range, **kwargs):
    try:
        context = kwargs["session_state"]["context"]
        key_measurements_by_kkm = context["key_measurements_by_kkm"]
        threshold = context["thresholds"]
        kkm = context["kkm"]
        measurement = int(measurement)

        # Check if we have any data
        if not key_measurements_by_kkm:
            return dash.no_update
        if threshold:
            threshold_kkm = threshold[kkm[measurement]]
            ref = [
                {
                    "y": v,
                    "label": k.replace("_", " ").title(),
                    "color": "red.6" if k == "upper_limit" else "yellow.6",
                }
                for k, v in threshold_kkm.items()
                if v
            ]
        else:
            ref = []

        start_date = datetime.fromisoformat(dates_range[0].split("T")[0]).date()
        end_date = datetime.fromisoformat(dates_range[1].split("T")[0]).date()

        data = key_measurements_by_kkm[kkm[measurement]]
        channels = context["channels"]
        series = [
            {
                "name": channel,
                "color": COLORS_CHANNELS[i % len(COLORS_CHANNELS)],
            }
            for i, channel in enumerate(channels)
        ]
        return data, series, ref

    except Exception as e:
        return dash.no_update


@omero_project_dash.expanded_callback(
    dash.dependencies.Output("text_km", "children"),
    dash.dependencies.Output("kkm_table", "data"),
    dash.dependencies.Output("pagination", "total"),
    dash.dependencies.Output("clicked_data_paper", "hiddenFrom"),
    [
        dash.dependencies.Input("line-chart", "clickData"),
        dash.dependencies.Input("pagination", "value"),
    ],
)
def update_project_view(clicked_data, page, **kwargs):
    try:
        if clicked_data:
            context = kwargs["session_state"]["context"]
            key_measurements_by_dataset_id = context[
                "key_measurements_by_dataset_id"
            ]
            data = key_measurements_by_dataset_id[str(clicked_data["dataset_id"])]
            total = 1
            page_data = {
                "caption": data["caption"],
                "head": data["head"],
                "body": data["body"],
            }
            return (
                data["caption"],
                page_data,
                total,
                {"visible": True},
            )

        else:
            return dash.no_update
    except Exception as e:
        return dash.no_update


@omero_project_dash.expanded_callback(
    dash.dependencies.Output("input_parameters_container", "children"),
    dash.dependencies.Output("sample_container", "children"),
    [dash.dependencies.Input("blank-input", "children")],
)
def update_modal(*args, **kwargs):
    context = kwargs["session_state"]["context"]
    input_parameters = context.get("input_parameters")
    sample = context.get("sample")

    if input_parameters:
        mm_input_parameters = getattr(mm_schema, input_parameters["type"])
        mm_input_parameters = mm_input_parameters(**input_parameters["fields"])
        input_parameters_form = dft.get_form(
            mm_input_parameters, disabled=False, form_id="input_parameters_form"
        )
    else:
        input_parameters_form = dmc.Text(
            "No input parameters configured", c="dimmed"
        )

    if sample:
        mm_sample = getattr(mm_schema, sample["type"])
        mm_sample = mm_sample(**sample["fields"])
        sample_form = dft.get_form(mm_sample, disabled=False, form_id="sample_form")
    else:
        sample_form = dmc.Text("No sample configured", c="dimmed")

    return (
        input_parameters_form,
        sample_form,
    )


omero_project_dash.clientside_callback(
    """
    function updateLoadingState(n_clicks) {
        if (n_clicks > 0 ) {
            return true;
        }
        return false;
    }


    """,
    dash.dependencies.Output("loading-overlay", "visible", allow_duplicate=True),
    dash.dependencies.Input("submit_config", "n_clicks"),
    prevent_initial_call=True,
)
omero_project_dash.clientside_callback(
    """
    function updateLoadingThresholdState(n_clicks) {
        if (n_clicks > 0) {
            return true;
        }
        return false;
    }


    """,
    dash.dependencies.Output(
        "loading-overlay-threshold", "visible", allow_duplicate=True
    ),
    dash.dependencies.Input("modal-submit-button", "n_clicks"),
    prevent_initial_call=True,
)


@omero_project_dash.expanded_callback(
    dash.dependencies.Output("save_config_result", "children"),
    dash.dependencies.Output("loading-overlay", "visible"),
    [
        dash.dependencies.Input("submit_config", "n_clicks"),
        dash.dependencies.State("sample_form", "children"),
        dash.dependencies.State("input_parameters_form", "children"),
    ],
    prevent_initial_call=True,
)
def update_config_project(submit_click, sample_form, input_form, **kwargs):
    context = kwargs["session_state"]["context"]
    project_id = int(context["project_id"])
    request = kwargs["request"]
    sample = context.get("sample")
    mm_sample_cls = getattr(mm_schema, sample["type"]) if sample else None
    input_parameters = context.get("input_parameters")
    mm_input_parameters_cls = (
        getattr(mm_schema, input_parameters["type"]) if input_parameters else None
    )
    if dft.validate_form(input_form) and (
        sample_form is None or dft.validate_form(sample_form)
    ):
        try:
            input_parameters_data = dft.extract_form_data(input_form)
            mm_input_parameters = mm_input_parameters_cls(**input_parameters_data)
            if sample_form and mm_sample_cls:
                sample_data = dft.extract_form_data(sample_form)
                mm_sample = mm_sample_cls(**sample_data)
            else:
                mm_sample = None
            response_type, response_msg = views.save_config(
                request=request,
                project_id=project_id,
                input_parameters=mm_input_parameters,
                sample=mm_sample,
            )

            return my_components.alert_handler(
                response_type,
                response_msg,
                with_close_button=True,
                duration=3000,
            )
        except Exception as e:
            return my_components.alert_handler(
                "unidentified error",
                str(e),
                response_details=traceback.format_exc(),
                with_close_button=True,
                duration=3000,
            )
    else:
        return my_components.alert_handler(
            "unidentified error",  # TODO: Make datatype error
            "Please fill in all fields",
            response_details=f"Sample form valid: {dft.validate_form(sample_form)}\n"
            f"Input parameter form valid: {dft.validate_form(input_form)}",
            with_close_button=True,
            duration=3000,
        )


@omero_project_dash.expanded_callback(
    dash.dependencies.Output("thresholds-dropdown", "data"),
    [dash.dependencies.Input("blank-input", "children")],
)
def update_thresholds(*args, **kwargs):
    try:
        kkm = kwargs["session_state"]["context"]["kkm"]
        # TODO: Move to kkm titles if and once implemented
        kkm = [k.replace("_", " ").title() for k in kkm]
        data = [{"value": f"{i}", "label": f"{k}"} for i, k in enumerate(kkm)]
        return data
    except Exception as e:
        return dash.no_update


@omero_project_dash.expanded_callback(
    dash.dependencies.Output({"index": dash.dependencies.MATCH}, "variant"),
    dash.dependencies.Input({"index": dash.dependencies.MATCH}, "n_clicks"),
)
def update_heart(n, **kwargs):
    if n % 2 == 0:
        return "default"
    return "filled"


@omero_project_dash.expanded_callback(
    dash.dependencies.Output("accordion-compose-controls", "children"),
    dash.dependencies.Output("thresholds-button-container", "children"),
    [dash.dependencies.Input("blank-input", "children")],
)
def update_thresholds_controls(*args, **kwargs):
    try:
        context = kwargs["session_state"]["context"]
        kkm = context["kkm"]
        threshold = context["thresholds"]
        if threshold:
            new_kkm = threshold
        else:
            new_kkm = {k: {"upper_limit": "", "lower_limit": ""} for k in kkm}

        threshold_control = [
            dmc.AccordionItem(
                [
                    my_components.make_control(
                        key.replace("_", " ").title(),
                        f"action-{i}",
                    ),
                    dmc.AccordionPanel(
                        id=key + "_panel",
                        children=[
                            dmc.Fieldset(
                                id=key + "_fieldset",
                                children=[
                                    dmc.NumberInput(
                                        label="Upper Limit",
                                        placeholder="Enter upper limit",
                                        leftSection=my_components.get_icon(
                                            icon="hugeicons:chart-maximum",
                                            color=THEME["primary"],
                                        ),
                                        value=value.get("upper_limit", ""),
                                    ),
                                    dmc.NumberInput(
                                        label="Lower Limit",
                                        placeholder="Enter lower limit",
                                        leftSection=my_components.get_icon(
                                            icon="hugeicons:chart-minimum",
                                            color=THEME["primary"],
                                        ),
                                        value=value.get("lower_limit", ""),
                                    ),
                                ],
                                variant="filled",
                                radius="md",
                                style={"padding": "10px", "margin": "10px"},
                            )
                        ],
                    ),
                ],
                value=f"item-{i}",
            )
            for i, (key, value) in enumerate(new_kkm.items())
        ]
        button = dmc.Button(
            "Update",
            id="modal-submit-button",
            style=BUTTON_STYLE,
        )
        return threshold_control, button
    except Exception as e:
        return dash.no_update


@omero_project_dash.expanded_callback(
    dash.dependencies.Output("notifications-container", "children"),
    dash.dependencies.Output("loading-overlay-threshold", "visible"),
    [
        dash.dependencies.Input("modal-submit-button", "n_clicks"),
        dash.dependencies.State("accordion-compose-controls", "children"),
    ],
    prevent_initial_call=True,
)
def threshold_callback1(*args, **kwargs):
    try:
        context = kwargs["session_state"]["context"]
        kkm = context["kkm"]
        output = get_accordion_data(args[1], kkm)
        request = kwargs["request"]
        project_id = int(context["project_id"])
        if output and args[0]:
            response_type, response_msg = views.save_threshold(
                request=request,
                project_id=project_id,
                threshold=output,
            )

            return my_components.notification_handler(
                response_type, response_msg, None
            )[1:]
        else:
            return dash.no_update, False
    except Exception as e:
        return dash.no_update


def get_accordion_data(accordion_state, kkm):
    dict_data = {}
    try:
        for i in accordion_state:
            index = i["props"]["children"][1]["props"]["children"][0]["props"][
                "children"
            ]
            key = (
                i["props"]["children"][0]["props"]["children"][0]["props"][
                    "children"
                ]
                .replace(" ", "_")
                .lower()
            )
            dict_data[key] = {
                "upper_limit": (
                    index[0]["props"]["value"]
                    if "value" in index[0]["props"]
                    else ""
                ),
                "lower_limit": (
                    index[1]["props"]["value"]
                    if "value" in index[1]["props"]
                    else ""
                ),
            }
    except Exception as e:
        dict_data = {key: {"upper_limit": "", "lower_limit": ""} for key in kkm}
        print(f"Error: {e}")
    return dict_data


@omero_project_dash.expanded_callback(
    dash.dependencies.Output("delete-confirm_delete", "opened"),
    dash.dependencies.Output("delete-notifications-container", "children"),
    dash.dependencies.Output("delete-modal-submit-button", "loading"),
    [
        dash.dependencies.Input("delete_data", "n_clicks"),
        dash.dependencies.Input("delete-modal-submit-button", "n_clicks"),
        dash.dependencies.Input("delete-modal-close-button", "n_clicks"),
        dash.dependencies.State("delete-confirm_delete", "opened"),
    ],
    prevent_initial_call=True,
)
def delete_project(*args, **kwargs):
    try:
        triggered_button = kwargs["callback_context"].triggered[0]["prop_id"]
        project_id = kwargs["session_state"]["context"]["project_id"]
        request = kwargs["request"]
        opened = not args[3]
        if triggered_button == "delete-modal-submit-button.n_clicks" and args[0] > 0:
            response_type, response_msg = views.delete_project(
                request, project_id=project_id
            )

            return my_components.notification_handler(
                response_type, response_msg, opened
            )
        else:
            return opened, None, False
    except Exception as e:
        return dash.no_update


@omero_project_dash.expanded_callback(
    dash.dependencies.Output("download", "data"),
    [
        dash.dependencies.Input("download-yaml", "n_clicks"),
        dash.dependencies.Input("download-json", "n_clicks"),
        dash.dependencies.Input("download-text", "n_clicks"),
    ],
    prevent_initial_call=True,
)
def download_project_data(*args, **kwargs):
    try:
        if not kwargs["callback_context"].triggered:
            raise dash.no_update

        triggered_id = (
            kwargs["callback_context"].triggered[0]["prop_id"].split(".")[0]
        )
        context = kwargs["session_state"]["context"]
        mm_dataset_collection = deserialize(context["mm_dataset_collection"])
        file_name = context["project_name"]
        yaml_dumper = YAMLDumper()
        json_dumper = JSONDumper()
        if triggered_id == "download-yaml":
            return dict(
                content=yaml_dumper.dumps(mm_dataset_collection),
                filename=f"{file_name}.yaml",
            )

        elif triggered_id == "download-json":
            return dict(
                content=json_dumper.dumps(mm_dataset_collection),
                filename=f"{file_name}.json",
            )

        elif triggered_id == "download-text":
            return dict(
                content=yaml_dumper.dumps(mm_dataset_collection),
                filename=f"{file_name}.txt",
            )

        raise dash.no_update
    except Exception as e:
        return dash.no_update


omero_project_dash.clientside_callback(
    """
    function loadingDeleteButton(n_clicks) {
        if (n_clicks > 0) {
            return true;
        }
        return false;
    }
    """,
    dash.dependencies.Output(
        "delete-modal-submit-button", "loading", allow_duplicate=True
    ),
    dash.dependencies.Input("delete-modal-submit-button", "n_clicks"),
    prevent_initial_call=True,
)
