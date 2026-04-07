import dash
import dash_mantine_components as dmc
import pandas as pd
import plotly.express as px
from dash import dcc, html
from django_plotly_dash import DjangoDash
from skimage.exposure import rescale_intensity

import omero_metrics.dash_apps.dash_utils.omero_metrics_components as my_components
from omero_metrics.dash_apps.dash_analyses import dataset_shared_components as dsc
from omero_metrics.styles import (
    CONTAINER_STYLE,
    CONTENT_PAPER_STYLE,
    GRAPH_STYLE,
    INPUT_BASE_STYLES,
    LINE_CHART_SERIES,
    MANTINE_THEME,
    PLOT_LAYOUT,
    THEME,
)
from omero_metrics.tools.serializers import deserialize_partial

dashboard_name = "omero_dataset_foi"
omero_dataset_foi = DjangoDash(
    name=dashboard_name,
    serve_locally=True,
)

omero_dataset_foi.layout = dmc.MantineProvider(
    theme=MANTINE_THEME,
    children=[
        dsc.notification_provider(),
        dsc.notifications_container(),
        dsc.confirm_delete_modal(),
        dsc.dataset_header_paper(
            "Field Illumination", "Dataset Analysis", "FOI Analysis"
        ),
        dmc.Container(
            children=[
                # Main Content
                dmc.Grid(
                    gutter="md",
                    align="stretch",
                    children=[
                        # Left Column - Intensity Map
                        dmc.GridCol(
                            span=6,
                            children=[
                                dmc.Paper(
                                    children=[
                                        dmc.Stack(
                                            [
                                                dmc.Group(
                                                    [
                                                        dmc.Text(
                                                            "Intensity Map",
                                                            fw=500,
                                                            size="lg",
                                                        ),
                                                        dmc.Select(
                                                            id="channel_dropdown_foi",
                                                            clearable=False,
                                                            allowDeselect=False,
                                                            w="200",
                                                            leftSection=my_components.get_icon(
                                                                icon="material-symbols:layers"
                                                            ),
                                                            rightSection=my_components.get_icon(
                                                                icon="radix-icons:chevron-down"
                                                            ),
                                                            styles=INPUT_BASE_STYLES,
                                                        ),
                                                    ],
                                                    justify="space-between",
                                                ),
                                                dcc.Graph(
                                                    id="intensity_map",
                                                    config={
                                                        "displayModeBar": True,
                                                        "scrollZoom": True,
                                                        "modeBarButtonsToRemove": [
                                                            "lasso2d",
                                                            "select2d",
                                                        ],
                                                    },
                                                    style=GRAPH_STYLE,
                                                ),
                                            ],
                                            gap="md",
                                            justify="space-between",
                                            h="100%",
                                        ),
                                    ],
                                    **CONTENT_PAPER_STYLE,
                                ),
                            ],
                        ),
                        # Right Column - Key Measurements
                        dmc.GridCol(
                            span=6,
                            children=[
                                dsc.dataset_table_paper(),
                            ],
                        ),
                    ],
                ),
                # Hidden element for callbacks
                html.Div(id="blank-input"),
                # Intensity Profiles Section
                dmc.Paper(
                    children=[
                        dmc.Stack(
                            [
                                dmc.Group(
                                    [
                                        dmc.Text(
                                            "Intensity Profiles",
                                            fw=500,
                                            size="lg",
                                        ),
                                        dmc.SegmentedControl(
                                            id="profile-type",
                                            data=[
                                                {
                                                    "value": "natural",
                                                    "label": "Smooth",
                                                },
                                                {
                                                    "value": "linear",
                                                    "label": "Linear",
                                                },
                                            ],
                                            value="natural",
                                            color=THEME["primary"],
                                        ),
                                    ],
                                    justify="space-between",
                                ),
                                dmc.LineChart(
                                    id="intensity_profile",
                                    h=300,
                                    dataKey="Pixel",
                                    data={},
                                    series=LINE_CHART_SERIES,
                                    xAxisLabel="Position (pixels)",
                                    yAxisLabel="Intensity",
                                    tickLine="y",
                                    gridAxis="x",
                                    withXAxis=True,
                                    withYAxis=True,
                                    withLegend=True,
                                    strokeWidth=2,
                                    withDots=False,
                                ),
                            ],
                            gap="xl",
                        ),
                    ],
                    shadow="xs",
                    p="md",
                    radius="md",
                    mt="md",
                ),
            ],
            style=CONTAINER_STYLE,
        ),
    ],
)


# Register shared callbacks
dsc.register_delete_dataset_callback(omero_dataset_foi)
dsc.register_download_datasets_callback(omero_dataset_foi)
dsc.register_update_kkm_table_callback(omero_dataset_foi)
dsc.register_download_table_callback(omero_dataset_foi)


@omero_dataset_foi.expanded_callback(
    dash.dependencies.Output("channel_dropdown_foi", "data"),
    dash.dependencies.Output("channel_dropdown_foi", "value"),
    [dash.dependencies.Input("blank-input", "children")],
)
def update_dropdown_menu(*args, **kwargs):
    try:
        channel_names = kwargs["session_state"]["context"]["channel_names"]
        return [
            {"label": str(name), "value": str(i)}
            for i, name in enumerate(channel_names)
        ], "0"
    except Exception as e:
        return [{"label": "Error loading channels", "value": "0"}], "0"


@omero_dataset_foi.expanded_callback(
    dash.dependencies.Output("intensity_map", "figure"),
    [
        dash.dependencies.Input("channel_dropdown_foi", "value"),
    ],
)
def update_intensity_map(channel, **kwargs):
    try:
        channel = int(channel)
        ctx = deserialize_partial(kwargs["session_state"]["context"], "image_data")
        images = ctx["image_data"]
        image = images[channel]
        image_channel = image[0, 0, :, :]
        image_channel = rescale_intensity(
            image_channel,
            in_range=(0, image_channel.max()),
            out_range=(0.0, 1.0),
        )
        # Create intensity map
        fig = px.imshow(
            image_channel,
            color_continuous_scale="hot",
            labels={"color": "Intensity"},
        )
        fig.update_layout(
            **PLOT_LAYOUT,
            xaxis_title="X Position (pixels)",
            yaxis_title="Y Position (pixels)",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            coloraxis_colorbar=dict(
                thickness=15,
                len=0.7,
                title=dict(text="Intensity", side="right"),
                tickfont=dict(size=10),
            ),
        )
        return fig
    except Exception as e:
        fig = px.imshow([[0]])
        fig.add_annotation(
            text=f"Error loading data: {str(e)}",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        return fig


@omero_dataset_foi.expanded_callback(
    dash.dependencies.Output("intensity_profile", "data"),
    dash.dependencies.Output("intensity_profile", "curveType"),
    [
        dash.dependencies.Input("channel_dropdown_foi", "value"),
        dash.dependencies.Input("profile-type", "value"),
    ],
)
def update_profile_type(channel, curve_type, **kwargs):
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
        return df_profile.to_dict("records"), curve_type

    except Exception as e:
        return [{"Pixel": 0}], "linear"


def restyle_dataframe(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """Improve column names for better readability."""
    value = getattr(df, col).str.replace("_", " ", regex=True).str.title()
    setattr(df, col, value)
    return df


omero_dataset_foi.clientside_callback(
    """
    function(n_clicks) {
        if (n_clicks > 0) {
            return true;
        }
        return false;
    }
    """,
    dash.dependencies.Output(
        "confirm-delete-button", "loading", allow_duplicate=True
    ),
    dash.dependencies.Input("confirm-delete-button", "n_clicks"),
    prevent_initial_call=True,
)
