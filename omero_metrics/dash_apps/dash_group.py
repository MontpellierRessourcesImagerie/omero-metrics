import dash
import dash_mantine_components as dmc
import pandas as pd
from dash import dash_table, dcc, html
from django_plotly_dash import DjangoDash

import omero_metrics.dash_apps.dash_utils.omero_metrics_components as my_components
from omero_metrics import views
from omero_metrics.styles import (
    CONTAINER_STYLE,
    DATEPICKER_STYLES,
    HEADER_PAPER_STYLE,
    MANTINE_THEME,
    PAPER_STYLE,
    STYLE_DATA_CONDITIONAL,
    TAB_ITEM_STYLE,
    TAB_STYLES,
    TABLE_CELL_STYLE,
    TABLE_HEADER_STYLE,
    TABLE_STYLE,
    THEME,
)

dashboard_name = "omero_group_dash"
dash_app_group = DjangoDash(
    name=dashboard_name,
    serve_locally=True,
)


dash_app_group.layout = dmc.MantineProvider(
    theme=MANTINE_THEME,
    children=[
        dmc.NotificationProvider(position="top-center"),
        html.Div(id="notifications-container"),
        dmc.Paper(
            children=[
                dmc.Group(
                    [
                        dmc.Group(
                            [
                                html.Img(
                                    src="/static/omero_metrics/images/metrics_logo.png",
                                    style={
                                        "width": "120px",
                                        "height": "auto",
                                    },
                                ),
                                dmc.Stack(
                                    [
                                        dmc.Title(
                                            "Group Dashboard",
                                            c=THEME["primary"],
                                            size="h2",
                                        ),
                                        dmc.Text(
                                            "Group Analysis Dashboard",
                                            c=THEME["text"]["secondary"],
                                            size="sm",
                                        ),
                                    ],
                                    gap="xs",
                                ),
                            ],
                        ),
                        dmc.Badge(
                            "Group Analysis",
                            color=THEME["primary"],
                            variant="dot",
                            size="lg",
                        ),
                    ],
                    justify="space-between",
                ),
            ],
            **HEADER_PAPER_STYLE,
        ),
        dmc.Tabs(
            styles=TAB_STYLES,
            children=[
                dmc.TabsList(
                    [
                        dmc.TabsTab(
                            "Microscope Health",
                            leftSection=my_components.get_icon(
                                icon="tabler:microscope"
                            ),
                            value="microscope_health",
                            color=THEME["primary"],
                            style=TAB_ITEM_STYLE,
                        ),
                        dmc.TabsTab(
                            "History",
                            leftSection=my_components.get_icon(icon="bx:history"),
                            value="history",
                            color=THEME["primary"],
                            style=TAB_ITEM_STYLE,
                        ),
                    ],
                    grow=True,
                    justify="space-around",
                    variant="light",
                    style={"backgroundColor": THEME["surface"]},
                ),
                dmc.TabsPanel(
                    dmc.Container(
                        [
                            dmc.Paper(
                                children=[
                                    dmc.Group(
                                        [
                                            html.Img(
                                                src="/static/omero_metrics/images/microscope.png",
                                                style={
                                                    "width": "100px",
                                                    "objectFit": "contain",
                                                },
                                            ),
                                            dmc.Stack(
                                                [
                                                    dmc.Title(
                                                        "Microscope Health Dashboard",
                                                        c=THEME["primary"],
                                                        size="h3",
                                                    ),
                                                    dmc.Text(
                                                        "View information about your microscope group",
                                                        c="dimmed",
                                                        size="sm",
                                                    ),
                                                ],
                                                gap=5,
                                            ),
                                        ],
                                        justify="space-between",
                                        align="center",
                                    ),
                                    dmc.Divider(mb="md"),
                                    html.Div(id="microscope_info"),
                                ],
                                withBorder=True,
                                shadow="sm",
                                radius="md",
                                p="lg",
                                style=PAPER_STYLE,
                            ),
                        ],
                        fluid=True,
                        style=CONTAINER_STYLE,
                    ),
                    value="microscope_health",
                ),
                dmc.TabsPanel(
                    dmc.Container(
                        children=[
                            dmc.Paper(
                                children=[
                                    dmc.Group(
                                        [
                                            dmc.Button(
                                                id="download_table",
                                                children=[
                                                    my_components.get_icon(
                                                        icon="ic:round-download"
                                                    ),
                                                    "Download",
                                                ],
                                                variant="filled",
                                                color=THEME["primary"],
                                                w="auto",
                                            ),
                                            dcc.Download(id="download"),
                                            dmc.DatePickerInput(
                                                id="date-picker",
                                                label="Select Date Range",
                                                valueFormat="DD-MM-YYYY",
                                                type="range",
                                                w=250,
                                                leftSection=my_components.get_icon(
                                                    icon="clarity:date-line"
                                                ),
                                                styles=DATEPICKER_STYLES,
                                            ),
                                            dmc.Button(
                                                id="delete-all",
                                                children=[
                                                    my_components.get_icon(
                                                        icon="ic:round-delete-forever"
                                                    ),
                                                    "Delete All",
                                                ],
                                                variant="filled",
                                                color="red",
                                                w=250,
                                            ),
                                            dmc.Modal(
                                                title="Confirm Delete",
                                                id="confirm_delete",
                                                children=[
                                                    dmc.Text(
                                                        "Are you sure you want to delete all annotations including ROIs?"
                                                    ),
                                                    dmc.Space(h=20),
                                                    dmc.Group(
                                                        [
                                                            dmc.Button(
                                                                "Submit",
                                                                id="modal-submit-button",
                                                                color="red",
                                                            ),
                                                            dmc.Button(
                                                                "Close",
                                                                color="gray",
                                                                variant="outline",
                                                                id="modal-close-button",
                                                            ),
                                                        ],
                                                        justify="flex-end",
                                                    ),
                                                ],
                                            ),
                                        ],
                                        justify="space-between",
                                        align="flex-end",
                                    ),
                                    dmc.Space(h=20),
                                    dmc.Divider(mb="md"),
                                    dmc.Space(h=20),
                                    dmc.Text(
                                        "File Annotations",
                                        c=THEME["primary"],
                                        size="xl",
                                    ),
                                    html.Div(
                                        id="project_file_annotations_table",
                                        style={"margin": "10px"},
                                    ),
                                    html.Div(id="blank-input"),
                                    html.Div(id="result"),
                                ],
                                withBorder=True,
                                shadow="sm",
                                radius="md",
                                p="lg",
                            ),
                        ],
                        fluid=True,
                        style=CONTAINER_STYLE,
                    ),
                    value="history",
                ),
            ],
            value="microscope_health",
        ),
    ],
)


