from datetime import datetime
from typing import Union

import dash_mantine_components as dmc
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, html
from dash_iconify import DashIconify
from plotly.subplots import make_subplots

from omero_metrics.styles import (
    BUTTON_STYLE,
    COLORS_CHANNELS,
    HEADER_PAPER_STYLE,
    THEME,
)


def alert_handler(
    response_type,
    response_msg,
    response_details=None,
    with_close_button=None,
    duration=None,
):

    if response_type == "success":
        title = "Success!"
        icon = get_icon(icon="radix-icons:check")
        color = "green"
    elif response_type == "authorisation_error":
        title = "Authorisation Error!"
        icon = get_icon(icon="radix-icons:lock-closed")
        color = "red"
    elif response_type == "analysis_error":
        title = "Analysis Error!"
        icon = get_icon(icon="radix-icons:alert")
        color = "orange"
    elif response_type == "unidentified_error":
        title = "Error!"
        icon = get_icon(icon="radix-icons:alert")
        color = "red"

    children = [dmc.Text(response_msg, size="sm")]
    if response_details:
        children.append(dmc.Code(response_details, block=True))

    return [
        dmc.Alert(
            children=children,
            color=color,
            icon=icon,
            title=title,
            radius="md",
            withCloseButton=with_close_button,
            duration=duration,
        )
    ], False


def notification_handler(response_type, response_msg, opened):
    if response_type == "success":
        title = "Success!"
        icon = get_icon(icon="radix-icons:check")
        color = "green"
    elif response_type == "authorisation_error":
        title = "Authorisation Error!"
        icon = get_icon(icon="radix-icons:lock-closed")
        color = "red"
    elif response_type == "unidentified_error":
        title = "Error!"
        icon = get_icon(icon="radix-icons:alert")
        color = "red"

    notification = dmc.Notification(
        title=title,
        id="simple-notify",
        action="show",
        message=response_msg,
        icon=icon,
        color=color,
    )
    return opened, notification, False


def get_icon(icon, size=20, color=None):
    return DashIconify(icon=icon, height=size, color=color)


def make_control(text, action_id):
    return dmc.Flex(
        [
            dmc.AccordionControl(text),
            dmc.ActionIcon(
                children=get_icon(icon="lets-icons:check-fill"),
                color="green",
                variant="default",
                n_clicks=0,
                id={"index": action_id},
            ),
        ],
        justify="center",
        align="center",
    )


download_group = dmc.Group(
    [
        dmc.Menu(
            [
                dmc.MenuTarget(
                    dmc.Button(
                        id="activate_download",
                        children="Download",
                        leftSection=DashIconify(
                            icon="material-symbols:download", width=20
                        ),
                        rightSection=DashIconify(
                            icon="carbon:chevron-down", width=20
                        ),
                        color=THEME["primary"],
                        variant="outline",
                    )
                ),
                dmc.MenuDropdown(
                    [
                        dmc.MenuItem(
                            "YAML",
                            id="download-yaml",
                            leftSection=DashIconify(
                                icon="vscode-icons:file-type-yaml", width=20
                            ),
                        ),
                        dmc.MenuItem(
                            "JSON",
                            id="download-json",
                            leftSection=DashIconify(
                                icon="vscode-icons:file-type-json", width=20
                            ),
                        ),
                        dmc.MenuItem(
                            "Text",
                            id="download-text",
                            leftSection=DashIconify(
                                icon="vscode-icons:file-type-text", width=20
                            ),
                        ),
                    ]
                ),
            ],
            trigger="click",
        ),
        dcc.Download(id="download"),
    ]
)


download_table = dmc.Group(
    [
        dmc.Menu(
            [
                dmc.MenuTarget(
                    dmc.ActionIcon(
                        DashIconify(icon="material-symbols:download", width=20),
                        color=THEME["primary"],
                    )
                ),
                dmc.MenuDropdown(
                    [
                        dmc.MenuItem(
                            "CSV",
                            id="table-download-csv",
                            leftSection=DashIconify(icon="iwwa:file-csv", width=20),
                        ),
                        dmc.MenuItem(
                            "Excel",
                            id="table-download-xlsx",
                            leftSection=DashIconify(
                                icon="vscode-icons:file-type-excel", width=20
                            ),
                        ),
                        dmc.MenuItem(
                            "JSON",
                            id="table-download-json",
                            leftSection=DashIconify(
                                icon="vscode-icons:file-type-json", width=20
                            ),
                        ),
                    ]
                ),
            ],
            trigger="click",
        ),
        dcc.Download(id="table-download"),
    ]
)


