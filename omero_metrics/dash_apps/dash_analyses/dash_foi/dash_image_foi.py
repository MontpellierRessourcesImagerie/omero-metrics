import dash
import dash_mantine_components as dmc
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, html
from django_plotly_dash import DjangoDash

import omero_metrics.dash_apps.dash_utils.omero_metrics_components as my_components
from omero_metrics.styles import (
    LINE_CHART_SERIES,
    MANTINE_THEME,
    PLOTLY_LAYOUT,
    THEME,
)
from omero_metrics.tools.serializers import deserialize_partial

dashboard_name = "omero_image_foi"
omero_image_foi = DjangoDash(
    name=dashboard_name,
    serve_locally=True,
)


def create_control_panel():
    return dmc.Paper(
        h="100%",
        shadow="xs",
        p="md",
        radius="md",
        children=[
            dmc.Stack(
                [
                    dmc.Text(
                        "Visualization Controls",
                        size="lg",
                        fw=500,
                        c=THEME["primary"],
                    ),
                    dmc.Divider(
                        label="Channel Selection",
                        labelPosition="center",
                    ),
                    dmc.Select(
                        id="channel_dropdown",
                        label="Channel",
                        w="100%",
                        allowDeselect=False,
                        leftSection=my_components.get_icon(
                            "material-symbols:layers"
                        ),
                        rightSection=my_components.get_icon(
                            "radix-icons:chevron-down"
                        ),
                        styles={
                            "rightSection": {"pointerEvents": "none"},
                            "item": {"fontSize": "14px"},
                            "input": {"borderColor": THEME["primary"]},
                        },
                    ),
                    dmc.Divider(
                        label="Display Options",
                        labelPosition="center",
                        mt="md",
                    ),
                    dmc.SegmentedControl(
                        id="segmented",
                        value="All",
                        data=[
                            {"value": "Center", "label": "Center"},
                            {"value": "Line", "label": "Line"},
                            {"value": "Square", "label": "Square"},
                            {"value": "All", "label": "All"},
                            {"value": "None", "label": "None"},
                        ],
                        color=THEME["primary"],
                        fullWidth=True,
                    ),
                    dmc.Stack(
                        [
                            dmc.Checkbox(
                                id="checkbox-state",
                                label="Enable Contour View",
                                checked=False,
                                color=THEME["primary"],
                            ),
                        ],
                        gap="xs",
                    ),
                    dmc.Divider(
                        label="Color Settings",
                        labelPosition="center",
                        mt="md",
                    ),
                    dmc.Select(
                        id="color_select",
                        label="Color Scheme",
                        allowDeselect=False,
                        data=[
                            {
                                "value": "Hot",
                                "label": "Hot",
                            },
                            {
                                "value": "Viridis",
                                "label": "Viridis",
                            },
                            {
                                "value": "Inferno",
                                "label": "Inferno",
                            },
                        ],
                        value="Hot",
                        leftSection=my_components.get_icon(
                            "material-symbols:palette"
                        ),
                        styles={
                            "rightSection": {"pointerEvents": "none"},
                            "item": {"fontSize": "14px"},
                            "input": {"borderColor": THEME["primary"]},
                        },
                    ),
                    dmc.Switch(
                        id="switch-invert-colors",
                        label="Invert Colors",
                        checked=False,
                        size="md",
                        color=THEME["primary"],
                    ),
                ],
                gap="sm",
            ),
        ],
    )


def create_intensity_profile():
    return dmc.Paper(
        h="100%",
        children=[
            dmc.Stack(
                [
                    dmc.Group(
                        [
                            dmc.Text(
                                "Intensity Profiles",
                                size="lg",
                                fw=500,
                                c=THEME["primary"],
                            ),
                            dmc.Badge(
                                "Microscope-Metrics Analysis",
                                color="blue",
                                variant="light",
                                size="sm",
                            ),
                        ],
                        justify="space-between",
                    ),
                    dmc.LineChart(
                        id="intensity_profile",
                        h=250,
                        dataKey="Pixel",
                        data={},
                        series=LINE_CHART_SERIES,
                        xAxisLabel="Position (pixels)",
                        yAxisLabel="Intensity",
                        gridAxis="x",
                        withXAxis=True,
                        withYAxis=True,
                        withLegend=True,
                        strokeWidth=2,
                        withDots=False,
                        curveType="linear",
                    ),
                ],
                gap="md",
            ),
        ],
        p="md",
        radius="md",
        withBorder=True,
        shadow="sm",
    )


omero_image_foi.layout = dmc.MantineProvider(
    [
        my_components.header_component(
            "OMERO Image Analysis",
            "Interactive analysis of image data",
            "FOI Analysis",
            load_buttons=False,
        ),
        dmc.Container(
            [
                dmc.Grid(
                    [
                        dmc.GridCol(
                            [
                                dmc.Paper(
                                    [
                                        dmc.Text(
                                            "Intensity Map",
                                            size="lg",
                                            fw=500,
                                            c=THEME["primary"],
                                            mb="md",
                                        ),
                                        dcc.Graph(
                                            id="rois-graph",
                                            style={"height": "400px"},
                                        ),
                                    ],
                                    p="md",
                                    radius="md",
                                    withBorder=True,
                                    shadow="sm",
                                ),
                            ],
                            span=8,
                        ),
                        dmc.GridCol(
                            create_control_panel(),
                            span=4,
                        ),
                    ],
                    gutter="md",
                ),
                dmc.Space(h="md"),
                create_intensity_profile(),
                html.Div(id="blank-input", style={"display": "none"}),
            ],
            size="xl",
            px="md",
            py="md",
            style={"backgroundColor": THEME["background"]},
        ),
    ],
    theme=MANTINE_THEME,
)