@dash_app_group.expanded_callback(
    dash.dependencies.Output("date-picker", "value"),
    dash.dependencies.Output("date-picker", "minDate"),
    dash.dependencies.Output("date-picker", "maxDate"),
    [dash.dependencies.Input("blank-input", "children")],
)
def update_date_range(*args, **kwargs):
    df = pd.read_json(kwargs["session_state"]["context"]["file_ann"])
    min_date = df.Date.min()
    max_date = df.Date.max()
    return [min_date, max_date], min_date, max_date


@dash_app_group.expanded_callback(
    dash.dependencies.Output("microscope_info", "children"),
    dash.dependencies.Input("blank-input", "children"),
)
def render_content(*args, **kwargs):
    group_name = kwargs["session_state"]["context"]["group_name"]
    group_id = kwargs["session_state"]["context"]["group_id"]
    group_description = kwargs["session_state"]["context"]["group_description"]
    return dmc.Stack(
        [
            dmc.Title("Microscope Information", c=THEME["primary"], order=4),
            dmc.Text(f"Group Name: {group_name}", size="sm"),
            dmc.Text(f"Group ID: {group_id}", size="sm"),
            dmc.Text(f"Group Description: {group_description}", size="sm"),
        ],
        align="flex-start",
        gap="xs",
    )


@dash_app_group.expanded_callback(
    dash.dependencies.Output("project_file_annotations_table", "children"),
    [
        dash.dependencies.Input("date-picker", "value"),
    ],
    prevent_initial_call=True,
)
def load_table_project(dates, **kwargs):
    file_ann = pd.read_json(kwargs["session_state"]["context"]["file_ann"])
    if dates is not None:
        file_ann = file_ann[
            (file_ann["Date"].dt.date >= pd.to_datetime(dates[0]).date())
            & (file_ann["Date"].dt.date <= pd.to_datetime(dates[1]).date())
        ]

    else:
        pass

    file_ann_subset = file_ann[
        file_ann.columns[~file_ann.columns.str.contains("ID")]
    ].copy()
    file_ann_table = dash_table.DataTable(
        id="datatable_file_ann",
        data=file_ann_subset.to_dict("records"),
        sort_action="native",
        sort_mode="multi",
        row_selectable="multi",
        page_action="native",
        page_current=0,
        page_size=5,
        style_table=TABLE_STYLE,
        style_cell=TABLE_CELL_STYLE,
        style_header=TABLE_HEADER_STYLE,
        style_data_conditional=STYLE_DATA_CONDITIONAL,
    )
    return file_ann_table


@dash_app_group.expanded_callback(
    dash.dependencies.Output("confirm_delete", "opened"),
    dash.dependencies.Output("notifications-container", "children"),
    dash.dependencies.Output("modal-submit-button", "loading"),
    [
        dash.dependencies.Input("delete-all", "n_clicks"),
        dash.dependencies.Input("modal-submit-button", "n_clicks"),
        dash.dependencies.Input("modal-close-button", "n_clicks"),
        dash.dependencies.State("confirm_delete", "opened"),
    ],
    prevent_initial_call=True,
)
def delete_all_callback(*args, **kwargs):
    triggered_button = kwargs["callback_context"].triggered[0]["prop_id"]
    group_id = kwargs["session_state"]["context"]["group_id"]
    request = kwargs["request"]
    opened = not args[3]
    if triggered_button == "modal-submit-button.n_clicks" and args[0] > 0:
        response_type, response_msg = views.delete_all(request, group_id=group_id)

        return my_components.notification_handler(
            response_type, response_msg, opened
        )
    else:
        return opened, None, False


@dash_app_group.expanded_callback(
    dash.dependencies.Output("download", "data"),
    dash.dependencies.Input("download_table", "n_clicks"),
    dash.dependencies.State("datatable_file_ann", "data"),
    prevent_initial_call=True,
)
def download_file(*args, **kwargs):
    table_data = args[1]
    df = pd.DataFrame(table_data)
    return dcc.send_data_frame(df.to_csv, "File_annotation.csv")


dash_app_group.clientside_callback(
    """
    function loadingDeleteButtonGroup(n_clicks) {
        if (n_clicks > 0) {
            return true;
        }
        return false;
    }
    """,
    dash.dependencies.Output("modal-submit-button", "loading", allow_duplicate=True),
    dash.dependencies.Input("modal-submit-button", "n_clicks"),
    prevent_initial_call=True,
)