delete_button = dmc.Button(
    id="delete_data",
    children="Delete",
    color="red",
    variant="filled",
    leftSection=DashIconify(icon="ic:round-delete-forever"),
)


def header_component(title, description, tag, load_buttons=True, context_info=None):
    title_children = [
        dmc.Title(title, order=3, c=THEME["text"]["primary"]),
        dmc.Text(description, c=THEME["text"]["secondary"], size="sm"),
    ]
    if context_info:
        title_children.append(
            dmc.Text(context_info, size="xs", c=THEME["text"]["muted"])
        )

    badge = dmc.Badge(
        tag,
        color="green",
        variant="light",
        size="md",
        radius="sm",
    )

    right_section = (
        dmc.Group(
            [download_group, delete_button, badge],
            gap="sm",
        )
        if load_buttons
        else badge
    )

    return dmc.Paper(
        children=[
            dmc.Group(
                [
                    dmc.Group(
                        [
                            html.Div(
                                style={
                                    "width": "4px",
                                    "height": "48px",
                                    "backgroundColor": THEME["primary"],
                                    "borderRadius": "2px",
                                    "flexShrink": "0",
                                },
                            ),
                            dmc.Stack(title_children, gap=4),
                        ],
                        gap="md",
                    ),
                    right_section,
                ],
                justify="space-between",
                align="flex-start",
            ),
        ],
        **HEADER_PAPER_STYLE,
    )


def thresholds_paper(accordion_children):
    return [
        dmc.Accordion(
            id="accordion-compose-controls",
            chevron=DashIconify(icon="ant-design:plus-outlined"),
            disableChevronRotation=True,
            children=accordion_children,
        ),
        dmc.Group(
            justify="flex-end",
            mt="xl",
            children=[
                dmc.Button(
                    "Update",
                    id="modal-submit-button",
                    style=BUTTON_STYLE,
                ),
            ],
        ),
        html.Div(id="notifications-container"),
    ]


def get_title_line_chart(project_id, value):
    title = dmc.Text(f"Project ID: {project_id}")
    dates = value["dates"]
    kkm = value["kkm"]
    dfs = value["key_measurements_list"]
    measurement = 0
    df = get_data_trends(kkm, measurement, dates, dfs)
    channels = [c for c in df.columns if c not in ["dataset_index", "date"]]
    series = [
        {
            "name": channel,
            "color": COLORS_CHANNELS[i % len(COLORS_CHANNELS)],
        }
        for i, channel in enumerate(channels)
    ]
    line_chart = dmc.LineChart(
        id=f"line-chart-{project_id}",
        h=300,
        dataKey="date",
        withLegend=True,
        legendProps={
            "horizontalAlign": "top",
            "left": 50,
        },
        data=df.to_dict("records"),
        series=series,
        curveType="linear",
        style={"padding": 20},
        xAxisLabel="Processed Date",
        connectNulls=True,
    )
    return title, line_chart


def get_data_trends(kkm, measurement, dates, dfs):
    complete_df = pd.DataFrame()
    for i, df in enumerate(dfs):
        dfi = df.pivot_table(columns="channel_name", values=kkm).reset_index(
            names="Measurement"
        )
        dfi["dataset_index"] = i
        dfi["date"] = dates[i]
        complete_df = pd.concat([complete_df, dfi])
    complete_df = complete_df.reset_index(drop=True)
    complete_df = complete_df[complete_df["Measurement"] == kkm[measurement]]
    complete_df = complete_df.drop(columns="Measurement")
    return complete_df


def empty_state(
    icon="material-symbols:info-outline",
    title="No data available",
    description="",
):
    """Reusable empty/placeholder state component."""
    children = [
        get_icon(icon=icon, size=48, color="dimmed"),
        dmc.Text(title, size="lg", fw=500, c="dimmed", ta="center"),
    ]
    if description:
        children.append(dmc.Text(description, size="sm", c="dimmed", ta="center"))
    return dmc.Stack(
        children=children,
        align="center",
        justify="center",
        gap="sm",
        style={"minHeight": "200px", "padding": "40px"},
    )