@omero_image_foi.expanded_callback(
    dash.dependencies.Output("channel_dropdown", "data"),
    dash.dependencies.Output("channel_dropdown", "value"),
    [dash.dependencies.Input("blank-input", "children")],
)
def callback_channel(_, **kwargs):
    ctx = deserialize_partial(kwargs["session_state"]["context"], "mm_image")
    mm_image = ctx["mm_image"]
    return [
        {"label": c.name, "value": str(i), "description": f"Channel {i+1}"}
        for i, c in enumerate(mm_image.channel_series.channels)
    ], "0"


@omero_image_foi.expanded_callback(
    dash.dependencies.Output("rois-graph", "figure"),
    [
        dash.dependencies.Input("channel_dropdown", "value"),
        dash.dependencies.Input("color_select", "value"),
        dash.dependencies.Input("checkbox-state", "checked"),
        dash.dependencies.Input("switch-invert-colors", "checked"),
        dash.dependencies.Input("segmented", "value"),
    ],
)
def callback_image(channel, color, checked_contour, inverted_color, roi, **kwargs):
    context = kwargs["session_state"]["context"]
    ctx = deserialize_partial(context, "mm_image")
    mm_image = ctx["mm_image"]
    if inverted_color:
        color = color + "_r"
    image_data = mm_image.array_data[0, 0, :, :, int(channel)]
    image_data = np.float32(image_data / image_data.max())
    df_lines = pd.DataFrame(context["rois_lines"])
    df_rects = pd.DataFrame(context["rois_rectangles"])
    df_points = pd.DataFrame(context["rois_points"])
    df_lines.columns = df_lines.columns.str.upper()
    df_rects.columns = df_rects.columns.str.upper()
    df_points.columns = df_points.columns.str.upper()

    df_point_channel = df_points[df_points["C"] == int(channel)].copy()

    fig = px.imshow(
        image_data,
        zmin=image_data.min(),
        zmax=image_data.max(),
        color_continuous_scale=color,
    )
    fig.add_trace(
        go.Scatter(
            x=df_point_channel.X,
            y=df_point_channel.Y,
            mode="markers",
            marker=dict(
                size=8,
                color="red",
                line=dict(width=1, color="white"),
            ),
            customdata=df_point_channel.ROI_NAME.str.replace(" ROIs", ""),
            hovertemplate="<b>%{customdata}</b><br>X: %{x}<br>Y: %{y}<extra></extra>",
        )
    )
    # TODO: it can make the page unresponsive, fix the bug
    if checked_contour:
        fig.plotly_restyle({"type": "contour"}, 0)
        fig.update_yaxes(autorange="reversed")

    fig.update_layout(**PLOTLY_LAYOUT)
    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis=dict(showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showgrid=False, zeroline=False, visible=False),
    )
    corners = [
        dict(
            type="rect",
            x0=row.X,
            y0=row.Y,
            x1=row.X + row.W,
            y1=row.Y + row.H,
            xref="x",
            yref="y",
            line=dict(
                color="RoyalBlue",
                width=2,
            ),
        )
        for i, row in df_rects.iterrows()
    ]

    lines = [
        dict(
            type="line",
            x0=row.X1,
            y0=row.Y1,
            x1=row.X2,
            y1=row.Y2,
            xref="x",
            yref="y",
            line=dict(
                color="RoyalBlue",
                width=2,
                dash="dash",
            ),
        )
        for i, row in df_lines.iterrows()
    ]

    if roi == "All":
        fig.update_layout(shapes=corners + lines)
        fig.plotly_restyle({"visible": True}, 1)
    elif roi == "Line":
        fig.update_layout(shapes=lines)
        fig.plotly_restyle({"visible": False}, 1)
    elif roi == "Square":
        fig.update_layout(shapes=corners)
        fig.plotly_restyle({"visible": False}, 1)
    elif roi == "Center":
        fig.update_layout(shapes=None)
        fig.plotly_restyle({"visible": True}, 1)
    elif roi == "None":
        fig.update_layout(shapes=None)
        fig.plotly_restyle({"visible": False}, 1)

    return fig


@omero_image_foi.expanded_callback(
    dash.dependencies.Output("intensity_profile", "data"),
    [dash.dependencies.Input("channel_dropdown", "value")],
)
def update_intensity_profiles(channel, **kwargs):
    try:
        ctx = deserialize_partial(
            kwargs["session_state"]["context"], "intensity_profiles"
        )
        df_intensity_profiles = ctx["intensity_profiles"]
        df_profile = df_intensity_profiles.filter(regex=f"ch0*{channel}_")
        df_profile.columns = (
            df_profile.columns.str.replace(
                r"ch\d+_leftTop_to_rightBottom", "Diagonal (↘)", regex=True
            )
            .str.replace(r"ch\d+_leftBottom_to_rightTop", "Diagonal (↗)", regex=True)
            .str.replace(r"ch\d+_center_horizontal", "Horizontal (→)", regex=True)
            .str.replace(r"ch\d+_center_vertical", "Vertical (↓)", regex=True)
        )
        df_profile.insert(0, "Pixel", range(len(df_profile)))
        return df_profile.to_dict("records")
    except Exception as e:
        return [{"Pixel": 0}]
